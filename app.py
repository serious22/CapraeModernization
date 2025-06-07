import streamlit as st
import pandas as pd
from utils.fetch_data import fetch_raw_leads, fetch_enriched_leads

# Initialize session state variables
for key in ["raw_leads", "selected_companies", "show_enriched", "loading", "enriched_leads"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "loading" or key == "show_enriched" else []


st.set_page_config(page_title="AI-Powered LeadGen Tool", layout="wide")

st.title("🚀 Caprae Capital Lead Generation Tool")

# Input form
with st.form("lead_form"):
    sector = st.selectbox("Select Sector", ["Healthcare", "Construction", "Retail"])
    region = st.selectbox("Select Region", ["California", "Texas", "New York"])
    purpose = st.selectbox("Purpose", ["Job Search", "Sales Prospecting", "Investor Research"])
    submitted = st.form_submit_button("🔍 Search Leads")

# Search logic
if submitted:
    st.session_state.raw_leads = fetch_raw_leads(sector, region)
    st.session_state.selected_companies = []
    st.session_state.show_enriched = False
    st.session_state.loading = False

# Display raw leads
if "raw_leads" in st.session_state and st.session_state.raw_leads and not st.session_state.get("loading"):
    st.subheader("🧾 Leads Matching Criteria")

    header = st.columns([0.05, 0.2, 0.2, 0.2, 0.35])
    header[0].markdown("**✅**")
    header[1].markdown("**Company Name**")
    header[2].markdown("**Sector**")
    header[3].markdown("**Region**")
    header[4].markdown("**Location**")

selected_companies = []

for i, lead in enumerate(st.session_state.raw_leads):
    cols = st.columns([0.05, 0.2, 0.2, 0.2, 0.35])
    checked = cols[0].checkbox("Select Lead", key=f"check_{i}", label_visibility="collapsed")
    cols[1].markdown(lead["company_name"])
    cols[2].markdown(lead["sector"])
    cols[3].markdown(lead["region"])
    cols[4].markdown(lead["location"])
    if checked:
        selected_companies.append(lead)

# Store selection
st.session_state.selected_companies = selected_companies

    # Enrich Button
enrich_button = st.button(
"✨ Enrich Selected Companies",
disabled=(len(selected_companies) == 0)
)

if enrich_button:
    st.session_state.loading = True
    
    selected_names = [c["company_name"] for c in st.session_state.selected_companies]
    all_enriched = fetch_enriched_leads(selected_names)
    enriched = [e for e in all_enriched if e["company_name"] in selected_names]
    st.session_state.enriched_leads = enriched
    st.session_state.loading = False
    st.session_state.show_enriched = True
    # st.rerun()

# Display enriched leads
if st.session_state.show_enriched and st.session_state.enriched_leads:
    st.markdown("### 🧠 Enriched Company Details")
    enriched_df = pd.DataFrame(st.session_state.enriched_leads)
    st.dataframe(enriched_df, use_container_width=True)
