import streamlit as st
import pandas as pd
from utils.fetch_data import fetch_raw_leads, fetch_enriched_leads, rank_enriched_leads
import datetime

# --- Initialize Session State Variables ---
if 'sector' not in st.session_state:
    st.session_state.sector = None
if 'region' not in st.session_state:
    st.session_state.region = None
if 'purpose' not in st.session_state:
    st.session_state.purpose = None
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = {}
if 'all_filtered_and_ranked_df' not in st.session_state:
    st.session_state.all_filtered_and_ranked_df = pd.DataFrame()
if 'loading' not in st.session_state:
    st.session_state.loading = False
if 'show_selection_message' not in st.session_state:
    st.session_state.show_selection_message = False
if 'selected_company_names' not in st.session_state:
    st.session_state.selected_company_names = []
if 'detailed_display_df' not in st.session_state:
    st.session_state.detailed_display_df = pd.DataFrame()

# --- Helper function to clear results ---
def clear_results():
    st.session_state.all_filtered_and_ranked_df = pd.DataFrame()
    st.session_state.show_selection_message = False
    st.session_state.selected_company_names = []
    st.session_state.detailed_display_df = pd.DataFrame()
    st.session_state.loading = False

# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="Intelligent Lead Ranking System")

st.title("💡 Intelligent Lead Ranking System")
st.markdown("---")

# --- Define Your Search Criteria & Goal ---
st.header("1. Define Your Search Criteria & Goal")

col1, col2 = st.columns(2)
with col1:
    unique_sectors = ["Healthcare", "Construction", "Retail", "Software", "Renewable Energy", "Finance", "Education", "Food & Beverage", "Technology", "Logistics", "Consulting", "Real Estate", "Agriculture", "Pharmaceutical"]
    selected_sector = st.selectbox(
        "Select Target Sector(s) (e.g., Healthcare, Technology, All)",
        options=["All"] + unique_sectors,
        key="sector_input",
        on_change=clear_results
    )
    if selected_sector == "All":
        st.session_state.sector = ""
    else:
        st.session_state.sector = selected_sector

with col2:
    unique_regions = ["California", "Texas", "Washington", "Oregon", "New York", "Massachusetts", "Florida", "Illinois", "New Jersey"]
    selected_region = st.selectbox(
        "Select Target Region(s) (e.g., California, Texas, All)",
        options=["All"] + unique_regions,
        key="region_input",
        on_change=clear_results
    )
    if selected_region == "All":
        st.session_state.region = ""
    else:
        st.session_state.region = selected_region

selected_purpose = st.selectbox(
    "What is your primary goal for these leads?",
    options=["Select Purpose", "Job Search", "Investor Research", "Sales Prospecting", "Merger and Acquisition/Partnership", "Market Research / Competitive Analysis"],
    key="purpose_input",
    on_change=clear_results
)
if selected_purpose != st.session_state.get('purpose', None):
    clear_results()
    st.session_state.user_inputs = {}
st.session_state.purpose = selected_purpose


