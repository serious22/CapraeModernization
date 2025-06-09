import json
import pandas as pd
import datetime

# --- Constants ---
RAW_LEADS_FILE = "data\\raw_leads.json"
ENRICHED_LEADS_FILE = "data\\enriched_leads.json"

# --- Helper Functions for Scoring Logic ---

def _get_numeric_value(data, key, default=0):
    """Safely extracts a numeric value from a dictionary or directly, handling common string formats."""
    value = data.get(key, str(default)) if isinstance(data, dict) else str(data)

    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        # Remove commas, dollar signs, and convert common abbreviations
        value = value.replace(",", "").replace("$", "").replace("M", "000000").replace("K", "000").strip()
        try:
            return float(value)
        except ValueError:
            pass
    return default

def _score_company_size(employees_count, preference):
    """Scores based on preferred company size categories."""
    if not preference: return 0

    employees_count = _get_numeric_value(None, None, employees_count) # Use helper to ensure it's numeric
    
    if "Small" in preference and 1 <= employees_count <= 50:
        return 20
    elif "Medium" in preference and 51 <= employees_count <= 500:
        return 20
    elif "Large" in preference and employees_count > 500:
        return 20
    elif "Specific Range" in preference: # For M&A, needs more robust parsing for ranges like "50-200 employees"
        return 10 # Default for range not perfectly matched here
    return 0

def _score_revenue_threshold(revenue, threshold_str):
    """Scores based on revenue matching a threshold string (e.g., '> $1M ARR')."""
    revenue = _get_numeric_value(None, None, revenue) # Use helper
    if not threshold_str:
        return 0

    threshold_str = threshold_str.replace(" ", "").lower()
    
    try:
        if ">" in threshold_str:
            val = _get_numeric_value(None, None, threshold_str.split('>$')[-1].replace('m', '000000').replace('k', '000').replace('arr','').replace('valuation',''))
            return 25 if revenue > val else 0
        elif "<" in threshold_str:
            val = _get_numeric_value(None, None, threshold_str.split('<$')[-1].replace('m', '000000').replace('k', '000').replace('arr','').replace('valuation',''))
            return 25 if revenue < val else 0
        # Add more complex parsing for exact values or ranges if needed
    except (ValueError, IndexError): # Catch errors if split fails or conversion
        pass
    return 0

def _score_investment_stage(year_founded, employees_count, revenue, funding_status, stage_preference):
    """Infers company stage and scores based on user preference."""
    if not stage_preference: return 0

    year_founded = _get_numeric_value(None, None, year_founded)
    employees_count = _get_numeric_value(None, None, employees_count)
    revenue = _get_numeric_value(None, None, revenue)
    
    company_stage = "Unknown"
    # Basic inference logic (can be made more sophisticated)
    funding_lower = funding_status.lower()

    if year_founded >= 2020 and employees_count < 50 and revenue < 1000000 and "seed" in funding_lower:
        company_stage = "Seed/Angel"
    elif 2015 <= year_founded < 2020 and 50 <= employees_count < 200 and 1000000 <= revenue < 10000000 and ("series a" in funding_lower or "series b" in funding_lower):
        company_stage = "Series A/B"
    elif employees_count >= 200 and revenue >= 10000000 and ("series c" in funding_lower or "growth equity" in funding_lower):
        company_stage = "Growth Equity"
    elif employees_count >= 500 and revenue >= 50000000 and "public" in funding_lower:
        company_stage = "Mature/Public Ready"

    return 25 if company_stage == stage_preference else 0

def _score_growth_rate(growth_percentage):
    """Scores based on employee growth percentage."""
    growth_percentage = _get_numeric_value(None, None, growth_percentage)
    if growth_percentage > 20: return 25 # Very High Growth
    if growth_percentage > 10: return 15 # High Growth
    if growth_percentage > 0: return 5  # Moderate Growth
    if growth_percentage < 0: return -10 # Negative Growth
    return 0

