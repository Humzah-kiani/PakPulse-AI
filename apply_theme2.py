import os
import glob

# Mapping old muddy grey/blue colors to fresh crisp white/blue colors
COLOR_MAP = {
    # Backgrounds
    "#f5f7fa": "#f8fafc", # Main grey background -> Cool White
    "245, 247, 250": "248, 250, 252", # rgba equivalent if any
    
    # Primary Blues
    "#3b82f6": "#2563eb", # Light/Standard blue -> Crisp Royal Blue
    "59, 130, 246": "37, 99, 235", # rgb for shadow/rgba
    
    "#1e40af": "#1d4ed8", # Dark blue -> Primary Dark
    "30, 64, 175": "29, 78, 216", 

    "#60a5fa": "#3b82f6", # Soft blue borders -> standard blue
    
    # Header & Banner Linear Gradients
    "#dbeafe": "#eff6ff", # Very light blue header background
    "#bfdbfe": "#dfe8ff", # Soft blue secondary header background

    "#93c5fd": "#bfdbfe" # Border colors for header
}

def apply_theme_to_file(filepath):
    if not os.path.exists(filepath):
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    for old_color, new_color in COLOR_MAP.items():
        content = content.replace(old_color, new_color)
        content = content.replace(old_color.upper(), new_color.upper())

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"No changes for {filepath}")

# Gather all UI files
base_dir = r'd:\FYP\Pak-Pulse-AI-Outbreak-Disease-Early-Warning-System'
ui_files = glob.glob(os.path.join(base_dir, '*.py')) + glob.glob(os.path.join(base_dir, 'pages', '*.py')) + glob.glob(os.path.join(base_dir, 'src', 'dashboard_styles.py'))

for f in ui_files:
    apply_theme_to_file(f)
