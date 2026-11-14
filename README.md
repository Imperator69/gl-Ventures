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
- `/team/dominik-lerch/`, `/team/gianluca-graf/` und `/en/team/...`: Partnerprofile
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

## SEO, AEO und KI-Suche

- Pro Seite: Title, Description, Canonical, hreflang DE/EN/x-default, Open Graph, Twitter Card
- JSON-LD: Organization + ProfessionalService, WebSite, WebPage (Startseite mit `speakable`), Service (mit Leistungsbausteinen und Zielgruppen), Person, ProfilePage, FAQPage, BreadcrumbList
- Kurze, sichtbare Antworten: Kurzprofil „auf einen Blick“ neben der FAQ, erste FAQ-Antwort jeweils aufgeklappt, FAQ mit Fragen zu Personen und zur Abgrenzung der Leistungen
- Partnerprofile als eigene Seiten (Namenssuche nach Visitenkarten-Kontakt)
- `sitemap.xml` mit hreflang, `robots.txt` erlaubt Such- und KI-Crawler ausdrücklich
- `llms.txt` (Kurzfassung mit Kurzantworten) und `llms-full.txt` (Volltext) für KI-Assistenten, automatisch aus `content.py`
- IndexNow: Nach jedem Deploy meldet `tools/indexnow.py` alle URLs an Bing (Grundlage auch für ChatGPT-Suche und Copilot). Der Schlüssel `SITE["indexnow_key"]` ist öffentlich und liegt als `<key>.txt` im Webroot

## Google Tag, Analytics und Search Console

Alles wird in `src/content.py` unter `SITE["tracking"]` eingetragen. Leere Werte bedeuten: ausgeschaltet.

| Feld | Woher | Wirkung |
|---|---|---|
| `google_tag_id` | Google Analytics → Verwaltung → Datenstreams → Web → Mess-ID (`G-...`) | Einwilligungs-Banner, Analytics nach Zustimmung, Abschnitt in der Datenschutzerklärung, Google-Freigaben in der CSP, „Cookie-Einstellungen“ im Footer |
| `google_site_verification` | Search Console → Property `https://www.gl-ventures.at` (URL-Präfix) → Bestätigung per HTML-Tag → Wert hinter `content=` | Meta-Tag zur Bestätigung |
| `bing_site_verification` | Bing Webmaster Tools → HTML-Meta-Tag | Meta-Tag zur Bestätigung |

- Ohne Zustimmung wird nichts von Google geladen und kein Cookie gesetzt. Die Entscheidung liegt im `localStorage` (`glv-consent`).
- Gemessen wird zusätzlich das Ereignis `contact_click` (Telefon, E-Mail, Kontakt speichern, LinkedIn).
- GTM-Container (`GTM-...`) werden nicht unterstützt, weil sie Inline-Skripte brauchen, die die CSP sperrt.
- Zum lokalen Testen: `GOOGLE_TAG_ID=G-TEST123 python3 build.py`.
- In Google Analytics einstellen: Datenaufbewahrung höchstens 14 Monate, Google-Signale aus, Zusatz zur Datenverarbeitung akzeptieren. Darauf verlässt sich der Text der Datenschutzerklärung.

## Offen

- Impressum: derzeit GG Beratung mit Anschrift und Kontakt. Firmenbuchnummer, UID, Rechtsform und Gewerbe ergänzen, sobald feststeht, wer die Seite dauerhaft betreibt.
- Datenschutz: Auftragsverarbeitungsvertrag mit World4You bestätigen.
- Mess-ID und Bestätigungscodes eintragen (siehe oben), danach in Search Console und Bing Webmaster Tools die Sitemap einreichen.
- Google-Unternehmensprofil und LinkedIn-Firmenseite anlegen und unter `sameAs` in `build.py` verlinken.