# --- Conditional Inputs based on Purpose ---
if st.session_state.purpose != "Select Purpose":
    st.header(f"2. Customize Criteria for: {st.session_state.purpose}")
    
    if st.session_state.purpose == "Job Search":
        current_company_size_preference = st.session_state.user_inputs.get("company_size_preference", "")
        st.session_state.user_inputs["company_size_preference"] = st.selectbox(
            "Preferred Company Size:",
            options=["", "Small (1-50 employees)", "Medium (51-500 employees)", "Large (500+ employees)"],
            index=["", "Small (1-50 employees)", "Medium (51-500 employees)", "Large (500+ employees)"].index(current_company_size_preference),
            key="job_size_pref",
            on_change=clear_results
        )
        # current_desired_role_focus = st.session_state.user_inputs.get("desired_role_focus", "")
        # st.session_state.user_inputs["desired_role_focus"] = st.selectbox(
        #     "Desired Role Focus (e.g., Engineering, Sales, HR):",
        #     options=["", "Engineering", "Sales", "Marketing", "Human Resources", "Finance", "Operations", "Product Management", "Executive"],
        #     index=["", "Engineering", "Sales", "Marketing", "Human Resources", "Finance", "Operations", "Product Management", "Executive"].index(current_desired_role_focus),
        #     key="job_role_focus",
        #     on_change=clear_results
        # )

    elif st.session_state.purpose == "Investor Research":
        current_investment_stage = st.session_state.user_inputs.get("investment_stage", "")
        st.session_state.user_inputs["investment_stage"] = st.selectbox(
            "Preferred Investment Stage:",
            options=["", "Seed/Angel", "Series A/B", "Growth Equity", "Mature/Public Ready"],
            index=["", "Seed/Angel", "Series A/B", "Growth Equity", "Mature/Public Ready"].index(current_investment_stage),
            key="inv_stage_pref",
            on_change=clear_results
        )
        current_revenue_threshold_valuation = st.session_state.user_inputs.get("revenue_threshold_valuation", "")
        st.session_state.user_inputs["revenue_threshold_valuation"] = st.selectbox(
            "Revenue Threshold / Valuation:",
            options=["", "Under $1M", "$1M - $5M", "$5M - $10M", "$10M - $50M", "$50M - $100M", "Over $100M"],
            index=["", "Under $1M", "$1M - $5M", "$5M - $10M", "$10M - $50M", "$50M - $100M", "Over $100M"].index(current_revenue_threshold_valuation),
            key="inv_rev_val",
            on_change=clear_results
        )
        # current_tech_focus = st.session_state.user_inputs.get("tech_focus", "")
        # st.session_state.user_inputs["tech_focus"] = st.selectbox(
        #     "Focus Technology/Industry Areas:",
        #     options=["", "AI", "Robotics", "Fintech", "Biotech", "Clean Energy", "SaaS", "E-commerce", "Healthcare IT", "Logistics Tech", "EdTech"],
        #     index=["", "AI", "Robotics", "Fintech", "Biotech", "Clean Energy", "SaaS", "E-commerce", "Healthcare IT", "Logistics Tech", "EdTech"].index(current_tech_focus),
        #     key="inv_tech_focus",
        #     on_change=clear_results
        # )

    elif st.session_state.purpose == "Sales Prospecting":
        current_buyer_type = st.session_state.user_inputs.get("buyer_type", "")
        st.session_state.user_inputs["buyer_type"] = st.selectbox(
            "Target Buyer Type:",
            options=["", "B2B", "B2C", "B2B2C"],
            index=["", "B2B", "B2C", "B2B2C"].index(current_buyer_type),
            key="sales_buyer_type",
            on_change=clear_results
        )
        current_product_category = st.session_state.user_inputs.get("your_product_category", "")
        st.session_state.user_inputs["your_product_category"] = st.selectbox(
            "Your Product/Service Category (select the best fit):",
            options=["", "CRM Software", "Cloud Security", "HR Software", "Marketing Automation", "Data Analytics Platform", "Financial Advisory", "Supply Chain Management", "Project Management Tools", "E-commerce Solutions", "AI/ML Solutions"],
            index=["", "CRM Software", "Cloud Security", "HR Software", "Marketing Automation", "Data Analytics Platform", "Financial Advisory", "Supply Chain Management", "Project Management Tools", "E-commerce Solutions", "AI/ML Solutions"].index(current_product_category),
            key="sales_prod_cat",
            on_change=clear_results
        )
        # current_pain_points_addressed = st.session_state.user_inputs.get("pain_points_addressed", "")
        # st.session_state.user_inputs["pain_points_addressed"] = st.selectbox(
        #     "Common Pain Points Your Product Solves:",
        #     options=["", "Inefficient Operations", "Lack of Data Insights", "Cybersecurity Risks", "High Employee Turnover", "Poor Customer Engagement", "Slow Growth", "Compliance Issues", "Manual Processes"],
        #     index=["", "Inefficient Operations", "Lack of Data Insights", "Cybersecurity Risks", "High Employee Turnover", "Poor Customer Engagement", "Slow Growth", "Compliance Issues", "Manual Processes"].index(current_pain_points_addressed),
        #     key="sales_pain_points",
        #     on_change=clear_results
        # )

    elif st.session_state.purpose == "Merger and Acquisition/Partnership":
        current_target_size_preference = st.session_state.user_inputs.get("target_size_preference", "")
        st.session_state.user_inputs["target_size_preference"] = st.selectbox(
            "Preferred Target Company Size:",
            options=["", "Small (1-50 employees)", "Medium (51-500 employees)", "Large (500+ employees)"],
            index=["", "Small (1-50 employees)", "Medium (51-500 employees)", "Large (500+ employees)"].index(current_target_size_preference),
            key="ma_target_size",
            on_change=clear_results
        )
        current_type_of_alliance = st.session_state.user_inputs.get("type_of_alliance", "")
        st.session_state.user_inputs["type_of_alliance"] = st.selectbox(
            "Type of Alliance Sought:",
            options=["", "Acquisition Target", "Strategic Partner", "Joint Venture"],
            index=["", "Acquisition Target", "Strategic Partner", "Joint Venture"].index(current_type_of_alliance),
            key="ma_alliance_type",
            on_change=clear_results
        )
        current_synergy_areas = st.session_state.user_inputs.get("synergy_areas", "")
        st.session_state.user_inputs["synergy_areas"] = st.selectbox(
            "Key Synergy Areas:",
            options=["", "Market Expansion", "Technology Integration", "Talent Acquisition", "Cost Reduction", "Product Diversification", "Customer Base Access"],
            index=["", "Market Expansion", "Technology Integration", "Talent Acquisition", "Cost Reduction", "Product Diversification", "Customer Base Access"].index(current_synergy_areas),
            key="ma_synergy",
            on_change=clear_results
        )

    elif st.session_state.purpose == "Market Research / Competitive Analysis":
        current_niche = st.session_state.user_inputs.get("your_niche", "")
        st.session_state.user_inputs["your_niche"] = st.selectbox(
            "Your Niche/Product Category (select the best fit):",
            options=["", "Healthcare AI Software", "Sustainable Construction Materials", "Luxury Fashion E-commerce", "Cybersecurity Solutions", "Supply Chain Management Software", "Cloud Infrastructure", "Drug Discovery", "Urban Planning", "Data Strategy Consulting", "Organic Farming", "K-12 Learning Software", "Pharmaceutical Manufacturing", "Industrial Automation", "Wealth Management"],
            index=["", "Healthcare AI Software", "Sustainable Construction Materials", "Luxury Fashion E-commerce", "Cybersecurity Solutions", "Supply Chain Management Software", "Cloud Infrastructure", "Drug Discovery", "Urban Planning", "Data Strategy Consulting", "Organic Farming", "K-12 Learning Software", "Pharmaceutical Manufacturing", "Industrial Automation", "Wealth Management"].index(current_niche),
            key="mr_niche",
            on_change=clear_results
        )
        current_revenue_range = st.session_state.user_inputs.get("your_revenue_range", "")
        st.session_state.user_inputs["your_revenue_range"] = st.selectbox(
            "Your Company's Approximate Annual Revenue Range (for comparison):",
            options=["", "Under $1M", "$1M - $5M", "$5M - $10M", "$10M - $50M", "$50M - $100M", "Over $100M"],
            index=["", "Under $1M", "$1M - $5M", "$5M - $10M", "$10M - $50M", "$50M - $100M", "Over $100M"].index(current_revenue_range),
            key="mr_your_revenue_range",
            on_change=clear_results
        )
        current_competitor_focus = st.session_state.user_inputs.get("competitor_focus", "Direct Competitors")
        st.session_state.user_inputs["competitor_focus"] = st.radio(
            "Focus on:",
            options=["Direct Competitors", "Adjacent Market Players", "Emerging Disruptors"],
            index=["Direct Competitors", "Adjacent Market Players", "Emerging Disruptors"].index(current_competitor_focus),
            key="mr_focus",
            on_change=clear_results
        )


