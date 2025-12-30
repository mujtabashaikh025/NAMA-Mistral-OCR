import streamlit as st
# 1. Page Configuration
st.set_page_config(
    page_title="Document Verification Portal",
    layout="wide",  # This makes the layout span the full width like your screenshot
    initial_sidebar_state="expanded"
)

# Optional: Add some CSS to reduce top white space for a tighter header
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.5, 6, 2], gap="small", vertical_alignment="center")

with col1:
    # REPLACE 'nama_logo.png' with your actual file path
    # 'use_column_width=False' keeps it from getting too big
    st.image("NG-Service-logo.png", width=250) 

with col2:
    # HTML is used here to force the text to be perfectly centered
    st.markdown(
        "<h1 style='text-align: center; margin: 0; font-size: 36px;'>NAMA Compliance AI Audit</h1>", 
        unsafe_allow_html=True
    )

with col3:
    st.image("velyana-new.png", width=200)

pages = {
    "Services": [
        st.Page("app.py", title="📝 Document Verification"),
        st.Page("pages/compliance.py", title="🚀 Report Generation"),
    ]
}

pg = st.navigation(pages)
pg.run()
