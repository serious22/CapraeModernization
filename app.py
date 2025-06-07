import streamlit as st
import json
from utils.fetch_data import fetch_raw_leads, fetch_enriched_leads
import pandas as pd

st.set_page_config(page_title="LeadGen Tool", layout="wide")
st.title("🔍 AI-Enhanced Lead Generation Tool")

# Sidebar Filters
st.sidebar.header("Lead Search Criteria")
sector = st.sidebar.selectbox("Select Sector", ["Healthcare", "Construction", "Retail", "Software", "Real Estate"])
region = st.sidebar.selectbox("Select Region", ["California", "New York", "Texas", "Florida"])
purpose = st.sidebar.selectbox("Purpose", ["Sales Prospecting", "Business Partnerships", "Job Search", "Market Research"])

if st.sidebar.button("Search Leads"):
    st.session_state.raw_leads = fetch_raw_leads(sector, region)
    
selected_companies = []
selected_leads = []
# Display Raw Leads
if st.session_state.raw_leads:
    st.subheader("🔍 Companies Found")
    # Convert to DataFrame for nicer display
    df = pd.DataFrame(st.session_state.raw_leads)
    st.dataframe(df)

    # Let user select companies from dropdown/multiselect
    company_names = df["company_name"].tolist()
    selected_companies = st.multiselect("✅ Select companies to enrich:", company_names)

    if st.button("Enrich Selected Companies"):
        st.session_state.enriched_leads = fetch_enriched_leads(selected_companies)

    # Show enrichment
    if selected_leads:
        st.subheader("📈 Enriched Lead Data")
        enriched_data = fetch_enriched_leads(selected_leads)
        st.dataframe(enriched_data)

        if purpose == "Job Search":
            st.info("Ranking based on hiring activity")
            sorted_data = sorted(enriched_data, key=lambda x: x.get("hiring_activity", 0), reverse=True)
            st.dataframe(sorted_data)
        else:
            st.success(f"Enriched {len(enriched_data)} leads based on purpose: {purpose}")
