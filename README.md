# Tax Intelligence Platform

**A production-grade, three-module tax analysis suite built for client-facing advisory work.**

---

## What Is This?

The Tax Intelligence Platform is a unified Streamlit application that replicates the complete analytical workflow of a tax practice -- from return optimization through audit risk assessment to forward-looking tax law change planning. A client profile entered once flows automatically through all three modules, producing actionable findings and a downloadable professional memo.

---

## Why Does It Exist?

Every filing season, tax professionals face three core questions for each client:

1. Is this return optimized -- are we leaving credits or deductions on the table?
2. Does this return create audit exposure the client should know about?
3. What does the TCJA sunset mean for this client's 2026 tax liability, and what should we do now?

These questions are typically answered manually, across separate tools, by experienced staff. This platform answers all three in seconds, with full data traceability back to IRS publications.

---

## The Three Modules

### Module 1 -- Return Optimizer
Analyzes AGI, filing status, dependents, and deductions against current IRS guidelines. Compares standard vs. itemized deduction outcomes, identifies applicable credits (EITC, CTC, AOC, Child Care), and computes net federal tax liability. Produces a waterfall chart of the full tax calculation.

**Data source:** IRS Revenue Procedure 2023-34; IRS Publications 596, 503, 970.

### Module 2 -- Audit Risk Scorer
Applies IRS Discriminant Information Function (DIF) score logic and known statistical audit red-flag thresholds to score the client's audit probability on a 0-100 scale. Adjusts for AGI tier using IRS Data Book 2023 audit rates. Produces a risk gauge, contributing factor breakdown, and a plain-English analyst recommendation.

**Data source:** TRAC IRS Audit Reports 2023; IRS Data Book 2023, Table 9a; IRS Publication 1345.

### Module 3 -- TCJA Sunset Projector
Projects the client's federal tax liability under current 2025 law versus post-TCJA sunset 2026 law. Quantifies the dollar and percentage impact of bracket reversion, standard deduction reduction, and child tax credit rollback. Flags urgency and recommends year-end planning actions where material exposure exists.

**Data source:** CBO January 2024 Budget and Economic Outlook; Joint Committee on Taxation TCJA Sunset Analysis.

---

## What Does This Tell Us?

The platform makes visible what most clients never see: the gap between what they owe, what they could owe if their return were better optimized, the risk profile of their filing, and the trajectory of their liability heading into a year of significant tax law change.

For a tax practice, this represents the difference between reactive compliance and proactive client advisory -- the direction every CPA firm is moving.

---

## Technical Stack

- **Python** -- core analytics and tax calculation engine
- **Streamlit** -- interactive front-end and dashboard
- **Plotly** -- waterfall charts, bar charts, and gauge visualizations
- **FPDF2** -- professional PDF memo generation
- **Pandas / NumPy** -- data structuring and computation

---

## Data Integrity Note

All tax parameters -- brackets, rates, deduction amounts, credit thresholds, and phase-out ranges -- are hardcoded from IRS-published authoritative sources and CBO projections. Client data is entered by the user at runtime and is never stored or transmitted. The platform produces planning estimates only and does not constitute a filed return or formal tax opinion.

---

*Built by Prakash Balasubramanian -- Mathematics & Statistics, UMBC | IRS VITA Certified Tax Preparer*
