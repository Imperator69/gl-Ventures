#!/usr/bin/env python3
"""Static site generator for gl-ventures.at (Python 3 stdlib only).

    python3 build.py          # writes the complete site to ./public

Content lives in src/content.py, styles/scripts/images in src/static.
Upload the contents of ./public to the web root.
"""
import base64
import datetime
import hashlib
import json
import shutil
from html import escape
from pathlib import Path

from src.content import EN, LANGS, SERVICE_IDS, SITE

ROOT = Path(__file__).parent
STATIC = ROOT / "src" / "static"
OUT = ROOT / "public"
TODAY = datetime.date.today().isoformat()
D = SITE["domain"]
ORG_ID = f"{D}/#organization"


def e(s):
    return escape(str(s), quote=True)


def asset_version(name):
    return hashlib.sha256((STATIC / name).read_bytes()).hexdigest()[:10]


ICON = {
    "arrow": '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>',
    "down": '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 5v14m-6-6 6 6 6-6"/></svg>',
    "out": '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>',
    "mail": '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "phone": '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "pin": '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12Z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "check": '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m5 12 4.5 4.5L19 7"/></svg>',
    "save": '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="10" cy="8" r="3.5"/><path d="M3.5 19a6.5 6.5 0 0 1 11.6-4M18 14v6m-3-3h6"/></svg>',
    "linkedin": '<svg class="i" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.56V9h3.56v11.45ZM22.23 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0h.01Z"/></svg>',
}

SECTOR_ICON = {
    "Defense": '<path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6l-8-3Z"/>',
    "Energy": '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/>',
    "Innovation": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3Z"/>',
    "Blockchain": '<path d="M12 2 3 7v10l9 5 9-5V7l-9-5Z"/><path d="m3 7 9 5 9-5M12 12v10"/>',
    "Digitalisierung": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
}
SECTOR_ICON["Digitalisation"] = SECTOR_ICON["Digitalisierung"]


def sector_icon(title):
    return f'<svg class="sector-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" aria-hidden="true">{SECTOR_ICON[title]}</svg>'


def og_image_name(L):
    return "og-image.jpg" if L["lang"] == "de" else "og-image-en.jpg"


def service_path(L, sid):
    return L["paths"]["service"].format(id=sid)


def other(L):
    return [x for x in LANGS if x is not L][0]


# ---------------------------------------------------------------- structured data

def address_ld(L):
    return {
        "@type": "PostalAddress",
        "streetAddress": SITE["street"],
        "postalCode": SITE["postal_code"],
        "addressLocality": SITE["city"][L["lang"]],
        "addressCountry": "AT",
    }


def org_ld(L):
    org = {
        "@type": ["Organization", "ProfessionalService"],
        "@id": ORG_ID,
        "name": SITE["name"],
        "legalName": SITE["legal_name"],
        "alternateName": [SITE["legal_name"], f"{SITE['name']} {SITE['city'][L['lang']]}"],
        "url": f"{D}/",
        "description": L["home"]["description"],
        "slogan": L["ui"]["tagline"],
        "logo": {"@type": "ImageObject", "url": f"{D}/assets/logo-512.png", "width": 512, "height": 512},
        "image": f"{D}/assets/og-image.jpg",
        "address": address_ld(L),
        "hasMap": SITE["maps"],
        "geo": {"@type": "GeoCoordinates", "latitude": SITE["geo"]["lat"], "longitude": SITE["geo"]["lng"]},
        "telephone": SITE["people"][0]["phone"],
        "email": SITE["people"][0]["email"],
        "areaServed": [{"@type": "Country", "name": "Austria"}, {"@type": "Place", "name": "Europe"}, "International"],
        "availableLanguage": ["de", "en"],
        "knowsAbout": [s["title"] for s in L["sectors"]] + [L["services"][sid]["name"] for sid in SERVICE_IDS],
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "name": p["name"],
                "contactType": "business enquiries",
                "email": p["email"],
                "telephone": p["phone"],
                "availableLanguage": ["de", "en"],
            }
            for p in SITE["people"]
        ],
        "member": [{"@id": f"{D}/#{p['id']}"} for p in SITE["people"]],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": f"{SITE['name']} Services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@id": f"{D}{service_path(L, sid)}#service"}} for sid in SERVICE_IDS
            ],
        },
        "sameAs": [],
    }
    if SITE["vat_id"]:
        org["vatID"] = SITE["vat_id"]
    return org


def person_ld(L, p):
    t = L["people"][p["id"]]
    return {
        "@type": "Person",
        "@id": f"{D}/#{p['id']}",
        "name": p["name"],
        "jobTitle": t["role"],
        "description": t["bio"],
        "image": f"{D}/assets/{p['image']}-960.webp",
        "email": p["email"],
        "telephone": p["phone"],
        "worksFor": {"@id": ORG_ID},
        "sameAs": [p["linkedin"]],
    }


