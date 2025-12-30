import streamlit as st


pages = {
    "Services": [
        st.Page("app.py", title="📝 Document Verification"),
        st.Page("pages/compliance2.py", title="🚀 Report Generation"),
    ]
}

pg = st.navigation(pages)
pg.run()
