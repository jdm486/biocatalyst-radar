import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BioCatalyst Radar",
    layout="wide"
)

# -----------------------------
# Load data
# -----------------------------
watchlist = pd.read_csv("data/watchlist.csv")
scores = pd.read_csv("data/scores.csv")

df = watchlist.merge(scores, on="ticker", how="left")

# -----------------------------
# Scoring logic
# -----------------------------
def calculate_score(row):
    return round(
        row["biology"] * 3
        + row["clinical_data"] * 4
        + row["catalyst"] * 3
        + row["regulatory"] * 2
        + row["commercial"] * 2
        + row["competition"] * 2
        + row["cash_runway"] * 2
        + row["management_bd"] * 1
        + row["valuation"] * 1,
        1,
    )


def get_rating(score):
    if score >= 80:
        return "A — High-conviction watchlist"
    elif score >= 70:
        return "B — Catalyst watch"
    elif score >= 60:
        return "C — Speculative / volatile option"
    elif score >= 45:
        return "D — Avoid unless thesis improves"
    else:
        return "E — Avoid"


def get_action(rating):
    if rating.startswith("A"):
        return "Prioritise for deep diligence"
    elif rating.startswith("B"):
        return "Track closely around catalyst"
    elif rating.startswith("C"):
        return "Keep on volatile watchlist"
    elif rating.startswith("D"):
        return "Do not prioritise yet"
    else:
        return "Avoid for now"


df["investment_score"] = df.apply(calculate_score, axis=1)
df["rating"] = df["investment_score"].apply(get_rating)
df["suggested_action"] = df["rating"].apply(get_action)

# -----------------------------
# Header
# -----------------------------
st.title("BioCatalyst Radar")
st.caption("Biotech and health-tech investment intelligence dashboard")

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

category_filter = st.sidebar.multiselect(
    "Category",
    sorted(df["category"].dropna().unique())
)

area_filter = st.sidebar.multiselect(
    "Therapeutic area",
    sorted(df["therapeutic_area"].dropna().unique())
)

rating_filter = st.sidebar.multiselect(
    "Rating",
    sorted(df["rating"].dropna().unique())
)

filtered = df.copy()

if category_filter:
    filtered = filtered[filtered["category"].isin(category_filter)]

if area_filter:
    filtered = filtered[filtered["therapeutic_area"].isin(area_filter)]

if rating_filter:
    filtered = filtered[filtered["rating"].isin(rating_filter)]

filtered = filtered.sort_values("investment_score", ascending=False)

# -----------------------------
# Dashboard summary
# -----------------------------
st.subheader("Investment Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Companies tracked", len(filtered))

with col2:
    st.metric(
        "Highest score",
        f"{filtered['investment_score'].max()}/100"
    )

with col3:
    top_company = filtered.iloc[0]["ticker"] if len(filtered) > 0 else "N/A"
    st.metric("Top-ranked company", top_company)

with col4:
    priority_count = filtered[filtered["investment_score"] >= 70].shape[0]
    st.metric("Priority watchlist", priority_count)

st.divider()

# -----------------------------
# Top investment watchlist
# -----------------------------
st.subheader("Top Investment Watchlist")

st.caption(
    "Ranked view of companies based on clinical quality, catalyst strength, regulatory path, cash runway, differentiation and valuation asymmetry."
)

watchlist_cols = [
    "ticker",
    "company",
    "category",
    "therapeutic_area",
    "stage",
    "next_catalyst",
    "catalyst_timing",
    "investment_score",
    "rating",
    "suggested_action",
    "analyst_view",
]

st.dataframe(
    filtered[watchlist_cols],
    use_container_width=True,
    hide_index=True,
    height=360
)

st.divider()

# -----------------------------
# Priority names
# -----------------------------
st.subheader("Priority Names to Review")

priority_df = filtered[filtered["investment_score"] >= 70]

if len(priority_df) > 0:
    for _, row in priority_df.iterrows():
        with st.expander(f"{row['ticker']} — {row['company']} | {row['rating']}"):
            st.write(f"**Score:** {row['investment_score']}/100")
            st.write(f"**Next catalyst:** {row['next_catalyst']} ({row['catalyst_timing']})")
            st.write(f"**Suggested action:** {row['suggested_action']}")
            st.warning(row["analyst_view"])
else:
    st.info("No companies currently score above 70.")

st.divider()

# -----------------------------
# Company deep dive
# -----------------------------
st.subheader("Company Deep Dive")

selected_company = st.selectbox(
    "Select company",
    filtered["company"].tolist()
)

company = filtered[filtered["company"] == selected_company].iloc[0]

