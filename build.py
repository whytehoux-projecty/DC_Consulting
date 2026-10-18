#!/usr/bin/env python3
"""Generates the DC Consulting static site into ./dist.
Run:  python3 build.py
Edit SITE below and the page bodies, then rebuild. No dependencies."""
import os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

import json, html as _html, re

CONTENT_FILE = os.path.join(ROOT, "content", "content.json")
ASSET_DIR = os.path.join(ROOT, "content", "assets")

DEFAULTS = {
    "name": "DC Consulting",
    "tagline": "Sourcing, documentation & logistics",
    "domain": "https://www.example.com",
    "email": "enquiries@example.com",
    "phone": "[Phone number]",
    "address": "[Registered office address]",
    "company_no": "[Company name & registration number]",
    "form_endpoint": "",
    "logo": "",
    "hero_image": "",
    "hero_alt": "",
    "linkedin": "", "x": "", "facebook": "", "instagram": "",
    "home_eyebrow": "Ground execution for physical commodity contracts",
    "home_h1": "We turn procurement mandates into delivered cargo.",
    "home_lead": "DC Consulting sources, processes, documents and ships rare earth minerals, crude oil and gemstones. We work with procurement firms and directly with corporations and institutions.",
    "about_p1": "Procurement firms and trading houses are good at winning mandates from large buyers. Delivering on those mandates in producing regions needs people, facilities and relationships on the ground. DC Consulting provides that capability.",
    "about_p2": "We work across rare earth minerals, crude oil and gemstones, and take on other strategic materials case by case. We are a contractor, not a trading house: our job is to execute the physical delivery of a contract that someone else holds.",
    "about_region": "West and Central Africa, with delivery to international ports and vaults",
    "ceo_name": "", "ceo_title": "", "ceo_photo": "", "ceo_message": "",
    "replacements": [],
}

# Drives the admin form. type: text | textarea | image | url
SCHEMA = [
    {"group": "Company", "fields": [
        {"key": "name", "label": "Company name", "type": "text", "help": "Changing this renames the company everywhere on the site."},
        {"key": "tagline", "label": "Tagline under the logo", "type": "text"},
        {"key": "email", "label": "Public email (also receives enquiries)", "type": "text"},
        {"key": "phone", "label": "Phone", "type": "text"},
        {"key": "address", "label": "Office address", "type": "text"},
        {"key": "company_no", "label": "Registered company name & number", "type": "text"},
        {"key": "domain", "label": "Website address (https://…)", "type": "url", "help": "Used for search engines and sharing previews."},
        {"key": "form_endpoint", "label": "Form service URL (optional)", "type": "url", "help": "Leave empty to make the enquiry form open the visitor's email app."},
    ]},
    {"group": "Logo and images", "fields": [
        {"key": "logo", "label": "Logo", "type": "image", "help": "PNG, JPG, WebP or SVG. Shown at about 40px tall."},
        {"key": "hero_image", "label": "Home page banner image", "type": "image", "help": "Wide image (about 1600x900). Optional."},
        {"key": "hero_alt", "label": "Banner image description", "type": "text", "help": "Describe the image for visitors who cannot see it."},
    ]},
    {"group": "Social media links", "fields": [
        {"key": "linkedin", "label": "LinkedIn URL", "type": "url"},
        {"key": "x", "label": "X (Twitter) URL", "type": "url"},
        {"key": "facebook", "label": "Facebook URL", "type": "url"},
        {"key": "instagram", "label": "Instagram URL", "type": "url"},
    ]},
    {"group": "Home page text", "fields": [
        {"key": "home_eyebrow", "label": "Small line above the headline", "type": "text"},
        {"key": "home_h1", "label": "Headline", "type": "text"},
        {"key": "home_lead", "label": "Introduction", "type": "textarea"},
    ]},
    {"group": "About page text", "fields": [
        {"key": "about_p1", "label": "First paragraph", "type": "textarea"},
        {"key": "about_p2", "label": "Second paragraph", "type": "textarea"},
        {"key": "about_region", "label": "Operating region", "type": "text"},
    ]},
    {"group": "CEO message", "fields": [
        {"key": "ceo_name", "label": "Name", "type": "text"},
        {"key": "ceo_title", "label": "Title", "type": "text"},
        {"key": "ceo_photo", "label": "Photo", "type": "image"},
        {"key": "ceo_message", "label": "Message", "type": "textarea", "help": "Leave empty to hide this section. Blank line = new paragraph."},
    ]},
]

