# gl-ventures.at

Statische Website der GL Ventures GmbH (DE/EN). Kein Framework, kein npm: ein Python-Skript erzeugt alle Seiten.

## Bauen und ansehen

```sh
python3 build.py                       # erzeugt ./public
python3 -m http.server -d public 8000  # http://localhost:8000
```

Deployment (World4You): Inhalt von `public/` (inkl. `.htaccess`) per FTP/SFTP ins Webroot laden.

## Wo was liegt

| Pfad | Inhalt |
|---|---|
| `src/content.py` | Alle Texte DE/EN, Firmendaten, Kontakte, Impressumsangaben |
| `src/static/` | `styles.css`, `main.js`, Schrift (Inter, selbst gehostet), Bilder, `.htaccess`, Icons |
| `build.py` | Templates, Schema.org-Daten, `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, Manifest |
| `tools/make_images.py` | Erzeugt Social-Vorschaubild und Icons neu (Pillow) |
| `public/` | Generierte Website (wird mitcommittet) |

## Seiten

- `/`, `/en/`: Startseite
- `/leistungen/{complex-services,strategic-advisory,venture-building}/` und `/en/services/...`: Leistungsseiten
- `/impressum/`, `/datenschutz/`, `/en/legal-notice/`, `/en/privacy/`
- `/404.html`

## SEO / KI-Suche

- Pro Seite: Title, Description, Canonical, hreflang DE/EN/x-default, Open Graph, Twitter Card
- JSON-LD: Organization + ProfessionalService, WebSite, WebPage, Service (mit Leistungsbausteinen), Person, FAQPage, BreadcrumbList
- `sitemap.xml` mit hreflang, `robots.txt` erlaubt Such- und KI-Crawler ausdrücklich
- `llms.txt` (Kurzfassung) und `llms-full.txt` (Volltext) für KI-Assistenten, automatisch aus `content.py`
- Keine Cookies, kein Tracking, keine externen Ressourcen (DSGVO, Performance)

## Offen

- Impressum: Firmenbuchnummer, UID, Geschäftsführung, Gewerbe in `src/content.py` (`SITE`) eintragen. `build.py` meldet fehlende Angaben.
- Datenschutz: Auftragsverarbeitungsvertrag mit World4You bestätigen.
- Nach Go-live: Google Search Console und Bing Webmaster Tools verifizieren, Sitemap einreichen; Google-Unternehmensprofil anlegen und unter `sameAs` in `build.py` verlinken.
