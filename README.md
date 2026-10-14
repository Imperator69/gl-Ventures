# gl-ventures.at

Statische Landing Page, ohne Build-Schritt. Lokal ansehen: `python3 -m http.server` und http://localhost:8000 öffnen.

## Struktur
- `index.html`: Landing Page inkl. Meta-Tags, Open Graph, Schema.org JSON-LD (Organization, WebSite, WebPage, FAQPage)
- `impressum.html`, `datenschutz.html`: Pflichtseiten (AT: ECG, UGB, MedienG; DSGVO)
- `robots.txt`: Suchmaschinen und KI-Crawler (GPTBot, ClaudeBot, PerplexityBot, Google-Extended u.a.) zugelassen
- `sitemap.xml`, `llms.txt`, `site.webmanifest`, `favicon.svg`
- `assets/styles.css`

## Offen
- Alle Platzhalter in `[eckigen Klammern]` mit Inhalten der bisherigen Website ersetzen (`grep -rn '\[' *.html llms.txt`)
- FAQ im JSON-LD und sichtbare FAQ synchron halten
- `assets/og-image.png` (1200x630) anlegen
- Nach Go-live: Google Search Console und Bing Webmaster Tools verifizieren, Sitemap einreichen
