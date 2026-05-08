import re

with open('d:/FYP/src/auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r"# ---------------------------- PROFESSIONAL MODERN STYLE ----------------------------.*?# ---------------------------- LOGIN PAGE ----------------------------"

replacement = """# ---------------------------- PROFESSIONAL MODERN STYLE ----------------------------
    page_style = \"\"\"
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stToolbar"] {display: none !important;}
    section[data-testid="stSidebar"] {display: none !important;}
    div[data-testid="collapsedControl"] {display: none !important;}
    
    /* Full viewport background */
    .stApp {
        background: linear-gradient(180deg, #f8fbff 0%, #e6f0fa 100%) !important;
        background-image: 
            radial-gradient(circle at 50% 20%, rgba(255,255,255,0.8) 0%, transparent 40%),
            linear-gradient(180deg, #f8fbff 0%, #e6f0fa 100%) !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif !important;
        min-height: 100vh !important;
    }

    .stApp > header {
        background-color: transparent !important;
    }

    /* Centers the main block */
    .block-container {
        padding: 0 !important;
        max-width: 900px !important;
        margin: 0 auto !important;
        width: 100% !important;
    }
    
    .stAppViewContainer {
        background: transparent !important;
    }

    /* Login UI container */
    .login-ui-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 2rem;
        margin-top: 1rem;
    }

    /* Form Buttons inside streamlit */
    .stButton > button {
        height: 45px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }
    
    /* LOGIN button style (Primary) */
    .btn-login .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    .btn-login .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-2px) !important;
    }

    /* REGISTER button style (Secondary) */
    .btn-register .stButton > button {
        background: #ffffff !important;
        color: #2563eb !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    .btn-register .stButton > button:hover {
        background: #f8fafc !important;
        border-color: #94a3b8 !important;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    \"\"\"
    st.markdown(page_style, unsafe_allow_html=True)

    # ---------------------------- PAGE SWITCHER ----------------------------
    def goto(page):
        st.session_state.welcome_page = page
        st.rerun()

    # ---------------------------- WELCOME PAGE ----------------------------
    if st.session_state.welcome_page == "welcome":
        # Top Bar
        st.markdown(\"\"\"
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; position: fixed; top: 0; left: 0; right: 0; z-index: 100;">
            <div style="font-weight: 700; font-size: 1.25rem; color: #0f172a; font-family: 'Inter', sans-serif;">
                PakPulse-AI
            </div>
            <div style="display: flex; gap: 1rem; color: #64748b; font-size: 1.1rem; background: rgba(255,255,255,0.7); padding: 0.4rem 0.8rem; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <span title="Settings" style="cursor: pointer; opacity: 0.8;">⚙️</span>
                <span title="Share" style="cursor: pointer; opacity: 0.8;">📤</span>
                <span title="Profile" style="cursor: pointer; opacity: 0.8;">👤</span>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)

        # SVG Logo
        logo_svg = \"\"\"
        <svg width="110" height="110" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M50 8 V92 M8 50 H92" stroke="#1d4ed8" stroke-width="1.5" stroke-dasharray="3 3" />
            <path d="M25 25 L75 75 M25 75 L75 25" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="2 3" />
            <rect x="36" y="15" width="28" height="70" rx="3" fill="none" stroke="#1d4ed8" stroke-width="3" />
            <rect x="15" y="36" width="70" height="28" rx="3" fill="none" stroke="#1d4ed8" stroke-width="3" />
            <!-- Inner background -->
            <rect x="37.5" y="37.5" width="25" height="25" fill="#eff6ff" />
            
            <circle cx="50" cy="50" r="10" fill="#ffffff" stroke="#2563eb" stroke-width="2.5" />
            <path d="M45 45 L55 55 M45 55 L55 45" stroke="#2563eb" stroke-width="1.5" />
            
            <!-- Nodes -->
            <circle cx="50" cy="15" r="3.5" fill="#1e40af" />
            <circle cx="50" cy="85" r="3.5" fill="#1e40af" />
            <circle cx="15" cy="50" r="3.5" fill="#1e40af" />
            <circle cx="85" cy="50" r="3.5" fill="#1e40af" />
            
            <circle cx="36" cy="36" r="3.5" fill="#2563eb" />
            <circle cx="64" cy="64" r="3.5" fill="#2563eb" />
            <circle cx="36" cy="64" r="3.5" fill="#2563eb" />
            <circle cx="64" cy="36" r="3.5" fill="#2563eb" />
        </svg>
        \"\"\"

        st.markdown(f\"\"\"
        <div class="login-ui-wrapper" style="margin-top: 3rem;">
            <!-- Glow background circle & Logo -->
            <div style="width: 250px; height: 250px; background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(220,240,255,0.6) 45%, transparent 75%); border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; margin-bottom: 0.5rem; pointer-events: none;">
                <div style="position: absolute; width: 350px; height: 350px; background: radial-gradient(circle, rgba(255,255,255,0.5) 0%, rgba(230,245,255,0.1) 60%, transparent 100%); border-radius: 50%; z-index: -1;"></div>
                <div style="z-index: 1; display: flex; flex-direction: column; align-items: center;">
                    {logo_svg}
                    <div style="color: #0f4c8a; font-size: 1.8rem; font-weight: 700; margin-top: 10px; letter-spacing: -0.5px;">PakPulse<span style="font-weight: 400; color: #475569;">·</span>AI</div>
                    <div style="color: #0c3e75; font-size: 0.65rem; font-weight: 700; letter-spacing: 1px; margin-top: 0px;">DISEASE EARLY WARNING SYSTEM</div>
                </div>
            </div>
            
            <h1 style="color: #1e293b; font-size: 2.4rem; font-weight: 600; margin-bottom: 1.5rem; text-align: center; letter-spacing: -0.5px;">Welcome Back</h1>
            
            <div style="max-width: 620px; text-align: center; color: #475569; font-size: 0.95rem; line-height: 1.7; margin-bottom: 2.5rem;">
                PakPulse AI is a comprehensive outbreak prediction and health surveillance ecosystem.
                Leveraging advanced AI models, real-time climate telemetry, and national epidemiological
                reports, we dynamically predict potential outbreaks and visualize disease risk levels across
                all districts. Our analytical platform empowers healthcare officers with
                proactive early warning signals to safeguard public wellness.
            </div>
            
            <div style="color: #334155; font-size: 0.95rem; margin-bottom: 1.5rem; text-align: center; font-weight: 400;">
                Enter your personal details to use all of site features
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)

        # Buttons side by side
        col1, col2, col3, col4 = st.columns([1, 1.8, 1.8, 1])
        
        with col2:
            st.markdown('<div class="btn-login" style="width: 100%;">', unsafe_allow_html=True)
            if st.button("LOGIN", use_container_width=True):
                goto("login")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="btn-register" style="width: 100%;">', unsafe_allow_html=True)
            if st.button("REGISTER", use_container_width=True):
                goto("register")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Footer Links and Copyright
        st.markdown(\"\"\"
        <div style="width: 100%; display: flex; flex-direction: column; align-items: center; margin-top: 3rem; margin-bottom: 2rem;">
            <div style="color: #64748b; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; justify-content: center;">
                <span style="cursor: pointer; text-decoration: none;" onmouseover="this.style.color='#2563eb'" onmouseout="this.style.color='#64748b'">Privacy Policy</span> 
                <span style="color: #cbd5e1;">·</span> 
                <span style="cursor: pointer; text-decoration: none;" onmouseover="this.style.color='#2563eb'" onmouseout="this.style.color='#64748b'">Terms of Service</span> 
                <span style="color: #cbd5e1;">·</span> 
                <span style="cursor: pointer; text-decoration: none;" onmouseover="this.style.color='#2563eb'" onmouseout="this.style.color='#64748b'">Contact Us</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; position: fixed; bottom: 15px; left: 20px; right: 20px; color: #94a3b8; font-size: 0.8rem; pointer-events: none;">
            <span>© 2024 PakPulse AI. All rights reserved.</span>
            <span>© 2024 PakPulse AI. All rights reserved.</span>
        </div>
        \"\"\", unsafe_allow_html=True)

    # ---------------------------- LOGIN PAGE ----------------------------"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('d:/FYP/src/auth.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
