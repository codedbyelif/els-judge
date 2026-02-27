import streamlit as st
import pandas as pd
import requests
import sys
import os

# Ensure core models can be imported for direct DB reads
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import SessionLocal
from models.domain import Submission, FinalVerdict

st.set_page_config(page_title="LLM Consensus Engine", page_icon="🛡️", layout="wide")

st.title("🛡️ LLM Consensus Engine")
st.markdown("A production-ready pipeline to validate generated code across multiple LLMs.")

@st.cache_data(ttl=5)
def get_recent_submissions():
    db = SessionLocal()
    try:
        results = db.query(Submission, FinalVerdict).outerjoin(FinalVerdict).order_by(Submission.id.desc()).limit(20).all()
        data = []
        for sub, ver in results:
            data.append({
                "ID": sub.id,
                "Time": sub.created_at.strftime("%Y-%m-%d %H:%M:%S") if sub.created_at else "",
                "Risk Score": ver.aggregated_risk_score if ver else None,
                "Severity": ver.severity_level if ver else "Pending",
                "Disagreement": f"{(ver.disagreement_rate * 100):.1f}%" if ver else "N/A"
            })
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame()
    finally:
        db.close()

# --- Layout: Main Submission Area and Sidebar --- 

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Submit Code for Review")
    with st.form("submission_form"):
        orig = st.text_area("Original Code", height=200, placeholder="def hello_world():\n    pass")
        sugg = st.text_area("Suggested Code", height=200, placeholder="def hello_world():\n    print('hello world!')")
        submit = st.form_submit_button("Run Consensus Pipeline", use_container_width=True)
        
        if submit:
            if not orig or not sugg:
                st.warning("Please provide both Original and Suggested code.")
            else:
                with st.spinner("Dispatching to multiple models..."):
                    try:
                        res = requests.post("http://localhost:8000/api/submit-code", json={
                            "original_code": orig,
                            "suggested_code": sugg
                        }, timeout=60)
                        
                        if res.status_code == 200:
                            st.success("Pipeline successful!")
                            data = res.json()
                            with st.expander("Show Latest Report", expanded=True):
                                st.markdown(data.get("markdown_report", ""))
                        else:
                            st.error(f"Error {res.status_code}: {res.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to FastAPI backend. Is it running on port 8000?")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

with col2:
    st.subheader("Recent Submissions")
    df = get_recent_submissions()
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Details viewer
        selected_id = st.selectbox("View details for submission ID", options=["Select"] + df["ID"].tolist())
        if selected_id != "Select":
            db = SessionLocal()
            verdict = db.query(FinalVerdict).filter(FinalVerdict.submission_id == selected_id).first()
            if verdict:
                st.markdown(f"**Score:** {verdict.aggregated_risk_score}")
                st.markdown(f"**Disagreements:** {verdict.disagreement_rate * 100}%")
                with st.expander("Full Report"):
                    st.markdown(verdict.markdown_report)
            db.close()
    else:
        st.info("No submissions found in DB.")
