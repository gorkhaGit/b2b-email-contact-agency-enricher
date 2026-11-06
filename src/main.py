from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import re
from urllib.parse import urljoin, urlparse, urlunparse

from apify import Actor
from bs4 import BeautifulSoup
import httpx

PROTO = "https" + "://"
HTTP_PROTO = "http" + "://"

# Curated multi-ecosystem B2B Agency & SaaS Partner catalog + live directory discovery
ECOSYSTEM_SEEDS = [
    # Zapier Solution Partners
    {"name": "Automation Consulting Services", "url": "https://www.automationconsultingservices.com", "eco": "Zapier Partner", "tier": "Platinum Solution Partner", "hq": "United States", "tags": ["Zapier", "ChatGPT", "HubSpot", "Airtable"]},
    {"name": "Flow Digital", "url": "https://flow.digital", "eco": "Zapier Partner", "tier": "Platinum Solution Partner", "hq": "United States", "tags": ["Zapier", "Make", "HubSpot", "Salesforce"]},
    {"name": "Connex Digital", "url": "https://connex.digital", "eco": "Zapier Partner", "tier": "Platinum Solution Partner", "hq": "Canada", "tags": ["Zapier", "AI Automation", "CRM"]},
    {"name": "GetUWired", "url": "https://www.getuwired.com", "eco": "Zapier Partner", "tier": "Platinum Solution Partner", "hq": "United States", "tags": ["Zapier", "ActiveCampaign", "Keap"]},
    {"name": "Sidekick Strategies", "url": "https://sidekickstrategies.com", "eco": "Zapier Partner", "tier": "Gold Solution Partner", "hq": "United States", "tags": ["Zapier", "HubSpot", "RevOps"]},
    # Make.com Certified Partners
    {"name": "Business Automated", "url": "https://www.business-automated.com", "eco": "Make.com Partner", "tier": "Gold Partner", "hq": "Finland", "tags": ["Make.com", "OpenAI", "Airtable", "AI Agents"]},
    {"name": "The Automation Partner", "url": "https://www.theautomationpartner.com", "eco": "Make.com Partner", "tier": "Certified Partner", "hq": "Netherlands", "tags": ["Make.com", "Workflow Automation"]},
    {"name": "Meticulosity", "url": "https://www.meticulosity.com", "eco": "Make.com Partner", "tier": "Gold Partner", "hq": "United States", "tags": ["Make.com", "HubSpot", "Enterprise Automation"]},
    {"name": "Flowmondo", "url": "https://flowmondo.com", "eco": "Make.com Partner", "tier": "Gold Partner", "hq": "United Kingdom", "tags": ["Make.com", "Zapier", "Pipedrive", "Monday.com"]},
    {"name": "9x", "url": "https://www.go9x.com", "eco": "Make.com Partner", "tier": "Gold Partner", "hq": "Germany", "tags": ["Make.com", "AI Operations", "Airtable", "OpenAI"]},
    {"name": "Makeitfuture", "url": "https://www.makeitfuture.com", "eco": "Make.com Partner", "tier": "Platinum Partner", "hq": "Romania", "tags": ["Make.com", "AI Automation", "Enterprise"]},
    # Stripe Certified Partners
    {"name": "10Clouds", "url": "https://10clouds.com", "eco": "Stripe Partner", "tier": "Premier Services Partner", "hq": "Poland", "tags": ["Stripe Billing", "Stripe Connect", "FinTech", "AI"]},
    {"name": "Netguru", "url": "https://www.netguru.com", "eco": "Stripe Partner", "tier": "Verified Partner", "hq": "Poland", "tags": ["Stripe", "Commerce", "FinTech Consulting"]},
    {"name": "Viget", "url": "https://www.viget.com", "eco": "Stripe Partner", "tier": "Verified Partner", "hq": "United States", "tags": ["Stripe Connect", "Product Engineering"]},
    {"name": "StrtupBoost", "url": "https://strtupboost.com", "eco": "Stripe Partner", "tier": "Verified Partner", "hq": "United States", "tags": ["Stripe", "SaaS Growth"]},
    {"name": "DockYard", "url": "https://dockyard.com", "eco": "Stripe Partner", "tier": "Verified Partner", "hq": "United States", "tags": ["Stripe", "Custom Web Apps", "Elixir"]},
    # ClickUp Solution Partners
    {"name": "ZenPilot", "url": "https://www.zenpilot.com", "eco": "ClickUp Partner", "tier": "Premier Solution Partner", "hq": "United States", "tags": ["ClickUp", "Agency Operations", "Consulting"]},
    {"name": "ProcessDriven", "url": "https://processdriven.co", "eco": "ClickUp Partner", "tier": "Verified Consultant", "hq": "United States", "tags": ["ClickUp", "SmartSuite", "SOPs"]},
    {"name": "L5.ai", "url": "https://www.l5.ai", "eco": "ClickUp Partner", "tier": "Global Solution Partner", "hq": "India", "tags": ["ClickUp", "AI Transformation", "RevOps"]},
    {"name": "360VIER GmbH", "url": "https://360vier.de", "eco": "ClickUp Partner", "tier": "Solution Partner", "hq": "Germany", "tags": ["ClickUp", "Digital Workspaces"]},
    {"name": "Paperless Movement", "url": "https://paperlessmovement.com", "eco": "ClickUp Partner", "tier": "Verified Consultant", "hq": "Spain", "tags": ["ClickUp", "Productivity", "PKM"]},
    # Supabase Ecosystem Partners
    {"name": "Marmelab", "url": "https://marmelab.com", "eco": "Supabase Partner", "tier": "Solution Partner", "hq": "France", "tags": ["Supabase", "React-Admin", "PostgreSQL", "Full-Stack"]},
    {"name": "Trigger.dev", "url": "https://trigger.dev", "eco": "Supabase Partner", "tier": "Technology Partner", "hq": "United Kingdom", "tags": ["Supabase", "Background Jobs", "TypeScript"]},
    {"name": "Resend", "url": "https://resend.com", "eco": "Supabase Partner", "tier": "Technology Partner", "hq": "United States", "tags": ["Supabase", "Developer Email API"]},
    {"name": "Upstash", "url": "https://upstash.com", "eco": "Supabase Partner", "tier": "Technology Partner", "hq": "United States", "tags": ["Supabase", "Serverless Redis", "Vector DB"]},
    # CNCF Cloud Native & KCSP Vendors
    {"name": "Isovalent (Cilium)", "url": "https://isovalent.com", "eco": "CNCF Landscape", "tier": "Graduated / KCSP", "hq": "United States", "tags": ["Kubernetes", "eBPF", "Cilium", "Cloud Native Security"]},
    {"name": "Giant Swarm", "url": "https://www.giantswarm.io", "eco": "CNCF Landscape", "tier": "KCSP Certified Provider", "hq": "Germany", "tags": ["Kubernetes", "Managed Cloud Native", "KCSP"]},
    {"name": "Weaveworks", "url": "https://www.weave.works", "eco": "CNCF Landscape", "tier": "GitOps / Cloud Native", "hq": "United Kingdom", "tags": ["Kubernetes", "Flux", "GitOps"]},
    {"name": "Container Solutions", "url": "https://www.container-solutions.com", "eco": "CNCF Landscape", "tier": "KCSP Certified Provider", "hq": "United Kingdom", "tags": ["Kubernetes", "Cloud Migration", "DevOps"]},
    {"name": "tetrate.io", "url": "https://tetrate.io", "eco": "CNCF Landscape", "tier": "Service Mesh / KCSP", "hq": "United States", "tags": ["Istio", "Envoy", "Zero Trust", "Kubernetes"]},
]

