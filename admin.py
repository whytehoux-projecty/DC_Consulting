#!/usr/bin/env python3
"""DC Consulting site admin — a local control panel.

Run:   python3 admin.py
Open:  the address it prints (http://127.0.0.1:8765)

It edits content/content.json, stores uploaded images in content/assets/, and
rebuilds the finished site into dist/. It only listens on your own computer.
Upload the dist/ folder to your web host when you are happy with the result.
No third-party packages are needed."""
import base64, json, os, re, secrets, shutil, subprocess, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import build  # noqa: E402  (defines DEFAULTS, SCHEMA, load)

DIST = os.path.join(ROOT, "dist")
CONTENT_DIR = os.path.join(ROOT, "content")
ASSET_DIR = os.path.join(CONTENT_DIR, "assets")
BACKUP_DIR = os.path.join(CONTENT_DIR, "backups")
ADMIN_HTML = os.path.join(ROOT, "admin", "index.html")
PORT = int(os.environ.get("ADMIN_PORT", "8765"))
TOKEN = secrets.token_urlsafe(24)
MAX_BODY = 8 * 1024 * 1024
MAX_TEXT = 6000

FIELD_TYPES = {f["key"]: f["type"] for g in build.SCHEMA for f in g["fields"]}
IMAGE_EXT = {".png": b"\x89PNG", ".jpg": b"\xff\xd8\xff", ".jpeg": b"\xff\xd8\xff", ".webp": b"RIFF", ".svg": None}
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json",
        ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8"}


def clean_values(raw):
    """Keep only known keys, enforce types and limits."""
    if not isinstance(raw, dict):
        raise ValueError("Invalid data")
    out = {}
    for key, ftype in FIELD_TYPES.items():
        v = raw.get(key, build.DEFAULTS[key])
        if not isinstance(v, str):
            raise ValueError(f"{key} must be text")
        v = v.strip()
        if len(v) > MAX_TEXT:
            raise ValueError(f"{key} is too long")
        if ftype == "url" and v and not re.match(r"^https?://\S+$", v, re.I):
            raise ValueError(f"{key} must start with http:// or https://")
        if ftype == "image" and v:
            if not re.match(r"^assets/[A-Za-z0-9._-]+$", v) or not os.path.isfile(os.path.join(CONTENT_DIR, v)):
                raise ValueError(f"{key}: image not found, upload it again")
        out[key] = v
    reps = raw.get("replacements", [])
    if not isinstance(reps, list) or len(reps) > 50:
        raise ValueError("Too many replacement rules (max 50)")
    clean = []
    for r in reps:
        if not (isinstance(r, list) and len(r) == 2 and all(isinstance(x, str) for x in r)):
            raise ValueError("Invalid replacement rule")
        if not r[0].strip() or len(r[0]) > 200 or len(r[1]) > 200:
            raise ValueError("Each rule needs text to find (max 200 characters)")
        clean.append([r[0], r[1]])
    out["replacements"] = clean
    return out


def save_content(values):
    os.makedirs(CONTENT_DIR, exist_ok=True)
    path = os.path.join(CONTENT_DIR, "content.json")
    if os.path.isfile(path):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        shutil.copy(path, os.path.join(BACKUP_DIR, time.strftime("content-%Y%m%d-%H%M%S.json")))
        old = sorted(os.listdir(BACKUP_DIR))
        for name in old[:-20]:
            os.remove(os.path.join(BACKUP_DIR, name))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(values, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def rebuild():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "build.py")], cwd=ROOT,
                       capture_output=True, text=True, timeout=60)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def store_image(filename, b64):
    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in IMAGE_EXT:
        raise ValueError("Use a PNG, JPG, WebP or SVG image")
    try:
        data = base64.b64decode(b64, validate=True)
    except Exception:
        raise ValueError("Could not read the image data")
    if not data or len(data) > 5 * 1024 * 1024:
        raise ValueError("Image must be under 5 MB")
    sig = IMAGE_EXT[ext]
    if sig is not None and not data.startswith(sig):
        raise ValueError("That file does not look like a real " + ext[1:].upper() + " image")
    if ext == ".svg":
        low = data.lower()
        if any(b in low for b in (b"<script", b"javascript:", b"onload=", b"onerror=", b"<foreignobject", b"<iframe")):
            raise ValueError("This SVG contains active content and was rejected. Export a plain SVG or use PNG.")
    stem = re.sub(r"[^A-Za-z0-9_-]+", "-", os.path.splitext(os.path.basename(filename))[0]).strip("-")[:40] or "image"
    name = f"{stem}-{secrets.token_hex(3)}{ext}"
    os.makedirs(ASSET_DIR, exist_ok=True)
    with open(os.path.join(ASSET_DIR, name), "wb") as f:
        f.write(data)
    return "assets/" + name


