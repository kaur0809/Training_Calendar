import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Training Calendar",
    page_icon="📚",
    layout="wide"
)

# =====================================================
# PURPLE THEME
# =====================================================

st.markdown("""
<style>

.stApp{
    background-color:#F8F9FC;
}

[data-testid="stSidebar"]{
    background-color:#4C1D95;
}

[data-testid="stSidebar"] *{
    color:white;
}

h1,h2,h3{
    color:#374151;
}

[data-testid="stMetric"]{
    background:white;
    border-radius:12px;
    padding:15px;
    border-left:5px solid #7C3AED;
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
    st.info("Upload your Excel file to begin.")
    st.stop()

# =====================================================
# LOAD DATA
# =====================================================

try:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        # Load first sheet
        df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace("  ", " ", regex=False)
    )

except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

# =====================================================
# DEBUG SECTION
# =====================================================

with st.expander("🔍 Debug Columns"):

    st.write("Columns detected in Excel:")
    st.write(df.columns.tolist())

# =====================================================
# REQUIRED COLUMNS
# =====================================================

required_cols = [
    "University",
    "Program",
    "Semester",
    "Batch details",
    "Mapped Trainers",
    "Delivery hrs",
    "No of students"
]

missing_cols = [
    col for col in required_cols
    if col not in df.columns
]

if missing_cols:

    st.error(
        f"Missing columns: {missing_cols}"
    )

    st.write("Detected Columns:")
    st.write(df.columns.tolist())

    st.stop()

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
# SAFE NUMERIC CONVERSION
# =====================================================

filtered_df["Delivery hrs"] = pd.to_numeric(
    filtered_df["Delivery hrs"],
    errors="coerce"
)

filtered_df["No of students"] = pd.to_numeric(
    filtered_df["No of students"],
    errors="coerce"
)

# =====================================================
# KPI SECTION
# =====================================================

st.subheader("Training Overview")

total_universities = filtered_df["University"].nunique()

total_batches = filtered_df["Batch details"].nunique()

total_students = filtered_df["No of students"].sum()

total_hours = filtered_df["Delivery hrs"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Universities",
    total_universities
)

c2.metric(
    "Batches",
    total_batches
)

c3.metric(
    "Students",
    int(total_students)
)

c4.metric(
    "Training Hours",
    round(total_hours, 1)
)

# =====================================================
# DATA TABLE
# =====================================================

st.subheader("Training Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=600
)

# =====================================================
# FOOTER
# =====================================================

st.caption(
    f"Showing {len(filtered_df)} records"
)
