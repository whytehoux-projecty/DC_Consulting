# DC Consulting website + admin

Plain HTML, CSS and JavaScript. The finished site is the `dist/` folder.
You only need Python 3 (no packages) to use the admin. Hosting needs no Python.

## Edit the site with the admin
1. Open a terminal in this folder and run:  `python3 admin.py`
2. Open the address it prints (http://127.0.0.1:8765).
3. Change text, upload your logo and images, add social links, write the CEO message.
4. Press **Save & rebuild site**, then **Preview site** to check it.
5. Upload the contents of `dist/` to your web host.

The admin only runs on your own computer. Stop it with Ctrl+C.

### What the admin controls
- Company name (renames it everywhere), tagline, email, phone, address, company number, website address
- Logo, home page banner image, social media links (LinkedIn, X, Facebook, Instagram)
- Home page headline and introduction, About page paragraphs and region
- CEO message with photo (hidden until you write one)
- **Find & replace** rules that change words across all visible page text (not links or layout)
- Form delivery URL (optional). With none set, the enquiry form opens the visitor's email app.

Your edits are saved in `content/content.json`; uploads in `content/assets/`.
The last 20 saves are kept in `content/backups/` so you can restore an earlier version.

## What the admin does not edit
Services, commodities and compliance wording live in `build.py`. Edit them there
(or ask your AI coding tool), then run `python3 build.py`. Find & replace can still
change individual words in those pages.

## Before you go live
1. Fill in the yellow placeholders: company number, address, phone.
2. Set your real website address (used for search engines and sharing previews).
3. Add leadership details, licences and your AML/KYC summary.
4. Have a lawyer review `privacy.html` and the compliance and delivery-terms wording.
5. Use real photos of your own operations, not stock photos.
6. Decide how enquiries reach you (email app fallback, or a form service URL in the admin).

## Folders
- `dist/`    the finished site, upload this
- `content/` your saved edits and images (created by the admin)
- `src/`     the stylesheet and script
- `admin/`   the admin page; `admin.py` is its server
- `build.py` generates `dist/`