def _score_hiring_activity(hiring_activity_score):
    """Scores based on numerical hiring activity (0-10 scale)."""
    hiring_activity_score = _get_numeric_value(None, None, hiring_activity_score)
    if hiring_activity_score >= 8: return 30 # Very High Activity
    if hiring_activity_score >= 6: return 20 # High Activity
    if hiring_activity_score >= 4: return 10 # Moderate Activity
    if hiring_activity_score > 0: return 5  # Low Activity but present
    return 0

def _score_recent_funding(funding_desc):
    """Scores based on recent funding status."""
    if "series d" in funding_desc.lower() or "($100m)" in funding_desc.lower(): # Top tier funding
        return 40
    if "series c" in funding_desc.lower() or "($50m)" in funding_desc.lower(): # Strong mid-tier funding
        return 35
    if "series b" in funding_desc.lower() or "($20m)" in funding_desc.lower() or "($30m)" in funding_desc.lower(): # Mid-tier funding
        return 30
    if "seed" in funding_desc.lower() or "series a" in funding_desc.lower() or "($5m)" in funding_desc.lower() or "($2m)" in funding_desc.lower(): # Early stage funding
        return 20
    if "secured" in funding_desc.lower() or "raised capital" in funding_desc.lower() or "grant" in funding_desc.lower(): # General positive funding
        return 10
    if "publicly traded" in funding_desc.lower(): # Established company
        return 5
    return 0

# --- Core Data Fetching Functions ---

def fetch_raw_leads(sector, region):
    with open(RAW_LEADS_FILE, "r") as file:
        all_leads = json.load(file)
        # Filter by sector and region (using the raw_leads format)
        filtered = [
            lead for lead in all_leads
            if sector.lower() in lead.get("sector", "").lower()
            and region.lower() in lead.get("region", "").lower()
        ]
    return filtered

def fetch_enriched_leads(company_names):
    with open(ENRICHED_LEADS_FILE, "r") as f:
        all_leads = json.load(f)
    # Ensure exact company name matching from the raw_leads (company_name) to enriched (Company)
    clean_company_names = [name.strip().lower() for name in company_names]
    return [lead for lead in all_leads if lead.get("company_name", "").strip().lower() in clean_company_names]

# --- Ranking Function (Main Logic) ---