st.markdown("---")
st.header("3. Find & Rank Leads")

# --- The Single Action Button ---
button_disabled = (st.session_state.purpose == "Select Purpose")

if st.button("🔎 Find & Rank Leads", key="find_rank_button", disabled=button_disabled):
    st.session_state.loading = True
    clear_results() # Ensure all results are cleared before a new search begins

    with st.spinner("Fetching, enriching, and ranking leads... This might take a moment based on the number of leads."):
        st.write("Step 1: Filtering raw leads by **Sector** and **Region**...")
        filtered_raw_leads = fetch_raw_leads(st.session_state.sector, st.session_state.region)
        
        if not filtered_raw_leads:
            st.warning("No raw leads found matching your sector and region criteria. Please adjust your search.")
            st.session_state.loading = False
            st.stop()

        company_names_to_enrich = [lead["company_name"] for lead in filtered_raw_leads]

        st.write(f"Step 2: Enriching {len(company_names_to_enrich)} filtered leads...")
        enriched_leads_data = fetch_enriched_leads(company_names_to_enrich)
        
        if not enriched_leads_data:
            st.warning("No enriched data found for the filtered raw leads. Check your `enriched_leads.json` file or selected criteria.")
            st.session_state.loading = False
            st.stop()

        st.write("Step 3: Ranking leads based on your **purpose** and **custom criteria**...")
        final_ranked_leads = rank_enriched_leads(
            enriched_leads_data,
            st.session_state.purpose,
            st.session_state.user_inputs,
            st.session_state.sector,
            st.session_state.region
        )
        
        st.session_state.all_filtered_and_ranked_df = pd.DataFrame(final_ranked_leads)
        
        st.success("Leads fetched, enriched, and ranked successfully!")
        st.session_state.show_selection_message = True
    st.session_state.loading = False


