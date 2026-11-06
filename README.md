# B2B Website Email, Phone & Agency Lead Enricher (Bulk URLs + 6 Directories)

> **High-Speed Async Python B2B Email Extractor, Domain Contact Enricher & Multi-Ecosystem Agency Finder.** Pass any list of company domains/URLs (from Google Maps, Clay, Apollo, or CSVs) **OR** pull verified B2B agencies across **Zapier, Make.com, Stripe, ClickUp, Supabase, and CNCF** at **256 MB RAM** with **$0.00 proxy cost**.

---

## 🚀 Two High-Value Modes in One Actor

1. **Mode 1 — Bulk Website / Domain Contact Enricher (`websites` input):**
   Drop 10 to 10,000 raw company URLs or domains. The engine crawls each domain's homepage + internal `/contact`, `/about`, and `/impressum` pages + `JSON-LD` schemas concurrently to extract:
   - Verified business emails (prioritizing `hello@`, `contact@`, `founders@`, `sales@` + de-obfuscating `[at]` emails)
   - Direct phone numbers (`tel:`)
   - LinkedIn company pages, X/Twitter, GitHub, and YouTube profiles
   - Detected website tech signals (`HubSpot`, `Stripe`, `Intercom`, `Calendly`, `Next.js`, `Shopify`, `Webflow`)
2. **Mode 2 — Built-In 6-Ecosystem B2B Partner Lead Finder (`directorySource` input):**
   Pull pre-vetted B2B consulting agencies, AI automation shops, and cloud-native vendors across:
   - **Zapier Solution Partners** (`Platinum`, `Gold`, `Silver`)
   - **Make.com Certified Partners** (`Platinum`, `Gold`, `Certified`)
   - **Stripe Partner Ecosystem** (`Premier`, `Verified`)
   - **ClickUp Verified Consultants & Solution Partners**
   - **Supabase Technology & Solution Partners**
   - **CNCF Cloud Native & KCSP Certified Vendors**

---

## 🔌 Free 1-Click n8n Integration Template

Import [`integrations/n8n_b2b_enricher_workflow.json`](./integrations/n8n_b2b_enricher_workflow.json) directly into **n8n** to enrich Google Maps leads, Clay webhooks, or CRM domains automatically via the Apify sync endpoint.

---

## 📊 Scraped Data Evidence (Live Sample Output)

- **JSON Sample:** [`evidence/sample_leads.json`](./evidence/sample_leads.json)
- **CSV Sample:** [`evidence/sample_leads.csv`](./evidence/sample_leads.csv)

### Sample Enriched B2B Record
```json
{
  "companyName": "Automation Consulting Services",
  "domain": "automationconsultingservices.com",
  "website": "https://www.automationconsultingservices.com",
  "sourceEcosystem": "Zapier Partner",
  "partnerTier": "Platinum Solution Partner",
  "primaryEmail": "",
  "emails": [],
  "phones": [],
  "linkedinUrl": "",
  "twitterUrl": "",
  "githubUrl": "",
  "youtubeUrl": "",
  "contactPageUrl": "",
  "techAndServices": [
    "Airtable",
    "ChatGPT",
    "HubSpot",
    "Zapier"
  ],
  "headquarters": "United States",
  "description": "Enriched B2B profile for Automation Consulting Services (automationconsultingservices.com).",
  "pagesScanned": 0,
  "scrapedAt": "2026-11-06T05:36:13.887785+00:00"
}
```
