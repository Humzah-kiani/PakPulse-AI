import os

filepath = r"d:\FYP\Pak-Pulse-AI-Outbreak-Disease-Early-Warning-System\src\auth.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Background color
content = content.replace("linear-gradient(to right, #e2e2e2, #c9d6ff)", "#f8fafc")

# 2. Heading text color (currently inline muddy #1e40af gradient)
content = content.replace("linear-gradient(90deg, #1e40af 0%, #3b82f6 50%, #1e40af 100%)", "linear-gradient(90deg, #1d4ed8 0%, #2563eb 50%, #1d4ed8 100%)")

# 3. Logo insertion on the first page
first_opening = 'st.markdown("<div class=\'glass-card\'>", unsafe_allow_html=True)'
logo_insertion = '''col1, col2, col3 = st.columns([1.2, 1, 1.2])
        with col2:
            st.image("assets/logo.png", use_container_width=True)'''
content = content.replace(first_opening, logo_insertion, 1)

# 4. Remove all other opening cards
content = content.replace(first_opening, "")

# 5. Remove all closing divs
closing_div = 'st.markdown("</div>", unsafe_allow_html=True)'
content = content.replace(closing_div, "")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("done")
