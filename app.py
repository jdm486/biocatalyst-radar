import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BioCatalyst Radar",
    layout="wide"
)

st.title("BioCatalyst Radar")
st.caption("Private biotech investment intelligence dashboard")

watchlist = pd.read_csv("data/watchlist.csv")

st.sidebar.header("Filters")

category_filter = st.sidebar.multiselect(
    "Category",
    sorted(watchlist["category"].dropna().unique())
)

area_filter = st.sidebar.multiselect(
    "Therapeutic area",
    sorted(watchlist["therapeutic_area"].dropna().unique())
)

filtered = watchlist.copy()

if category_filter:
    filtered = filtered[filtered["category"].isin(category_filter)]

if area_filter:
    filtered = filtered[filtered["therapeutic_area"].isin(area_filter)]

st.subheader("Investment Watchlist")
st.dataframe(filtered, use_container_width=True)

st.divider()

selected_company = st.selectbox(
    "Select a company for deeper review",
    filtered["company"].tolist()
)

company = filtered[filtered["company"] == selected_company].iloc[0]

st.subheader(f"{company['company']} ({company['ticker']})")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Category", company["category"])
    st.metric("Stage", company["stage"])

with col2:
    st.metric("Therapeutic area", company["therapeutic_area"])
    st.metric("Asset", company["asset"])

with col3:
    st.metric("Next catalyst", company["next_catalyst"])
    st.metric("Timing", company["catalyst_timing"])

st.write("## Investment View")
st.info(company["investment_view"])

st.write("## Manual Investment Score")

biology = st.slider("Biology / target validation", 0, 5, 3)
clinical_data = st.slider("Clinical data quality", 0, 5, 3)
catalyst = st.slider("Catalyst quality", 0, 5, 3)
regulatory = st.slider("Regulatory path", 0, 5, 3)
commercial = st.slider("Commercial opportunity", 0, 5, 3)
competition = st.slider("Competitive differentiation", 0, 5, 3)
cash_runway = st.slider("Cash runway / dilution risk", 0, 5, 3)
management_bd = st.slider("Management / BD validation", 0, 5, 3)
valuation = st.slider("Valuation asymmetry", 0, 5, 3)

score = (
    biology * 3
    + clinical_data * 4
    + catalyst * 3
    + regulatory * 2
    + commercial * 2
    + competition * 2
    + cash_runway * 2
    + management_bd * 1
    + valuation * 1
)

score = round(score, 1)

if score >= 80:
    rating = "A — High-conviction watchlist"
elif score >= 70:
    rating = "B — Catalyst watch"
elif score >= 60:
    rating = "C — Speculative / volatile option"
elif score >= 45:
    rating = "D — Avoid unless thesis improves"
else:
    rating = "E — Avoid"

st.metric("Investment score", f"{score}/100")
st.success(rating)

st.write("## Draft Investment Memo")

memo = f"""
### {company['company']} Investment Memo

**Recommendation:** {rating}  
**Score:** {score}/100  
**Category:** {company['category']}  
**Therapeutic area:** {company['therapeutic_area']}  
**Lead asset/platform:** {company['asset']}  
**Stage:** {company['stage']}  
**Next catalyst:** {company['next_catalyst']}  
**Timing:** {company['catalyst_timing']}  

#### Investment thesis
- Is the biology credible?
- Is there promising human data?
- Is there a clear value inflection point?
- Is the company funded through the catalyst?
- Is valuation attractive relative to realistic upside?

#### Key risks
- Clinical efficacy risk
- Safety risk
- Regulatory risk
- Financing / dilution risk
- Competitive differentiation risk
- Commercial adoption risk

#### What would make this more investable?
- Stronger human efficacy data
- Confirmed regulatory pathway
- Financing overhang removed
- Pharma partnership or external validation
- Valuation pullback without thesis breaking

#### What would break the thesis?
- Failed or ambiguous clinical readout
- Safety signal
- Trial delay
- Discounted financing before catalyst
- Competitor data materially better
"""

st.markdown(memo)
