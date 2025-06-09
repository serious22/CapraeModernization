import streamlit as st
import pandas as pd
from utils.fetch_data import fetch_raw_leads, fetch_enriched_leads, rank_enriched_leads
import datetime # Make sure this import is present if not already


# --- 1. Initialize Session State Variables (Crucial for Streamlit) ---
if 'sector' not in st.session_state:
    st.session_state.sector = None
if 'region' not in st.session_state:
    st.session_state.region = None
if 'purpose' not in st.session_state:
    st.session_state.purpose = None
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = {}
if 'all_filtered_and_ranked_df' not in st.session_state: # To store the fully ranked DataFrame
    st.session_state.all_filtered_and_ranked_df = pd.DataFrame()
if 'loading' not in st.session_state:
    st.session_state.loading = False
if 'show_selection_message' not in st.session_state: # To control when to show the "select leads" message
    st.session_state.show_selection_message = False
if 'selected_company_names' not in st.session_state: # To store names of companies user selects from the ranked table
    st.session_state.selected_company_names = []
if 'detailed_display_df' not in st.session_state: # For displaying detailed info of selected leads
    st.session_state.detailed_display_df = pd.DataFrame()

# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="Intelligent Lead Ranking System")

st.title("💡 Intelligent Lead Ranking System")
st.markdown("---")

# --- 2. Define Your Search Criteria & Goal ---
st.header("1. Define Your Search Criteria & Goal")

col1, col2 = st.columns(2)
with col1:
    unique_sectors = ["Healthcare", "Construction", "Retail", "Software", "Renewable Energy", "Finance", "Education", "Food & Beverage", "Technology", "Logistics", "Consulting", "Real Estate", "Agriculture", "Pharmaceutical"]
    st.session_state.sector = st.selectbox(
        "Select Target Sector(s) (e.g., Healthcare, Technology, All)",
        options=["All"] + unique_sectors,
        key="sector_input"
    )
    if st.session_state.sector == "All":
        st.session_state.sector = ""

with col2:
    unique_regions = ["California", "Texas", "Washington", "Oregon", "New York", "Massachusetts", "Florida", "Illinois", "New Jersey"]
    st.session_state.region = st.selectbox(
        "Select Target Region(s) (e.g., California, Texas, All)",
        options=["All"] + unique_regions,
        key="region_input"
    )
    if st.session_state.region == "All":
        st.session_state.region = ""

st.session_state.purpose = st.selectbox(
    "What is your primary goal for these leads?",
    options=["Select Purpose", "Job Search", "Investor Research", "Sales Prospecting", "Merger and Acquisition/Partnership", "Market Research / Competitive Analysis"],
    key="purpose_input"
)

