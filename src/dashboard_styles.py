"""
Professional Dashboard Styling for PakPulse AI
Enterprise-grade design system for consistent, professional appearance
"""

PROFESSIONAL_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Variables - Crisp Blue and White Color Palette */
    :root {
        --primary-blue: #2563eb;
        --primary-blue-light: #60a5fa;
        --primary-blue-dark: #1d4ed8;
        --secondary-blue: #bfdbfe;
        --accent-blue: #eff6ff;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --border-color: #e2e8f0;
        --border-radius: 12px;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    
    /* Main App Container - Crisp Blue and White background */
    .stApp, div[data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%) !important;
        background-image: 
            radial-gradient(circle at 50% 20%, rgba(255,255,255,0.6) 0%, transparent 60%),
            linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%) !important;
        background-attachment: fixed !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        min-height: 100vh !important;
    }
    
    /* Main Content Area - transparent to show gradient */
    .main .block-container {
        padding: 2.5rem 3rem;
        background: transparent !important;
        max-width: 1400px;
        border-radius: var(--border-radius);
        box-shadow: none; 
        margin: 2rem auto;
        border: none; 
    }
    
    /* Ensure clean transparency for harmonious view */
    .main {
        background: transparent !important;
    }
    
    /* Sidebar - Clean crisp white */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #bae6fd !important;
        box-shadow: 2px 0 10px rgba(37,99,235,0.05) !important;
    }
    
    /* Sidebar content - transparent to show gradient */
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [class*="css-"],
    section[data-testid="stSidebar"] [class*="st-"] {
        background: transparent !important;
    }
    
    /* Force light background */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
    }
    
    /* Sidebar text - ensure good visibility */
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    
    /* Streamlit Native Auto-Generated Sidebar Navigation Item styling */
    [data-testid="stSidebarNav"] span {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        text-transform: capitalize !important;
        letter-spacing: 0.5px !important;
        color: #1e293b !important;
    }
    [data-testid="stSidebarNav"] a:hover span {
        color: #2563eb !important;
    }
    [data-testid="stSidebarNav"] {
        padding-top: 1rem !important;
    }
    
    /* Sidebar links and navigation - professional styling */
    section[data-testid="stSidebar"] a {
        color: #3b82f6 !important;
    }
    
    section[data-testid="stSidebar"] a:hover {
        color: #2563eb !important;
    }
    
    /* Sidebar buttons - light background friendly */
    section[data-testid="stSidebar"] .stButton > button {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #f1f5f9 !important;
        color: #1e293b !important;
        border-color: #94a3b8 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #3b82f6 !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #2563eb !important;
        color: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Typography - Professional */
    h1 {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 2.5rem;
        letter-spacing: -0.02em;
        margin-bottom: 0.75rem;
        line-height: 1.2;
    }
    
    h2 {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.875rem;
        letter-spacing: -0.01em;
        margin-bottom: 0.5rem;
        line-height: 1.3;
    }
    
    h3 {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    p, li {
        color: var(--text-secondary);
        font-size: 0.9375rem;
        line-height: 1.6;
    }
    
    /* Cards and Containers */
    .element-container {
        margin-bottom: 1.5rem;
    }
    
    /* Metrics - Professional Styling */
    [data-testid="stMetricValue"] {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    /* Info Boxes - Professional */
    .stInfo {
        border-left: 4px solid var(--primary-blue-light);
        background: linear-gradient(90deg, #eff6ff 0%, #ffffff 100%);
        border-radius: var(--border-radius);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
    }
    
    .stSuccess {
        border-left: 4px solid #10b981;
        background: linear-gradient(90deg, #f0fdf4 0%, #ffffff 100%);
        border-radius: var(--border-radius);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
    }
    
    .stWarning {
        border-left: 4px solid #f59e0b;
        background: linear-gradient(90deg, #fffbeb 0%, #ffffff 100%);
        border-radius: var(--border-radius);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
    }
    
    .stError {
        border-left: 4px solid #ef4444;
        background: linear-gradient(90deg, #fef2f2 0%, #ffffff 100%);
        border-radius: var(--border-radius);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
    }
    
    /* Buttons - Professional */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9375rem;
        padding: 0.625rem 1.5rem;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
        color: white;
        border: none;
    }
    
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--primary-blue-dark) 0%, var(--primary-blue) 100%);
        box-shadow: var(--shadow-lg);
    }
    
    button[kind="secondary"] {
        background: var(--bg-primary);
        color: var(--primary-blue);
        border: 1.5px solid var(--primary-blue-light);
    }
    
    button[kind="secondary"]:hover {
        background: var(--accent-blue);
        color: var(--primary-blue-dark);
        border-color: var(--primary-blue);
    }
    
    /* Input Fields - Professional */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 1.5px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        background: var(--bg-primary);
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-blue-light);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    /* Labels */
    label {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9375rem;
        margin-bottom: 0.5rem;
    }
    
    /* Dataframes - Professional */
    .dataframe {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
    
    /* Tabs - Professional */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: var(--text-secondary);
        border-radius: 8px 8px 0 0;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--primary-blue);
        background: var(--accent-blue);
        border-bottom: 3px solid var(--primary-blue);
    }
    
    /* Expanders - Professional */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        background: var(--bg-secondary);
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    .streamlit-expanderContent {
        padding: 1rem;
        background: var(--bg-primary);
        border-radius: 0 0 8px 8px;
        border: 1px solid var(--border-color);
        border-top: none;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-blue-light) 0%, var(--primary-blue) 100%);
        border-radius: 4px;
    }
    
    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 2rem 0;
    }
    
    /* Sidebar Text */
    .sidebar .sidebar-content {
        color: var(--text-primary);
    }
    
    .sidebar .sidebar-content h3 {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 1.125rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Checkboxes and Radio */
    .stCheckbox > label,
    .stRadio > label {
        font-weight: 500;
        color: var(--text-primary);
    }
    
    /* Selectbox and Multiselect */
    .stSelectbox label,
    .stMultiSelect label {
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--primary-blue-light);
    }
    
    /* Code Blocks */
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* Professional Header Cards */
    .header-card {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
        color: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-xl);
        margin-bottom: 2rem;
    }
    
    .header-card h1,
    .header-card h2,
    .header-card h3 {
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .header-card p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
    }
    
    /* Professional Section Cards */
    .section-card {
        background: var(--bg-primary);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1.5rem;
            margin: 1rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
    }
    
    /* Smooth transitions */
    * {
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    }
</style>
"""