# --- Display Ranked Results Table for Selection ---
if not st.session_state.all_filtered_and_ranked_df.empty:
    st.header("4. Top Ranked Leads for Your Selection")
    st.markdown("Select companies from the ranked list below for a detailed view. Higher **Rank Score** indicates a better fit.")

    display_df = st.session_state.all_filtered_and_ranked_df.copy()
    
    if 'Website' not in display_df.columns:
        display_df['Website'] = ''
    if 'Industry' not in display_df.columns:
        display_df['Industry'] = ''
    if 'City' not in display_df.columns:
        display_df['City'] = ''
    if 'State' not in display_df.columns:
        display_df['State'] = ''

    display_df['Location'] = display_df['City'] + ", " + display_df['State']
    display_df['Sector'] = display_df['Industry']
    if 'Region' not in display_df.columns and 'State' in display_df.columns:
        display_df['Region'] = display_df['State']

    display_cols_for_selection = [
        "Company", "Location", "Sector", "Region", "Website", "Rank Score"
    ]
    existing_selection_cols = [col for col in display_cols_for_selection if col in display_df.columns]
    
    display_df['Select'] = False

    edited_df = st.data_editor(
        display_df[existing_selection_cols + ['Select']],
        column_order=['Select'] + existing_selection_cols,
        hide_index=True,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select company for detailed view",
                default=False,
            ),
            "Website": st.column_config.LinkColumn(
                "Website",
                help="Company Website",
                display_text="🌐 Website"
            ),
            "Rank Score": st.column_config.ProgressColumn(
                "Rank Score",
                help="Overall match score based on your criteria",
                format="%f",
                min_value=0,
                max_value=max(display_df['Rank Score'].max(), 100)
            )
        },
        num_rows="dynamic",
        use_container_width=True,
        key="ranked_leads_editor"
    )

    st.session_state.selected_company_names = edited_df[edited_df['Select']]['Company'].tolist()

    if st.session_state.show_selection_message:
        st.info("👆 Select companies using the checkboxes above for a detailed view below.")
        st.session_state.show_selection_message = False

    # --- New Button for Detailed Data ---
    if st.session_state.selected_company_names:
        if st.button("Show Detailed Information for Selected Leads", key="show_detailed_button"):
            st.subheader("5. Detailed Information for Selected Leads")
            st.markdown("Here are the full details for the companies you selected.")
            
            st.session_state.detailed_display_df = st.session_state.all_filtered_and_ranked_df[
                st.session_state.all_filtered_and_ranked_df['Company'].isin(st.session_state.selected_company_names)
            ].copy()

            if 'Select' in st.session_state.detailed_display_df.columns:
                st.session_state.detailed_display_df = st.session_state.detailed_display_df.drop(columns=['Select'])

            st.dataframe(st.session_state.detailed_display_df, use_container_width=True)

            csv_data_selected = st.session_state.detailed_display_df.to_csv(index=False)
            st.download_button(
                label="Download Selected Leads Details as CSV",
                data=csv_data_selected,
                file_name=f"selected_leads_for_{st.session_state.purpose.replace(' ', '_').lower()}.csv",
                mime="text/csv"
            )
    else:
        if not st.session_state.detailed_display_df.empty and st.session_state.get('last_selected_company_count', 0) > 0:
            st.session_state.detailed_display_df = pd.DataFrame()
        st.session_state.last_selected_company_count = len(st.session_state.selected_company_names)