# Updated function signature to accept sector and region directly
def rank_enriched_leads(leads, purpose, user_inputs, sector, region):
    ranked = []
    
    for lead in leads:
        score = 0
        
        # --- Common Factors (for all purposes) ---
        
        # Data Completeness
        essential_fields = [
            "Company", "Website", "Industry", "Employees Count", "Revenue",
            "Year Founded", "City", "State", "Company Phone", "Owner's Email"
        ]
        filled_essential_fields = sum(1 for field in essential_fields if lead.get(field) not in [None, "", "0", 0])
        score += (filled_essential_fields / len(essential_fields)) * 10 # Max 10 points for completeness

        # Recency (Using 'Updated' field)
        try:
            updated_date_str = lead.get("Updated")
            if updated_date_str:
                updated_date = datetime.datetime.strptime(updated_date_str, "%Y-%m-%d")
                days_since_update = (datetime.datetime.now() - updated_date).days
                if days_since_update < 90: # Updated in last 3 months
                    score += 10
                elif days_since_update < 365: # Updated in last year
                    score += 5
        except (ValueError, TypeError): # Handle invalid date formats or missing 'Updated' field
            pass 

        # Industry Match (from initial search)
        company_industry_enriched = lead.get("Industry", "").lower()
        if sector.lower() in company_industry_enriched: # Check if the selected sector is present in enriched industry
            score += 20
        elif any(s in company_industry_enriched for s in sector.lower().split()): # Basic related check
            score += 10

        # Location Match (from initial search)
        company_city = lead.get("City", "").lower()
        company_state = lead.get("State", "").lower()
        region_lower = region.lower()

        if region_lower in company_city.lower() or region_lower in company_state.lower():
            score += 20
        elif region_lower.split(" ")[0] in company_city.lower() or region_lower.split(" ")[0] in company_state.lower(): # Partial match (e.g., "San Francisco" in "San Francisco, CA")
            score += 10
        

        # --- Purpose-Specific Scoring ---

        if purpose == "Job Search":
            # Extra Input: Company Size (user_inputs["company_size_preference"])
            employees_count = _get_numeric_value(lead, "Employees Count")
            score += _score_company_size(employees_count, user_inputs.get("company_size_preference", ""))

            # Hiring Activity (Numerical)
            hiring_activity_value = _get_numeric_value(lead, "Hiring Activity")
            score += _score_hiring_activity(hiring_activity_value)

            # Recent Employee Growth %
            employee_growth_perc = _get_numeric_value(lead, "Recent Employee Growth %")
            score += _score_growth_rate(employee_growth_perc)

            # Owner's LinkedIn Availability
            if lead.get("Owner's LinkedIn"):
                score += 10

            # Year Founded (Desirable age for job seekers - examples for growth/established)
            year_founded = _get_numeric_value(lead, "Year Founded")
            current_year = datetime.datetime.now().year
            if current_year - year_founded <= 10 and year_founded > 0: # Founded in last 10 years (growth-oriented)
                score += 15 
            elif current_year - year_founded > 20 and year_founded > 0: # Established (stability)
                score += 10 

            # Professional Presence (Website available, Company LinkedIn available)
            if lead.get("Website") and "http" in lead["Website"]:
                score += 5
            else: 
                score -= 5 # Penalty for no website

            if lead.get("Company LinkedIn"):
                score += 5

            # BBB Rating (Good reputation)
            bbb_rating = lead.get("BBB Rating", "").upper()
            if "A" in bbb_rating: score += 5
            elif "F" in bbb_rating or "D" in bbb_rating: score -= 10


        elif purpose == "Investor Research":
            # Extra Inputs: Investment Stage (user_inputs["investment_stage"]), Revenue Threshold/Valuation (user_inputs["revenue_threshold_valuation"])
            
            revenue = _get_numeric_value(lead, "Revenue")
            score += _score_revenue_threshold(revenue, user_inputs.get("revenue_threshold_valuation", ""))
            
            year_founded = _get_numeric_value(lead, "Year Founded")
            employees_count = _get_numeric_value(lead, "Employees Count")
            funding_status = lead.get("Recent Funding / Investment", "").lower() 
            score += _score_investment_stage(year_founded, employees_count, revenue, funding_status, user_inputs.get("investment_stage", ""))

            # Recent Funding / Investment (Crucial Extra Field)
            score += _score_recent_funding(funding_status)

            # Recent Employee Growth % (Crucial Extra Field)
            employee_growth_perc = _get_numeric_value(lead, "Recent Employee Growth %")
            score += _score_growth_rate(employee_growth_perc)

            # Owner's LinkedIn / Title (Strong leadership, decision-maker)
            owner_title = lead.get("Owner's Title", "").lower()
            if lead.get("Owner's LinkedIn") and any(title in owner_title for title in ["ceo", "founder", "cto", "president", "managing director"]):
                score += 15
            elif lead.get("Owner's LinkedIn"): # Any owner LinkedIn is a plus
                score += 5

            # Product/Service Category (Innovation/Disruption) - based on keywords
            product_category = lead.get("Product/Service Category", "").lower()
            if any(keyword in product_category for keyword in ["ai", "robotics", "genomics", "clean energy", "biotech", "fintech"]): 
                score += 15

            # High Revenue & Employee Count (General health, higher is often better for later stages)
            if revenue > 50000000: score += 10 # High revenue
            if employees_count > 300: score += 5 # Large employee base
            
            # Website quality / professionalism (Implied by presence)
            if lead.get("Website") and "http" in lead["Website"]:
                score += 5


        elif purpose == "Sales Prospecting":
            # Extra Inputs: Buyer Type (user_inputs["buyer_type"]), Your Product (user_inputs["your_product_category"])

            # Buyer Type Match
            company_business_type = lead.get("Business Type (B2B, B2B2C)", "").lower()
            user_buyer_type = user_inputs.get("buyer_type", "").lower()
            if company_business_type == user_buyer_type:
                score += 30
            elif user_buyer_type == "b2b" and company_business_type == "b2b2c": 
                score += 15
            elif user_buyer_type == "b2c" and company_business_type == "b2b2c":
                score += 10


            # Relevance to Your Product (This is critical and needs specific mapping based on your product)
            your_product = user_inputs.get("your_product_category", "").lower()
            product_category = lead.get("Product/Service Category", "").lower()
            industry = lead.get("Industry", "").lower()

            # Example rules (adjust these to your actual product's target market)
            if "crm software" in your_product and ("sales" in product_category or "marketing" in product_category or "client management" in product_category or "consulting" in industry): score += 35
            elif "cloud security" in your_product and ("software" in industry or "technology" in industry or "cybersecurity" in product_category or "it services" in industry): score += 35
            elif "hr software" in your_product and (_get_numeric_value(lead, "Employees Count") > 50 or "human resources" in product_category): score += 35
            
            # If no specific relevance rules, check general fit based on size/revenue
            employees_count = _get_numeric_value(lead, "Employees Count")
            revenue = _get_numeric_value(lead, "Revenue")
            # Example: Your product targets mid-market companies (50-500 employees, >$1M revenue)
            if 50 <= employees_count <= 500 and revenue > 1000000: score += 25 


            # Contact Information Availability (Owner's Email & Phone are highly valuable)
            if lead.get("Owner's Email") and lead.get("Owner's Phone Number"):
                score += 20
            elif lead.get("Owner's LinkedIn"): 
                score += 10
            elif lead.get("Company Phone") or lead.get("Owner's Email"): # Company Email assumed to be mapped to Owner's Email for simplicity
                score += 5
            else: 
                score -= 15

            # Website Availability & Quality
            if lead.get("Website") and "http" in lead["Website"]:
                score += 10
            else:
                score -= 10 

            # BBB Rating (important for trustworthiness)
            bbb_rating = lead.get("BBB Rating", "").upper()
            if "A" in bbb_rating: score += 5
            elif "D" in bbb_rating or "F" in bbb_rating: score -= 10

            # Hiring Activity (Indicates pain point or growth that needs solutions)
            hiring_activity_value = _get_numeric_value(lead, "Hiring Activity")
            if hiring_activity_value >= 7: # High activity, might need solutions
                score += 10 

        elif purpose == "Merger and Acquisition/Partnership":
            # Extra Inputs: Size of Target (user_inputs["target_size_preference"]), Type of Alliance Sought (user_inputs["type_of_alliance"])
            
            employees_count = _get_numeric_value(lead, "Employees Count")
            revenue = _get_numeric_value(lead, "Revenue")
            year_founded = _get_numeric_value(lead, "Year Founded")

            # Size of Target Match
            score += _score_company_size(employees_count, user_inputs.get("target_size_preference", ""))
            
            # Type of Alliance Sought Match (Requires detailed logic based on lead characteristics)
            alliance_type = user_inputs.get("type_of_alliance", "").lower()
            product_category = lead.get("Product/Service Category", "").lower()
            
            if alliance_type == "acquisition target":
                # Ideal: Smaller, high growth, innovative tech, potentially seeking exit
                if year_founded >= 2018 and employees_count < 100 and ("ai" in product_category or "innovative" in product_category or "robotics" in product_category): score += 30
                funding_score = _score_recent_funding(lead.get("Recent Funding / Investment", ""))
                if funding_score > 0: # If they just raised, could be more valuable but more expensive
                    score += funding_score * 0.5 # Add half the funding score
                else: # No recent funding might make them more amenable
                    score += 10 

            elif alliance_type == "strategic partner":
                # Ideal: Established, complementary product, similar target audience, similar size/growth
                if year_founded <= 2018 and 50 <= employees_count <= 500 and "complementary" in product_category: score += 30 # "complementary" keyword would need defining
                # Check for strong LinkedIn presence / website for a good partner
                if lead.get("Company LinkedIn") and lead.get("Website"): score += 10
            
            # Product/Service Category Synergy (Crucial for M&A/Partnership) - highly customized
            # Example: User is in "Healthcare AI" looking for "Diagnostic Software" partners
            # This requires more complex logic, perhaps mapping `sector` and `Industry` with `Product/Service Category`
            if sector.lower() == "healthcare" and "ai" in product_category: # Assuming the sector input from app.py is "Healthcare"
                if "medical device software" in product_category or "telehealth" in product_category:
                    score += 25


            # Revenue & Employee Count (General health, appropriate scale)
            if revenue > 10000000: score += 10 # Solid revenue
            if employees_count > 50: score += 5 # Established team
            
            # Recent Funding / Investment
            funding_status = lead.get("Recent Funding / Investment", "").lower()
            score += _score_recent_funding(funding_status)
            
            # Recent Employee Growth %
            employee_growth_perc = _get_numeric_value(lead, "Recent Employee Growth %")
            if employee_growth_perc > 10: score += 10 # Growing, good for most alliances

            # Owner's LinkedIn / Title (Access to decision-makers)
            if lead.get("Owner's LinkedIn") and lead.get("Owner's Title"):
                score += 10


        elif purpose == "Market Research / Competitive Analysis":
            # Extra Inputs: Your Niche (user_inputs["your_niche"]), Your Revenue (user_inputs["your_revenue"])
            
            # Your Niche Match (Crucial for identifying competitors/market segments)
            company_product_category = lead.get("Product/Service Category", "").lower()
            your_niche = user_inputs.get("your_niche", "").lower()

            if your_niche in company_product_category: # Direct competitor/niche match
                score += 35
            elif any(keyword in company_product_category for keyword in your_niche.split()): # Keyword match within broader niche
                score += 20
            
            # Revenue Comparison (to your revenue for competitor analysis)
            company_revenue = _get_numeric_value(lead, "Revenue")
            your_revenue = _get_numeric_value(None, None, user_inputs.get("your_revenue", 0))

            if your_revenue > 0:
                revenue_diff_ratio = abs(company_revenue - your_revenue) / your_revenue if your_revenue > 0 else float('inf')
                if revenue_diff_ratio < 0.2: # Within 20% - direct competitor size
                    score += 20
                elif company_revenue > your_revenue * 2: # Much larger (market leader)
                    score += 15
                elif company_revenue < your_revenue * 0.5 and company_revenue > 0: # Smaller (emerging/niche player)
                    score += 10
            elif company_revenue > 0: # If user revenue is 0, just look at company revenue for general market insights
                score += 5


            # Hiring Activity (Strategic insights into their growth/focus areas)
            hiring_activity_value = _get_numeric_value(lead, "Hiring Activity")
            score += _score_hiring_activity(hiring_activity_value) # Higher score for more activity

            # Recent Funding / Investment (Signals market interest, potential for aggressive moves)
            funding_status = lead.get("Recent Funding / Investment", "").lower()
            score += _score_recent_funding(funding_status)

            # Recent Employee Growth % (Traction, market share gain)
            employee_growth_perc = _get_numeric_value(lead, "Recent Employee Growth %")
            score += _score_growth_rate(employee_growth_perc) # High growth gets higher score

            # Year Founded (New entrants vs. established players)
            year_founded = _get_numeric_value(lead, "Year Founded")
            current_year = datetime.datetime.now().year
            if current_year - year_founded <= 5 and year_founded > 0: score += 10 # New entrant/disruptor
            elif current_year - year_founded > 20 and year_founded > 0: score += 10 # Established player/market leader

            # Website / Company LinkedIn (Ease of research, strong public presence)
            if lead.get("Website") and lead.get("Company LinkedIn"):
                score += 10


        lead["Rank Score"] = max(0, score) # Ensure score doesn't go negative
        ranked.append(lead)

    ranked.sort(key=lambda x: x["Rank Score"], reverse=True)
    return ranked