ECO_FILTER_MAP = {
    "zapier_partners": "Zapier Partner",
    "make_partners": "Make.com Partner",
    "stripe_partners": "Stripe Partner",
    "clickup_partners": "ClickUp Partner",
    "supabase_partners": "Supabase Partner",
    "cncf_cloud_native": "CNCF Landscape",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,12}")
OBFUSCATED_EMAIL_RE = re.compile(
    r"([a-zA-Z0-9._%+-]+)\s*(?:\[at\]|\(at\)|\s+at\s+)\s*([a-zA-Z0-9.-]+)\s*(?:\[dot\]|\(dot\)|\.|\s+dot\s+)\s*([a-zA-Z]{2,12})",
    re.I,
)
BAD_EMAIL_EXT = re.compile(r"\.(png|jpg|jpeg|gif|svg|webp|css|js|woff|woff2|ttf|ico|pdf|mp4|mp3)$", re.I)
BAD_EMAIL_WORDS = re.compile(
    r"(sentry|example|domain|email\.com|yoursite|wixpress|cloudflare|placeholder|u00|noreply|no-reply|donotreply|webpack|bootstrap)",
    re.I,
)
TECH_SIGNAL_PATTERNS = {
    "HubSpot": r"hs-scripts\.com|hubspot\.com",
    "Stripe": r"js\.stripe\.com|stripe\.com",
    "Intercom": r"widget\.intercom\.io|intercom\.com",
    "Google Tag Manager": r"googletagmanager\.com",
    "Crisp Chat": r"client\.crisp\.chat",
    "Calendly": r"calendly\.com",
    "Typeform": r"typeform\.com",
    "Webflow": r"webflow\.com",
    "Framer": r"framer\.com|framerusercontent\.com",
    "Next.js": r"_next/static",
    "Shopify": r"cdn\.shopify\.com",
    "WordPress": r"wp-content/",
}


