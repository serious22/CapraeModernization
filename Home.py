import streamlit as st
import base64
import os

# --- Helper to encode image as base64 ---
def encode_image(image_path):
    abs_path = os.path.join(os.getcwd(), image_path)
    try:
        with open(abs_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
            # Determine MIME type based on file extension
            if image_path.lower().endswith((".png", ".webp")):
                mime_type = "image/png"
            elif image_path.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif image_path.lower().endswith(".gif"):
                mime_type = "image/gif"
            else:
                mime_type = "application/octet-stream" # Fallback
            return encoded_string, mime_type
    except FileNotFoundError:
        return "", ""

# --- Paths to local images (relative to the app's root directory) ---
hero_img_data, hero_img_mime = encode_image("assets/hero.png")
grow_img_data, grow_img_mime = encode_image("assets/grow.png")


# Construct data URIs for embedding. Use Unsplash/placehold.co as fallbacks.
hero_data_uri = f"data:{hero_img_mime};base64,{hero_img_data}" if hero_img_data else "https://images.unsplash.com/photo-1551288259-86532d667610?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
grow_data_uri = f"data:{grow_img_mime};base64,{grow_img_data}" if grow_img_data else "https://placehold.co/600x400/333333/66CC66?text=Data+Insights"


# Set Streamlit page configuration
st.set_page_config(
    page_title="Scoutify: Intelligent Lead Ranking",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown(f"""
    <style>
    /* General Body Styles */
    body {{
        font-family: 'Inter', sans-serif;
        background-color: #1a1a1a;
        color: #f0f0f0;
    }}

    /* Hide Streamlit's default header and footer for a cleaner look */
    .stApp > header {{
        display: none;
    }}
    .stApp > footer {{
        display: none;
    }}

    /* Hero Section Styling - Using data URI for background image */
    .hero-section {{
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("{hero_data_uri}") no-repeat center center;
        background-size: cover;
        padding: 100px 50px;
        text-align: center;
        color: #f0f0f0;
        border-radius: 10px;
        margin-top: 30px;
    }}
    .hero-section h1 {{
        font-size: 3.8em;
        color: #4CAF50;
        margin-bottom: 20px;
        letter-spacing: 1.5px;
        line-height: 1.2;
    }}
    .hero-section p {{
        font-size: 1.3em;
        color: #ddd;
        max-width: 800px;
        margin: 0 auto 40px auto;
        line-height: 1.6;
    }}
    .hero-buttons {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }}
    .stButton > button {{
        background-color: #4CAF50;
        color: white;
        padding: 12px 25px;
        border-radius: 8px;
        border: none;
        font-size: 1.1em;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.2s ease;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.4);
    }}
    .stButton > button:hover {{
        background-color: #5cb85c;
        transform: translateY(-2px);
        box-shadow: 5px 5px 12px rgba(0,0,0,0.5);
    }}
    .stButton > button:active {{
        transform: translateY(0);
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }}
    
    /* Section Headings */
    h2 {{
        color: #4CAF50;
        font-size: 2.5em;
        text-align: center;
        margin-top: 60px;
        margin-bottom: 30px;
        border-bottom: 2px solid #333;
        padding-bottom: 15px;
        display: inline-block;
        width: auto;
        margin-left: auto;
        margin-right: auto;
    }}

    /* Service Cards (Grid Layout) */
    .service-card-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin-top: 40px;
        margin-bottom: 60px;
    }}
    .service-card {{
        background-color: #2e2e2e;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        flex: 1 1 calc(33% - 40px);
        min-width: 280px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .service-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.6);
    }}
    .service-card .icon {{
        font-size: 3em;
        color: #4CAF50;
        margin-bottom: 15px;
    }}
    .service-card h3 {{
        color: #f0f0f0;
        font-size: 1.5em;
        margin-bottom: 10px;
    }}
    .service-card p {{
        color: #bbb;
        font-size: 0.95em;
        line-height: 1.5;
    }}

    /* Grow Your Business Section */
    .grow-business-section {{
        display: flex;
        align-items: center;
        gap: 50px;
        padding: 50px;
        background-color: #222222;
        border-radius: 10px;
        margin-top: 60px;
        margin-bottom: 60px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }}
    .grow-business-image {{
        flex: 1;
        min-width: 300px;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    .grow-business-image img {{ /* Style for the image inside grow-business-image div */
        width:100%;
        height:auto;
        border-radius:8px;
    }}
    .grow-business-content {{
        flex: 2;
        text-align: left;
    }}
    .grow-business-content h2 {{
        text-align: left;
        margin-top: 0;
        font-size: 2.2em;
        border-bottom: none;
        padding-bottom: 0;
    }}
    .feature-list {{
        list-style: none;
        padding: 0;
        margin-top: 20px;
    }}
    .feature-list li {{
        font-size: 1.1em;
        color: #f0f0f0;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }}
    .feature-list li .bullet-icon {{
        color: #4CAF50;
        font-size: 1.5em;
        margin-right: 10px;
    }}

    /* Clients Section */
    .client-logos-container {{
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 30px;
        margin-top: 40px;
        margin-bottom: 80px;
    }}
    .client-logo {{
        background-color: #2e2e2e;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        height: 100px;
        width: 150px;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    .client-logo img {{
        max-width: 100%;
        max-height: 100%;
        filter: brightness(0) invert(1) opacity(0.7);
    }}

    /* Footer Styling */
    .app-footer {{
        text-align: center;
        padding: 30px 0;
        margin-top: 50px;
        background-color: #222222;
        color: #aaa;
        font-size: 0.9em;
        border-top: 1px solid #333;
        border-radius: 8px 8px 0 0;
    }}

    /* Responsive adjustments */
    @media (max-width: 900px) {{
        .hero-section h1 {{
            font-size: 2.8em;
        }}
        .hero-section p {{
            font-size: 1.1em;
        }}
        .service-card {{
            flex: 1 1 calc(50% - 20px);
        }}
        .grow-business-section {{
            flex-direction: column;
            text-align: center;
        }}
        .grow-business-content h2 {{
            text-align: center;
        }}
        .client-logo {{
            width: 120px;
            height: 80px;
        }}
    }}

    @media (max-width: 600px) {{
        .hero-section h1 {{
            font-size: 2em;
        }}
        .hero-section p {{
            font-size: 1em;
        }}
        .service-card {{
            flex-direction: column;
            align-items: center;
            flex: 1 1 100%;
        }}
        .hero-buttons {{
            flex-direction: column;
            gap: 10px;
        }}
    }}
    </style>
""", unsafe_allow_html=True)


# --- App Name Display ---
st.markdown('<h1 style="text-align: center; color: #4CAF50; font-size: 4em; margin-bottom: 50px; letter-spacing: 3px; text-shadow: 2px 2px 6px rgba(0,0,0,0.4);">Scoutify</h1>', unsafe_allow_html=True)


# --- Hero Section ---
st.markdown(f"""
    <div class="hero-section">
        <h1>Unlock Your Next Big Opportunity with Scoutify</h1>
        <p>
            Leverage cutting-edge AI to precisely identify, rank, and engage with the leads
            that matter most to your goals – whether for job searching, investment, sales,
            partnerships, or market intelligence.
        </p>
        <div class="hero-buttons">
            <a href="#section-start-ranking" style="text-decoration: none;">
                <button type="button" class="stButton">Start Ranking Leads</button>
            </a>
            <a href="#section-learn-more" style="text-decoration: none;">
                <button type="button" class="stButton" style="background-color: #666; border: 1px solid #777;">Learn More</button>
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)


# --- Section: How Scoutify Helps You (Services/Features) ---
st.markdown('<h2><a name="section-learn-more"></a>How Scoutify Helps You</h2>', unsafe_allow_html=True)
st.markdown("""
    <div class="service-card-container">
        <div class="service-card">
            <div class="icon">🔍</div>
            <h3>Job Search Precision</h3>
            <p>Find your ideal employer by ranking companies based on hiring trends, growth, and cultural fit.</p>
        </div>
        <div class="service-card">
            <div class="icon">📈</div>
            <h3>Investor Target Identification</h3>
            <p>Uncover high-growth startups and established firms aligned with your investment thesis and criteria.</p>
        </div>
        <div class="service-card">
            <div class="icon">💼</div>
            <h3>Sales Prospecting Power</h3>
            <p>Identify warm leads with the highest conversion potential for your specific product or service.</p>
        </div>
        <div class="service-card">
            <div class="icon">🤝</div>
            <h3>M&A / Partnership Scouting</h3>
            <p>Discover strategic acquisition targets or synergistic partners for expansion and collaboration.</p>
        </div>
        <div class="service-card">
            <div class="icon">📊</div>
            <h3>Market Research & Competitor Analysis</h3>
            <p>Gain deep insights into market dynamics, emerging trends, and competitor strategies.</p>
        </div>
        <div class="service-card">
            <div class="icon">💡</div>
            <h3>Customized AI Ranking</h3>
            <p>Our intelligent algorithms learn your priorities to deliver truly relevant and actionable lead scores.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Section: Grow Your Business (Simulated Features with Image) ---
st.markdown('<h2>Grow Your Business with Data-Driven Decisions</h2>', unsafe_allow_html=True)
st.markdown(f"""
    <div class="grow-business-section">
        <div class="grow-business-image">
            <img src="{grow_data_uri}" alt="Data Insights" style="width:100%; height:auto; border-radius:8px;">
        </div>
        <div class="grow-business-content">
            <h2>Unlock Unparalleled Opportunities</h2>
            <p>Scoutify provides you with a distinct advantage by transforming raw data into clear, actionable intelligence.</p>
            <ul class="feature-list">
                <li><span class="bullet-icon">✅</span> Pinpoint companies actively hiring for relevant roles.</li>
                <li><span class="bullet-icon">✅</span> Track recent funding rounds and employee growth.</li>
                <li><span class="bullet-icon">✅</span> Filter by specific industries, regions, and business types.</li>
                <li><span class="bullet-icon">✅</span> Access owner contact information for direct outreach.</li>
                <li><span class="bullet-icon">✅</span> Save time and resources on manual lead qualification.</li>
            </ul>
            <a href="#section-start-ranking" style="text-decoration: none;">
                <button type="button" class="stButton">Get Started Today</button>
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)


# --- Section: Call to Action to Lead Ranking System ---
st.markdown('<h2><a name="section-start-ranking"></a>Ready to Find Your Leads?</h2>', unsafe_allow_html=True)
st.info(
    """
    Head over to the **'Lead Ranking System'** page in the sidebar to configure your search criteria
    and unlock a curated list of high-potential leads!
    """
)
st.markdown("---")

# --- Footer ---
st.markdown('<div class="app-footer">© 2025 Scoutify. All rights reserved.</div>', unsafe_allow_html=True)
