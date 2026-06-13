import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BioCatalyst Radar",
    layout="wide"
)

st.title("BioCatalyst Radar")
st.caption("Private biotech investment intelligence dashboard")

# -----------------------------
# Load data
# -----------------------------
watchlist = pd.read_csv("data/watchlist.csv")
scores = pd.read_csv("data/scores.csv")

df = watchlist.merge(scores, on="ticker", how="left")

# -----------------------------
# Score calculation
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


df["investment_score"] = df.apply(calculate_score, axis=1)
df["rating"] = df["investment_score"].apply(get_rating)

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

# -----------------------------
# Top dashboard
# -----------------------------
st.subheader("Top Investment Watchlist")

summary_cols = [
    "ticker",
    "company",
    "category",
    "therapeutic_area",
    "stage",
    "next_catalyst",
    "catalyst_timing",
    "investment_score",
    "rating",
    "analyst_view",
]

st.dataframe(
    filtered[summary_cols].sort_values("investment_score", ascending=False),
    use_container_width=True,
    hide_index=True
)

st.divider()

# -----------------------------
# Company deep dive
# -----------------------------
selected_company = st.selectbox(
    "Select a company for deeper review",
    filtered["company"].tolist()
)

company = filtered[filtered["company"] == selected_company].iloc[0]

st.subheader(f"{company['company']} ({company['ticker']})")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Investment score", f"{company['investment_score']}/100")

with col2:
    st.metric("Rating", company["rating"])

with col3:
    st.metric("Stage", company["stage"])

with col4:
    st.metric("Next catalyst", company["catalyst_timing"])

st.write("## Company Snapshot")

snap1, snap2, snap3 = st.columns(3)

with snap1:
    st.write("**Category**")
    st.write(company["category"])
    st.write("**Therapeutic area**")
    st.write(company["therapeutic_area"])

with snap2:
    st.write("**Asset / platform**")
    st.write(company["asset"])
    st.write("**Next catalyst**")
    st.write(company["next_catalyst"])

with snap3:
    st.write("**Investment view**")
    st.info(company["investment_view"])

st.write("## Analyst View")
st.warning(company["analyst_view"])

# -----------------------------
# Score breakdown
# -----------------------------
st.write("## Score Breakdown")

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
        "Score out of 5": [
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
    score_breakdown["Score out of 5"] / 5 * score_breakdown["Weight"]
).round(1)

st.dataframe(score_breakdown, use_container_width=True, hide_index=True)

# -----------------------------
# Manual scenario adjustment
# -----------------------------
st.write("## Scenario Test")

st.caption("Adjust the assumptions below to see how the rating changes.")

biology = st.slider("Biology / target validation", 0, 5, int(company["biology"]))
clinical_data = st.slider("Clinical data quality", 0, 5, int(company["clinical_data"]))
catalyst = st.slider("Catalyst quality", 0, 5, int(company["catalyst"]))
regulatory = st.slider("Regulatory path", 0, 5, int(company["regulatory"]))
commercial = st.slider("Commercial opportunity", 0, 5, int(company["commercial"]))
competition = st.slider("Competitive differentiation", 0, 5, int(company["competition"]))
cash_runway = st.slider("Cash runway / dilution risk", 0, 5, int(company["cash_runway"]))
management_bd = st.slider("Management / BD validation", 0, 5, int(company["management_bd"]))
valuation = st.slider("Valuation asymmetry", 0, 5, int(company["valuation"]))

scenario_score = round(
    biology * 3
    + clinical_data * 4
    + catalyst * 3
    + regulatory * 2
    + commercial * 2
    + competition * 2
    + cash_runway * 2
    + management_bd * 1
    + valuation * 1,
    1,
)

scenario_rating = get_rating(scenario_score)

st.metric("Scenario score", f"{scenario_score}/100")
st.success(scenario_rating)

# -----------------------------
# Investment memo
# -----------------------------
st.write("## Draft Investment Memo")

memo = f"""
# {company['company']} ({company['ticker']}) — Investment Memo

## Recommendation
{company['rating']}

## Investment Score
{company['investment_score']}/100

## Company Overview
- **Category:** {company['category']}
- **Therapeutic area:** {company['therapeutic_area']}
- **Lead asset/platform:** {company['asset']}
- **Stage:** {company['stage']}

## Key Catalyst
- **Catalyst:** {company['next_catalyst']}
- **Timing:** {company['catalyst_timing']}

## Current Investment View
{company['investment_view']}

## Analyst View
{company['analyst_view']}

## Investment Thesis
- Assess whether the biology is credible and clinically validated.
- Determine whether existing human data are strong enough to support further upside.
- Evaluate whether the next catalyst is meaningful enough to change valuation.
- Check whether the company is funded through the next major catalyst.
- Compare current valuation against realistic upside and downside cases.

## Key Risks
- Clinical efficacy risk
- Safety risk
- Regulatory risk
- Financing / dilution risk
- Competitive differentiation risk
- Commercial adoption risk

## What Would Make This More Investable?
- Stronger human efficacy data
- Confirmed regulatory pathway
- Financing overhang removed
- Pharma partnership or external validation
- Valuation pullback without thesis breaking

## What Would Break the Thesis?
- Failed or ambiguous clinical readout
- Safety signal
- Trial delay
- Discounted financing before catalyst
- Competitor data materially better
"""

st.markdown(memo)

st.download_button(
    label="Download memo",
    data=memo,
    file_name=f"{company['ticker']}_investment_memo.md",
    mime="text/markdown"
)
