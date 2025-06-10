import streamlit as st
import base64

# Set page config
st.set_page_config(page_title="About", layout="wide")

# Read and encode the image
with open("assets/me.jpeg", "rb") as f:
    data = base64.b64encode(f.read()).decode()

# Custom CSS and layout
st.markdown(f"""
    <style>
    body {{
        background-color: #121212;
        color: #f5f5f5;
        font-family: 'Segoe UI', sans-serif;
    }}

    .about-wrapper {{
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        padding: 60px 5vw;
        background-color: #121212;
        gap: 60px;
    }}

    .about-left {{
        flex: 1.2;
    }}

    .about-heading {{
        font-size: 3em;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }}

    .about-email {{
        font-size: 1.2em;
        color: #00ffcc;
        margin-bottom: 20px;
    }}

    .about-description {{
        font-size: 1.1em;
        line-height: 1.8;
        color: #cccccc;
        margin-bottom: 40px;
        max-width: 600px;
    }}

    .about-location {{
        font-size: 1em;
        color: #999999;
    }}

    .about-image {{
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }}

    .profile-img {{
        max-width: 100%;
        max-height: 500px;
        border-radius: 10px;
        filter: grayscale(100%) brightness(80%);
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        transition: filter 0.4s ease;
    }}

    .profile-img:hover {{
        filter: grayscale(0%) brightness(100%);
    }}

    @media (max-width: 900px) {{
        .about-wrapper {{
            flex-direction: column;
            text-align: center;
        }}
        .about-description {{
            margin: 0 auto;
        }}
    }}
    </style>

    <div class="about-wrapper">
        <div class="about-left">
            <div class="about-heading">ABOUT</div>
            <div class="about-email">siddhaantpahuja@gmail.com</div>
            <div class="about-description">
                Hello! I'm Siddhaant Pahuja, the mind behind Scoutify—a smart lead intelligence tool built to help you discover and prioritize high-potential businesses effortlessly. With a strong foundation in software development, automation, and data analytics, I’m passionate about building tools that solve real-world problems through simplicity, speed, and intelligence.
                <br><br>
                Scoutify was born from a simple idea: to cut through the noise of generic lead lists and deliver quality insights that drive action. Whether it’s ranking leads, enriching data, or surfacing hidden opportunities, every line of code in Scoutify is designed to help you make smarter, faster decisions.
                <br><br>
                My strength lies in connecting the dots—turning raw, scattered data into clear, usable intelligence. I’m committed to continuously evolving Scoutify to stay ahead of the curve and make lead generation not just efficient, but strategic.
            </div>
            <div class="about-location">
                New Delhi, India<br>
            </div>
        </div>
        <div class="about-image">
            <img src="data:image/jpeg;base64,{data}" class="profile-img" alt="Profile Picture"/>
        </div>
    </div>
""", unsafe_allow_html=True)
