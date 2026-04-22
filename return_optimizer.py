
# modules/return_optimizer.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tax_engine import (
    calculate_tax, calculate_eitc, calculate_ctc,
    STANDARD_DEDUCTION_2024, AOC_2024, CHILD_CARE_CREDIT_2024
)


def run(client_data: dict) -> dict:
    st.markdown("## Module 1 - Return Optimizer")
    st.markdown(
        "This module analyzes your client profile against current IRS guidelines "
        "to identify missed deductions, applicable credits, and the optimal filing strategy. "
        "All thresholds are sourced from IRS Revenue Procedure 2023-34 and IRS Publications 596, 503, and 970."
    )

    filing_status = client_data["filing_status"]
    agi = client_data["agi"]
    num_children = client_data["num_children"]
    itemized = client_data["itemized_deductions"]
    standard = STANDARD_DEDUCTION_2024[filing_status]
    has_college_student = client_data["has_college_student"]
    child_care_expenses = client_data["child_care_expenses"]
    has_schedule_c = client_data["has_schedule_c"]

    st.markdown("### Deduction Strategy")
    optimal_deduction = max(itemized, standard)
    deduction_choice = "Itemized" if itemized > standard else "Standard"
    deduction_savings = abs(itemized - standard)

    col1, col2, col3 = st.columns(3)
    col1.metric("Standard Deduction", f"${standard:,.0f}")
    col2.metric("Your Itemized Total", f"${itemized:,.0f}")
    col3.metric("Recommended", deduction_choice, f"${deduction_savings:,.0f} advantage")

    taxable_income = max(0, agi - optimal_deduction)
    federal_tax = calculate_tax(taxable_income, filing_status)

    st.markdown("### Credit Eligibility Analysis")
    credits_identified = {}
    flags = []

    eitc = calculate_eitc(agi, filing_status, num_children)
    if eitc > 0:
        credits_identified["Earned Income Tax Credit (EITC)"] = eitc
    elif num_children > 0:
        flags.append("EITC: Income exceeds threshold for this filing status.")

    ctc = calculate_ctc(agi, filing_status, num_children)
    if ctc > 0:
        credits_identified["Child Tax Credit (CTC)"] = ctc

    if has_college_student:
        aoc_phase_out_start = AOC_2024["phase_out_mfj_start"] if filing_status == "married_filing_jointly" else AOC_2024["phase_out_single_start"]
        aoc_phase_out_end = AOC_2024["phase_out_mfj_end"] if filing_status == "married_filing_jointly" else AOC_2024["phase_out_single_end"]
        if agi < aoc_phase_out_end:
            if agi < aoc_phase_out_start:
                aoc_credit = AOC_2024["max_credit"]
            else:
                phase_ratio = 1 - (agi - aoc_phase_out_start) / (aoc_phase_out_end - aoc_phase_out_start)
                aoc_credit = round(AOC_2024["max_credit"] * phase_ratio, 2)
            credits_identified["American Opportunity Credit (AOC)"] = aoc_credit
        else:
            flags.append("AOC: AGI exceeds phase-out range. Consider Lifetime Learning Credit.")

    if child_care_expenses > 0 and num_children > 0:
        max_exp = CHILD_CARE_CREDIT_2024["max_expenses_two_plus"] if num_children >= 2 else CHILD_CARE_CREDIT_2024["max_expenses_one_child"]
        rate = CHILD_CARE_CREDIT_2024["credit_rate_over_43k_agi"] if agi > 43000 else CHILD_CARE_CREDIT_2024["credit_rate_under_15k_agi"]
        cc_credit = round(min(child_care_expenses, max_exp) * rate, 2)
        credits_identified["Child and Dependent Care Credit"] = cc_credit

    total_credits = sum(credits_identified.values())
    net_tax = max(0, federal_tax - total_credits)

    if credits_identified:
        credit_df = pd.DataFrame(
            {"Credit": list(credits_identified.keys()), "Estimated Amount": [f"${v:,.2f}" for v in credits_identified.values()]}
        )
        st.dataframe(credit_df, use_container_width=True, hide_index=True)
    else:
        st.info("No additional credits identified beyond inputs provided.")

    if flags:
        st.markdown("**Advisory Flags:**")
        for flag in flags:
            st.warning(flag)

    st.markdown("### Tax Liability Waterfall")
    fig = go.Figure(go.Waterfall(
        name="Tax Calculation",
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Adjusted Gross Income", f"Less: {deduction_choice} Deduction", "Less: Tax Credits", "Net Federal Tax Liability"],
        y=[agi, -optimal_deduction, -total_credits, 0],
        totals={"marker": {"color": "#1f3a5f"}},
        decreasing={"marker": {"color": "#2ecc71"}},
        increasing={"marker": {"color": "#e74c3c"}},
        connector={"line": {"color": "#888"}},
    ))
    fig.update_layout(
        title="Federal Tax Liability Build -- Tax Year 2024",
        yaxis_title="Amount ($)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=13),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Gross Federal Tax", f"${federal_tax:,.2f}")
    col2.metric("Total Credits Applied", f"-${total_credits:,.2f}")
    col3.metric("Net Federal Tax Liability", f"${net_tax:,.2f}")

    client_data.update({
        "deduction_choice": deduction_choice,
        "optimal_deduction": optimal_deduction,
        "taxable_income": taxable_income,
        "gross_federal_tax": federal_tax,
        "total_credits": total_credits,
        "net_tax_2024": net_tax,
        "credits_identified": credits_identified,
        "flags": flags,
        "has_schedule_c": has_schedule_c,
    })
    return client_data
