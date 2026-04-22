
# modules/tcja_projector.py

import streamlit as st
import plotly.graph_objects as go
from tax_engine import (
    calculate_tax, calculate_ctc,
    STANDARD_DEDUCTION_2024, STANDARD_DEDUCTION_2026_SUNSET
)


def run(client_data: dict) -> dict:
    st.markdown("## Module 3 - TCJA Sunset Projector")
    st.markdown(
        "The Tax Cuts and Jobs Act (TCJA) provisions are scheduled to expire after December 31, 2025. "
        "Unless Congress acts, 2026 tax law reverts to pre-TCJA rules -- meaning higher rates, "
        "lower standard deductions, and reduced child tax credits for most filers. "
        "Source: CBO January 2024 Outlook; JCT TCJA Sunset Analysis."
    )

    filing_status = client_data["filing_status"]
    agi = client_data["agi"]
    num_children = client_data["num_children"]
    itemized = client_data["itemized_deductions"]

    std_2025 = STANDARD_DEDUCTION_2024[filing_status]
    std_2026 = STANDARD_DEDUCTION_2026_SUNSET[filing_status]

    optimal_2025 = max(itemized, std_2025)
    optimal_2026 = max(itemized, std_2026)

    taxable_2025 = max(0, agi - optimal_2025)
    taxable_2026 = max(0, agi - optimal_2026)

    gross_tax_2025 = calculate_tax(taxable_2025, filing_status, year="2024")
    gross_tax_2026 = calculate_tax(taxable_2026, filing_status, year="2026_sunset")

    ctc_2025 = calculate_ctc(agi, filing_status, num_children, year="2024")
    ctc_2026 = calculate_ctc(agi, filing_status, num_children, year="2026_sunset")

    net_2025 = max(0, gross_tax_2025 - ctc_2025)
    net_2026 = max(0, gross_tax_2026 - ctc_2026)

    delta = net_2026 - net_2025
    pct_change = (delta / net_2025 * 100) if net_2025 > 0 else 0

    st.markdown("### Side-by-Side: 2025 Law vs. 2026 Sunset Law")

    col1, col2, col3 = st.columns(3)
    col1.metric("2025 Net Federal Tax", f"${net_2025:,.2f}")
    col2.metric("2026 Projected Net Tax (Sunset)", f"${net_2026:,.2f}", f"+${delta:,.2f} ({pct_change:.1f}%)")
    col3.metric("Standard Deduction Change", f"${std_2025:,.0f} -> ${std_2026:,.0f}", f"-${std_2025 - std_2026:,.0f}")

    fig = go.Figure()
    categories = ["Gross Federal Tax", "Child Tax Credit", "Net Tax Liability"]
    vals_2025 = [gross_tax_2025, -ctc_2025, net_2025]
    vals_2026 = [gross_tax_2026, -ctc_2026, net_2026]

    fig.add_trace(go.Bar(name="2025 (Current Law)", x=categories, y=vals_2025, marker_color="#1f3a5f"))
    fig.add_trace(go.Bar(name="2026 (Post-Sunset)", x=categories, y=vals_2026, marker_color="#c0392b"))
    fig.update_layout(
        barmode="group",
        title="2025 vs. 2026 Tax Liability - TCJA Sunset Impact",
        yaxis_title="Amount ($)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=13),
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Planning Implications")
    if delta > 5000:
        st.error(
            f"This client faces a projected ${delta:,.2f} increase in federal tax liability under sunset law. "
            "Immediate planning is warranted. Consider accelerating income into 2025, maximizing retirement contributions, "
            "and reviewing itemized deduction strategy before year-end."
        )
    elif delta > 1000:
        st.warning(
            f"This client faces a projected ${delta:,.2f} increase under sunset law. "
            "A year-end planning review is recommended."
        )
    else:
        st.success(
            "This client's projected exposure to TCJA sunset is relatively limited based on current profile. "
            "Standard year-end review applies."
        )

    client_data["net_tax_2025"] = net_2025
    client_data["net_tax_2026_sunset"] = net_2026
    client_data["tcja_delta"] = delta
    client_data["tcja_pct_change"] = pct_change
    return client_data