def load():
    c = json.loads(json.dumps(DEFAULTS))
    try:
        with open(CONTENT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data.items():
            if k in c:
                c[k] = v
    except (FileNotFoundError, ValueError):
        pass
    return c

C = load()

def esc(t):
    return _html.escape(str(t), quote=True)

def paras(t):
    chunks = [x.strip() for x in re.split(r"\n\s*\n", str(t)) if x.strip()]
    return "".join(f"<p>{esc(x)}</p>" for x in chunks)

def safe_url(u):
    u = (u or "").strip()
    return u if re.match(r"^https?://", u, re.I) else ""

def safe_asset(p):
    p = (p or "").strip()
    return p if re.match(r"^assets/[A-Za-z0-9._-]+$", p) else ""

OLD_NAME = "DC Consulting"
SITE = {
    "name": esc(C["name"].strip() or OLD_NAME),
    "domain": esc(C["domain"].strip().rstrip("/") or DEFAULTS["domain"]),
    "email": esc(C["email"].strip() or DEFAULTS["email"]),
    "phone": esc(C["phone"].strip() or DEFAULTS["phone"]),
    "address": esc(C["address"].strip() or DEFAULTS["address"]),
    "company_no": esc(C["company_no"].strip() or DEFAULTS["company_no"]),
}

def initials(name):
    words = re.findall(r"[A-Za-z0-9]+", name)
    if not words:
        return "DC"
    return (words[0][0] + (words[1][0] if len(words) > 1 else words[0][1:2])).upper()

INITIALS = initials(C["name"])

def todo(t):
    """Yellow highlight for unfilled placeholders; plain text once filled in."""
    return f'<span class="todo">{t}</span>' if t.startswith("[") else t

try:
    with open(os.path.join(ROOT, "src/img/illustrations/sizes.json"), encoding="utf-8") as _f:
        IMG_SIZES = json.load(_f)
except (OSError, ValueError):
    IMG_SIZES = {}

def picture(name, alt, sizes, cls="", eager=False):
    """<picture> with AVIF, WebP and JPEG sources from src/img/illustrations (see sizes.json)."""
    meta = IMG_SIZES.get(name)
    if not meta:
        return ""
    widths = sorted(int(w) for w in meta["variants"])
    def srcset(fmt):
        return ", ".join(f'img/illustrations/{meta["variants"][str(w)]["files"][fmt]["file"]} {w}w' for w in widths)
    big = meta["variants"][str(widths[-1])]
    mid = meta["variants"][str(widths[len(widths) // 2])]
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img class="illustration {cls}" src="img/illustrations/{mid["files"]["jpeg"]["file"]}" '
            f'srcset="{srcset("jpeg")}" sizes="{sizes}" alt="{alt}" width="{big["width"]}" height="{big["height"]}" {load}></picture>')

try:
    with open(os.path.join(ROOT, "src/img/editorial/sizes.json"), encoding="utf-8") as _f:
        EDITORIAL_SIZES = json.load(_f)
except (OSError, ValueError):
    EDITORIAL_SIZES = {}

def editorial_picture(name, alt, sizes="(min-width: 900px) 600px, 100vw", cls="", eager=False, caption=None):
    """<picture> for editorial photography from src/img/editorial (see sizes.json)."""
    meta = EDITORIAL_SIZES.get(name)
    if not meta:
        return ""
    widths = sorted(int(w) for w in meta["variants"])
    def srcset(fmt):
        return ", ".join(f'img/editorial/{meta["variants"][str(w)]["files"][fmt]["file"]} {w}w' for w in widths)
    big = meta["variants"][str(widths[-1])]
    mid = meta["variants"][str(widths[len(widths) // 2])]
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    pic = (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
           f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
           f'<img class="editorial-img {cls}" src="img/editorial/{mid["files"]["jpeg"]["file"]}" '
           f'srcset="{srcset("jpeg")}" sizes="{sizes}" alt="{alt}" width="{big["width"]}" height="{big["height"]}" {load}></picture>')
    if caption:
        return f'<figure class="media-frame {cls}">{pic}<figcaption class="media-caption">{caption}</figcaption></figure>'
    return f'<div class="media-frame {cls}">{pic}</div>'

_logo = safe_asset(C["logo"])
BRAND_MARK = (f'<img class="brand-logo" src="{_logo}" alt="" height="40">' if _logo
              else '<img class="brand-logo brand-logo--mark" src="img/brand/logo-mark.svg" alt="" width="40" height="40">')

_hero = safe_asset(C["hero_image"])
HERO_ALT = esc(C["hero_alt"]) if C.get("hero_alt") else "Illustration of a supply route from mineral, oil and gem origins to a port and vault"
HERO_SIZES = "(min-width: 900px) 480px, calc(100vw - 4.5rem)"
if _hero:
    HERO_IMG = f'<img class="hero-img" src="{_hero}" alt="{HERO_ALT}" width="1600" height="900" fetchpriority="high">'
    HERO_PRELOAD = ""
else:
    HERO_IMG = editorial_picture("global-trade-routes-office", "Executive operations room with a backlit world map of global shipping routes", sizes=HERO_SIZES)
    HERO_PRELOAD = ""

# Bespoke glyphs: mitred strokes, square caps, drawn on a 24px grid to match the site's engineered geometry.
_SOCIAL_GLYPHS = {
    "linkedin": '<path d="M6 10v8.5"/><path d="M10.5 18.5V10"/><path d="M10.5 13.6c0-2.1 1.5-3.6 3.6-3.6s3.4 1.3 3.4 3.6v4.9"/><path d="M6 5.6v.9" stroke-width="2.6"/>',
    "x": '<path d="M5 4.5h3.6L19 19.5h-3.6z"/><path d="M18.6 4.5l-5.1 6.1"/><path d="M5.4 19.5l5.2-6.2"/>',
    "facebook": '<path d="M13.6 20.5V9.4c0-2.8 1.3-4.4 3.9-4.4h.9"/><path d="M9.8 12.4h7.6"/>',
    "instagram": '<path d="M5 5h14v14H5z"/><circle cx="12" cy="12" r="3.4"/><path d="M16.6 7.4h.01" stroke-width="2.4"/>',
}
_social_defs = [("linkedin", "LinkedIn"), ("x", "X"), ("facebook", "Facebook"), ("instagram", "Instagram")]

def _social_tile(k, lbl):
    svg = (f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
           f'stroke-width="1.7" stroke-linecap="square" stroke-linejoin="miter">{_SOCIAL_GLYPHS[k]}</svg>')
    url = safe_url(C[k])
    if url:
        return f'<a class="social" href="{esc(url)}" target="_blank" rel="noopener noreferrer" aria-label="{esc(C["name"].strip() or OLD_NAME)} on {lbl}" title="{lbl}">{svg}</a>'
    return f'<span class="social is-off" aria-hidden="true">{svg}</span>'

SOCIALS = '<div class="social-row" role="group" aria-label="Social media"><span class="social-label">Follow</span>' + "".join(_social_tile(k, l) for k, l in _social_defs) + '</div>'

def _ceo_section():
    photo = safe_asset(C["ceo_photo"])
    if photo:
        img = f'<img class="ceo-photo" src="{photo}" alt="{esc(C["ceo_name"] or "Managing Director")}" width="160" height="160">'
    else:
        img = f'<div class="ceo-portrait-frame">{editorial_picture("leadership-director-portrait", "Executive Managing Director of DC Consulting", sizes="200px", cls="ceo-portrait-img")}</div>'
    
    msg = C["ceo_message"].strip() or "Our team brings together field operations, laboratory verification and commodity logistics across West and Central Africa. When you contract with DC Consulting, you deal directly with principals who are personally accountable for cargo delivery."
    name = C["ceo_name"].strip() or "Executive Leadership"
    title = C["ceo_title"].strip() or "Managing Director & Head of Physical Execution"
    who = f'<p class="ceo-who"><strong>{esc(name)}</strong><br><span class="small">{esc(title)}</span></p>'
    return f'''<section class="section"><div class="container">
  <div class="section-head"><span class="eyebrow">Message from leadership</span><h2>Principal accountability on every mandate</h2></div>
  <div class="ceo-card ceo-card--editorial">{img}<div>{paras(msg)}{who}</div></div>
</div></section>'''

CEO_SECTION = _ceo_section()
LEADERSHIP = (esc(C["ceo_name"] + (", " + C["ceo_title"] if C["ceo_title"].strip() else ""))
              if C["ceo_name"].strip() else todo("[Names, roles and short bios of directors]"))
ABOUT_NOTICE = ('<aside class="notice"><strong>Before you rely on this page:</strong> add the company’s registered details, licences and leadership above. Institutional buyers will look for them first.</aside>'
                if SITE["company_no"].startswith("[") else "")

# Old icon keys -> ids in src/img/icons.svg
ICON_IDS = {
    "mineral": "mineral", "oil": "oil", "gem": "gem", "other": "other-materials",
    "source": "source", "process": "process", "docs": "documents", "ship": "ship",
    "shield": "shield-check", "eye": "inspect", "link": "chain", "one": "one-contract",
}

def icon(name):
    return (f'<div class="icon" aria-hidden="true"><svg class="icon-svg" viewBox="0 0 24 24" focusable="false">'
            f'<use href="img/icons.svg#{ICON_IDS[name]}"/></svg></div>')

def card_img(name, sizes="(min-width: 960px) 360px, (min-width: 700px) 50vw, 100vw"):
    if name in EDITORIAL_SIZES:
        meta = EDITORIAL_SIZES[name]
        widths = sorted(int(w) for w in meta["variants"])
        def srcset(fmt):
            return ", ".join(f'img/editorial/{meta["variants"][str(w)]["files"][fmt]["file"]} {w}w' for w in widths)
        big = meta["variants"][str(widths[-1])]
        mid = meta["variants"][str(widths[len(widths) // 2])]
        pic = (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
               f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
               f'<img class="illustration" src="img/editorial/{mid["files"]["jpeg"]["file"]}" '
               f'srcset="{srcset("jpeg")}" sizes="{sizes}" alt="" width="{big["width"]}" height="{big["height"]}" loading="lazy" decoding="async"></picture>')
        return f'<div class="card-media">{pic}</div>'
    return f'<div class="card-media">{picture(name, "", sizes)}</div>'

NAV = [
    ("index.html", "Home"),
    ("about.html", "About"),
    ("services.html", "Services"),
    ("commodities.html", "Commodities"),
    ("compliance.html", "Compliance"),
    ("contact.html", "Contact"),
]

def header(active):
    cur = lambda h: ' aria-current="page"' if h == active else ""
    links = "".join(
        f'<li><a href="{h}"{cur(h)}>{t}</a></li>' for h, t in NAV)
    mlinks = "".join(
        f'<a href="{h}"{cur(h)}>{t}</a>' for h, t in NAV)
    live_badge = "" if active == "index.html" else '<span class="live"><i class="dot" aria-hidden="true"></i>Mandate desk open</span>'
    return f'''<a class="skip-link" href="#main">Skip to main content</a>
<div class="status-bar" role="note"><div class="container status-inner">
  <span class="st-hide">B2B &middot; Corporate, Defence &amp; Government mandates</span>
  <span class="st-hide">NCNDA available on request</span>
  {live_badge}
</div></div>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html" aria-label="{SITE["name"]} home">
      {BRAND_MARK}
      <span class="brand-name">{SITE["name"]}<span class="brand-sub">{esc(C["tagline"])}</span></span>
    </a>
    <nav class="nav" aria-label="Main"><ul>{links}</ul></nav>
    <a class="btn btn--sm header-cta" href="contact.html">Submit Mandate</a>
    <button class="menu-btn" id="menu-btn" aria-expanded="false" aria-controls="mobile-nav" aria-label="Open menu">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
  </div>
  <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile">{mlinks}<a class="btn" href="contact.html">Submit Mandate</a></nav>
</header>'''

def footer():
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html">{BRAND_MARK}<span class="brand-name">{SITE["name"]}</span></a>
        <p class="footer-note" style="margin-top:1rem">We source, process, document and ship rare earth minerals, crude oil and gemstones for procurement firms, corporations and institutions.</p>
        <div class="footer-badges"><span class="chip chip--ok">NCNDA on request</span><span class="chip">Independent inspection</span><span class="chip">B2B only</span></div>
      </div>
      <div><h4>Company</h4><ul>
        <li><a href="about.html">About</a></li><li><a href="services.html">Services</a></li>
        <li><a href="compliance.html">Compliance</a></li><li><a href="contact.html">Contact</a></li></ul></div>
      <div><h4>Commodities</h4><ul>
        <li><a href="commodities.html#rare-earths">Rare earths</a></li><li><a href="commodities.html#crude-oil">Crude oil</a></li>
        <li><a href="commodities.html#gems">Gemstones</a></li><li><a href="commodities.html#other">Other materials</a></li></ul></div>
      <div><h4>Get in touch</h4><ul>
        <li><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>
        <li>{todo(SITE["phone"])}</li><li>{todo(SITE["address"])}</li></ul>{SOCIALS}</div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 {todo(SITE["company_no"])}. All rights reserved.</span>
      <span><a href="privacy.html">Privacy &amp; terms of use</a></span>
    </div>
  </div>
</footer>
<script src="js/config.js" defer></script>
<script src="js/main.js" defer></script>'''

def apply_text_changes(html):
    """Company rename plus user find/replace rules, applied to visible text only (never to tags, links or classes)."""
    name = SITE["name"]
    rules = []
    if name != OLD_NAME:
        rules.append((OLD_NAME, name))
    for r in C.get("replacements", []):
        try:
            find, rep = str(r[0]), str(r[1])
        except (IndexError, TypeError, KeyError):
            continue
        if find:
            rules.append((esc(find), esc(rep)))
    if not rules:
        return html
    def fix(t):
        for a, b in rules:
            t = t.replace(a, b)
        return t
    html = re.sub(r"(?<=>)([^<]+)(?=<)", lambda m: fix(m.group(1)), html)
    html = re.sub(r'(<meta (?:name|property)="(?:description|og:title|og:description|og:site_name)" content=")([^"]*)(")',
                  lambda m: m.group(1) + fix(m.group(2)) + m.group(3), html)
    return html

def page(fname, title, desc, body, head_extra=""):
    full_title = title if fname == "index.html" else f"{title} | {SITE['name']}"
    url = f'{SITE["domain"]}/{"" if fname == "index.html" else fname}'
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE["name"]}">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta name="theme-color" content="#0A1628">
<meta property="og:image" content="{SITE["domain"]}/img/social/og-default.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{SITE["name"]}: sourcing, documentation and logistics for strategic commodities">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE["domain"]}/img/social/og-default.png">
<link rel="icon" href="img/favicons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="img/favicons/apple-touch-icon.png">
<link rel="manifest" href="img/favicons/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=JetBrains+Mono:wght@400;500&amp;family=Plus+Jakarta+Sans:wght@500;600;700;800&amp;display=swap" rel="stylesheet">
<script>document.documentElement.className+=' js';</script>
<link rel="stylesheet" href="css/styles.css">
{head_extra}
</head>
<body>
{header(fname)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    html = apply_text_changes(html)
    with open(os.path.join(DIST, fname), "w", encoding="utf-8") as f:
        f.write(html)

def page_head(crumb, h1, lead):
    return f'''<section class="page-head"><div class="container">
  <p class="crumbs"><a href="index.html">Home</a> / {crumb}</p>
  <h1>{h1}</h1>
  <p class="lead">{lead}</p>
</div></section>'''

def cta(title="Have a requirement or an active mandate?", text="Tell us what you need, the quantity and where it must be delivered. We will reply with what we can and cannot do."):
    return f'''<section class="cta-band"><div class="container"><div class="cta-inner">
  <div><h2>{title}</h2><p>{text}</p></div>
  <a class="btn" href="contact.html">Submit a mandate</a>
</div></div></section>'''

# ----------------------------------------------------------------- HOME
home = f'''
<section class="hero"><div class="container hero-grid">
  <div class="reveal">
    <span class="eyebrow">{esc(C["home_eyebrow"])}</span>
    <h1>{esc(C["home_h1"])}</h1>
    <p class="lead">{esc(C["home_lead"])}</p>
    <div class="btn-row">
      <a class="btn" href="contact.html">Submit a mandate</a>
      <a class="btn btn--ghost" href="about.html">Explore how we work</a>
    </div>
  </div>
</div></section>

<section class="trust" aria-label="Execution capabilities"><div class="container trust-grid">
  <div class="trust-item"><span class="tk">01</span><div><h3>Direct origin access</h3><p>Producer, concession and terminal supply, verified before you commit.</p></div></div>
  <div class="trust-item"><span class="tk">02</span><div><h3>Specification-grade processing</h3><p>Refined, graded or blended to the buyer’s technical sheet.</p></div></div>
  <div class="trust-item"><span class="tk">03</span><div><h3>Full chain-of-custody dossier</h3><p>Permits, assays and provenance records on every shipment.</p></div></div>
  <div class="trust-item"><span class="tk">04</span><div><h3>Secured global logistics</h3><p>Tanker, container and armoured air transport, insured.</p></div></div>
</div></section>

<section class="section section--white"><div class="container">
  <div class="section-head">
    <span class="eyebrow">Why contractors like us exist</span>
    <h2>The gap between a contract and a cargo</h2>
    <p class="lead">Large buyers often hand sourcing to procurement firms. Those firms then need someone on the ground who can find material, prepare it, clear it and deliver it. That is our role.</p>
  </div>
  <div class="grid grid-3">
    <div class="card">{icon("one")}<h3>One point of accountability</h3><p>Instead of coordinating miners, laboratories, brokers and carriers separately, you work with one contractor under one agreement.</p></div>
    <div class="card">{icon("eye")}<h3>Verification you control</h3><p>Your appointed independent inspector can sample and test before release. We do not ask you to trust our word alone.</p></div>
    <div class="card">{icon("link")}<h3>Your client stays yours</h3><p>When you subcontract to us, we agree in writing not to approach your end buyer. Confidentiality terms are available before you share details.</p></div>
  </div>
  <div class="split" style="margin-top:3.5rem;align-items:center">
    <div>
      {editorial_picture("global-trade-routes-office", "Executive operations room with a backlit world map of global shipping routes", sizes="(min-width: 900px) 560px, 100vw", caption="Global trade routes: linking origin concessions directly to corporate buyer discharge ports")}
    </div>
    <div class="card card-services">
      <span class="eyebrow">Execution capability</span>
      <h2>One contractor, four services</h2>
      <ol class="steps">
        <li><strong>Source</strong><span>Secure material at origin and confirm it exists.</span></li>
        <li><strong>Process</strong><span>Refine, sort or blend to the buyer’s specification.</span></li>
        <li><strong>Document</strong><span>Assemble permits, assays and chain-of-custody records.</span></li>
        <li><strong>Ship</strong><span>Move it to the agreed port, airport or vault.</span></li>
      </ol>
    </div>
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="section-head">
    <span class="eyebrow">What we handle</span>
    <h2>Three core commodity areas</h2>
  </div>
  <div class="grid grid-3 divisions">
    <a class="card card--link card--media" href="commodities.html#rare-earths">{card_img("commodity-rare-earths-specimen")}{icon("mineral")}<h3>Rare earths &amp; critical minerals</h3><p>Concentrates and separated oxides for magnets, optics, electronics and alloys.</p><span class="more">View details →</span></a>
    <a class="card card--link card--media" href="commodities.html#crude-oil">{card_img("commodity-crude-oil-refinery")}{icon("oil")}<h3>Crude oil &amp; products</h3><p>Spot and term cargoes, terminal lifting, blending, inspection and tanker coordination.</p><span class="more">View details →</span></a>
    <a class="card card--link card--media" href="commodities.html#gems">{card_img("commodity-gems-display")}{icon("gem")}<h3>Gemstones</h3><p>Rough and cut stones, sorting and cutting, certification and insured transport.</p><span class="more">View details →</span></a>
  </div>
  <div class="bespoke"><div><span class="eyebrow">Bespoke strategic mandates</span><b>Something else, such as copper, gold doré or platinum group metals?</b><p>Send the specification and we will tell you whether we can execute it.</p></div><a class="btn btn--sm" href="commodities.html#other">Ask about other materials</a></div>
</div></section>

<section class="section section--navy" id="workflow"><div class="container">
  <div class="section-head">
    <span class="eyebrow">How an engagement runs</span>
    <h2>A clear, documented path from origin to delivery</h2>
    <p class="lead">Every mandate follows the same four stages. Engage us for the full chain or for a single stage. Select a stage to see how it differs by commodity.</p>
  </div>
  <div class="wf" data-wf>
    <div class="wf-tabs" role="tablist" aria-label="Execution stages">
      <button class="wf-tab" role="tab" id="wf-t1" aria-controls="wf-p1" aria-selected="true"><span class="n">01</span><span class="t">Sourcing</span></button>
      <button class="wf-tab" role="tab" id="wf-t2" aria-controls="wf-p2" aria-selected="false" tabindex="-1"><span class="n">02</span><span class="t">Processing</span></button>
      <button class="wf-tab" role="tab" id="wf-t3" aria-controls="wf-p3" aria-selected="false" tabindex="-1"><span class="n">03</span><span class="t">Documentation</span></button>
      <button class="wf-tab" role="tab" id="wf-t4" aria-controls="wf-p4" aria-selected="false" tabindex="-1"><span class="n">04</span><span class="t">Logistics &amp; delivery</span></button>
    </div>
    <div class="wf-panel on" role="tabpanel" id="wf-p1" aria-labelledby="wf-t1">
      <div><span class="stage-code">Stage 01 / Origin</span><h3>Sourcing and verification of supply</h3><p>Origin allocation, ownership checks and baseline sampling, so the material and the right to sell it are real before you commit.</p><div class="wf-actions"><a class="btn btn--ghost btn--sm" href="services.html">Read the full service detail</a></div></div>
      <dl class="wf-rows"><div class="wf-row"><dt>Rare earths</dt><dd>Off-take from licensed operations, with baseline sampling at source.</dd></div><div class="wf-row"><dt>Crude oil</dt><dd>Allocation lifting from producers, terminals and tank farms.</dd></div><div class="wf-row"><dt>Gemstones</dt><dd>Rough parcels from licensed producers and tenders, sealed and recorded.</dd></div></dl>
    </div>
    <div class="wf-panel" role="tabpanel" id="wf-p2" aria-labelledby="wf-t2">
      <div><span class="stage-code">Stage 02 / Specification</span><h3>Processing to specification</h3><p>Beneficiation, refining, blending, sorting or cutting to the buyer’s technical requirements before export.</p><div class="wf-actions"><a class="btn btn--ghost btn--sm" href="services.html">Read the full service detail</a></div></div>
      <dl class="wf-rows"><div class="wf-row"><dt>Rare earths</dt><dd>Crushing, milling, separation and chemical processing through partner plants.</dd></div><div class="wf-row"><dt>Crude oil</dt><dd>Terminal blending, water and sediment treatment, gravity and sulphur alignment.</dd></div><div class="wf-row"><dt>Gemstones</dt><dd>Cleaning, sorting, grading, sawing, cutting and polishing.</dd></div></dl>
    </div>
    <div class="wf-panel" role="tabpanel" id="wf-p3" aria-labelledby="wf-t3">
      <div><span class="stage-code">Stage 03 / Dossier</span><h3>Documentation and compliance</h3><p>Permits, assay reports, provenance records and banking documents, assembled so cargo can be cleared and financed.</p><div class="wf-actions"><a class="btn btn--ghost btn--sm" href="compliance.html">See the document set</a></div></div>
      <dl class="wf-rows"><div class="wf-row"><dt>Origin &amp; permits</dt><dd>Certificates of origin, export licences, royalty and tax clearance.</dd></div><div class="wf-row"><dt>Inspection</dt><dd>Assay, quality and quantity reports from the surveyor you appoint.</dd></div><div class="wf-row"><dt>Provenance &amp; banking</dt><dd>Chain-of-custody records, invoices, packing lists and bills of lading.</dd></div></dl>
    </div>
    <div class="wf-panel" role="tabpanel" id="wf-p4" aria-labelledby="wf-t4">
      <div><span class="stage-code">Stage 04 / Delivery</span><h3>Logistics and delivery</h3><p>Chartering, containers or secured air transport, with insurance, and the chain of custody kept intact until handover.</p><div class="wf-actions"><a class="btn btn--ghost btn--sm" href="services.html">Read the full service detail</a></div></div>
      <dl class="wf-rows"><div class="wf-row"><dt>Crude oil</dt><dd>Vessel chartering support, ship-to-ship coordination and discharge management.</dd></div><div class="wf-row"><dt>Rare earths &amp; bulk</dt><dd>Sealed drums and bulk bags in containers, with hazardous-goods clearance where needed.</dd></div><div class="wf-row"><dt>Gemstones</dt><dd>Courier or vault-to-vault secured air transport, with insurance.</dd></div></dl>
    </div>
  </div>
</div></section>

{cta()}
'''

# ----------------------------------------------------------------- ABOUT
about = page_head("About", "A contractor for the physical side of the deal",
    "We do the field work that sits behind procurement contracts: finding material, preparing it, clearing it and delivering it.") + f'''
<section class="section section--white"><div class="container split split--wide-left">
  <div>
    <span class="eyebrow">Who we are</span>
    <h2>What {SITE["name"]} does</h2>
    {paras(C["about_p1"])}{paras(C["about_p2"])}
    <dl class="facts">
      <div><dt>Registered entity</dt><dd>{todo(SITE["company_no"])}</dd></div>
      <div><dt>Operating region</dt><dd>{esc(C["about_region"])}</dd></div>
      <div><dt>Works with</dt><dd>Procurement firms, corporations, government institutions</dd></div>
      <div><dt>Leadership</dt><dd>{LEADERSHIP}</dd></div>
    </dl>
  </div>
  <div>
    {editorial_picture("corporate-mandate-execution", "Executive director reviewing procurement mandate agreements under confidentiality terms", sizes="(min-width: 900px) 460px, 100vw", caption="Physical execution bound by written non-circumvention agreements")}
    {ABOUT_NOTICE}
  </div>
</div></section>

{CEO_SECTION}

<section class="section"><div class="container split">
  <div>
    <div class="section-head" style="margin-bottom:1.5rem">
      <span class="eyebrow">Where we fit</span>
      <h2>Who does what in a typical contract</h2>
      <p class="lead">Many deals pass through three layers. We sit in the last one, and we do not go around the layers above us.</p>
    </div>
    <div class="flow">
      <div class="flow-node"><span class="flow-label">Tier 1</span><h3>End buyer</h3><p>A manufacturer, refinery, government institution or other organisation that needs the material.</p></div>
      <div class="flow-arrow" aria-hidden="true">↓ gives a purchasing mandate</div>
      <div class="flow-node"><span class="flow-label">Tier 2</span><h3>Procurement firm or trading house</h3><p>Holds the buyer relationship and the commercial terms. Needs someone to execute on the ground.</p></div>
      <div class="flow-arrow" aria-hidden="true">↓ subcontracts physical execution</div>
      <div class="flow-node flow-node--us"><span class="flow-label">Tier 3</span><h3>{SITE["name"]}</h3><p>Sources, processes, documents and ships. Bound by a written non-circumvention and confidentiality agreement.</p></div>
    </div>
  </div>
  <div style="align-self: center;">
    {editorial_picture("global-trade-routes-office", "Global trade route mapping connecting origin concessions to international discharge ports", sizes="(min-width: 900px) 500px, 100vw", caption="Global trade routes: linking origin concessions directly to corporate buyer discharge ports")}
  </div>
</div></section>

<section class="section section--tint"><div class="container">
  <div class="section-head"><span class="eyebrow">Who we serve</span><h2>Four kinds of client</h2></div>
  <div class="grid grid-4">
    <div class="card"><h3>Procurement firms</h3><p>Subcontract origin-to-port execution while keeping your end-buyer relationship private.</p></div>
    <div class="card"><h3>Corporations &amp; manufacturers</h3><p>Secure feedstock such as oxides, concentrates or distillates through a verifiable supply route.</p></div>
    <div class="card"><h3>Government &amp; institutions</h3><p>Strategic reserve and energy supply mandates, with full documentation for public-sector review.</p></div>
    <div class="card"><h3>Trading houses &amp; refiners</h3><p>Physical lifting, blending and shipping support for cargoes you have already contracted.</p></div>
  </div>
</div></section>
{cta("Talk to us about your mandate")}
'''

# ----------------------------------------------------------------- SERVICES
def service(n, ic, title, intro, cols, linktxt, linkhref, img_name=None, img_alt="", img_caption=""):
    cards = "".join(f'<div class="card"><h4>{t}</h4><p class="small" style="color:var(--ink-2)">{d}</p></div>' for t, d in cols)
    img_html = editorial_picture(img_name, img_alt, sizes="(min-width: 900px) 460px, 100vw", caption=img_caption) if img_name else ""
    return f'''<section class="section {"section--white" if n % 2 else ""}"><div class="container">
  <div class="service-split">
    <div>
      {icon(ic)}<span class="eyebrow">Stage {n}</span><h2>{title}</h2><p class="lead">{intro}</p>
      <div style="margin-top:1.5rem">{img_html}</div>
      <div style="margin-top:1.5rem"><a class="btn btn--ghost btn--sm" href="{linkhref}">{linktxt}</a></div>
    </div>
    <div class="grid" style="gap:1rem">{cards}</div>
  </div>
</div></section>'''

services = page_head("Services", "Four stages, used together or one at a time",
    "Engage us for the whole chain from origin to delivery, or subcontract only the stage you need.") + \
service(1, "source", "Sourcing and verification of supply",
    "We identify producers, concessions and terminals that can supply your specification, and confirm that the material and the right to sell it are real before you commit.",
    [("Rare earths & minerals", "Off-take from licensed operations, with baseline sampling at source."),
     ("Crude oil & products", "Allocation lifting from producers, terminals and tank farms."),
     ("Gemstones", "Rough parcels from licensed producers and tenders, sealed and recorded.")],
    "Start with sourcing", "contact.html",
    img_name="sourcing-gemstone-tender",
    img_alt="Secure gemstone tender room with sealed parcels, precision balance and bonded vault door",
    img_caption="Stage 1: Concession title verification, origin allocation and parcel inspection") + \
service(2, "process", "Processing to specification",
    "Raw material is prepared to the buyer’s technical requirements before export, to improve purity, grade compliance and transport efficiency.",
    [("Minerals", "Crushing, milling, magnetic or flotation separation and chemical processing through partner plants."),
     ("Crude & distillates", "Terminal blending, water and sediment treatment, and gravity and sulphur alignment."),
     ("Gemstones", "Cleaning, sorting, grading, sawing, cutting and polishing.")],
    "Send a specification", "contact.html",
    img_name="processing-facility-plant",
    img_alt="Industrial processing facility with ore conveyor and chemical refining reactors",
    img_caption="Stage 2: Milling, chemical beneficiation and grade alignment to buyer specification") + \
service(3, "docs", "Documentation and compliance",
    "We assemble the paperwork that customs, banks and compliance teams require. Cargo without a complete document set cannot be cleared or financed.",
    [("Origin & permits", "Certificates of origin, export licences, royalty and tax clearance."),
     ("Independent inspection", "Assay, quality and quantity reports from the surveyor you appoint."),
     ("Provenance & banking", "Chain-of-custody records, invoices, packing lists, bills of lading and documents formatted for letters of credit.")],
    "See the document set", "compliance.html",
    img_name="compliance-documentation-desk",
    img_alt="Export documentation desk with dossiers, official stamps and seals",
    img_caption="Stage 3: Export permits, surveyor assays and bankable letter-of-credit presentation") + \
service(4, "ship", "Logistics and delivery",
    "We arrange transport on the terms you choose and keep the chain of custody intact until handover.",
    [("Tankers", "Vessel chartering support, ship-to-ship coordination and discharge management."),
     ("Containers & bulk", "Sealed drums and bulk bags in containers, with hazardous-goods clearance where needed."),
     ("Secured air", "Courier or vault-to-vault transport for high-value stones, with insurance.")],
    "Discuss delivery", "contact.html",
    img_name="logistics-intermodal-hub",
    img_alt="Intermodal freight logistics hub coordinating container trucks, rail transport and air cargo",
    img_caption="Stage 4: Vessel chartering, containerized freight and secured vault-to-vault air transport") + cta()

# ----------------------------------------------------------------- COMMODITIES
def commodity(id_, ic, title, intro, tags, rows, img_name=None, img_alt="", img_caption=""):
    tag_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    facts = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
    img_html = editorial_picture(img_name, img_alt, sizes="(min-width: 900px) 460px, 100vw", caption=img_caption) if img_name else ""
    return f'''<section id="{id_}" class="commodity reveal" data-division="{id_}">
  <div class="commodity-head">{icon(ic)}<div><h2>{title}</h2><p>{intro}</p></div></div>
  <div class="commodity-grid">
    <div>
      <div class="tag-row">{tag_html}</div>
      <dl class="facts">{facts}</dl>
      <div class="btn-row"><a class="btn btn--sm" href="contact.html?division={title_param[id_]}">Enquire about this</a></div>
    </div>
    <div>
      {img_html}
    </div>
  </div>
</section>'''

title_param = {
    "rare-earths": "Rare%20earths%20%26%20critical%20minerals",
    "crude-oil": "Crude%20oil%20%26%20petroleum%20products",
    "gems": "Gemstones",
    "other": "Other%20materials",
}

commodities = page_head("Commodities", "What we handle",
    "Specifications and verification steps for each commodity area. Technical parameters are agreed per contract.") + f'''
<div class="filter-bar"><div class="container"><div class="filter-row" role="group" aria-label="Filter by division">
  <button type="button" class="filter-btn" data-filter="all" aria-pressed="true">All divisions</button>
  <button type="button" class="filter-btn" data-filter="rare-earths" aria-pressed="false">Rare earths &amp; critical minerals</button>
  <button type="button" class="filter-btn" data-filter="crude-oil" aria-pressed="false">Crude oil &amp; energy</button>
  <button type="button" class="filter-btn" data-filter="gems" aria-pressed="false">Gemstones</button>
  <button type="button" class="filter-btn" data-filter="other" aria-pressed="false">Bespoke / other</button>
  <span class="filter-count" id="filter-count" aria-live="polite"></span>
</div></div></div>
<div class="subnav"><div class="container"><ul>
  <li><a href="#rare-earths">Rare earths</a></li><li><a href="#crude-oil">Crude oil</a></li>
  <li><a href="#gems">Gemstones</a></li><li><a href="#other">Other materials</a></li></ul></div></div>
<section class="section"><div class="container">
''' + commodity("rare-earths", "mineral", "Rare earths &amp; critical minerals",
    "Used in permanent magnets, lasers and optics, electronics, alloys and batteries. We supply concentrates and separated products to the specification you give us.",
    ["Nd / Pr", "Dy / Tb", "Y / La / Gd", "Ta / Nb", "W", "Ti", "Li / Co", "MREC"],
    [("Forms", "Mixed carbonate, concentrates, separated oxides"),
     ("Purity", "Set by the buyer’s specification and confirmed by laboratory assay"),
     ("Packaging", "Steel drums or UN-certified bulk bags, in sealed containers"),
     ("Verification", "ICP-MS assay by an independent laboratory appointed by the buyer"),
     ("Provenance", "OECD due diligence approach to responsible mineral supply chains"),
     ("Note", "Radioactive material classes and export controls apply to some concentrates. We check these before quoting.")],
    img_name="commodity-rare-earths-specimen",
    img_alt="Rare earth oxide samples in laboratory vials beside ore specimens",
    img_caption="Separated oxides and mineral concentrates verified by buyer-appointed ICP-MS assay") + \
commodity("crude-oil", "oil", "Crude oil &amp; petroleum products",
    "Spot and term physical supply for refiners and traders, with terminal lifting, inspection and vessel coordination.",
    ["Light sweet", "Medium / heavy", "Condensate", "Diesel", "Jet A-1", "Fuel oil"],
    [("Grades", "As specified, for example by API gravity and sulphur content"),
     ("Volumes", "Cargo parcels from vessel-size lots; term arrangements by agreement"),
     ("Inspection", "Quality and quantity inspection at shore tank and on the vessel by an independent surveyor"),
     ("Vessels", "Tanker chartering support and discharge coordination"),
     ("Delivery terms", "FOB, CFR or CIF for ship cargo, agreed in each contract"),
     ("Note", "Allocation depends on the seller’s licence and the current sanctions position. We do not proceed where either is unclear.")],
    img_name="commodity-crude-oil-refinery",
    img_alt="Coastal petroleum refinery and terminal tank farm with ocean tanker loading infrastructure",
    img_caption="Terminal lifting, shore tank and vessel surveyor inspection for crude and refined distillates") + \
commodity("gems", "gem", "Gemstones",
    "Rough and cut stones, with sorting, cutting and certification, delivered under secured and insured transport.",
    ["Diamonds", "Emerald", "Ruby", "Sapphire", "Tourmaline", "Aquamarine", "Industrial crystals"],
    [("Forms", "Rough parcels, calibrated and cut stones, industrial and optical crystals"),
     ("Processing", "Cleaning, sorting, grading, sawing, cutting, polishing"),
     ("Certification", "Kimberley Process certificate for rough diamonds; independent gemmological reports for stones as requested"),
     ("Viewing", "In a bonded vault or secure room, with your representative present"),
     ("Transport", "Secured courier or vault-to-vault with insurance"),
     ("Delivery terms", "FCA, CIP or DAP, agreed in each contract")],
    img_name="commodity-gems-display",
    img_alt="Rough parcel and faceted certified gemstones with gemmological loupe",
    img_caption="Kimberley Process verified parcels and cut stones under insured vault-to-vault transport") + \
commodity("other", "other", "Other materials",
    "If your mandate falls outside the three areas above, send us the specification and we will tell you whether we can execute it.",
    ["Copper cathode", "Gold doré", "Platinum group metals", "Manganese", "Chrome", "Bauxite"],
    [("How it works", "You send the material, grade, monthly quantity, delivery point and payment structure."),
     ("Our reply", "We confirm what we can deliver, what we would need from you, and what we cannot do.")],
    img_name="processing-facility-plant",
    img_alt="Industrial minerals processing and chemical refining facility",
    img_caption="Custom processing and delivery logistics for copper cathode, PGMs and bulk industrial ores") + '''
</div></section>
''' + cta()

# ----------------------------------------------------------------- COMPLIANCE
def doc(n, title, body):
    return f'''<details class="doc"><summary><span class="num">{n}</span>{title}</summary><div class="doc-body">{body}</div></details>'''

compliance = page_head("Compliance", "Documentation, verification and how we stay compliant",
    "A shipment that cannot be documented cannot be cleared, financed or insured. This is what we prepare, and the rules we work within.") + f'''
<section class="section section--white"><div class="container split split--wide-left">
  <div>
    <div class="section-head"><span class="eyebrow">The document set</span><h2>Six groups of documents on every shipment</h2><p>Exact contents depend on the commodity, origin and destination.</p></div>
    {doc(1, "Certificate of origin", "Issued through the relevant chamber of commerce or authority. Used for tariff, sanctions and import compliance.")}
    {doc(2, "Independent inspection and assay", "Quality, quantity and composition reports from an independent surveyor or laboratory, such as assay for minerals, shore-tank and ship reports for oil, or gemmological reports for stones. The buyer chooses the inspector.")}
    {doc(3, "Government permits and payments", "Export licences, royalty and duty receipts, radiation or hazardous-goods clearance where required, and any foreign-exchange or central bank approvals.")}
    {doc(4, "Provenance and chain of custody", "Records of every transfer from origin to loading, supporting OECD-aligned due diligence, Kimberley Process requirements for rough diamonds, and sanctions screening.")}
    {doc(5, "Commercial and banking documents", "Commercial invoice, packing list, weight and quantity certificates, formatted to meet letter-of-credit presentation requirements agreed with your bank.")}
    {doc(6, "Transport and insurance", "Bill of lading or air waybill, charter party where applicable, and cargo insurance arranged on the terms agreed in the contract.")}
  </div>
  <div style="align-self:start;margin-top:2rem">
    {editorial_picture("compliance-documentation-desk", "Export compliance dossier with certificates of origin and verified stamps", sizes="(min-width: 900px) 440px, 100vw", caption="Full dossier verification: origin certificates, export clearances and bankable LC documents")}
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="section-head"><span class="eyebrow">Our rules</span><h2>How we work</h2></div>
  <div class="grid grid-3">
    <div class="card">{icon("shield")}<h3>Know your counterparty</h3><p>We verify the identity and ownership of the parties we deal with and screen them against sanctions lists before any contract proceeds.</p></div>
    <div class="card">{icon("eye")}<h3>Verify before release</h3><p>Your appointed inspector may sample material before processing, at sealing or loading, and at discharge.</p></div>
    <div class="card">{icon("link")}<h3>Confidentiality and non-circumvention</h3><p>We sign a mutual non-circumvention and non-disclosure agreement on request. We do not approach your end buyer without your written authority.</p></div>
  </div>
  <p class="notice" style="margin-top:2rem">We decline mandates where origin, ownership, licensing or sanctions status cannot be established to our satisfaction. {todo("[Add your AML / KYC policy summary and compliance officer contact here.]")}</p>
</div></section>

<section class="section section--tint"><div class="container split">
  <div>
    <span class="eyebrow">Three checkpoints</span>
    <h2>Inspection access</h2>
    <p>Buyers and their appointed surveyors are welcome at each stage.</p>
    <div style="margin-top:1.5rem">
      {editorial_picture("inspection-geological-assay", "Independent surveyor inspecting an ore sample at a field assay table", sizes="(min-width: 900px) 460px, 100vw", caption="Independent surveyor access at origin, loading port and destination discharge")}
    </div>
  </div>
  <div class="card" style="align-self:center">
    <ol class="steps">
      <li><strong>Before processing</strong><span>Sample raw ore, rough parcels or shore-tank stock to set a baseline.</span></li>
      <li><strong>At sealing or loading</strong><span>Independent sampling, serialised seals and the binding quality and quantity report.</span></li>
      <li><strong>At discharge</strong><span>Reconciliation at the destination port, airport or vault before final payment.</span></li>
    </ol>
  </div>
</div></section>
{cta("Need our confidentiality agreement first?", "Tick the confidentiality option on the enquiry form and we will send the agreement before you share end-buyer details.")}
'''

# ----------------------------------------------------------------- CONTACT
contact = page_head("Contact", "Make an enquiry",
    "Tell us what you need and where it must go. You do not have to name your end buyer.") + f'''
<section class="section"><div class="container split split--wide-left" style="gap:3rem">
  <form class="enquiry" id="enquiry-form">
    <fieldset>
      <legend>1. About you</legend>
      <div class="fields fields-2">
        <div><label for="f-org">Organisation</label><input type="text" id="f-org" required autocomplete="organization"></div>
        <div><label for="f-role">Your organisation is a</label>
          <select id="f-role" required>
            <option>Procurement firm / mandate holder</option><option>Corporation / end buyer</option>
            <option>Government or institution</option><option>Trading house / refinery</option><option>Other</option></select></div>
        <div><label for="f-name">Your name and title</label><input type="text" id="f-name" required autocomplete="name"></div>
        <div><label for="f-email">Work email</label><input type="email" id="f-email" required autocomplete="email"></div>
        <div><label for="f-phone">Phone <span class="opt">(optional)</span></label><input type="tel" id="f-phone" autocomplete="tel"></div>
      </div>
    </fieldset>
    <fieldset>
      <legend>2. What you need</legend>
      <div class="fields fields-2">
        <div><label for="f-division">Commodity area</label>
          <select id="f-division" required>
            <option>Rare earths &amp; critical minerals</option><option>Crude oil &amp; petroleum products</option>
            <option>Gemstones</option><option>Other materials</option></select></div>
        <div><label for="f-item" id="f-item-label">Material</label><select id="f-item" required></select></div>
      </div>
      <p class="small" style="margin:1.25rem 0 .5rem"><strong style="color:var(--ink)">Services you need</strong></p>
      <div class="checks" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">
        <label class="check"><input type="checkbox" name="services" value="Sourcing" checked> Sourcing</label>
        <label class="check"><input type="checkbox" name="services" value="Processing" checked> Processing</label>
        <label class="check"><input type="checkbox" name="services" value="Documentation" checked> Documentation</label>
        <label class="check"><input type="checkbox" name="services" value="Logistics" checked> Logistics</label>
      </div>
    </fieldset>
    <fieldset>
      <legend>3. Quantity and delivery</legend>
      <div class="fields fields-3">
        <div><label for="f-volume">Quantity</label><input type="text" id="f-volume" inputmode="decimal" required placeholder="e.g. 500"></div>
        <div><label for="f-unit">Unit</label><select id="f-unit" required></select></div>
        <div><label for="f-terms">Delivery terms</label><select id="f-terms" required></select></div>
      </div>
      <div class="fields fields-2" style="margin-top:1rem">
        <div><label for="f-dest">Destination port, airport or vault</label><input type="text" id="f-dest" required></div>
        <div><label for="f-timing">Timing</label>
          <select id="f-timing"><option>One-off spot delivery</option><option>Trial shipment, then ongoing supply</option><option>Long-term supply agreement</option><option>Not yet decided</option></select></div>
      </div>
      <div style="margin-top:1rem"><label for="f-notes">Specification and other notes <span class="opt">(optional)</span></label>
        <textarea id="f-notes" placeholder="Target purity or grade, preferred inspector, payment structure, anything we should know."></textarea></div>
    </fieldset>
    <fieldset>
      <legend>4. Confidentiality and consent</legend>
      <div class="checks">
        <label class="check"><input type="checkbox" id="f-nda" checked> <span>Send me your mutual confidentiality and non-circumvention agreement before I share end-buyer details.</span></label>
        <label class="check"><input type="checkbox" id="f-consent" required> <span>I agree that {SITE["name"]} may use these details to reply to my enquiry, as described in the <a href="privacy.html">privacy notice</a>.</span></label>
      </div>
      <div class="hp" aria-hidden="true"><label for="f-website">Leave this field empty</label><input type="text" id="f-website" tabindex="-1" autocomplete="off"></div>
    </fieldset>
    <button class="btn" type="submit">Send enquiry</button>
    <div id="form-status" class="form-status" role="status" aria-live="polite"></div>
  </form>

  <aside>
    <div class="card">
      <h3>Direct contact</h3>
      <ul class="contact-list">
        <li><strong>Email</strong><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>
        <li><strong>Phone</strong>{todo(SITE["phone"])}</li>
        <li><strong>Office</strong>{todo(SITE["address"])}</li>
        <li><strong>Regions</strong>West and Central Africa; delivery to international ports and vaults</li>
      </ul>
    </div>
    <div style="margin-top:1.25rem">
      {editorial_picture("logistics-charter-operations", "Marine cargo superintendent coordinating bulk vessel charter and loading operations", sizes="(min-width: 900px) 380px, 100vw", caption="Active mandate supervision: direct coordination from origin to discharge")}
    </div>
    <div class="card" style="margin-top:1.25rem">
      <h3>What happens next</h3>
      <ol class="steps">
        <li><strong>We review</strong><span>We check the request against what we can supply and document.</span></li>
        <li><strong>We reply</strong><span>You hear from a named person with questions or a first assessment.</span></li>
        <li><strong>We agree terms</strong><span>Confidentiality first, then a written proposal.</span></li>
      </ol>
      <p class="small">{todo("[State your real response time here once you can commit to it.]")}</p>
    </div>
  </aside>
</div></section>
'''

# ----------------------------------------------------------------- PRIVACY
privacy = page_head("Privacy &amp; terms", "Privacy notice and terms of use", "How we handle information you send us.") + f'''
<section class="section"><div class="container prose">
  <p class="notice"><strong>Draft for legal review.</strong> This is a plain-language starting point, not legal advice. Have a qualified lawyer adapt it to the jurisdictions where you operate before launch.</p>
  <h2>Who we are</h2>
  <p>{todo(SITE["company_no"])}, referred to here as {SITE["name"]}, operates this website. Contact: <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>.</p>
  <h2>What we collect</h2>
  <p>Only what you enter in the enquiry form or send us by email: your name, organisation, contact details and the details of your requirement.</p>
  <h2>How we use it</h2>
  <p>To reply to your enquiry, prepare a proposal, and meet legal and compliance obligations such as identity and sanctions checks. We do not sell your information.</p>
  <h2>Who sees it</h2>
  <p>Our staff and the service providers that host our website and email, who are bound to protect it. We may disclose information where the law requires.</p>
  <h2>How long we keep it</h2>
  <p>{todo("[State your retention period.]")}</p>
  <h2>Your rights</h2>
  <p>You can ask us to access, correct or delete your information by emailing us.</p>
  <h2>Website use</h2>
  <p>Information on this site is general and is not an offer to sell or a binding quotation. Any supply or service is subject to a written agreement. Descriptions of commodities, standards and delivery terms are illustrative; actual terms are agreed per contract.</p>
</div></section>
'''

# ----------------------------------------------------------------- WRITE
FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#1c3556"/><rect y="52" width="64" height="4" fill="#c1a066"/><text x="32" y="40" text-anchor="middle" font-family="Georgia,serif" font-weight="700" font-size="26" fill="#fff">DC</text></svg>'''

def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "css"))
    os.makedirs(os.path.join(DIST, "js"))
    shutil.copy(os.path.join(ROOT, "src/css/styles.css"), os.path.join(DIST, "css/styles.css"))
    shutil.copy(os.path.join(ROOT, "src/js/main.js"), os.path.join(DIST, "js/main.js"))
    if os.path.isdir(os.path.join(ROOT, "src/img")):
        shutil.copytree(os.path.join(ROOT, "src/img"), os.path.join(DIST, "img"))
        for f in ("favicon.ico", "favicon.svg"):
            shutil.copy(os.path.join(ROOT, "src/img/favicons", f), os.path.join(DIST, f))
    else:
        with open(os.path.join(DIST, "favicon.svg"), "w") as f:
            f.write(FAVICON.replace(">DC<", ">" + INITIALS + "<"))
    if os.path.isdir(ASSET_DIR):
        shutil.copytree(ASSET_DIR, os.path.join(DIST, "assets"))
    cfg = {"formEndpoint": safe_url(C["form_endpoint"]), "enquiryEmail": C["email"].strip() or DEFAULTS["email"]}
    with open(os.path.join(DIST, "js/config.js"), "w") as f:
        f.write("window.DC_CONFIG = " + json.dumps(cfg) + ";\n")

    page("index.html", f"{SITE['name']} | Sourcing, documentation & logistics for strategic commodities",
         "We source, process, document and ship rare earth minerals, crude oil and gemstones for procurement firms, corporations and institutions.", home, HERO_PRELOAD)
    page("about.html", "About", "Who DC Consulting is, where it fits in a commodity contract, and who it serves.", about)
    page("services.html", "Services", "Sourcing, processing, documentation and logistics for physical commodity contracts, as a full chain or one stage at a time.", services)
    page("commodities.html", "Commodities", "Rare earth minerals, crude oil, gemstones and other strategic materials: forms, verification and delivery terms.", commodities)
    page("compliance.html", "Compliance & documentation", "The six document groups on every shipment, independent inspection access, and our counterparty and sanctions checks.", compliance)
    page("contact.html", "Make an enquiry", "Send a commodity enquiry with quantity, delivery terms and destination. Confidentiality agreement available before you share end-buyer details.", contact)
    page("privacy.html", "Privacy & terms", "How DC Consulting handles information submitted through this website.", privacy)

    pages = ["", "about.html", "services.html", "commodities.html", "compliance.html", "contact.html", "privacy.html"]
    sm = "".join(f"<url><loc>{SITE['domain']}/{p}</loc></url>\n" for p in pages)
    with open(os.path.join(DIST, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    with open(os.path.join(DIST, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
    print("Built", len(os.listdir(DIST)), "items in", DIST)

if __name__ == "__main__":
    main()