def service_ld(L, sid):
    s = L["services"][sid]
    url = f"{D}{service_path(L, sid)}"
    return {
        "@type": "Service",
        "@id": f"{url}#service",
        "name": s["name"],
        "serviceType": s["kicker"],
        "description": s["summary"],
        "url": url,
        "provider": {"@id": ORG_ID},
        "areaServed": "International",
        "availableLanguage": ["de", "en"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": s["name"],
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": m["title"], "description": m["text"]}}
                for m in s["modules"]
            ],
        },
    }


def faq_ld(url, items):
    return {
        "@type": "FAQPage",
        "@id": f"{url}#faq",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in items
        ],
    }


def breadcrumb_ld(url, crumbs):
    return {
        "@type": "BreadcrumbList",
        "@id": f"{url}#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": f"{D}{path}"}
            for i, (name, path) in enumerate(crumbs)
        ],
    }


def webpage_ld(L, url, title, description, extra=None):
    page = {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": title,
        "description": description,
        "inLanguage": L["lang"],
        "isPartOf": {"@id": f"{D}/#website"},
        "about": {"@id": ORG_ID},
        "dateModified": TODAY,
        "primaryImageOfPage": f"{D}/assets/{og_image_name(L)}",
    }
    page.update(extra or {})
    return page


def website_ld():
    return {
        "@type": "WebSite",
        "@id": f"{D}/#website",
        "url": f"{D}/",
        "name": SITE["name"],
        "alternateName": SITE["legal_name"],
        "inLanguage": ["de", "en"],
        "publisher": {"@id": ORG_ID},
    }


def jsonld(graph):
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")
    return f'<script type="application/ld+json">{data}</script>'


# ---------------------------------------------------------------- layout

def head(L, *, path, alt_path, title, description, graph, robots="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1", preload_hero=False):
    url = f"{D}{path}"
    de_path, en_path = (path, alt_path) if L["lang"] == "de" else (alt_path, path)
    css_v, js_v = asset_version("styles.css"), asset_version("main.js")
    hero = ""
    if preload_hero:
        hero = '<link rel="preload" href="/assets/hero-1672.webp" as="image" imagesrcset="/assets/hero-640.webp 640w, /assets/hero-1080.webp 1080w, /assets/hero-1672.webp 1672w" imagesizes="100vw" fetchpriority="high">'
    alternates = ""
    if alt_path:
        alternates = (
            f'<link rel="alternate" hreflang="de" href="{D}{de_path}">'
            f'<link rel="alternate" hreflang="en" href="{D}{en_path}">'
            f'<link rel="alternate" hreflang="x-default" href="{D}{de_path}">'
        )
    og_alt = "en_GB" if L["lang"] == "de" else "de_AT"
    og_img = f"{D}/assets/{og_image_name(L)}"
    return f"""<!doctype html>
<html lang="{L['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="{robots}">
<meta name="author" content="{e(SITE['legal_name'])}">
<meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#09111d">
<meta name="geo.region" content="AT-9"><meta name="geo.placename" content="{e(SITE['city'][L['lang']])}"><meta name="geo.position" content="{SITE['geo']['lat']};{SITE['geo']['lng']}"><meta name="ICBM" content="{SITE['geo']['lat']}, {SITE['geo']['lng']}">
<link rel="canonical" href="{url}">{alternates}
<meta property="og:type" content="website"><meta property="og:site_name" content="{e(SITE['name'])}"><meta property="og:locale" content="{L['locale']}"><meta property="og:locale:alternate" content="{og_alt}">
<meta property="og:url" content="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{og_img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{e(SITE['name'])}: {e(L['ui']['tagline'])}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{og_img}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="text/markdown" title="LLM summary" href="/llms.txt">
<link rel="preload" href="/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>{hero}
<link rel="stylesheet" href="/styles.css?v={css_v}">
<script src="/main.js?v={js_v}" defer></script>
{jsonld(graph)}
</head>
"""


def header(L, *, alt_path, home, plain=False):
    ui = L["ui"]
    h = L["paths"]["home"]
    base = "" if home else h
    links = [
        (f"{base}#services", ui["services"]),
        (f"{base}#about", ui["about"]),
        (f"{base}#sectors", ui["sectors"]),
        (f"{base}#approach", ui["approach"]),
        (f"{base}#faq", ui["faq"]),
    ]
    nav = "".join(f'<a class="nav-link" href="{href}">{e(label)}</a>' for href, label in links)
    o = other(L)
    switch = f'<span class="lang-current" aria-current="true" title="{e(ui["lang_name"])}">{L["lang"].upper()}</span>'
    if alt_path:
        switch += f'<a class="lang-link" href="{alt_path}" lang="{o["lang"]}" hreflang="{o["lang"]}" title="{e(o["ui"]["lang_name"])}">{o["lang"].upper()}</a>'
    return f"""<body class="{'page-home' if home else ('page-plain' if plain else 'page-sub')}">
<a class="skip-link" href="#main">{e(ui['skip'])}</a>
<header class="site-header" id="header"><div class="wrap header-inner">
<a class="brand" href="{h}" title="{e(ui['home'])}"><span class="brand-mark">GL</span> <span class="brand-word">Ventures</span></a>
<nav class="nav" id="main-nav" aria-label="{e(ui['nav_label'])}">{nav}<a class="nav-link nav-cta" href="{base}#contact">{e(ui['contact'])}{ICON['arrow']}</a></nav>
<div class="header-tools"><div class="lang-switch">{switch}</div>
<button class="menu-toggle" type="button" aria-controls="main-nav" aria-expanded="false" aria-label="{e(ui['menu_open'])}" data-open-label="{e(ui['menu_open'])}" data-close-label="{e(ui['menu_close'])}"><span></span></button></div>
</div></header>
"""


