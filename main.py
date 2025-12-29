import streamlit as st
from PIL import Image
#app_page = st.Page(page="app.py", title="📝 Document Verification")
#compliance_page = st.Page(page="pages/compliance.py", title="🚀 Report Generation")
# st.image("nama-logo.png")


# 1. Open the images
img1 = Image.open("nama-logo.png")

# 2. Resize them to specific dimensions (width, height)
# You can also crop them to maintain aspect ratio if preferred
s1 = (250, 200) 
img1_resized = img1.resize(s1)

# 3. Display in columns
col1, col2 = st.columns(2)

with col1:
    st.image(img1_resized)

with col2:
    st.image("velyana-new.png")

pages = {
    "Services": [
        st.Page("app.py", title="📝 Document Verification"),
        st.Page("pages/compliance.py", title="🚀 Report Generation"),
    ]
}

pg = st.navigation(pages)
pg.run()
# pg = st.navigation(
#     pages=[app_page, compliance_page]
# )

# pg.run()