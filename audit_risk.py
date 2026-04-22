
# modules/audit_risk.py

import streamlit as st
import plotly.graph_objects as go
from tax_engine import AUDIT_RISK_WEIGHTS


def run(client_data: dict) -> dict:
    st.markdown("## Module 2 - Audit Risk Scorer")
    st.markdown(
        "The IRS uses a Discriminant Information Function (DIF) score to rank returns "
        "by audit probability. This module applies published risk factors and known IRS "
        "selection thresholds to estimate your client's relative audit exposure. "
        "Source: TRAC IRS Audit Reports (2023), IRS Publication 1345."
    )

    agi = client_data["agi"]
    has_schedule_c = client_data["has_schedule_c"]
    num_children = client_data["num_children"]
    charitable = client_data.get("charitable_contributions", 0)
    home_office = client_data.get("home_office_deduction", False)
    cash_income = client_data.get("cash_income", False)
    foreign_income = client_data.get("foreign_income", False)
    prior_amendment = client_data.get("prior_amendment", False)

    risk_factors = {}

    if has_schedule_c:
        risk_factors["Schedule C (Self-Employment) Income"] = AUDIT_RISK_WEIGHTS["schedule_c_income"]

    if agi > 0 and charitable / agi > 0.20:
        risk_factors["Charitable Deductions > 20% of AGI"] = AUDIT_RISK_WEIGHTS["high_charitable_ratio"]

    if home_office:
        risk_factors["Home Office Deduction Claimed"] = AUDIT_RISK_WEIGHTS["home_office_deduction"]

    if cash_income:
        risk_factors["Cash Income Reported on Return"] = AUDIT_RISK_WEIGHTS["cash_income_reported"]

    if foreign_income:
        risk_factors["Foreign Income or FBAR Requirement"] = AUDIT_RISK_WEIGHTS["foreign_income"]

    if prior_amendment:
        risk_factors["Amended Return Filed in Prior Year"] = AUDIT_RISK_WEIGHTS["prior_year_amendment"]

    if num_children > 0 and client_data.get("total_credits", 0) > 0:
        risk_factors["EITC or CTC Claim with Dependents"] = AUDIT_RISK_WEIGHTS["eitc_claim"]

    if agi >= 1000000:
        agi_multiplier = 1.8
        agi_note = "AGI >= $1M: IRS audit rate ~2.4% (IRS Data Book 2023)"
    elif agi >= 500000:
        agi_multiplier = 1.4
        agi_note = "AGI >= $500K: Elevated IRS scrutiny tier"
    elif agi >= 200000:
        agi_multiplier = 1.15
        agi_note = "AGI >= $200K: Moderate elevated scrutiny tier"
    else:
        agi_multiplier = 1.0
        agi_note = "AGI under $200K: Standard audit probability tier"

    raw_score = sum(risk_factors.values()) * 100
    adjusted_score = min(100, round(raw_score * agi_multiplier, 1))

    if adjusted_score < 20:
        risk_level = "Low"
        color = "#2ecc71"
        recommendation = "Return presents minimal audit risk indicators. Standard review procedures apply."
    elif adjusted_score < 50:
        risk_level = "Moderate"
        color = "#f39c12"
        recommendation = "One or more elevated risk factors identified. Recommend thorough documentation of all deductions and credits prior to filing."
    else:
        risk_level = "Elevated"
        color = "#e74c3c"
        recommendation = "Multiple high-weight DIF risk factors present. Recommend senior review before filing and preparation of supporting documentation package."

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=adjusted_score,
            title={"text": "Audit Risk Score (0-100)", "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 20], "color": "#eafaf1"},
                    {"range": [20, 50], "color": "#fef9e7"},
                    {"range": [50, 100], "color": "#fdedec"},
                ],
                "threshold": {"line": {"color": "black", "width": 3}, "thickness": 0.75, "value": adjusted_score},
            },
        ))
        fig.update_layout(height=320, paper_bgcolor="white", font=dict(family="Arial"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### Risk Level: **{risk_level}**")
        st.markdown(f"**Score:** {adjusted_score} / 100")
        st.markdown(f"**AGI Tier:** {agi_note}")
        st.markdown(f"**Analyst Recommendation:** {recommendation}")

    if risk_factors:
        st.markdown("### Contributing Risk Factors")
        for factor, weight in risk_factors.items():
            st.markdown(f"- **{factor}** - Risk weight: {weight:.0%}")
    else:
        st.success("No material DIF risk factors identified on this return.")

    client_data["audit_risk_score"] = adjusted_score
    client_data["audit_risk_level"] = risk_level
    client_data["audit_recommendation"] = recommendation
    client_data["audit_risk_factors"] = risk_factors
    return client_data
