# streamlit_ui.py
import streamlit as st
import requests
import json
import pandas as pd
from io import BytesIO

# --- Configuration ---
FASTAPI_URL = "http://127.0.0.1:8000/contracts/analyze/"

# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Contract Reviewer", layout="wide")
st.title("⚖️ AI-Powered Contract Review System")
st.markdown("Upload a contract (PDF/DOCX) for AI analysis, risk scoring, and summarization.")

# ----------------------------------------------------
# 1. RESULT DISPLAY FUNCTION
# ----------------------------------------------------

def display_results(result: dict):
    """Display the analysis results in a structured format"""
    
    # Total Risk Score Card
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    risk_rating = result.get('overall_risk_score', 0)
    risk_color = "🔴" if risk_rating >= 7 else ("🟠" if risk_rating >= 4 else "🟢")
    
    col1.metric("Overall Risk Score (0-10)", f"{risk_color} {risk_rating}", result.get('risk_rating', 'MODERATE'))
    col2.metric("Contract Title", result.get('contract_title', 'N/A'))
    col3.metric("Governing Law", result.get('governing_law', 'Not Specified'))

    st.markdown("---")

    # Summary
    st.header("📄 LLM Summary")
    st.info(result.get('summary', 'Summary not available.'))
    
    st.header("🔑 Key Entities and Terms")
    
    # Key Entities in table format
    terms_data = {
        "Effective Date": result.get('effective_date', 'N/A'),
        "Termination Date": result.get('termination_date', 'N/A'),
        "Payment Terms": result.get('payment_terms', 'N/A'),
        "Renewal Terms": result.get('renewal_terms', 'N/A'),
        "Confidentiality Clause": result.get('confidentiality_clause', 'N/A'),
        "Liability Clause": result.get('liability_clause', 'N/A'),
        "Termination Clauses": result.get('termination_clauses', 'N/A'),
    }
    
    df_terms = pd.DataFrame(terms_data.items(), columns=["Term", "Detail"])
    st.table(df_terms)

    # Parties Involved
    parties = result.get('parties_involved', [])
    if parties:
        st.subheader("👥 Parties Involved")
        df_parties = pd.DataFrame(parties)
        st.table(df_parties)

    # Risk Breakdown
    st.header("🚨 Identified Risks and Severity")
    
    risks = result.get('identified_risks', [])
    if risks:
        df_risks = pd.DataFrame(risks)
        st.dataframe(df_risks, use_container_width=True, height=250)
    else:
        st.success("✅ No specific risks were flagged by the AI.")
        
    # Obligations
    st.header("🤝 Party Obligations")
    obligations = result.get('obligations_summary', [])
    if obligations:
        df_obligations = pd.DataFrame(obligations)
        st.table(df_obligations)
    else:
        st.info("No specific obligations extracted.")


# ----------------------------------------------------
# 2. MAIN EXECUTION LOGIC
# ----------------------------------------------------

# --- File Uploader and API Call ---
uploaded_file = st.file_uploader(
    "Upload Contract Document", 
    type=["pdf", "docx", "doc", "txt"],
    help="Supports PDF, DOCX, DOC, and TXT file formats."
)

if uploaded_file:
    st.info(f"📄 File **{uploaded_file.name}** ready for analysis.")
    
    with st.form("analysis_form"):
        contract_type = st.text_input(
            "Contract Type (Optional)", 
            value="Master Services Agreement", 
            help="Helps the LLM contextually analyze the document."
        )
        analyze_button = st.form_submit_button("▶️ Analyze Contract")

    if analyze_button:
        # Prepare the file and data for the POST request
        files = {
            'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        data = {
            'contract_type': contract_type
        }

        with st.spinner("⏳ Processing contract with AI... This may take up to 60 seconds."):
            try:
                # Send the POST request to your running FastAPI backend
                response = requests.post(FASTAPI_URL, files=files, data=data, timeout=120)
                
                if response.status_code == 200:
                    analysis_result = response.json()
                    st.success("✅ Analysis Complete!")
                    
                    # Display results
                    display_results(analysis_result) 
                    
                    # Download JSON option
                    st.markdown("---")
                    st.download_button(
                        label="📥 Download Analysis as JSON",
                        data=json.dumps(analysis_result, indent=2),
                        file_name=f"contract_analysis_{uploaded_file.name}.json",
                        mime="application/json"
                    )
                
                elif response.status_code == 400:
                    st.error(f"❌ Bad Request (HTTP {response.status_code})")
                    try:
                        error_detail = response.json().get('detail', 'Invalid request.')
                        st.error(f"Error: {error_detail}")
                    except json.JSONDecodeError:
                        st.error(response.text)
                
                elif response.status_code == 500:
                    st.error(f"❌ Server Error (HTTP {response.status_code})")
                    try:
                        error_detail = response.json().get('detail', 'Internal server error.')
                        st.error(f"Error: {error_detail}")
                    except json.JSONDecodeError:
                        st.error(response.text)
                
                else:
                    st.error(f"❌ Analysis Failed (HTTP Error: {response.status_code})")
                    st.text(response.text)

            except requests.exceptions.Timeout:
                st.error("❌ Request Timeout: The analysis took too long. Please try with a smaller document.")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Error: Ensure your FastAPI backend is running at http://127.0.0.1:8000")
                st.info("💡 Start the backend with: `uvicorn main:app --reload`")
            
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
                st.exception(e)

else:
    st.info("👆 Please upload a contract document to begin analysis.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>AI-Powered Contract Review System v1.0 | Built with FastAPI + Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)