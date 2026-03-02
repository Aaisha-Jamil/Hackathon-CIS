import streamlit as st
import os
import json
from recommender import get_recommendations, get_or_create_user, add_dislike, update_allergies

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Mahadi PalatePal", layout="wide", initial_sidebar_state="collapsed")

PROVINCES = ["Punjab", "Sindh", "KPK", "Baluchistan"]
ALLERGY_OPTIONS = ["dairy", "nuts", "gluten", "eggs"]

def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

    /* Hide standard sidebar and header for full immersive view */
    [data-testid="collapsedControl"] { display: none; }
    header { visibility: hidden; }
    
    /* App Background */
    .stApp {
        background-color: #ede1ca !important; /* EXACT requested Beige */
        background-image: url("https://www.transparenttextures.com/patterns/arabesque.png") !important; 
        font-family: 'Lora', serif;
        color: #490d0e !important; /* Exact Maroon for general text */
    }

    /* Form Container (Landing Page Login Box) */
    [data-testid="stForm"] {
        background-color: #490d0e !important; /* EXACT requested Maroon */
        background-image: url("https://www.transparenttextures.com/patterns/arabesque.png");
        background-blend-mode: color-burn; /* Make texture visible but subtle on dark bg */
        padding: 50px;
        border-radius: 15px;
        border: 2px solid #C49A45 !important; /* Gold border */
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    /* Text inside the Form & Maroon Areas */
    [data-testid="stForm"] h1, [data-testid="stForm"] h2, [data-testid="stForm"] h3, 
    [data-testid="stForm"] label, [data-testid="stForm"] .stSelectbox label, 
    [data-testid="stForm"] .stMultiSelect label, 
    .maroon-bg h1, .maroon-bg h2, .maroon-bg h3, .maroon-bg p, .maroon-bg label, .maroon-bg div {
        color: #E2C792 !important; /* Soft Gold text on Maroon */
        font-family: 'Playfair Display', serif !important;
        text-align: center;
    }
    
    /* We removed [data-testid="stForm"] p from above so it doesn't ruined Button text */
    [data-testid="stForm"] p {
        color: #E2C792;
        font-family: 'Playfair Display', serif;
    }

    /* Maroon Side Panel (View 2 & 3) */
    .maroon-bg {
        background-color: #490d0e !important; /* EXACT requested Maroon */
        background-image: url("https://www.transparenttextures.com/patterns/arabesque.png");
        background-blend-mode: color-burn;
        padding: 40px;
        border-right: 2px solid #C49A45;
        box-shadow: 5px 0px 15px rgba(0,0,0,0.2);
    }

    /* Typography */
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #490d0e !important; }
    .title-text { font-size: 36px; font-weight: 700; text-align: center; margin-bottom: 20px; letter-spacing: 1px; font-style: italic; color: #E2C792 !important;}
    .subtitle-text { font-size: 18px; text-align: center; font-style: italic; margin-bottom: 40px; color: #C49A45 !important; border-bottom: 1px dashed #C49A45; padding-bottom: 20px;}

    /* Force the deeper wrapper containers to be Beige to remove any "Black background" bleeding through */
    div[data-baseweb="input"], div[data-baseweb="input"] > div,
    div[data-baseweb="select"], div[data-baseweb="select"] > div {
        background-color: #ede1ca !important;
        border-radius: 25px !important;
    }

    /* Inputs (Beige Pill Shape) */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div, 
    .stMultiSelect>div>div>div[data-baseweb="select"] {
        border-radius: 25px !important; /* Fully rounded pill shape */
        border: 1px solid #490d0e !important; /* Maroon border */
        background-color: #ede1ca !important; /* EXACT Beige */
        color: #490d0e !important; /* EXACT Maroon text inside input */
        font-family: 'Lora', serif !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
    }
    
    /* Ensure the placeholder text inside the beige inputs is also colored nicely */
    .stTextInput>div>div>input::placeholder,
    .stMultiSelect input::placeholder,
    textarea::placeholder,
    ::placeholder {
        color: rgba(73, 13, 14, 0.6) !important;
        -webkit-text-fill-color: rgba(73, 13, 14, 0.6) !important;
        opacity: 1 !important;
    }
    
    /* Streamlit multiselect custom placeholder div */
    div[class*="placeholder"], span[class*="placeholder"] {
        color: #490d0e !important;
        -webkit-text-fill-color: #490d0e !important;
        opacity: 0.8 !important;
    }
    
    /* Ensure the multiselect tags also look okay */
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: #490d0e !important;
        color: #ede1ca !important;
        border: 1px solid #C49A45 !important;
    }

    /* Standard Buttons (On Beige Background in View 2 & 3) */
    div[data-testid="stButton"] > button, .stButton>button {
        background-color: #490d0e !important; /* Maroon button */
        color: #ede1ca !important; /* Beige text */
        border: 1px solid #C49A45 !important;
        border-radius: 30px !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        padding: 8px 25px !important;
        width: 100%;
        transition: all 0.3s ease-in-out !important;
    }
    div[data-testid="stButton"] > button *, div[data-testid="stButton"] > button p {
        color: #ede1ca !important; /* Force text color to beige inside the button */
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #C49A45 !important;
        border-color: #490d0e !important;
    }
    div[data-testid="stButton"] > button:hover *, div[data-testid="stButton"] > button:hover p {
        color: #490d0e !important;
    }
    
    /* Form Submit Button & Selected Province Customization */
    [data-testid="stFormSubmitButton"] > button,
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
        padding: 15px 30px !important;
        border-width: 2px !important;
        border-radius: 40px !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        background-color: #490d0e !important;
        color: #ede1ca !important;
        border: 2px solid #C49A45 !important;
        width: 100% !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
    }
    [data-testid="stFormSubmitButton"] > button *, [data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stButton"] > button[kind="primary"] *, 
    div[data-testid="stButton"] > button[data-testid="baseButton-primary"] * {
        font-size: 20px !important;
        color: #ede1ca !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stButton"] > button[kind="primary"]:hover,
    div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover {
        transform: scale(1.05); /* Dynamic hover effect */
        background-color: #C49A45 !important;
        border-color: #490d0e !important;
        box-shadow: 0 5px 15px rgba(196, 154, 69, 0.4) !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover *, [data-testid="stFormSubmitButton"] > button:hover p,
    div[data-testid="stButton"] > button[kind="primary"]:hover *, 
    div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover * {
        color: #490d0e !important;
    }

    /* Remove ALL inner borders inside inputs and force icons to Maroon */
    [data-baseweb="input"] *, [data-baseweb="select"] * {
        border-right: none !important;
        border-left: none !important;
        border-top: none !important;
        border-bottom: none !important;
    }
    
    /* Specific Streamlit internal overrides found via DOM inspection */
    div[data-baseweb="input"] button {
        border-left: none !important;
        background-color: transparent !important;
    }
    div[data-baseweb="select"] > div > div:nth-child(2) {
        border-left: none !important;
    }
    
    /* Hover and Focus states - Keep background beige entirely, turn border black on focus */
    [data-baseweb="input"]:focus-within, [data-baseweb="select"]:focus-within,
    [data-baseweb="input"]:hover, [data-baseweb="select"]:hover {
        background-color: #ede1ca !important;
    }
    [data-baseweb="input"]:focus-within *, [data-baseweb="select"]:focus-within *,
    [data-baseweb="input"]:hover *, [data-baseweb="select"]:hover *,
    .stTextInput input:focus, .stTextInput input:hover,
    .stSelectbox div[role="button"]:focus, .stSelectbox div[role="button"]:hover,
    .stMultiSelect div[role="combobox"]:focus, .stMultiSelect div[role="combobox"]:hover {
        background-color: transparent !important; /* Definitively kill the gray highlight */
    }
    [data-baseweb="input"]:focus-within, [data-baseweb="select"]:focus-within {
        border: 2px solid #000000 !important;
        box-shadow: none !important;
    }
    
    /* Fix Chrome/Google Password Autofill Gray Background */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    input:-webkit-autofill:active{
        -webkit-box-shadow: 0 0 0 30px #ede1ca inset !important;
        -webkit-text-fill-color: #490d0e !important;
        transition: background-color 5000s ease-in-out 0s;
    }
    
    /* Extended Dropdown Lists / Popovers matching Beige */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #ede1ca !important;
    }
    ul[role="listbox"] li,
    ul[data-baseweb="menu"] li,
    div[data-baseweb="menu"] li {
        background-color: transparent !important; /* Rely on parent */
        color: #490d0e !important;
        font-family: 'Lora', serif !important;
        font-weight: 600 !important;
    }
    ul[role="listbox"] li:hover, ul[role="listbox"] li[aria-selected="true"],
    ul[role="listbox"] li:focus,
    ul[data-baseweb="menu"] li:hover, ul[data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #C49A45 !important;
        color: #490d0e !important;
    }
    
    /* Profile Details formatting */
    .profile-details p, .profile-details b {
        color: #ede1ca !important;
        text-align: left !important;
        font-family: 'Lora', serif !important;
        margin-bottom: 5px;
    }
    
    /* Re-apply the pill border only to the outermost container */
    [data-baseweb="input"], [data-baseweb="select"] {
        border: 1px solid #490d0e !important;
        border-radius: 25px !important;
        overflow: hidden !important; 
        background-color: #ede1ca !important;
    }

    /* Force all SVGs (Eye icon, Arrows, Clear buttons) to exactly Maroon */
    [data-baseweb="input"] svg, [data-baseweb="input"] svg path,
    [data-baseweb="select"] svg, [data-baseweb="select"] svg path {
        fill: #490d0e !important;
        stroke: #490d0e !important;
        color: #490d0e !important;
    }

    /* Cards */
    .dish-card {
        background-color: #490d0e !important; /* Maroon */
        border: 2px solid #C49A45;
        border-radius: 10px;
        padding: 20px;
        color: #ede1ca !important; /* Beige text */
        margin-bottom: 20px;
        display: flex;
        gap: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .dish-img-placeholder {
        width: 150px;
        height: 150px;
        background-color: #000000;
        border: 2px dashed #C49A45;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-style: italic;
        color: #C49A45;
        flex-shrink: 0;
    }
    /* Quick fix for the text inside the dish card */
    .dish-card h3, .dish-card p {
        color: #ede1ca !important;
        text-align: left;
    }
    /* Toasts / Notifications */
    [data-testid="stToast"] {
        background-color: #490d0e !important;
        border: 2px solid #C49A45 !important;
        border-radius: 10px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5) !important;
    }
    [data-testid="stToast"] * {
        color: #ede1ca !important;
        font-family: 'Playfair Display', serif !important;
    }
    [data-testid="stToast"] svg {
        fill: #C49A45 !important;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ── Session State Init ──────────────────────────────────────────────────────
if "view" not in st.session_state:
    st.session_state.view = "landing" # 'landing', 'quiz', 'results'
if "username" not in st.session_state:
    st.session_state.username = None
if "allergies" not in st.session_state:
    st.session_state.allergies = []
if "diet_preference" not in st.session_state:
    st.session_state.diet_preference = "Choose an option"
if "province" not in st.session_state:
    st.session_state.province = None
if "user_vector" not in st.session_state:
    st.session_state.user_vector = []
if "province_just_selected" not in st.session_state:
    st.session_state.province_just_selected = False

# ── Helper for Star Ratings ────────────────────────────────────────────────
def star_rating(label, key):
    return st.slider(label, min_value=1, max_value=5, value=3, step=1, key=key, format="%d ⭐")


# ── VIEW 1: Landing Page ────────────────────────────────────────────────────
if st.session_state.view == "landing":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("registry_form", clear_on_submit=False):
            st.markdown("""
                <div class="title-text">Welcome to PlatePal</div>
                <div class="subtitle-text">Discover the royal heritage of<br>Pakistani cuisine tailored to your soul.</div>
                <h3 style="text-align:center; color:#E2C792 !important;">Guest Registry</h3>
            """, unsafe_allow_html=True)
            
            username = st.text_input("Username:", placeholder="aaisha", autocomplete="new-password")
            password = st.text_input("Password:", type="password", placeholder="••••", autocomplete="new-password")
            
            st.write("<br>", unsafe_allow_html=True)
            diet_choice = st.selectbox("Culinary Preference:", ["Choose an option", "Any", "Vegetarian Only", "Non-Vegetarian Only"])
            
            selected_allergies = st.multiselect(
                "Diet Restrictions / Allergies:",
                options=ALLERGY_OPTIONS,
                default=[]
            )
            
            st.write("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Begin your exploration")
            
            if submit:
                if username.strip() and password.strip():
                    st.session_state.username = username.strip()
                    st.session_state.diet_preference = diet_choice
                    st.session_state.allergies = selected_allergies
                    
                    # Backend initialization
                    get_or_create_user(st.session_state.username)
                    update_allergies(st.session_state.username, selected_allergies)
                    
                    st.session_state.view = "quiz"
                    st.rerun()
                else:
                    st.error("Please provide both a username and password to proceed.")
            st.markdown("</div>", unsafe_allow_html=True)


# ── VIEW 2: Dual Pane Quiz ──────────────────────────────────────────────────
elif st.session_state.view == "quiz":
    left_pane, right_pane = st.columns([1, 2.5], gap="large")
    
    # Left Pane (Maroon)
    with left_pane:
        st.markdown(f"""
        <div class="maroon-bg" style="min-height: 80vh; border-radius: 10px;">
            <h2 style="text-align:center;">Guest Profile</h2>
            <hr style="border-color:#C49A45;">
            <div class="profile-details" style="padding-top: 20px;">
                <p><b>Name:</b> {st.session_state.username}</p>
                <p><b>Diet:</b> {st.session_state.diet_preference}</p>
                <p><b>Restrictions:</b> {', '.join(st.session_state.allergies) if st.session_state.allergies else 'None'}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("← Return Home"):
            st.session_state.clear()
            st.rerun()
        
    # Right Pane (Beige)
    with right_pane:
        if not st.session_state.province:
            st.markdown("<br><h2>Select Your Destination Province</h2><br>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("Punjab", use_container_width=True):
                st.session_state.province = "Punjab"
                st.session_state.province_just_selected = True
                st.rerun()
            if c2.button("Sindh", use_container_width=True):
                st.session_state.province = "Sindh"
                st.session_state.province_just_selected = True
                st.rerun()
            if c3.button("KPK", use_container_width=True):
                st.session_state.province = "KPK"
                st.session_state.province_just_selected = True
                st.rerun()
            if c4.button("Baluchistan", use_container_width=True):
                st.session_state.province = "Baluchistan"
                st.session_state.province_just_selected = True
                st.rerun()
        else:
            st.markdown("<br><h2>The province you have selected is: </h2><br>", unsafe_allow_html=True)
            if st.session_state.province_just_selected:
                st.session_state.province_just_selected = False

            sc1, sc2, sc3 = st.columns([1, 1.5, 1])
            with sc2:
                st.write("<br><br>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)
                
                # HTML template that precisely mimics the submit button
                button_html = f"""
                <div style="position: relative; width: 100%; height: 60px;">
                    <div style="
                        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                        background-color: #490d0e; 
                        color: #ede1ca; 
                        border: 2px solid #C49A45; 
                        border-radius: 40px; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center;
                        font-family: 'Playfair Display', serif;
                        font-size: 20px;
                        font-weight: 600;
                        pointer-events: none;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                    ">
                        {st.session_state.province}
                    </div>
                </div>
                """
                st.markdown(button_html, unsafe_allow_html=True)
                
                st.write("<br><br>", unsafe_allow_html=True)
        
        if st.session_state.province:
            st.markdown(f"<hr><h3>The {st.session_state.province} Taste Profile</h3>", unsafe_allow_html=True)
            st.write("Rate your preferences from 1 to 5 stars.")
            
            with st.form("star_quiz_form"):
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.markdown("<b>Savory Notes</b>", unsafe_allow_html=True)
                    spice = star_rating("Heat & Spice Tolerance", "q1")
                    savory_texture = star_rating("Meal Texture (Dry to Gravy)", "q2")
                    heaviness = star_rating("Appetite (Light to Heavy)", "q3")
                with sc2:
                    st.markdown("<b>Sweet Notes</b>", unsafe_allow_html=True)
                    sweetness = star_rating("Sweetness Intensity", "q4")
                    sweet_texture = star_rating("Dessert Richness", "q5")
                    
                st.write("---")
                if st.form_submit_button("Unveil Recommendations"):
                    final_texture = round((savory_texture + sweet_texture) / 2)
                    st.session_state.user_vector = [spice, sweetness, final_texture, heaviness]
                    st.session_state.view = "results"
                    st.rerun()


# ── VIEW 3: Results Page ────────────────────────────────────────────────────
elif st.session_state.view == "results":
    left_pane, right_pane = st.columns([1, 2.5], gap="large")
    
    # Left Pane (Maroon)
    with left_pane:
        st.markdown(f"""
        <div class="maroon-bg" style="min-height: 80vh; border-radius: 10px;">
            <h2 style="text-align:center;">Guest Profile</h2>
            <hr style="border-color:#C49A45;">
            <div class="profile-details" style="padding-top: 20px;">
                <p><b>Name:</b> {st.session_state.username}</p>
                <p><b>Diet:</b> {st.session_state.diet_preference}</p>
                <p><b>Restrictions:</b> {', '.join(st.session_state.allergies) if st.session_state.allergies else 'None'}</p>
                <p><b>Region:</b> {st.session_state.province}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("← Restart Quiz"):
            st.session_state.province = None
            st.session_state.view = "quiz"
            st.rerun()
        if st.button("← Home"):
            st.session_state.clear()
            st.rerun()
        
    # Right Pane (Beige)
    with right_pane:
        st.markdown(f"<br><h2>Royal Feasts of {st.session_state.province}</h2>", unsafe_allow_html=True)
        
        results = get_recommendations(
            user_vector=st.session_state.user_vector,
            province=st.session_state.province,
            allergies=st.session_state.allergies,
            username=st.session_state.username
        )

        if st.session_state.diet_preference == "Vegetarian Only":
            results = [d for d in results if d.get("is_veg", False)]
        elif st.session_state.diet_preference == "Non-Vegetarian Only":
            results = [d for d in results if not d.get("is_veg", False)]

        if not results:
            st.warning("Alas, our records yield no dishes matching your strict requirements in this region.")
        else:
            for dish in results:
                allergen_text = f"<p style='color:#FF9999;font-size:12px;'>Contains: {', '.join(dish.get('allergens', []))}</p>" if dish.get("allergens") else ""
                html_str = f'<div class="dish-card"><div><h3 style="margin-top:0; color:#E2C792 !important;">{dish["name"]}</h3><p style="margin-bottom: 5px;"><b>Spice:</b> {int(dish["spice"])} ⭐ &nbsp;|&nbsp; <b>Sweetness:</b> {int(dish["sweetness"])} ⭐</p><p style="font-size: 15px; line-height: 1.5; color: #F0E6D2;"><i>{dish["description"]}</i></p>{allergen_text}</div></div>'
                st.markdown(html_str, unsafe_allow_html=True)
                
                # Action Buttons
                ac1, ac2, ac3, ac4 = st.columns([1, 1, 1.5, 2])
                with ac1:
                    if st.button("Divine", key=f"like_{dish['id']}"):
                        st.toast(f"An excellent choice: {dish['name']}!")
                with ac2:
                    if st.button("Dislike", key=f"dislike_{dish['id']}"):
                        add_dislike(st.session_state.username, dish["id"])
                        st.toast(f"Noted. {dish['name']} shall not be served again.")
                        st.rerun()
                with ac3:
                    if st.button("Haven't Tried", key=f"havent_tried_{dish['id']}"):
                        st.toast(f"No problem! {dish['name']} remains an option for the future.")

            # Exit Button at the bottom
            st.markdown("<br><hr style='border-color:#C49A45;'><br>", unsafe_allow_html=True)
            ex1, ex2, ex3 = st.columns([1, 1, 1])
            with ex2:
                if st.button("Exit", type="primary", use_container_width=True):
                    st.session_state.view = "thank_you"
                    st.rerun()

# ── VIEW 4: Thank You Page ──────────────────────────────────────────────────
elif st.session_state.view == "thank_you":
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #490d0e !important; font-size: 60px;'>Thank You!</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #C49A45 !important; font-style: italic;'>Thank you for using PlatePal.</h3>", unsafe_allow_html=True)
