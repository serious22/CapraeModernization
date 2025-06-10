import streamlit as st

st.set_page_config(
    page_title="Scoutify: Documentation",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for consistent styling
st.markdown("""
    <style>
    body {
        font-family: 'Inter', sans-serif;
        background-color: #1a1a1a;
        color: #f0f0f0;
    }
    .stApp > header, .stApp > footer {
        display: none;
    }
    h1 {
        color: #4CAF50;
        text-align: center;
        margin-bottom: 30px;
    }
    h2 {
        color: #4CAF50;
        font-size: 2em;
        margin-top: 40px;
        margin-bottom: 20px;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }
    h3 {
        color: #f0f0f0;
        font-size: 1.5em;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    p {
        color: #ddd;
        line-height: 1.6;
    }
    ul {
        list-style-type: disc;
        margin-left: 20px;
        color: #ddd;
    }
    li {
        margin-bottom: 8px;
    }
    .stExpander > div > div > div > p {
        font-weight: bold; /* Make FAQ questions bold */
        color: #4CAF50;
    }
    .stExpander > div > div > div[data-testid="stExpanderChevron"] {
        color: #4CAF50; /* Style the expander chevron */
    }
    code {
        background-color: #2e2e2e;
        padding: 2px 4px;
        border-radius: 4px;
        color: #5cb85c;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


st.title("📚 Scoutify: Comprehensive Documentation")

st.markdown("---")

st.markdown(
    """
    Welcome to the Scoutify documentation! This page will guide you through how to effectively use the application,
    explain its core functionality, and answer common questions.
    """
)

st.header("How to Use the App: Step-by-Step Guide")

st.markdown("---")

st.subheader("1. Define Your Search Criteria & Goal")
st.markdown(
    """
    On the **'Lead Ranking System'** page, you'll start by defining your primary search parameters:
    * **Select Target Sector(s):** Choose the industry sector(s) relevant to your search (e.g., "Healthcare", "Technology"). Select "All" for a broader search.
    * **Select Target Region(s):** Specify the geographic region(s) where you want to find leads (e.g., "California", "New York"). Select "All" for a nationwide search.
    * **What is your primary goal for these leads?:** This is a crucial step. Your selection here will dynamically adjust the subsequent criteria you can provide. Options include:
        * `Job Search`
        * `Investor Research`
        * `Sales Prospecting`
        * `Merger and Acquisition/Partnership`
        * `Market Research / Competitive Analysis`
    """
)

st.subheader("2. Customize Criteria for Your Purpose")
st.markdown(
    """
    Once you select your primary goal, a new section will appear with specific criteria tailored to that purpose.
    For example:
    * **Job Search:** You might select "Preferred Company Size" and "Desired Role Focus."
    * **Investor Research:** You'll be asked about "Preferred Investment Stage," "Revenue Threshold / Valuation," and "Focus Technology/Industry Areas."
    * **Sales Prospecting:** You'll define "Target Buyer Type," "Your Product/Service Category," and "Common Pain Points Your Product Solves."

    **Note:** Changing any of these inputs (Sector, Region, Purpose, or custom criteria) will automatically clear any previously displayed results to ensure you're always working with current data.
    """
)

st.subheader("3. Find & Rank Leads")
st.markdown(
    """
    After you've set all your criteria, click the **'🔎 Find & Rank Leads'** button.
    The system will then perform the following actions:
    1.  **Filter Raw Leads:** It first filters the initial raw lead database based on your selected `Sector` and `Region`.
    2.  **Enrich Filtered Leads:** It then enriches *only* these filtered leads with additional, more detailed company information.
    3.  **Rank Enriched Leads:** Finally, it applies a sophisticated ranking algorithm that considers your `Purpose` and all the `Custom Criteria` you provided. Companies are given a **'Rank Score'** indicating how well they match your needs.

    A loading spinner will appear during this process, which may take a moment depending on the number of leads being processed.
    """
)

st.subheader("4. Top Ranked Leads for Your Selection")
st.markdown(
    """
    Once the ranking is complete, a table will appear displaying the top leads. This table provides an overview,
    including:
    * `Company Name`
    * `Location` (City, State)
    * `Sector` (Industry)
    * `Region` (State)
    * `Website`
    * `Rank Score` (A visual progress bar helps quickly identify top matches.)

    You can **select multiple companies** from this table using the checkboxes in the first column.
    """
)

st.subheader("5. Detailed Information for Selected Leads")
st.markdown(
    """
    After selecting companies from the ranked list, click the **'Show Detailed Information for Selected Leads'** button.
    A new table will then appear, providing comprehensive details for *only* the companies you selected.
    This includes fields like:
    * `Employees Count`
    * `Revenue`
    * `Hiring Activity`
    * `Recent Employee Growth %`
    * `Recent Funding / Investment`
    * `Owner's Title`
    * `Owner's LinkedIn`
    * ...and all other available enriched data points.

    You also have the option to **Download Selected Leads Details as CSV** for external analysis.
    """
)

st.header("What Scoutify Does")
st.markdown("---")
st.markdown(
    """
    Scoutify is an intelligent lead ranking system designed to cut through the noise and deliver high-potential
    business leads directly to you. It automates the tedious process of lead qualification by:
    * **Aggregating Data:** Pulling information from various internal data sources (simulated by JSON files).
    * **Enriching Profiles:** Adding crucial details like financial data, growth metrics, and key contacts.
    * **AI-Powered Ranking:** Applying a customizable algorithm that scores leads based on your specific strategic objectives
        (Job Search, Investor Research, Sales, M&A, Market Research). This ensures you see the most relevant opportunities first.
    * **Streamlining Discovery:** Presenting results in an interactive, easy-to-digest format that saves you time and resources.
    """
)

st.header("Ranking Methodology (High-Level)")
st.markdown("---")
st.markdown(
    """
    The **Rank Score** for each company is calculated dynamically based on your selected `Purpose` and the `Custom Criteria` you provide.
    The algorithm assigns points to companies for matching your preferences across various data points, including:
    * **Sector & Region Alignment:** A foundational score for geographic and industry relevance.
    * **Company Size:** Matching your preferred employee count ranges.
    * **Financial Health:** Based on revenue or valuation thresholds you set (e.g., for investor research).
    * **Growth Indicators:** High scores for recent employee growth or significant funding rounds (relevant for job seekers, investors, M&A).
    * **Hiring Activity:** Companies with active hiring are prioritized for job seekers.
    * **Strategic Fit:** Factors like buyer type, product category alignment, or synergy areas (for sales, M&A, market research).

    The higher the Rank Score (out of 100), the stronger the alignment with your defined criteria.
    """
)

st.header("Frequently Asked Questions (FAQs)")
st.markdown("---")

with st.expander("What is Scoutify?"):
    st.markdown(
        """
        Scoutify is an AI-powered application that helps you identify and rank business leads based on your specific goals,
        such as job searching, investor research, sales prospecting, or market analysis. It streamlines the process
        of finding the most relevant companies for your needs.
        """
    )

with st.expander("How accurate is the ranking?"):
    st.markdown(
        """
        The ranking algorithm is designed to maximize relevance based on the criteria you provide.
        Its accuracy directly correlates with how precisely you define your `Purpose` and `Custom Criteria`.
        The system continuously learns and adapts based on the available data, providing an intelligent score.
        """
    )

with st.expander("Where does the data come from?"):
    st.markdown(
        """
        Scoutify utilizes internal, pre-processed datasets (simulated via `raw_leads.json` and `enriched_leads.json` in this demonstration).
        These datasets contain a mix of publicly available company information and derived insights.
        """
    )

with st.expander("Can I upload my own data or connect to live sources?"):
    st.markdown(
        """
        In this version, direct user data uploads or live API connections are not implemented.
        The application operates on pre-loaded data for demonstration purposes.
        """
    )

with st.expander("What if no leads are found for my criteria?"):
    st.markdown(
        """
        If no companies match your exact `Sector` and `Region` filters, a warning message will appear.
        In such cases, try broadening your search by selecting "All" for Sector or Region, or by adjusting your custom criteria to be less restrictive.
        """
    )

with st.expander("How often is the data updated?"):
    st.markdown(
        """
        For this demonstration version, the underlying data is static. In a production environment,
        such a system would be integrated with live data sources and updated periodically to ensure freshness and accuracy.
        """
    )

with st.expander("How can I provide feedback or report an issue?"):
    st.markdown(
        """
        Thank you for using Scoutify! If you have any feedback, suggestions, or encounter issues, please visit the
        **'Contact'** page (or 'About Me' page if it contains contact info) for details on how to reach the developer.
        """
    )

st.markdown("---")
st.markdown('<div class="app-footer">© 2025 Scoutify. All rights reserved.</div>', unsafe_allow_html=True)
