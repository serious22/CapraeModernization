import streamlit as st
import pandas as pd
import json
import os
import joblib # For loading the trained model and preprocessors
import re # For cleaning revenue strings
import numpy as np # For numerical operations and NaN handling
# from utils.fetch_data import fetch_raw_leads, fetch_enriched_leads, rank_enriched_leads # Assuming these functions are now integrated or defined here


# --- Streamlit App Layout ---
# set_page_config() must be the very first Streamlit command
st.set_page_config(layout="wide", page_title="Intelligent Lead Ranking System")


# --- Configuration for data and models ---
DATA_DIR = 'data'
MODELS_DIR = 'models'
RAW_LEADS_FILE = 'raw_leads.json'
ENRICHED_LEADS_FILE = 'enriched_leads.json'
RANKING_MODEL_FILE = 'ranking_model.pkl' # This will be loaded from the models directory

# --- Data Loading (Integrated from fetch_data.py concept) ---
@st.cache_data # Use st.cache_data to load data only once
def load_json_data(file_path):
    abs_path = os.path.join(os.getcwd(), DATA_DIR, file_path)
    try:
        with open(abs_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Error: Data file '{file_path}' not found at '{abs_path}'. Please ensure the data files are in the '{DATA_DIR}' directory.")
        return []
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode JSON from '{file_path}'. Check file format.")
        return []

RAW_LEADS_DATA = load_json_data(RAW_LEADS_FILE)
ENRICHED_LEADS_DATA = load_json_data(ENRICHED_LEADS_FILE)


# --- ML Model and Preprocessor Loading ---
@st.cache_resource # Use st.cache_resource to load the ML assets only once
def load_ml_assets():
    model_path = os.path.join(os.getcwd(), MODELS_DIR, RANKING_MODEL_FILE)
    
    try:
        model = joblib.load(model_path)
        st.success("ML ranking model loaded successfully!")
        return model
    except FileNotFoundError:
        st.error(f"ML model '{RANKING_MODEL_FILE}' not found at '{model_path}'. Please run 'train_model.py' first.")
        return None
    except Exception as e:
        st.error(f"Error loading ML assets: {e}")
        return None

ml_ranking_pipeline = load_ml_assets()

# --- Functions for Lead Processing (Integrated from fetch_data.py concept) ---

def fetch_raw_leads_integrated(sector=None, region=None):
    """Fetches raw leads based on sector and region."""
    df_raw = pd.DataFrame(RAW_LEADS_DATA)
    if sector and sector != "All":
        df_raw = df_raw[df_raw['sector'] == sector]
    if region and region != "All":
        df_raw = df_raw[df_raw['region'] == region]
    return df_raw.to_dict('records')

def fetch_enriched_leads_integrated(company_names):
    """Fetches enriched data for a list of company names."""
    df_enriched = pd.DataFrame(ENRICHED_LEADS_DATA)
    # Ensure 'company_name' is the key for merging/filtering
    df_filtered = df_enriched[df_enriched['company_name'].isin(company_names)]
    return df_filtered.to_dict('records')


def preprocess_for_prediction(df_to_predict):
    """
    Preprocesses the DataFrame for ML prediction.
    MUST match the preprocessing steps in train_model.py exactly.
    """
    df_processed = df_to_predict.copy()

    # Convert numerical features
    df_processed['Employees Count'] = pd.to_numeric(df_processed['Employees Count'], errors='coerce')
    # Remove '$' and ',' from Revenue and convert to numeric
    df_processed['Revenue_Numeric'] = df_processed['Revenue'].replace({r'\$': '', r',': ''}, regex=True).astype(float) / 1_000_000
    df_processed['Hiring Activity'] = pd.to_numeric(df_processed['Hiring Activity'], errors='coerce')
    df_processed['Recent Employee Growth %'] = pd.to_numeric(df_processed['Recent Employee Growth %'], errors='coerce')

    # Create binary feature for funding presence
    df_processed['Is_Funded'] = df_processed['Recent Funding / Investment'].apply(
        lambda x: 1 if pd.notna(x) and str(x).lower() not in ["none reported", "n/a", ""] else 0
    )

    # Fill NaNs for numerical features - consistent with training (using mean here)
    for col in ['Employees Count', 'Revenue_Numeric', 'Hiring Activity', 'Recent Employee Growth %']:
        if col in df_processed.columns:
            df_processed[col].fillna(0, inplace=True) # Fallback to 0 if no training mean available
    
    # Select features that the model was trained on
    numerical_features_used = [
        'Employees Count',
        'Revenue_Numeric',
        'Hiring Activity',
        'Recent Employee Growth %',
        'Is_Funded'
    ]
    categorical_features_used = [
        'Industry',
        'Product/Service Category',
        'Business Type (B2B, B2B2C)'
    ]

    # Return only the columns needed by the model
    return df_processed[numerical_features_used + categorical_features_used]


def rank_enriched_leads_ml_integrated(filtered_leads_df):
    """
    Ranks enriched leads using the loaded ML model.
    """
    if filtered_leads_df.empty:
        return pd.DataFrame()

    if ml_ranking_pipeline is None: # Changed 'is' to '===' for robustness
        st.warning("ML ranking model not loaded. Please ensure the model is trained and saved. Falling back to a basic ranking logic.")
        # Fallback to a simple ranking logic if the ML model is not available
        filtered_leads_df['Rank Score'] = 0
        return filtered_leads_df.sort_values(by='Rank Score', ascending=False)

    try:
        # Preprocess data for prediction using the loaded pipeline's preprocessor
        features_for_prediction = preprocess_for_prediction(filtered_leads_df)
        
        # Make predictions
        predicted_ranks = ml_ranking_pipeline.predict(features_for_prediction)
        
        # Add predicted ranks to the DataFrame
        filtered_leads_df['Rank Score'] = predicted_ranks

        # Ensure rank scores are integers and within 0-100
        filtered_leads_df['Rank Score'] = filtered_leads_df['Rank Score'].clip(0, 100).astype(int)

        return filtered_leads_df.sort_values(by='Rank Score', ascending=False)

    except Exception as e:
        st.error(f"Error during ML ranking: {e}. Please check the model and input data.")
        # Fallback to a default ranking or return empty if an aerror occurs
        filtered_leads_df['Rank Score'] = 0
        return filtered_leads_df.sort_values(by='Rank Score', ascending=False)


# --- Initialize Session State Variables ---
# Ensure all session state variables used are initialized
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
if 'last_selected_company_count' not in st.session_state: # New initialization
    st.session_state.last_selected_company_count = 0

# --- Helper function to clear results ---
def clear_results():
    st.session_state.all_filtered_and_ranked_df = pd.DataFrame()
    st.session_state.show_selection_message = False
    st.session_state.selected_company_names = []
    st.session_state.detailed_display_df = pd.DataFrame()
    st.session_state.loading = False
    # Ensure the editor's state is also reset for the checkbox column
    if 'ranked_leads_editor' in st.session_state:
        del st.session_state['ranked_leads_editor']


st.title("💡 Intelligent Lead Ranking System")
st.markdown("---")

# --- Define Your Search Criteria & Goal ---
st.header("1. Define Your Search Criteria & Goal")

col1, col2 = st.columns(2)
with col1:
    unique_sectors = sorted(pd.DataFrame(RAW_LEADS_DATA)['sector'].unique().tolist()) # Use sorted unique values
    selected_sector = st.selectbox(
        "Select Target Sector(s) (e.g., Healthcare, Technology, All)",
        options=["All"] + unique_sectors,
        key="sector_input",
        on_change=clear_results
    )
    st.session_state.sector = selected_sector if selected_sector != "All" else ""

with col2:
    unique_regions = sorted(pd.DataFrame(RAW_LEADS_DATA)['region'].unique().tolist()) # Use sorted unique values
    selected_region = st.selectbox(
        "Select Target Region(s) (e.g., California, Texas, All)",
        options=["All"] + unique_regions,
        key="region_input",
        on_change=clear_results
    )
    st.session_state.region = selected_region if selected_region != "All" else ""

# Define purposes and their associated criteria with predefined options for dropdowns
PURPOSES_AND_CRITERIA_OPTIONS = {
    "Select Purpose": {}, # Added "Select Purpose" to the options
    "Job Search": {
        "Preferred Company Size": ["All", "Small (1-50 employees)", "Medium (51-500 employees)", "Large (500+ employees)"],
        # "Desired Role Focus": ["All", "Software Development", "Data Science", "Marketing", "Sales", "Human Resources", "Operations"]
    },
    "Investor Research": {
        "Preferred Investment Stage": ["All", "Seed/Angel", "Series A/B", "Growth Equity", "Mature/Public Ready"],
        "Revenue Threshold / Valuation": ["All", "Under $1M", "$1M - $5M", "$5M - $10M", "$10M - $50M", "$50M - $100M", "Over $100M"],
        # "Focus Technology/Industry Areas": ["All", "AI", "Robotics", "Fintech", "Biotech", "Clean Energy", "SaaS", "E-commerce", "Healthcare IT", "Logistics Tech", "EdTech"]
    },
    "Sales Prospecting": {
        "Target Buyer Type": ["All", "B2B", "B2C", "B2B2C"],
        "Your Product/Service Category": ["All", "CRM Software", "Cloud Security", "HR Software", "Marketing Automation", "Data Analytics Platform", "Financial Advisory", "Supply Chain Management", "Project Management Tools", "E-commerce Solutions", "AI/ML Solutions"],
        # "Common Pain Points Your Product Solves": ["All", "Inefficient Operations", "Lack of Data Insights", "Cybersecurity Risks", "High Employee Turnover", "Poor Customer Engagement", "Slow Growth", "Compliance Issues", "Manual Processes"]
    },
    "Merger and Acquisition/Partnership": {
        "Target Acquisition Criteria": ["All", "Market Share Expansion", "Technology Acquisition", "Talent Acquisition", "Geographic Expansion"],
        "Synergy Areas (e.g., tech, market access)": ["All", "Cross-Selling Opportunities", "Operational Efficiencies", "New Market Access", "Product Diversification"]
    },
    "Market Research / Competitive Analysis": {
        "Competitor Focus": ["All", "Direct Competitors", "Indirect Competitors", "Emerging Disruptors"],
        "Emerging Trends Relevance": ["All", "AI-driven Solutions", "Sustainability", "Remote Work Solutions", "Personalized Experiences"]
    },
}

selected_purpose_ui = st.selectbox(
    "What is your primary goal for these leads?",
    options=list(PURPOSES_AND_CRITERIA_OPTIONS.keys()),
    key="purpose_input"
)

# Only clear results and user inputs if the purpose actually changed
if selected_purpose_ui != st.session_state.get('purpose', None):
    clear_results()
    st.session_state.user_inputs = {}
st.session_state.purpose = selected_purpose_ui


# --- Conditional Inputs based on Purpose ---
if st.session_state.purpose != "Select Purpose":
    st.header(f"2. Customize Criteria for: {st.session_state.purpose}")
    
    current_purpose_options = PURPOSES_AND_CRITERIA_OPTIONS[st.session_state.purpose]
    for criteria_key, options in current_purpose_options.items():
        # Get current value from session state to set index for selectbox
        current_value = st.session_state.user_inputs.get(criteria_key, options[0] if options else "")
        try:
            default_index = options.index(current_value)
        except ValueError:
            default_index = 0 # Default to first option if value not found

        if criteria_key == "Competitor Focus": # Special case for radio buttons
             st.session_state.user_inputs[criteria_key] = st.radio(
                f"{criteria_key}:",
                options=options,
                index=default_index,
                key=f"custom_criteria_{criteria_key.replace(' ', '_').replace('/', '_').replace('-', '_').lower()}",
                on_change=clear_results
            )
        else: # Default to selectbox for others
            st.session_state.user_inputs[criteria_key] = st.selectbox(
                f"{criteria_key}:",
                options=options,
                index=default_index,
                key=f"custom_criteria_{criteria_key.replace(' ', '_').replace('/', '_').replace('-', '_').lower()}",
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
        filtered_raw_leads = fetch_raw_leads_integrated(st.session_state.sector, st.session_state.region)
        
        if not filtered_raw_leads:
            st.warning("No raw leads found matching your sector and region criteria. Please adjust your search.")
            st.session_state.loading = False
            st.stop()

        company_names_to_enrich = [lead["company_name"] for lead in filtered_raw_leads]

        st.write(f"Step 2: Ranking {len(company_names_to_enrich)} filtered leads...")
        enriched_leads_data = fetch_enriched_leads_integrated(company_names_to_enrich)
        
        if not enriched_leads_data:
            st.warning("No enriched data found for the filtered raw leads. Check your `enriched_leads.json` file or selected criteria.")
            st.session_state.loading = False
            st.stop()

        st.write("Step 3: Ranking leads based on your **purpose** and **custom criteria** using ML model...")
        final_ranked_leads = rank_enriched_leads_ml_integrated(
            pd.DataFrame(enriched_leads_data).copy() # Pass a copy to ML ranking
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
    
    # Ensure essential columns for display are present, add if missing with default values
    # This prevents errors if enriched data lacks these columns
    if 'Company' not in display_df.columns:
        display_df['Company'] = display_df['company_name'] # Use raw company_name if 'Company' is missing
    if 'Website' not in display_df.columns:
        display_df['Website'] = ''
    if 'Industry' not in display_df.columns:
        display_df['Industry'] = ''
    if 'City' not in display_df.columns:
        display_df['City'] = ''
    if 'State' not in display_df.columns:
        display_df['State'] = ''

    # Create derived columns for display if they don't exist
    display_df['Location'] = display_df.apply(lambda row: f"{row['City']}, {row['State']}" if row['City'] and row['State'] else (row['City'] or row['State']), axis=1)
    display_df['Sector'] = display_df['Industry'] # Alias for consistency
    if 'Region' not in display_df.columns and 'State' in display_df.columns:
        display_df['Region'] = display_df['State'] # Fallback for Region if not in data

    display_cols_for_selection = [
        "Company", "Location", "Sector", "Region", "Website", "Rank Score"
    ]
    # Filter to only include columns that actually exist in the DataFrame
    existing_selection_cols = [col for col in display_cols_for_selection if col in display_df.columns]
    
    # Add 'Select' column for checkboxes
    display_df['Select'] = False # Initialize checkbox column

    edited_df = st.data_editor(
        display_df[existing_selection_cols + ['Select']],
        column_order=['Select'] + existing_selection_cols,
        hide_index=True, # Re-added this line to hide the index
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
                max_value=100
            )
        },
        # num_rows="dynamic", # Removed due to potential TypeError for older Streamlit versions
        use_container_width=True,
        key="ranked_leads_editor"
    )

    # Get selected company names from the edited_df
    # Ensure 'Select' column exists and is boolean before filtering
    if 'Select' in edited_df.columns and edited_df['Select'].dtype == 'bool':
        st.session_state.selected_company_names = edited_df[edited_df['Select']]['Company'].tolist()
    else:
        st.session_state.selected_company_names = [] # No selection possible or 'Select' column not correctly recognized

    if st.session_state.show_selection_message:
        st.info("👆 Select companies using the checkboxes above for a detailed view below.")
        st.session_state.show_selection_message = False

    # --- New Button for Detailed Data ---
    if st.session_state.selected_company_names:
        if st.button("Show Detailed Information for Selected Leads", key="show_detailed_button"):
            st.subheader("5. Detailed Information for Selected Leads")
            st.markdown("Here are the full details for the companies you selected.")
            
            # Filter the complete ranked_leads_df (from session state) based on selected company names
            st.session_state.detailed_display_df = st.session_state.all_filtered_and_ranked_df[
                st.session_state.all_filtered_and_ranked_df['Company'].isin(st.session_state.selected_company_names)
            ].copy()

            # Drop the 'Select' column if it was added for display purposes
            if 'Select' in st.session_state.detailed_display_df.columns:
                st.session_state.detailed_display_df = st.session_state.detailed_display_df.drop(columns=['Select'])
            if 'company_name' in st.session_state.detailed_display_df.columns and 'Company' in st.session_state.detailed_display_df.columns:
                 st.session_state.detailed_display_df = st.session_state.detailed_display_df.drop(columns=['company_name'])
            
            st.dataframe(st.session_state.detailed_display_df, use_container_width=True, hide_index=True)

            csv_data_selected = st.session_state.detailed_display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Selected Leads Details as CSV",
                data=csv_data_selected,
                file_name=f"selected_leads_for_{st.session_state.purpose.replace(' ', '_').lower()}.csv",
                mime="text/csv",
                key="download_selected_csv" # Unique key for download button
            )
    else:
        # Clear detailed display if no companies are selected after a previous selection
        # This prevents an empty "Detailed Information" section from persisting
        if not st.session_state.detailed_display_df.empty and st.session_state.get('last_selected_company_count', 0) > 0:
            st.session_state.detailed_display_df = pd.DataFrame() # Clear the detailed dataframe
        st.session_state.last_selected_company_count = len(st.session_state.selected_company_names)

# --- Footer ---
st.markdown("---")
st.markdown('<div style="text-align: center; color: #aaa;">© 2025 Scoutify. All rights reserved.</div>', unsafe_allow_html=True)