def clean_email(raw: str) -> str:
    e = re.sub(r"^mailto:", "", raw or "", flags=re.I).split("?")[0].strip().lower()
    e = e.strip(".,;:'\"()[]<>")
    if not re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,12}$", e):
        return ""
    if BAD_EMAIL_EXT.search(e) or BAD_EMAIL_WORDS.search(e):
        return ""
    return e


def normalize_url(raw_url: str) -> str:
    u = str(raw_url or "").strip().rstrip(".,;)")
    if not u:
        return ""
    if not u.startswith((PROTO, HTTP_PROTO)):
        u = f"{PROTO}{u}"
    try:
        p = urlparse(u)
        if not p.netloc or "." not in p.netloc:
            return ""
        path = p.path if p.path and p.path != "/" else ""
        return urlunparse((p.scheme, p.netloc.lower(), path, "", "", ""))
    except Exception:
        return ""


def extract_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        return re.sub(r"^www\.", "", netloc)
    except Exception:
        return ""


async def fetch_html(client: httpx.AsyncClient, url: str, timeout: float = 9.0) -> str:
    try:
        resp = await client.get(url, headers=HEADERS, timeout=timeout, follow_redirects=True)
        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", "text/html").lower():
            return resp.text
    except Exception:
        pass
    return ""


def scan_html_for_signals(
    html: str,
    soup: BeautifulSoup,
    base_url: str,
    emails: set[str],
    phones: set[str],
    socials: dict[str, str],
    contact_candidates: list[str],
    tech_signals: set[str],
) -> None:
    # 1. Detect embedded tech stack scripts
    for tech_name, pat in TECH_SIGNAL_PATTERNS.items():
        if re.search(pat, html, re.I):
            tech_signals.add(tech_name)

    # 2. Parse JSON-LD structured data for official email/telephone/sameAs
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw_json = script.string or script.get_text() or ""
        for raw_e in EMAIL_RE.findall(raw_json):
            ce = clean_email(raw_e)
            if ce:
                emails.add(ce)

    # 3. Scan anchor links for mailto:, tel:, socials, and internal contact pages
    base_domain = extract_domain(base_url)
    for a in soup.find_all("a", href=True):
        href = (a["href"] or "").strip()
        if not href:
            continue
        low = href.lower()
        if low.startswith("mailto:"):
            ce = clean_email(href)
            if ce:
                emails.add(ce)
        elif low.startswith("tel:"):
            ph = re.sub(r"^tel:", "", href, flags=re.I).strip()
            ph_digits = re.sub(r"\D", "", ph)
            if 7 <= len(ph_digits) <= 15 and len(ph) <= 24:
                phones.add(str(ph))
        elif re.search(r"linkedin\.com/(company|in)/", low) and not socials["linkedinUrl"]:
            socials["linkedinUrl"] = str(href.split("?")[0])
        elif (
            re.search(r"(twitter\.com|x\.com)/[a-z0-9_]+", low)
            and not re.search(r"intent|share|status", low)
            and not socials["twitterUrl"]
        ):
            socials["twitterUrl"] = str(href.split("?")[0])
        elif re.search(r"github\.com/[a-z0-9_-]+", low) and not socials["githubUrl"]:
            socials["githubUrl"] = str(href.split("?")[0])
        elif re.search(r"youtube\.com/(c/|channel/|@)[a-z0-9_-]+", low) and not socials["youtubeUrl"]:
            socials["youtubeUrl"] = str(href.split("?")[0])
        elif re.search(
            r"/(contact|contact-us|about|about-us|get-in-touch|talk-to-us|impressum|legal|support)\b",
            low,
        ):
            try:
                resolved = normalize_url(urljoin(base_url, href))
                if resolved and extract_domain(resolved) == base_domain:
                    if resolved not in contact_candidates:
                        contact_candidates.append(resolved)
                    if not socials["contactPageUrl"]:
                        socials["contactPageUrl"] = resolved
            except Exception:
                pass

    # 4. Scan visible text + de-obfuscate [at] / (at) emails
    visible_text = soup.get_text(" ", strip=True)
    for raw_e in EMAIL_RE.findall(visible_text):
        ce = clean_email(raw_e)
        if ce:
            emails.add(ce)

    for m in OBFUSCATED_EMAIL_RE.finditer(visible_text):
        reconstructed = f"{m.group(1)}@{m.group(2)}.{m.group(3)}"
        ce = clean_email(reconstructed)
        if ce:
            emails.add(ce)