st.write(f"## {company['company']} ({company['ticker']})")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Investment score", f"{company['investment_score']}/100")

with col2:
    st.metric("Rating", company["rating"])

with col3:
    st.metric("Stage", company["stage"])

with col4:
    st.metric("Catalyst timing", company["catalyst_timing"])

st.write("### Investment View")
st.info(company["investment_view"])

st.write("### Analyst View")
st.warning(company["analyst_view"])

st.write("### Key Company Details")

detail1, detail2, detail3 = st.columns(3)

with detail1:
    st.write("**Category**")
    st.write(company["category"])
    st.write("**Therapeutic area**")
    st.write(company["therapeutic_area"])

with detail2:
    st.write("**Asset / platform**")
    st.write(company["asset"])
    st.write("**Stage**")
    st.write(company["stage"])

with detail3:
    st.write("**Next catalyst**")
    st.write(company["next_catalyst"])
    st.write("**Suggested action**")
    st.write(company["suggested_action"])

st.divider()

# -----------------------------
# Score breakdown
# -----------------------------
st.subheader("Score Breakdown")

score_breakdown = pd.DataFrame(
    {
        "Factor": [
            "Biology / target validation",
            "Clinical data quality",
            "Catalyst quality",
            "Regulatory path",
            "Commercial opportunity",
            "Competitive differentiation",
            "Cash runway / dilution risk",
            "Management / BD validation",
            "Valuation asymmetry",
        ],
        "Raw score out of 5": [
            company["biology"],
            company["clinical_data"],
            company["catalyst"],
            company["regulatory"],
            company["commercial"],
            company["competition"],
            company["cash_runway"],
            company["management_bd"],
            company["valuation"],
        ],
        "Weight": [
            15,
            20,
            15,
            10,
            10,
            10,
            10,
            5,
            5,
        ],
    }
)

score_breakdown["Weighted score"] = (
    score_breakdown["Raw score out of 5"] / 5 * score_breakdown["Weight"]
).round(1)

st.dataframe(
    score_breakdown,
    use_container_width=True,
    hide_index=True
)

st.write("### Interpretation")

lowest_factors = score_breakdown.sort_values("Weighted score").head(3)
highest_factors = score_breakdown.sort_values("Weighted score", ascending=False).head(3)

left, right = st.columns(2)

with left:
    st.write("**Strongest areas**")
    for _, row in highest_factors.iterrows():
        st.write(f"- {row['Factor']}: {row['Raw score out of 5']}/5")

with right:
    st.write("**Weakest areas / diligence focus**")
    for _, row in lowest_factors.iterrows():
        st.write(f"- {row['Factor']}: {row['Raw score out of 5']}/5")

st.divider()

# -----------------------------
# Investment memo
# -----------------------------
st.subheader("Draft Investment Memo")

memo = f"""
# {company['company']} ({company['ticker']}) — Investment Memo

## Recommendation
{company['rating']}

## Investment Score
{company['investment_score']}/100

## Suggested Action
{company['suggested_action']}

## Company Overview
- Category: {company['category']}
- Therapeutic area: {company['therapeutic_area']}
- Lead asset/platform: {company['asset']}
- Stage: {company['stage']}

## Key Catalyst
- Catalyst: {company['next_catalyst']}
- Timing: {company['catalyst_timing']}

## Investment View
{company['investment_view']}

## Analyst View
{company['analyst_view']}

## Score Breakdown
- Biology / target validation: {company['biology']}/5
- Clinical data quality: {company['clinical_data']}/5
- Catalyst quality: {company['catalyst']}/5
- Regulatory path: {company['regulatory']}/5
- Commercial opportunity: {company['commercial']}/5
- Competitive differentiation: {company['competition']}/5
- Cash runway / dilution risk: {company['cash_runway']}/5
- Management / BD validation: {company['management_bd']}/5
- Valuation asymmetry: {company['valuation']}/5

## Diligence Questions
- Is the biology and mechanism credible?
- Is the available clinical data strong enough to justify investment risk?
- Is the next catalyst meaningful enough to change valuation?
- Is the company funded through the next catalyst?
- Is the asset differentiated enough versus competitors?
- Is the current valuation attractive relative to realistic upside?
- What would break the investment thesis?

## Key Risks
- Clinical efficacy risk
- Safety risk
- Regulatory risk
- Financing / dilution risk
- Competitive differentiation risk
- Commercial adoption risk
"""

st.markdown(memo)

st.download_button(
    label="Download memo",
    data=memo,
    file_name=f"{company['ticker']}_investment_memo.md",
    mime="text/markdown"
)
