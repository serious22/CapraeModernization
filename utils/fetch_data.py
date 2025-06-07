import json

RAW_LEADS_FILE = "data\\raw_leads.json"
ENRICHED_LEADS_FILE = "data\\enriched_leads.json"

def fetch_raw_leads(sector, region):
    with open(RAW_LEADS_FILE, "r") as file:
        all_leads = json.load(file)
        # Filter by sector and region (mock filtering for now)
        filtered = [
    lead for lead in all_leads
    if sector.lower() in lead.get("sector", "").lower()
    and region.lower() in lead.get("region", "").lower()
]
    return filtered

def fetch_enriched_leads(company_names):
    with open(ENRICHED_LEADS_FILE, "r") as file:
        enriched = json.load(file)
        matched = [lead for lead in enriched if lead["company_name"] in company_names]
        return matched
