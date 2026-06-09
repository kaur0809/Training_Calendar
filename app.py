import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Training Resource Dashboard",
    page_icon="📚",
    layout="wide"
)

# =====================================================
# THEME
# =====================================================

st.markdown("""
<style>

/* App Background */
.stApp{
    background-color:#F8F9FC;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background-color:#4C1D95;
}

[data-testid="stSidebar"] *{
    color:white;
}

/* Headers */
h1,h2,h3{
    color:#374151;
}

/* KPI Cards */
[data-testid="stMetric"]{
    background:white;
    border-radius:12px;
    padding:15px;
    border-left:5px solid #7C3AED;
    box-shadow:0px 2px 6px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================

st.title("📚 Training Resource Management Dashboard")

# =====================================================
# FILE UPLOADER
# =====================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload Training Dataset",
    type=["xlsx", "csv"]
)

if uploaded_file is None:
    st.warning("Please upload your training dataset.")
    st.stop()

# =====================================================
# LOAD DATA
# =====================================================

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# Debug columns
st.write("Columns in uploaded file:")
st.write(df.columns.tolist())


# =====================================================
# DATE CONVERSION
# =====================================================

df["Start date"] = pd.to_datetime(df["Start date"])
df["Closing date"] = pd.to_datetime(df["Closing date"])

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Filters")

university_filter = st.sidebar.multiselect(
    "University",
    options=sorted(df["University"].dropna().unique()),
    default=sorted(df["University"].dropna().unique())
)

program_filter = st.sidebar.multiselect(
    "Program",
    options=sorted(df["Program"].dropna().unique()),
    default=sorted(df["Program"].dropna().unique())
)

trainer_filter = st.sidebar.multiselect(
    "Mapped Trainers",
    options=sorted(df["Mapped Trainers"].dropna().unique()),
    default=sorted(df["Mapped Trainers"].dropna().unique())
)

# =====================================================
# FILTER DATA
# =====================================================

filtered_df = df[
    (df["University"].isin(university_filter))
    &
    (df["Program"].isin(program_filter))
    &
    (df["Mapped Trainers"].isin(trainer_filter))
]

# =====================================================
# KPI SECTION
# =====================================================

total_universities = filtered_df["University"].nunique()

total_batches = filtered_df["Batch details"].nunique()

total_students = filtered_df["No of students"].sum()

total_hours = filtered_df["Delivery hrs"].sum()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Universities",
        total_universities
    )

with c2:
    st.metric(
        "Batches",
        total_batches
    )

with c3:
    st.metric(
        "Students",
        int(total_students)
    )

with c4:
    st.metric(
        "Training Hours",
        round(total_hours, 1)
    )

# =====================================================
# DATA SUMMARY
# =====================================================

st.subheader("Dataset Summary")

summary_cols = [
    "University",
    "Program",
    "Semester",
    "Batch details",
    "Mapped Trainers",
    "Delivery hrs",
    "No of students",
    "Start date",
    "Closing date"
]

available_cols = [c for c in summary_cols if c in filtered_df.columns]

st.dataframe(
    filtered_df[available_cols],
    use_container_width=True,
    height=500
)

# =====================================================
# FOOTER
# =====================================================

st.caption(
    f"Showing {len(filtered_df)} records"
)