def footer(L):
    ui = L["ui"]
    year = datetime.date.today().year
    services = "".join(
        f'<li><a href="{service_path(L, sid)}">{e(L["services"][sid]["name"])}</a></li>' for sid in SERVICE_IDS
    )
    people = "".join(
        f'<li class="footer-person"><span>{e(p["name"])}</span><a href="tel:{p["phone"]}">{p["phone_display"]}</a><a href="mailto:{p["email"]}">{p["email"]}</a></li>'
        for p in SITE["people"]
    )
    return f"""<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
<div class="footer-brand"><a class="brand" href="{L['paths']['home']}"><span class="brand-mark">GL</span> <span class="brand-word">Ventures</span></a><p>{e(ui['tagline'])}</p></div>
<div><p class="footer-title">{e(ui['services'])}</p><ul>{services}</ul></div>
<div><p class="footer-title">{e(ui['contact'])}</p><ul>{people}</ul></div>
<div><p class="footer-title">{e(ui['location'])}</p><address>{e(SITE['legal_name'])}<br>{e(SITE['street'])}<br>{SITE['postal_code']} {e(SITE['city'][L['lang']])}, {e(SITE['country'][L['lang']])}</address></div>
</div>
<div class="footer-bottom"><span>© {year} {e(SITE['legal_name'])}. {e(ui['rights'])}</span>
<nav aria-label="{e(ui['legal_nav'])}"><a href="{L['paths']['imprint']}">{e(ui['imprint'])}</a><a href="{L['paths']['privacy']}">{e(ui['privacy'])}</a><a href="/sitemap.xml">Sitemap</a></nav></div>
</div></footer>
</body>
</html>
"""


def section_head(eyebrow, title, lead=None, hid=None, cls=""):
    lead_html = f'<p class="lead">{e(lead)}</p>' if lead else ""
    return f'<div class="section-head {cls} reveal"><div><p class="eyebrow">{e(eyebrow)}</p><h2 id="{hid}">{e(title)}</h2></div>{lead_html}</div>'


def disclosures(items, group, numbered=False):
    out = []
    for i, f in enumerate(items):
        num = f'<span class="num">{i + 1:02d}</span>' if numbered else ""
        out.append(
            f'<details class="disclosure" name="{group}"><summary>{num}<span class="q">{e(f["q"])}</span><span class="plus" aria-hidden="true"></span></summary>'
            f'<div class="disclosure-body"><p>{e(f["a"])}</p></div></details>'
        )
    return f'<div class="disclosures">{"".join(out)}</div>'


def contact_cards(L):
    ui = L["ui"]
    cards = []
    for p in SITE["people"]:
        t = L["people"][p["id"]]
        cards.append(f"""<article class="contact-card" id="contact-{p['id']}">
<div class="contact-person"><img src="/assets/{p['image']}-160.webp" width="160" height="160" alt="" loading="lazy" decoding="async"><div><h3>{e(p['name'])}</h3><p class="meta">{e(t['role'])}</p></div></div>
<div class="contact-actions">
<a class="action action-primary" href="tel:{p['phone']}">{ICON['phone']}<span>{p['phone_display']}</span></a>
<a class="action action-primary" href="mailto:{p['email']}">{ICON['mail']}<span>{p['email']}</span></a>
<a class="action" href="/vcard/{p['id']}.vcf" download="{p['id']}.vcf">{ICON['save']}<span>{e(ui['save_contact'])}</span></a>
<a class="action" href="{p['linkedin']}" target="_blank" rel="noopener noreferrer">{ICON['linkedin']}<span>LinkedIn</span><span class="sr-only">: {e(p['name'])}</span></a>
</div></article>""")
    return "".join(cards)


def address_line(L):
    return f"{e(SITE['street'])}, {SITE['postal_code']} {e(SITE['city'][L['lang']])}, {e(SITE['country'][L['lang']])}"


def contact_address(L):
    return (f'<p class="cta-address">{ICON["pin"]}<span>{address_line(L)}<br>'
            f'<a href="{e(SITE["maps"])}" target="_blank" rel="noopener noreferrer">{e(L["ui"]["route"])}</a></span></p>')


def quick_contact(L):
    """Mobile bar: business-card visitors usually know which partner they met."""
    links = "".join(
        f'<a href="#contact-{p["id"]}"><img src="/assets/{p["image"]}-160.webp" width="160" height="160" alt="" loading="lazy" decoding="async"><span>{e(p["name"])}</span></a>'
        for p in SITE["people"]
    )
    return f'<nav class="quick-contact" aria-label="{e(L["ui"]["quick_contact"])}">{links}</nav>\n'