# --- 3. Conditional Inputs based on Purpose ---
if st.session_state.purpose != "Select Purpose":
    st.header(f"2. Customize Criteria for: {st.session_state.purpose}")
    # Initialize user_inputs for the current purpose to prevent issues if a new purpose is selected
    if st.session_state.purpose != st.session_state.get('last_selected_purpose_for_inputs', ''):
        st.session_state.user_inputs = {}
        st.session_state.last_selected_purpose_for_inputs = st.session_state.purpose

    if st.session_state.purpose == "Job Search":
        st.session_state.user_inputs["company_size_preference"] = st.multiselect(
            "Preferred Company Size:",
            options=["Small (1-50 employees)", "Medium (51-500 employees)", "Large (500+ employees)"],
            default=st.session_state.user_inputs.get("company_size_preference", []), # Retain previous selection
            key="job_size_pref"
        )
        # Add other job search specific inputs here
        # st.session_state.user_inputs["desired_role_keywords"] = st.text_input("Keywords for desired roles (e.g., 'Senior Software Engineer')", value=st.session_state.user_inputs.get("desired_role_keywords", ""), key="job_role_keywords")


    elif st.session_state.purpose == "Investor Research":
        st.session_state.user_inputs["investment_stage"] = st.selectbox(
            "Preferred Investment Stage:",
            options=["", "Seed/Angel", "Series A/B", "Growth Equity", "Mature/Public Ready"],
            index=["", "Seed/Angel", "Series A/B", "Growth Equity", "Mature/Public Ready"].index(st.session_state.user_inputs.get("investment_stage", "")), # Retain previous selection
            key="inv_stage_pref"
        )
        st.session_state.user_inputs["revenue_threshold_valuation"] = st.text_input(
            "Revenue Threshold / Valuation (e.g., '> $10M ARR', '< $5M Valuation')",
            value=st.session_state.user_inputs.get("revenue_threshold_valuation", ""), # Retain previous selection
            key="inv_rev_val"
        )
        # Add other investor specific inputs here

    elif st.session_state.purpose == "Sales Prospecting":
        st.session_state.user_inputs["buyer_type"] = st.selectbox(
            "Target Buyer Type:",
            options=["", "B2B", "B2C", "B2B2C"],
            index=["", "B2B", "B2C", "B2B2C"].index(st.session_state.user_inputs.get("buyer_type", "")), # Retain previous selection
            key="sales_buyer_type"
        )
        st.session_state.user_inputs["your_product_category"] = st.text_input(
            "Briefly describe your product/service category (e.g., 'CRM Software', 'Cloud Security')",
            value=st.session_state.user_inputs.get("your_product_category", ""), # Retain previous selection
            key="sales_prod_cat"
        )
        # Add other sales specific inputs here

    elif st.session_state.purpose == "Merger and Acquisition/Partnership":
        st.session_state.user_inputs["target_size_preference"] = st.multiselect(
            "Preferred Target Company Size:",
            options=["Small (1-50 employees)", "Medium (51-500 employees)", "Large (500+ employees)"],
            default=st.session_state.user_inputs.get("target_size_preference", []), # Retain previous selection
            key="ma_target_size"
        )
        st.session_state.user_inputs["type_of_alliance"] = st.selectbox(
            "Type of Alliance Sought:",
            options=["", "Acquisition Target", "Strategic Partner", "Joint Venture"],
            index=["", "Acquisition Target", "Strategic Partner", "Joint Venture"].index(st.session_state.user_inputs.get("type_of_alliance", "")), # Retain previous selection
            key="ma_alliance_type"
        )
        # Add other M&A specific inputs here

    elif st.session_state.purpose == "Market Research / Competitive Analysis":
        st.session_state.user_inputs["your_niche"] = st.text_input(
            "Describe your niche/product category (e.g., 'Healthcare AI Software', 'Sustainable Construction Materials')",
            value=st.session_state.user_inputs.get("your_niche", ""), # Retain previous selection
            key="mr_niche"
        )
        st.session_state.user_inputs["your_revenue"] = st.text_input(
            "Your company's approximate annual revenue (for comparison, e.g., '$5M', '$50,000')",
            value=st.session_state.user_inputs.get("your_revenue", ""), # Retain previous selection
            key="mr_your_revenue"
        )
        # Add other market research specific inputs here


st.markdown("---")
st.header("3. Find & Rank Leads")

# --- The Single Action Button ---
# Disable button if purpose is not selected
button_disabled = (st.session_state.purpose == "Select Purpose")

if st.button("🔎 Find & Rank Leads", key="find_rank_button", disabled=button_disabled):
    st.session_state.loading = True
    st.session_state.all_filtered_and_ranked_df = pd.DataFrame() # Clear previous results
    st.session_state.show_selection_message = False # Hide previous selection message
    st.session_state.selected_company_names = [] # Clear selected names
    st.session_state.detailed_display_df = pd.DataFrame() # Clear detailed view

    with st.spinner("Fetching, enriching, and ranking leads... This might take a moment based on the number of leads."):
        # Step 1: Filter raw leads based on initial sector and region
        st.write("Step 1: Filtering raw leads by Sector and Region...")
        filtered_raw_leads = fetch_raw_leads(st.session_state.sector, st.session_state.region)
        
        if not filtered_raw_leads:
            st.warning("No raw leads found matching your sector and region criteria. Please adjust your search.")
            st.session_state.loading = False
            st.stop() # Stop execution here if no leads

        # Extract company names for enrichment - ALL filtered raw leads will be enriched
        company_names_to_enrich = [lead["company_name"] for lead in filtered_raw_leads]

        # Step 2: Enrich ALL filtered raw leads
        st.write(f"Step 2: Enriching {len(company_names_to_enrich)} filtered leads...")
        enriched_leads_data = fetch_enriched_leads(company_names_to_enrich)
        
        if not enriched_leads_data:
            st.warning("No enriched data found for the filtered raw leads. Check your enriched_leads.json file or selected criteria.")
            st.session_state.loading = False
            st.stop()

        # Step 3: Rank the enriched leads based on purpose and specific inputs
        st.write("Step 3: Ranking leads based on your purpose and custom criteria...")
        final_ranked_leads = rank_enriched_leads(
            enriched_leads_data,
            st.session_state.purpose,
            st.session_state.user_inputs,
            st.session_state.sector, # Pass the original sector for ranking
            st.session_state.region  # Pass the original region for ranking
        )
        
        # Convert to DataFrame for better display
        st.session_state.all_filtered_and_ranked_df = pd.DataFrame(final_ranked_leads)
        
        # Display the results
        st.success("Leads fetched, enriched, and ranked successfully!")
        st.session_state.show_selection_message = True # Show the selection message after results are loaded
    st.session_state.loading = False