def rank_emails(emails: set[str], target_domain: str) -> list[str]:
    def score(e: str) -> tuple[int, int, str]:
        same_dom = 0 if (target_domain and e.endswith(target_domain)) else 1
        prefix = e.split("@")[0]
        preferred = 0 if prefix in ("hello", "contact", "info", "sales", "partnerships", "founders", "team", "hi") else 1
        return (same_dom, preferred, e)

    return sorted(emails, key=score)[:12]


def sanitize_record(record: dict) -> dict:
    clean: dict = {}
    for k, v in record.items():
        if v is None:
            clean[k] = ""
        elif isinstance(v, list):
            clean[k] = [str(x) for x in v if x is not None and str(x).strip() != ""]
        elif isinstance(v, int):
            clean[k] = int(v)
        else:
            clean[k] = str(v)
    return clean


async def enrich_company_entry(
    entry: dict,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    crawl_contact_pages: bool,
    search_query: str,
) -> dict | None:
    website = normalize_url(entry.get("url", ""))
    if not website:
        return None

    domain = extract_domain(website)
    async with semaphore:
        emails: set[str] = set()
        phones: set[str] = set()
        socials: dict[str, str] = {
            "linkedinUrl": "",
            "twitterUrl": "",
            "githubUrl": "",
            "youtubeUrl": "",
            "contactPageUrl": "",
        }
        contact_candidates: list[str] = []
        tech_signals: set[str] = set(entry.get("tags") or [])
        pages_scanned = 0

        company_name = str(entry.get("name") or "").strip()
        description = ""

        # Step 1: Fetch Homepage
        home_html = await fetch_html(client, website, timeout=9.0)
        if home_html:
            pages_scanned += 1
            soup = BeautifulSoup(home_html, "html.parser")
            if not company_name:
                og_site = soup.find("meta", attrs={"property": "og:site_name"})
                title_tag = soup.find("title")
                if og_site and og_site.get("content"):
                    company_name = og_site["content"].strip()
                elif title_tag and title_tag.get_text(strip=True):
                    company_name = re.split(r"\||-|—|:", title_tag.get_text(strip=True))[0].strip()

            meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
                "meta", attrs={"property": "og:description"}
            )
            if meta_desc and meta_desc.get("content"):
                description = meta_desc["content"].strip()[:400]

            scan_html_for_signals(
                home_html,
                soup,
                website,
                emails,
                phones,
                socials,
                contact_candidates,
                tech_signals,
            )

        # Step 2: Deep Crawl Internal Contact / About Pages if enabled
        if crawl_contact_pages:
            root_base = f"{urlparse(website).scheme}://{urlparse(website).netloc}"
            for fallback_path in ("/contact", "/contact-us", "/about", "/impressum"):
                cand = f"{root_base}{fallback_path}"
                if cand not in contact_candidates:
                    contact_candidates.append(cand)

            for sub_url in contact_candidates[:2]:
                if len(emails) >= 3 and socials["linkedinUrl"]:
                    break
                sub_html = await fetch_html(client, sub_url, timeout=6.5)
                if sub_html:
                    pages_scanned += 1
                    if not socials["contactPageUrl"]:
                        socials["contactPageUrl"] = sub_url
                    scan_html_for_signals(
                        sub_html,
                        BeautifulSoup(sub_html, "html.parser"),
                        sub_url,
                        emails,
                        phones,
                        socials,
                        [],
                        tech_signals,
                    )

        if not company_name:
            company_name = domain.split(".")[0].replace("-", " ").title()

        sorted_emails = rank_emails(emails, domain)
        tech_list = sorted(tech_signals)[:15]
        source_eco = str(entry.get("eco") or "Custom Bulk Website")
        partner_tier = str(entry.get("tier") or "B2B Domain Enrichment")
        headquarters = str(entry.get("hq") or "Global")

        if search_query:
            hay = (
                f"{company_name} {domain} {source_eco} {partner_tier} "
                f"{' '.join(tech_list)} {headquarters} {description}"
            ).lower()
            if search_query.lower() not in hay:
                return None

        record = {
            "companyName": company_name,
            "domain": domain,
            "website": website,
            "sourceEcosystem": source_eco,
            "partnerTier": partner_tier,
            "primaryEmail": sorted_emails[0] if sorted_emails else "",
            "emails": sorted_emails,
            "phones": sorted(phones)[:5],
            "linkedinUrl": socials["linkedinUrl"],
            "twitterUrl": socials["twitterUrl"],
            "githubUrl": socials["githubUrl"],
            "youtubeUrl": socials["youtubeUrl"],
            "contactPageUrl": socials["contactPageUrl"],
            "techAndServices": tech_list,
            "headquarters": headquarters,
            "description": description or f"Enriched B2B profile for {company_name} ({domain}).",
            "pagesScanned": pages_scanned,
            "scrapedAt": datetime.now(timezone.utc).isoformat(),
        }
        return sanitize_record(record)