def cta_band(L):
    ui = L["ui"]
    return f"""<section class="cta-band" id="contact" aria-labelledby="cta-title"><div class="wrap">
<div class="cta-inner reveal"><div><p class="eyebrow">{e(ui['contact'])}</p><h2 id="cta-title">{e(ui['cta_title'])}</h2><p class="lead">{e(ui['cta_text'])}</p>{contact_address(L)}</div>
<div class="contact-cards">{contact_cards(L)}</div></div>
</div></section>
"""


# ---------------------------------------------------------------- pages

def page_home(L):
    H, ui = L["home"], L["ui"]
    path, alt = L["paths"]["home"], other(L)["paths"]["home"]
    url = f"{D}{path}"
    graph = [
        org_ld(L),
        website_ld(),
        webpage_ld(L, url, H["title"], H["description"], {"mainEntity": {"@id": f"{url}#services"}}),
        {
            "@type": "ItemList",
            "@id": f"{url}#services",
            "name": f"{SITE['name']} Services",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": service_ld(L, sid)} for i, sid in enumerate(SERVICE_IDS)
            ],
        },
        *[person_ld(L, p) for p in SITE["people"]],
        faq_ld(url, H["faq"]),
    ]

    audiences = "".join(
        f'<article class="audience reveal"><h3>{e(a["title"])}</h3><p>{e(a["text"])}</p></article>'
        for a in H["audiences"]
    )

    services = []
    for i, sid in enumerate(SERVICE_IDS):
        s = L["services"][sid]
        points = "".join(f'<li>{ICON["check"]}<span>{e(m["title"])}</span></li>' for m in s["modules"])
        services.append(f"""<article class="service reveal" id="{sid}" aria-labelledby="{sid}-title">
<p class="eyebrow">{i + 1:02d} / {e(s['kicker'])}</p><h3 id="{sid}-title">{e(s['name'])}</h3><p class="service-tagline">{e(s['tagline'])}</p>
<p class="service-summary">{e(s['summary'])}</p>
<ul class="service-points">{points}</ul>
<a class="service-link" href="{service_path(L, sid)}">{e(ui['more'])}<span class="sr-only">: {e(s['name'])}</span>{ICON['arrow']}</a></article>""")

    sectors = "".join(
        f'<article class="sector reveal">{sector_icon(s["title"])}<h3>{e(s["title"])}</h3><p>{e(s["text"])}</p><p class="tags">{e(s["tags"])}</p></article>'
        for s in L["sectors"]
    )
    steps = "".join(
        f'<li class="reveal"><span class="step-num">{i + 1:02d}</span><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></li>'
        for i, s in enumerate(H["approach_steps"])
    )
    principles = "".join(
        f'<div class="principle reveal">{ICON["check"]}<div><h3>{e(p["title"])}</h3><p>{e(p["text"])}</p></div></div>'
        for p in H["principles"]
    )
    people = []
    for p in SITE["people"]:
        t = L["people"][p["id"]]
        people.append(f"""<article class="person reveal" id="{p['id']}">
<div class="portrait"><img src="/assets/{p['image']}-960.webp" srcset="/assets/{p['image']}-480.webp 480w, /assets/{p['image']}-960.webp 960w" sizes="(max-width: 48rem) 100vw, 40vw" width="960" height="{p['image_h']}" alt="{e(t['alt'])}" loading="lazy" decoding="async"></div>
<div class="person-body"><h3>{e(p['name'])}</h3><p class="role">{e(t['role'])}</p><p>{e(t['bio'])}</p><p class="tags">{e(t['tags'])}</p>
<div class="person-links"><a href="#contact-{p['id']}">{ICON['phone']}<span>{e(ui['contact'])}</span></a><a href="{p['linkedin']}" target="_blank" rel="noopener noreferrer">{ICON['linkedin']}<span>LinkedIn</span><span class="sr-only">: {e(p['name'])}</span></a></div></div>
</article>""")
    avatars = "".join(
        f'<img src="/assets/{p["image"]}-160.webp" width="160" height="160" alt="" decoding="async">' for p in SITE["people"]
    )
    names = " &amp; ".join(e(p["name"]) for p in SITE["people"])

    body = f"""<main id="main">
<section class="hero" id="top" aria-labelledby="hero-title">
<img class="hero-image" src="/assets/hero-1672.webp" srcset="/assets/hero-640.webp 640w, /assets/hero-1080.webp 1080w, /assets/hero-1672.webp 1672w" sizes="100vw" width="1672" height="941" alt="" fetchpriority="high" decoding="async">
<div class="hero-shade" aria-hidden="true"></div>
<div class="wrap hero-content">
<h1 id="hero-title"><span class="eyebrow hero-eyebrow"><span class="dot" aria-hidden="true"></span>{e(H['h1_kicker'])}</span><span class="h1-main">{e(H['h1_a'])}<br><span>{e(H['h1_b'])}</span></span></h1>
<p class="hero-intro">{e(H['intro'])}</p>
<div class="hero-actions"><a class="button button-light" href="#contact">{e(H['cta_primary'])}{ICON['arrow']}</a><a class="button button-outline" href="#services">{e(H['cta_secondary'])}{ICON['down']}</a></div>
<a class="hero-people" href="#contact"><span class="avatars">{avatars}</span><span><strong>{names}</strong><span>{e(ui['your_contacts'])}<span class="reach"> · {e(ui['reach_directly'])}</span></span></span>{ICON['arrow']}</a>
</div>
</section>

<section class="section audience-section" aria-labelledby="audience-title"><div class="wrap">
{section_head(H['audience_eyebrow'], H['audience_title'], H['audience_lead'], 'audience-title')}
<div class="audiences">{audiences}</div>
</div></section>

<section class="section alt services-section" id="services" aria-labelledby="services-title"><div class="wrap">
{section_head(H['services_eyebrow'], H['services_title'], H['services_lead'], 'services-title')}
<div class="services">{''.join(services)}</div>
</div></section>

<section class="section about-section" id="about" aria-labelledby="about-title"><div class="wrap">
{section_head(H['about_eyebrow'], H['about_title'], H['about_lead'], 'about-title')}
<div class="people">{''.join(people)}</div>
</div></section>

<section class="section dark sectors-section" id="sectors" aria-labelledby="sectors-title"><div class="wrap">
{section_head(H['sectors_eyebrow'], H['sectors_title'], H['sectors_lead'], 'sectors-title')}
<div class="sectors">{sectors}</div>
</div></section>

<section class="section approach-section" id="approach" aria-labelledby="approach-title"><div class="wrap">
{section_head(H['approach_eyebrow'], H['approach_title'], None, 'approach-title')}
<ol class="steps">{steps}</ol>
<div class="principles">{principles}</div>
</div></section>

<section class="section alt faq-section" id="faq" aria-labelledby="faq-title"><div class="wrap split">
{section_head(H['faq_eyebrow'], H['faq_title'], None, 'faq-title', 'sticky')}
{disclosures(H['faq'], 'faq')}
</div></section>

<section class="cta-band" id="contact" aria-labelledby="contact-title"><div class="wrap">
<div class="cta-inner reveal"><div><p class="eyebrow">{e(H['contact_eyebrow'])}</p><h2 id="contact-title">{e(H['contact_title'])}</h2><p class="lead">{e(H['contact_lead'])}</p>
{contact_address(L)}</div>
<div class="contact-cards">{contact_cards(L)}</div></div>
</div></section>
</main>
{quick_contact(L)}"""
    return path, head(L, path=path, alt_path=alt, title=H["title"], description=H["description"], graph=graph, preload_hero=True) + header(L, alt_path=alt, home=True) + body + footer(L)