class Handler(BaseHTTPRequestHandler):
    server_version = "DCAdmin"

    def log_message(self, fmt, *args):
        pass

    # ---- helpers
    def _host_ok(self):
        return (self.headers.get("Host") or "") in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def _send(self, code, body, ctype="application/json", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _api_ok(self):
        if not self._host_ok():
            self._send(403, {"error": "Forbidden"})
            return False
        if self.headers.get("X-Admin-Token") != TOKEN:
            self._send(403, {"error": "Session expired. Reload the page."})
            return False
        return True

    def _json_body(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        if n <= 0 or n > MAX_BODY:
            raise ValueError("Request too large or empty")
        if "application/json" not in (self.headers.get("Content-Type") or ""):
            raise ValueError("Expected JSON")
        return json.loads(self.rfile.read(n).decode("utf-8"))

    # ---- GET
    def do_GET(self):
        if not self._host_ok():
            return self._send(403, "Forbidden", "text/plain")
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            with open(ADMIN_HTML, encoding="utf-8") as f:
                page = f.read().replace("__TOKEN__", TOKEN)
            return self._send(200, page, "text/html; charset=utf-8",
                              {"Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'"})
        if path == "/api/state":
            if not self._api_ok():
                return
            return self._send(200, {"values": build.load(), "schema": build.SCHEMA,
                                    "built": os.path.isfile(os.path.join(DIST, "index.html"))})
        if path.startswith("/content/assets/"):
            name = os.path.basename(path)
            return self._file(os.path.join(ASSET_DIR, name))
        if path == "/site" or path == "/site/":
            self.send_response(302)
            self.send_header("Location", "/site/index.html")
            self.end_headers()
            return
        if path.startswith("/site/"):
            rel = path[len("/site/"):]
            full = os.path.realpath(os.path.join(DIST, rel))
            if not full.startswith(os.path.realpath(DIST) + os.sep):
                return self._send(404, "Not found", "text/plain")
            return self._file(full)
        return self._send(404, "Not found", "text/plain")

    def _file(self, full):
        if not os.path.isfile(full):
            return self._send(404, "Not found", "text/plain")
        ext = os.path.splitext(full)[1].lower()
        with open(full, "rb") as f:
            data = f.read()
        extra = {"Content-Security-Policy": "script-src 'none'"} if ext == ".svg" else {}
        self._send(200, data, MIME.get(ext, "application/octet-stream"), extra)

    # ---- POST
    def do_POST(self):
        path = urlparse(self.path).path
        if not self._api_ok():
            return
        try:
            body = self._json_body()
            if path == "/api/content":
                values = clean_values(body)
                save_content(values)
                ok, log = rebuild()
                return self._send(200 if ok else 500, {"ok": ok, "log": log})
            if path == "/api/upload":
                rel = store_image(body.get("filename", ""), body.get("data", ""))
                return self._send(200, {"path": rel})
            return self._send(404, {"error": "Unknown action"})
        except (ValueError, KeyError) as e:
            return self._send(400, {"error": str(e)})
        except Exception as e:  # keep the server alive, show a readable message
            return self._send(500, {"error": f"Unexpected error: {e}"})


def main():
    os.makedirs(ASSET_DIR, exist_ok=True)
    if not os.path.isfile(os.path.join(DIST, "index.html")):
        rebuild()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"\nDC Consulting admin is running.\n  Open:  http://127.0.0.1:{PORT}\n  Stop:  press Ctrl+C\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
