# gl-ventures.at

Statische Website der GL Ventures GmbH (DE/EN). Kein Framework, kein npm: ein Python-Skript erzeugt alle Seiten.

## Bauen und ansehen

```sh
python3 build.py                       # erzeugt ./public
python3 -m http.server -d public 8000  # http://localhost:8000
```

## Deployment (GitHub Actions → World4You)

`.github/workflows/deploy.yml` baut die Seite und lädt `public/` per FTPS hoch, bei jedem Push auf `main`/`Main` oder manuell über *Actions → Deploy to World4You → Run workflow*. Hochgeladen werden nur geänderte Dateien.

Einmalig einrichten unter *Settings → Secrets and variables → Actions*:

| Typ | Name | Wert |
|---|---|---|
| Secret | `FTP_SERVER` | FTP-Server aus dem World4You-Kundenbereich |
| Secret | `FTP_USERNAME` | FTP-Benutzer |
| Secret | `FTP_PASSWORD` | FTP-Passwort |
| Variable (optional) | `FTP_SERVER_DIR` | Zielordner, Standard `./`, muss mit `/` enden |
| Variable (optional) | `FTP_PROTOCOL` | Standard `ftps`; `ftp` nur, wenn der Server kein TLS anbietet |

Zugangsdaten nie in Dateien im Repository speichern: Das Repository ist öffentlich.

Manuell geht es weiterhin: Inhalt von `public/` (inkl. `.htaccess`) per FTP ins Webroot laden.

## Wo was liegt

| Pfad | Inhalt |
|---|---|
| `src/content.py` | Alle Texte DE/EN, Firmendaten, Kontakte, Betreiber lt. Impressum (`SITE["operator"]`). In Überschriften markieren `*Sternchen*` den kursiven Akzent |
| `src/static/` | `styles.css`, `main.js`, Schriften (Inter, Instrument Serif; selbst gehostet), Bilder, `.htaccess`, Icons |
| `build.py` | Templates, Schema.org-Daten, `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, Manifest |
| `tools/make_images.py` | Erzeugt Social-Vorschaubilder (DE/EN), Icons, Avatare und vCard-Fotos neu (Pillow) |
| `public/` | Generierte Website (wird mitcommittet) |

## Seiten

- `/`, `/en/`: Startseite
- `/leistungen/{complex-services,strategic-advisory,venture-building}/` und `/en/services/...`: Leistungsseiten
- `/impressum/`, `/datenschutz/`, `/en/legal-notice/`, `/en/privacy/`
- `/404.html`
- `/vcard/dominik-lerch.vcf`, `/vcard/gianluca-graf.vcf`: Kontakt speichern (mit Foto)

## Design und Scroll-Effekte

- Dunkler Einstieg, helle Inhaltsbereiche; Inter für Text, Instrument Serif kursiv als Akzent in Überschriften
- Leistungen: Auf großen Bildschirmen bleibt der Bereich stehen und die drei Leistungen wechseln beim Scrollen. Am Handy, ohne JavaScript und bei „Bewegung reduzieren“ sind es normale Karten untereinander
- Einstiegsbild mit Tiefenwirkung, Überschrift fährt zeilenweise ein, Laufband, Fortschrittslinie im Kopf, gestaffeltes Einblenden
- Keine Inline-Styles im HTML (die Content-Security-Policy in `.htaccess` erlaubt nur eigene Dateien)

## Für Besucher über die Visitenkarte

- Einstieg zeigt beide Partner mit Foto, ein Tipp führt direkt zu den Kontaktkarten
- Kontaktkarten: Anrufen, E-Mail, Kontakt speichern (vCard), LinkedIn, große Tippflächen
- Mobil erscheint nach dem Hero eine Leiste mit beiden Partnern (springt zur jeweiligen Kontaktkarte)

## SEO / KI-Suche

- Pro Seite: Title, Description, Canonical, hreflang DE/EN/x-default, Open Graph, Twitter Card
- JSON-LD: Organization + ProfessionalService, WebSite, WebPage, Service (mit Leistungsbausteinen), Person, FAQPage, BreadcrumbList
- `sitemap.xml` mit hreflang, `robots.txt` erlaubt Such- und KI-Crawler ausdrücklich
- `llms.txt` (Kurzfassung) und `llms-full.txt` (Volltext) für KI-Assistenten, automatisch aus `content.py`
- Keine Cookies, kein Tracking, keine externen Ressourcen (DSGVO, Performance)

## Offen

- Impressum: derzeit GG Beratung mit Anschrift und Kontakt. Firmenbuchnummer, UID, Rechtsform und Gewerbe ergänzen, sobald feststeht, wer die Seite dauerhaft betreibt.
- Datenschutz: Auftragsverarbeitungsvertrag mit World4You bestätigen.
- Nach Go-live: Google Search Console und Bing Webmaster Tools verifizieren, Sitemap einreichen; Google-Unternehmensprofil anlegen und unter `sameAs` in `build.py` verlinken.