def breadcrumbs_html(L, crumbs):
    items = []
    for i, (name, path) in enumerate(crumbs):
        if i < len(crumbs) - 1:
            items.append(f'<li><a href="{path}">{e(name)}</a></li>')
        else:
            items.append(f'<li aria-current="page">{e(name)}</li>')
    return f'<nav class="breadcrumbs" aria-label="{e(L["ui"]["breadcrumb"])}"><ol>{"".join(items)}</ol></nav>'


def page_service(L, sid):
    ui, s = L["ui"], L["services"][sid]
    path, alt = service_path(L, sid), service_path(other(L), sid)
    url = f"{D}{path}"
    crumbs = [(ui["home"], L["paths"]["home"]), (ui["services"], f"{L['paths']['home']}#services"), (s["name"], path)]
    graph = [
        org_ld(L),
        website_ld(),
        webpage_ld(L, url, s["title"], s["description"], {"mainEntity": {"@id": f"{url}#service"}, "breadcrumb": {"@id": f"{url}#breadcrumb"}}),
        service_ld(L, sid),
        breadcrumb_ld(url, crumbs),
        faq_ld(url, s["faq"]),
    ]
    idx = SERVICE_IDS.index(sid)
    starting = "".join(f'<li class="reveal">{ICON["check"]}<span>{e(x)}</span></li>' for x in s["starting_points"])
    mods = "".join(
        f'<li class="reveal"><span class="num">{j + 1:02d}</span><div><h3>{e(m["title"])}</h3><p>{e(m["text"])}</p></div></li>'
        for j, m in enumerate(s["modules"])
    )
    outcomes = "".join(
        f'<article class="outcome reveal"><h3>{e(o["title"])}</h3><p>{e(o["text"])}</p></article>' for o in s["outcomes"]
    )
    others = "".join(
        f'<a class="other-service reveal" href="{service_path(L, o)}"><span class="num">{SERVICE_IDS.index(o) + 1:02d}</span><span class="name">{e(L["services"][o]["name"])}</span><span class="tag">{e(L["services"][o]["tagline"])}</span>{ICON["arrow"]}</a>'
        for o in SERVICE_IDS if o != sid
    )
    body = f"""<main id="main">
<section class="page-hero" aria-labelledby="page-title">
<img class="hero-image" src="/assets/hero-1672.webp" srcset="/assets/hero-640.webp 640w, /assets/hero-1080.webp 1080w, /assets/hero-1672.webp 1672w" sizes="100vw" width="1672" height="941" alt="" decoding="async">
<div class="hero-shade" aria-hidden="true"></div>
<div class="wrap page-hero-content">
{breadcrumbs_html(L, crumbs)}
<p class="eyebrow">{idx + 1:02d} / {e(s['kicker'])}</p>
<h1 id="page-title">{e(s['name'])}</h1>
<p class="page-tagline">{e(s['tagline'])}</p>
<p class="hero-intro">{e(s['summary'])}</p>
<div class="hero-actions"><a class="button button-light" href="#contact">{e(ui['get_in_touch'])}{ICON['arrow']}</a></div>
</div></section>

<section class="section" aria-labelledby="starting-title"><div class="wrap split">
{section_head(ui['starting_points'], ui['starting_points_title'], None, 'starting-title', 'sticky')}
<ul class="checklist">{starting}</ul>
</div></section>

<section class="section alt" aria-labelledby="modules-title"><div class="wrap">
{section_head(ui['modules'], ui['modules_title'], None, 'modules-title')}
<ol class="module-grid">{mods}</ol>
</div></section>

<section class="section" aria-labelledby="outcomes-title"><div class="wrap">
{section_head(ui['outcomes'], ui['outcomes_title'], None, 'outcomes-title')}
<div class="outcomes">{outcomes}</div>
</div></section>

<section class="section alt" aria-labelledby="sfaq-title"><div class="wrap split">
{section_head(ui['faq'], f"{ui['service_faq']} {s['name']}", None, 'sfaq-title', 'sticky')}
{disclosures(s['faq'], 'sfaq')}
</div></section>

<section class="section" aria-labelledby="others-title"><div class="wrap">
<div class="section-head reveal"><div><h2 id="others-title">{e(ui['other_services'])}</h2></div></div>
<div class="other-services">{others}</div>
</div></section>
{cta_band(L)}</main>
{quick_contact(L)}"""
    return path, head(L, path=path, alt_path=alt, title=s["title"], description=s["description"], graph=graph) + header(L, alt_path=alt, home=False) + body + footer(L)


