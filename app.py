
# app.py -- Tax Intelligence Platform

import streamlit as st
import os
import sys

# Add subdirectories directly to path -- eliminates __init__.py requirement
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

import return_optimizer
import audit_risk
import tcja_projector
from pdf_export import generate_pdf

st.set_page_config(
    page_title="Tax Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <div style="background-color:#1f3a5f;padding:24px 32px 16px 32px;border-radius:8px;margin-bottom:24px;">
        <h1 style="color:white;margin:0;font-family:Arial;font-size:28px;">Tax Intelligence Platform</h1>
        <p style="color:#a8c4e0;margin:6px 0 0 0;font-size:14px;">
        Federal Return Optimization &middot; Audit Risk Assessment &middot; TCJA Sunset Planning
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "Enter your client's tax profile in the sidebar. All three modules will update automatically, "
    "and findings carry forward from Module 1 through Module 3 without re-entry."
)

with st.sidebar:
    st.markdown("## Client Profile")
    st.markdown("*All inputs are used across all three modules.*")

    filing_status = st.selectbox(
        "Filing Status",
        ["single", "married_filing_jointly", "head_of_household"],
        format_func=lambda x: x.replace("_", " ").title(),
    )
    agi = st.number_input("Adjusted Gross Income (AGI)", min_value=0, max_value=10000000, value=75000, step=1000)
    num_children = st.number_input("Number of Qualifying Children", min_value=0, max_value=10, value=1, step=1)
    itemized_deductions = st.number_input("Total Itemized Deductions", min_value=0, max_value=500000, value=12000, step=500)
    child_care_expenses = st.number_input("Child/Dependent Care Expenses", min_value=0, max_value=20000, value=0, step=500)
    charitable_contributions = st.number_input("Charitable Contributions (included in itemized)", min_value=0, max_value=200000, value=0, step=500)

    st.markdown("---")
    st.markdown("**Additional Flags**")
    has_schedule_c = st.checkbox("Self-Employment / Schedule C Income")
    has_college_student = st.checkbox("Qualifying College Student (AOC Eligible)")
    home_office_deduction = st.checkbox("Home Office Deduction Claimed")
    cash_income = st.checkbox("Cash Income Reported")
    foreign_income = st.checkbox("Foreign Income / FBAR")
    prior_amendment = st.checkbox("Amended Return Filed in Prior Year")

client_data = {
    "filing_status": filing_status,
    "agi": agi,
    "num_children": num_children,
    "itemized_deductions": itemized_deductions,
    "child_care_expenses": child_care_expenses,
    "charitable_contributions": charitable_contributions,
    "has_schedule_c": has_schedule_c,
    "has_college_student": has_college_student,
    "home_office_deduction": home_office_deduction,
    "cash_income": cash_income,
    "foreign_income": foreign_income,
    "prior_amendment": prior_amendment,
}

st.markdown("---")
client_data = return_optimizer.run(client_data)
st.markdown("---")
client_data = audit_risk.run(client_data)
st.markdown("---")
client_data = tcja_projector.run(client_data)

st.markdown("---")
st.markdown("## Export Client Memo")
st.markdown("Generate a professional one-page PDF memo summarizing all three modules for client or partner review.")

os.makedirs("exports", exist_ok=True)
export_path = "exports/client_memo.pdf"

if st.button("Generate PDF Client Memo", type="primary"):
    generate_pdf(client_data, export_path)
    with open(export_path, "rb") as f:
        st.download_button(
            label="Download Memo (PDF)",
            data=f,
            file_name="Tax_Intelligence_Client_Memo.pdf",
            mime="application/pdf",
        )
    st.success("Memo generated successfully.")

st.markdown(
    """
    <div style="margin-top:40px;padding:12px;background:#f4f6f9;border-radius:6px;font-size:11px;color:#888;">
    Data sources: IRS Rev. Proc. 2023-34 &middot; IRS Publications 596, 503, 970 &middot; IRS Data Book 2023 &middot;
    CBO January 2024 Budget and Economic Outlook &middot; JCT TCJA Sunset Analysis.
    All figures are estimates for planning purposes only.
    </div>
    """,
    unsafe_allow_html=True,
)
