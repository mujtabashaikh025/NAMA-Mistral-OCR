import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import re
import os

# --- 1. CONFIGURATION ---
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
        "<h1 style='text-align: center; margin: 0; font-size: 36px;'> </h1>", 
        unsafe_allow_html=True
    )

with col3:
    st.image("velyana-new.png", width=200)

# REPLACE with your actual API Key
api_key =  st.secrets["GEMINI_API_KEY"] 

# --- 2. HELPER FUNCTIONS ---

def clean_json_string(json_str):
    """Cleans Markdown formatting from JSON string."""
    cleaned = re.sub(r"```json\s*", "", json_str)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()

def get_compliance_table(pdf_bytes, key):
    """Sends the PDF file DIRECTLY to Gemini (no local text extraction needed)."""
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-3-pro-preview')
        
        system_prompt = """
        You are a Technical QA Engineer reviewing a scanned Vendor Specification Document.
        
        **YOUR TASK:**
        Look at the document image/PDF and extract a comprehensive Compliance Table.
        
        **INPUT DATA:**
        The document contains a list of "APPLICABLE STANDARDS" (BS EN, ISO, etc.) and specific sections (Climatic Data, Design Considerations, Materials). 
        Next to each item, the vendor has written a response (e.g., "Comply", "Noncomply", "Not related") or used a **handwritten tick/check mark**.
        
        **RULES FOR EXTRACTION:**
        1. **Identify every Standard** (e.g., BS EN 558-1, ISO 9001) and **Key Section** (Climatic Data, Scope, etc.).
        2. **Determine Status:**
           - If text says "Comply", "Included", or has a positive context -> **"Comply"**.
           - If text says "Noncomply", "Not related", "Excluded" -> **"Not Comply"**.
           - **CRITICAL:** If you see a **handwritten tick ($\checkmark$)** or check mark next to a section (especially Climatic Data/Design Considerations) -> Mark as **"Comply"**.
        3. **Generate Remark:**
           - If "Not Comply", explain the deviation (e.g., "Vendor excludes galvanization standard").
           - If "Comply" but with a note (e.g., "Comply (Ductile Iron used)"), include that note.

        **OUTPUT FORMAT (JSON ARRAY):**
        [
            {"Standard_Section": "BS EN 558-1", "Status": "Comply", "Remark": "Face-to-face dimensions for valves"},
            {"Standard_Section": "BS EN ISO 1461", "Status": "Not Comply", "Remark": "Vendor states 'Not related', deviating from galvanization requirement"}
        ]
        """

        # Create the data part for Gemini
        pdf_data = {
            "mime_type": "application/pdf",
            "data": pdf_bytes
        }

        # Send both prompt and PDF data
        response = model.generate_content(
            contents=[system_prompt, pdf_data],
            generation_config={"response_mime_type": "application/json"}
        )
        
        return json.loads(clean_json_string(response.text))

    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return []

# --- 3. STREAMLIT UI ---

st.title("📑 Smart Compliance Report Generator")
#st.markdown("**Upload a Vendor Specification Compliance Statement**.")

uploaded_file = st.file_uploader("**Upload Compliance Statement PDF**", type=["pdf"])

if uploaded_file and st.button("Generate Report",type="primary"):
    
    with st.spinner("👀 Analyzing Statement & Compliance..."):
        
        bytes_data = uploaded_file.getvalue()
        
        if bytes_data:
            table_data = get_compliance_table(bytes_data, api_key)
            
            if table_data:
                df = pd.DataFrame(table_data)

                # --- METRIC CALCULATION LOGIC ---
                total_items = len(df)
                
                # We filter for rows that contain "Comply" but NOT "Not Comply" (case insensitive)
                compliant_df = df[
                    df['Status'].astype(str).str.contains("Comply", case=False) & 
                    ~df['Status'].astype(str).str.contains("Not", case=False)
                ]
                
                num_comply = len(compliant_df)
                num_non_comply = total_items - num_comply
                
                # Calculate Percentage: (Comply / Total) * 100
                if total_items > 0:
                    compliance_pct = (num_comply / total_items) * 100
                else:
                    compliance_pct = 0.0

                # --- DISPLAY METRICS ---
                a, b = st.columns(2)
                a.metric("Compliance Percentage", f"{compliance_pct:.1f}%", border=True)
                b.metric("Number of Non-Compliance", f"{num_non_comply}", border=True)

                # --- VISUALS ---
                def color_status(val):
                    val_str = str(val).lower()
                    if 'comply' in val_str and 'not' not in val_str:
                        return 'background-color: #d4edda; color: #155724' # Green
                    return 'background-color: #f8d7da; color: #721c24'     # Red

                st.subheader("Compliance Report")
                st.dataframe(
                    df.style.map(color_status, subset=['Status']),
                    column_config={
                        "Standard_Section": "Standard / Section",
                        "Status": "Compliance Status",
                        "Remark": "AI Observations / Remarks"
                    },
                    use_container_width=True
                )
                
                # Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Report",
                    data=csv,
                    file_name="compliance_table.csv",
                    mime="text/csv",
                )
            else:
                st.warning("Could not extract a table. Please ensure the PDF is not password protected.")