def legal_shell(L, *, key, path, alt, title, description, h1, inner):
    ui = L["ui"]
    url = f"{D}{path}"
    crumbs = [(ui["home"], L["paths"]["home"]), (ui[key], path)]
    graph = [org_ld(L), website_ld(), webpage_ld(L, url, title, description, {"breadcrumb": {"@id": f"{url}#breadcrumb"}}), breadcrumb_ld(url, crumbs)]
    body = f"""<main id="main" class="legal">
<div class="wrap legal-wrap">
{breadcrumbs_html(L, crumbs)}
<h1>{e(h1)}</h1>
{inner}
</div></main>
"""
    return path, head(L, path=path, alt_path=alt, title=title, description=description, graph=graph) + header(L, alt_path=alt, home=False, plain=True) + body + footer(L)


MISSING = []


def val(L, v, label):
    v = v[L["lang"]] if isinstance(v, dict) else v
    if v:
        return e(v)
    MISSING.append(label)
    return f'<span class="missing">[{e(L["imprint"]["missing"])}]</span>'


def page_imprint(L):
    I = L["imprint"]
    lb = I["labels"]
    city = SITE["city"][L["lang"]]
    rows = [
        (lb["company"], e(SITE["legal_name"])),
        (lb["form"], e(lb["form_value"])),
        (lb["seat"], e(city)),
        (lb["address"], f"{e(SITE['street'])}, {SITE['postal_code']} {e(city)}, {e(SITE['country'][L['lang']])}"),
        (lb["register_no"], val(L, SITE["company_register_no"], "Firmenbuchnummer")),
        (lb["register_court"], val(L, SITE["company_register_court"], "Firmenbuchgericht")),
        (lb["vat"], val(L, SITE["vat_id"], "UID-Nummer")),
        (lb["directors"], val(L, SITE["managing_directors"], "Geschäftsführung")),
        (lb["licence"], val(L, SITE["trade_licence"], "Gewerbe")),
        (lb["authority"], val(L, SITE["trade_authority"], "Gewerbebehörde")),
        (lb["chamber"], val(L, SITE["chamber"], "Kammer")),
        (lb["law"], e(lb["law_value"])),
        (lb["contact"], "<br>".join(f'{e(p["name"])}: <a href="mailto:{p["email"]}">{p["email"]}</a>, <a href="tel:{p["phone"]}">{p["phone_display"]}</a>' for p in SITE["people"])),
    ]
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    inner = f"""<p class="lead">{e(I['intro'])}</p>
<dl class="facts">{dl}</dl>
<h2>{e(I['media_title'])}</h2><p>{e(I['media_text'])}</p>
<h2>{e(I['liability_title'])}</h2><p>{e(I['liability_text'])}</p>
<h2>{e(I['copyright_title'])}</h2><p>{e(I['copyright_text'])}</p>"""
    return legal_shell(L, key="imprint", path=L["paths"]["imprint"], alt=other(L)["paths"]["imprint"], title=I["title"], description=I["description"], h1=I["h1"], inner=inner)