def build_target_queue(
    raw_websites: list,
    directory_source: str,
) -> list[dict]:
    queue: list[dict] = []
    seen_domains: set[str] = set()

    # 1. User-supplied custom bulk websites/domains always take priority
    for item in raw_websites:
        for token in re.split(r"[\s,;]+", str(item or "").strip()):
            norm = normalize_url(token)
            dom = extract_domain(norm)
            if norm and dom and dom not in seen_domains:
                seen_domains.add(dom)
                queue.append(
                    {
                        "name": "",
                        "url": norm,
                        "eco": "Custom Bulk Domain",
                        "tier": "Direct Website Enrichment",
                        "hq": "Global",
                        "tags": [],
                    }
                )

    # 2. Append built-in 6-ecosystem B2B Partner seeds unless custom_urls_only
    if directory_source != "custom_urls_only":
        target_eco = ECO_FILTER_MAP.get(directory_source)
        for seed in ECOSYSTEM_SEEDS:
            if target_eco and seed["eco"] != target_eco:
                continue
            dom = extract_domain(seed["url"])
            if dom and dom not in seen_domains:
                seen_domains.add(dom)
                queue.append(seed)

    return queue


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        raw_websites = actor_input.get("websites") or []
        directory_source = str(actor_input.get("directorySource") or "all_ecosystems").strip()
        search_query = str(actor_input.get("searchQuery") or "").strip()
        max_items = int(actor_input.get("maxItems") or 25)
        crawl_contact_pages = bool(actor_input.get("crawlContactPages", True))
        only_with_emails = bool(actor_input.get("onlyWithEmails", False))

        queue = build_target_queue(raw_websites, directory_source)
        Actor.log.info(
            f"Starting B2B Website Email & Agency Lead Enricher | "
            f"Queued targets: {len(queue)} | Source: {directory_source} | maxItems: {max_items}"
        )

        semaphore = asyncio.Semaphore(10)
        saved_count = 0
        batch_size = 10

        async with httpx.AsyncClient() as client:
            for i in range(0, len(queue), batch_size):
                if saved_count >= max_items:
                    break
                chunk = queue[i : i + batch_size]
                tasks = [
                    enrich_company_entry(
                        entry,
                        client,
                        semaphore,
                        crawl_contact_pages,
                        search_query,
                    )
                    for entry in chunk
                ]
                results = await asyncio.gather(*tasks)
                for record in results:
                    if not record or saved_count >= max_items:
                        continue
                    if only_with_emails and not record.get("primaryEmail"):
                        continue
                    try:
                        await Actor.push_data(record)
                        saved_count += 1
                        try:
                            await Actor.charge(event_name="lead-enriched", count=1)
                        except Exception:
                            pass
                        Actor.log.info(
                            f"[{saved_count}/{max_items}] {record['companyName']} ({record['domain']}) | "
                            f"Eco: {record['sourceEcosystem']} | Email: {record['primaryEmail'] or 'none'} | "
                            f"Pages: {record['pagesScanned']}"
                        )
                    except Exception as exc:
                        Actor.log.warning(f"Skipped invalid record: {exc}")

        Actor.log.info(f"Run completed! Total B2B leads enriched and pushed: {saved_count}")