# --- 4. Display Ranked Results Table for Selection ---
if not st.session_state.all_filtered_and_ranked_df.empty:
    st.header("4. Top Ranked Leads for Your Selection")
    st.markdown("Select the companies from the ranked list below for a detailed view. The higher the 'Rank Score', the better the fit.")

    # Convert DataFrame to display format and ensure 'Website' exists
    display_df = st.session_state.all_filtered_and_ranked_df.copy()
    
    # Ensure 'Website' column exists, if not, create it as empty
    if 'Website' not in display_df.columns:
        display_df['Website'] = ''

    # Filter columns to display initially for raw lead selection
    display_cols_for_selection = [
        "Company", "Location", "Sector", "Region", "Website", "Rank Score"
    ]
    # Make sure these columns exist before trying to select them
    existing_selection_cols = [col for col in display_cols_for_selection if col in display_df.columns]
    
    # Add a checkbox column for user selection
    display_df['Select'] = False # Initialize selection column

    # Use st.data_editor for interactive selection
    edited_df = st.data_editor(
        display_df[existing_selection_cols + ['Select']],
        column_order=['Select'] + existing_selection_cols, # Put checkbox first
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
                display_text="🌐 Website" # Display a link icon
            )
        },
        num_rows="dynamic", # Allow adding/deleting rows if needed (though not directly used here)
        use_container_width=True,
        key="ranked_leads_editor" # Unique key for the data_editor
    )

    # Get selected companies
    st.session_state.selected_company_names = edited_df[edited_df['Select']]['Company'].tolist()

    if st.session_state.show_selection_message:
        st.info("👆 Please select companies using the checkboxes above for a detailed view below.")
        st.session_state.show_selection_message = False # Only show once

    if st.session_state.selected_company_names:
        st.subheader("5. Detailed Information for Selected Leads")
        st.markdown("Here are the full details for the companies you selected.")
        
        # Filter the original ranked dataframe to get full details for selected companies
        # Use .isin() for efficient lookup of multiple company names
        st.session_state.detailed_display_df = st.session_state.all_filtered_and_ranked_df[
            st.session_state.all_filtered_and_ranked_df['Company'].isin(st.session_state.selected_company_names)
        ].copy() # Make a copy to avoid SettingWithCopyWarning

        # Optional: Hide 'Select' column if it was copied over
        if 'Select' in st.session_state.detailed_display_df.columns:
            st.session_state.detailed_display_df = st.session_state.detailed_display_df.drop(columns=['Select'])

        st.dataframe(st.session_state.detailed_display_df, use_container_width=True)

        # Optional: Download button for selected leads
        csv_data_selected = st.session_state.detailed_display_df.to_csv(index=False)
        st.download_button(
            label="Download Selected Leads Details as CSV",
            data=csv_data_selected,
            file_name=f"selected_leads_for_{st.session_state.purpose.replace(' ', '_').lower()}.csv",
            mime="text/csv"
        )
    else:
        if not st.session_state.detailed_display_df.empty: # Only show this if there was previously a detailed view but now nothing selected
            st.info("Select companies from the ranked list above to see their detailed information here.")