def page_privacy(L):
    P = L["privacy"]
    secs = "".join(f"<h2>{e(s['h'])}</h2>" + "".join(f"<p>{e(p)}</p>" for p in s["p"]) for s in P["sections"])
    inner = secs + f'<p class="meta">{e(P["updated"])}: {TODAY}</p>'
    return legal_shell(L, key="privacy", path=L["paths"]["privacy"], alt=other(L)["paths"]["privacy"], title=P["title"], description=P["description"], h1=P["h1"], inner=inner)


def page_404():
    de, en = LANGS
    graph = [website_ld()]
    body = f"""<main id="main" class="notfound"><div class="wrap">
<p class="eyebrow">404</p>
<h1>{e(de['ui']['not_found_title'])}</h1><p class="lead">{e(de['ui']['not_found_text'])}</p>
<p lang="en" class="lead">{e(en['ui']['not_found_text'])}</p>
<div class="hero-actions"><a class="button button-dark" href="/">{e(de['ui']['to_home'])}{ICON['arrow']}</a><a class="button button-ghost" href="/en/" lang="en">{e(en['ui']['to_home'])}{ICON['arrow']}</a></div>
</div></main>
"""
    return "/404.html", head(de, path="/404.html", alt_path=None, title=f"404 | {SITE['name']}", description=de["ui"]["not_found_text"], graph=graph, robots="noindex,follow") + header(de, alt_path=None, home=False, plain=True) + body + footer(de)


# ---------------------------------------------------------------- machine-readable files

def sitemap(pages):
    rows = []
    for path, alt in pages:
        de_p, en_p = (path, alt) if not path.startswith("/en/") else (alt, path)
        prio = "1.0" if path in ("/", "/en/") else ("0.8" if "/leistungen/" in path or "/services/" in path else "0.3")
        rows.append(
            f"<url><loc>{D}{path}</loc><lastmod>{TODAY}</lastmod><priority>{prio}</priority>"
            f'<xhtml:link rel="alternate" hreflang="de" href="{D}{de_p}"/>'
            f'<xhtml:link rel="alternate" hreflang="en" href="{D}{en_p}"/>'
            f'<xhtml:link rel="alternate" hreflang="x-default" href="{D}{de_p}"/></url>'
        )
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n"


def llms_txt():
    de, en = LANGS
    lines = [
        f"# {SITE['name']}",
        "",
        f"> {SITE['legal_name']} is a boutique advisory based in Vienna, Austria, offering Complex Services, Strategic Advisory and Venture Building to businesses, investors and public stakeholders. Sectors: defense, energy, innovation, blockchain, digitalisation. Languages: German, English.",
        "",
        "## Key facts",
        f"- Legal name: {SITE['legal_name']}",
        f"- Address: {SITE['street']}, {SITE['postal_code']} Vienna, Austria",
        "- Partners: " + "; ".join(f"{p['name']} ({en['people'][p['id']]['role']}, {p['email']}, {p['phone_display']})" for p in SITE["people"]),
        "- Services: " + ", ".join(en["services"][sid]["name"] for sid in SERVICE_IDS),
        "- Sectors: " + ", ".join(s["title"] for s in en["sectors"]),
        f"- Website: {D}/",
        "- Contact cards (vCard): " + ", ".join(f"{D}/vcard/{p['id']}.vcf" for p in SITE["people"]),
        "- Not to be confused with other companies named GL Ventures outside Austria.",
        "",
        "## Pages (English)",
        f"- [Home]({D}/en/): overview, sectors, partners, FAQ, contact",
        *[f"- [{en['services'][sid]['name']}]({D}{service_path(en, sid)}): {en['services'][sid]['tagline']}" for sid in SERVICE_IDS],
        "",
        "## Seiten (Deutsch)",
        f"- [Startseite]({D}/): Überblick, Kompetenzfelder, Partner, FAQ, Kontakt",
        *[f"- [{de['services'][sid]['name']}]({D}{service_path(de, sid)}): {de['services'][sid]['tagline']}" for sid in SERVICE_IDS],
        "",
        "## Optional",
        f"- [Full text for LLMs]({D}/llms-full.txt)",
        f"- [Impressum]({D}/impressum/)",
        f"- [Datenschutz]({D}/datenschutz/)",
        "",
    ]
    return "\n".join(lines)


def llms_full_txt():
    out = []
    for L in LANGS:
        H = L["home"]
        out += [f"# {SITE['name']} ({L['lang'].upper()})", "", H["intro"], "", f"## {H['audience_title']}", H["audience_lead"]]
        out += [f"- {a['title']}: {a['text']}" for a in H["audiences"]]
        for sid in SERVICE_IDS:
            s = L["services"][sid]
            out += ["", f"## {s['name']}: {s['tagline']}", f"URL: {D}{service_path(L, sid)}", "", s["summary"], ""]
            out += [f"- {m['title']}: {m['text']}" for m in s["modules"]]
            out += [""] + [f"- {x}" for x in s["starting_points"]]
            out += [""] + [f"- {o['title']}: {o['text']}" for o in s["outcomes"]]
            out += [""] + [f"Q: {f['q']}\nA: {f['a']}" for f in s["faq"]]
        out += ["", f"## {H['sectors_title']}"] + [f"- {s['title']}: {s['text']}" for s in L["sectors"]]
        out += ["", f"## {H['approach_title']}"] + [f"{i + 1}. {s['title']}: {s['text']}" for i, s in enumerate(H["approach_steps"])]
        out += [f"- {p['title']}: {p['text']}" for p in H["principles"]]
        out += ["", f"## {H['about_title']}", H["about_lead"]]
        out += [f"- {p['name']}, {L['people'][p['id']]['role']}: {L['people'][p['id']]['bio']} ({p['email']}, {p['phone_display']}, {p['linkedin']})" for p in SITE["people"]]
        out += ["", f"## FAQ"] + [f"Q: {f['q']}\nA: {f['a']}\n" for f in H["faq"]]
        out += [f"## {L['ui']['contact']}", f"{SITE['legal_name']}, {SITE['street']}, {SITE['postal_code']} {SITE['city'][L['lang']]}, {SITE['country'][L['lang']]}", "", "---", ""]
    return "\n".join(out)


ROBOTS = f"""# {SITE['name']}: {D}/
# Search engines and AI assistants are welcome to crawl and cite this site.
User-agent: *
Allow: /

User-agent: Googlebot
User-agent: Bingbot
User-agent: Applebot
User-agent: DuckDuckBot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: GPTBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: ClaudeBot
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: Meta-ExternalAgent
User-agent: MistralAI-User
User-agent: CCBot
Allow: /

Sitemap: {D}/sitemap.xml
"""


def manifest():
    return json.dumps({
        "name": SITE["name"],
        "short_name": SITE["name"],
        "description": EN["home"]["description"],
        "lang": "de",
        "start_url": "/",
        "display": "browser",
        "background_color": "#09111d",
        "theme_color": "#09111d",
        "icons": [
            {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
            {"src": "/assets/logo-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
        ],
    }, indent=2) + "\n"


def vcard(p):
    """vCard 3.0 (best iOS/Android support), CRLF line endings, folded at 75 octets."""
    def esc(v):
        return str(v).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")

    t = EN["people"][p["id"]]
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{esc(p['family'])};{esc(p['given'])};;;",
        f"FN:{esc(p['name'])}",
        f"ORG:{esc(SITE['legal_name'])}",
        f"TITLE:{esc(t['role'])}",
        f"TEL;TYPE=CELL,VOICE:{p['phone']}",
        f"EMAIL;TYPE=INTERNET,WORK:{p['email']}",
        f"ADR;TYPE=WORK:;;{esc(SITE['street'])};{esc(SITE['city']['de'])};;{SITE['postal_code']};{esc(SITE['country']['de'])}",
        f"URL:{D}/",
        f"X-SOCIALPROFILE;TYPE=linkedin:{p['linkedin']}",
    ]
    photo = STATIC / "assets" / f"{p['image']}-vcard.jpg"
    if photo.exists():
        lines.append("PHOTO;ENCODING=b;TYPE=JPEG:" + base64.b64encode(photo.read_bytes()).decode())
    lines += [f"REV:{TODAY}", "END:VCARD"]

    def fold(line):
        parts, chunk = [], ""
        for ch in line:
            if len((chunk + ch).encode("utf-8")) > (74 if parts else 75):
                parts.append(chunk)
                chunk = ""
            chunk += ch
        return "\r\n ".join(parts + [chunk])

    return "\r\n".join(fold(x) for x in lines) + "\r\n"


# ---------------------------------------------------------------- build

def write(path, text):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)

    indexed = []
    for L in LANGS:
        o = other(L)
        for path, html in [page_home(L), *[page_service(L, sid) for sid in SERVICE_IDS], page_imprint(L), page_privacy(L)]:
            write(path, html)
        indexed += [(L["paths"]["home"], o["paths"]["home"])]
        indexed += [(service_path(L, sid), service_path(o, sid)) for sid in SERVICE_IDS]
        indexed += [(L["paths"]["imprint"], o["paths"]["imprint"]), (L["paths"]["privacy"], o["paths"]["privacy"])]
    write(*page_404())
    for p in SITE["people"]:
        (OUT / "vcard").mkdir(exist_ok=True)
        (OUT / "vcard" / f"{p['id']}.vcf").write_bytes(vcard(p).encode("utf-8"))

    write("/sitemap.xml", sitemap(indexed))
    write("/robots.txt", ROBOTS)
    write("/llms.txt", llms_txt())
    write("/llms-full.txt", llms_full_txt())
    write("/site.webmanifest", manifest())

    print(f"Built {len(indexed) + 1} pages into {OUT.relative_to(ROOT)}/")
    missing = sorted(set(MISSING))
    if missing:
        print("Impressum incomplete, fill in src/content.py SITE:", ", ".join(missing))


if __name__ == "__main__":
    main()
