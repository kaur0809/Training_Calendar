import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
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

st.markdown("""
### 📚University Training Planning Dashboard
Monitor trainer allocation, delivery hours, student coverage and program execution.
""")

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

total_batches = filtered_df["No. of batches"].sum()

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
#-------------
# CHART1

hours_df = (
    filtered_df.groupby("University")["Delivery hrs"]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    hours_df,
    x="University",
    y="Delivery hrs",
    title="Training Hours by University",
    color_discrete_sequence=["#7C3AED"]
)

fig1.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#374151"),
    title_font_size=18
)



#====
#CHART2

trainer_df = (
    filtered_df.groupby("Mapped Trainers")["Delivery hrs"]
    .sum()
    .reset_index()
)

fig2 = px.bar(
    trainer_df,
    x="Mapped Trainers",
    y="Delivery hrs",
    title="Trainer Workload",
    color_discrete_sequence=["#4C1D95"]
)

fig2.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#374151"),
    title_font_size=18
)

###====SHOW SIDE BY SIDE

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

#=====CHART3

student_df = (
    filtered_df.groupby("University")["No of students"]
    .sum()
    .reset_index()
)

fig3 = px.pie(
    student_df,
    names="University",
    values="No of students",
    title="Student Distribution"
)

fig3.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#374151"),
    title_font_size=18
)

st.plotly_chart(fig3, use_container_width=True)

#======
total_programs = filtered_df["Program"].nunique()
total_trainers = filtered_df["Mapped Trainers"].nunique()


#CALENDAR


st.subheader("Training Timeline")

calendar_options = {
    "initialView": "dayGridMonth",
    "height": 700
}

calendar(
    events=events,
    options=calendar_options,
    key="timeline"
)

## SUMMARY TABLE
st.subheader("University Summary")

summary_df = (
    filtered_df
    .groupby("University")
    .agg({
        "Program": "nunique",
        "No of students": "sum",
        "Delivery hrs": "sum"
    })
    .reset_index()
)

summary_df.columns = [
    "University",
    "Programs",
    "Students",
    "Training Hours"
]

st.dataframe(
    summary_df,
    use_container_width=True
)

### CREATE EVENTS 
events = []

for _, row in filtered_df.iterrows():

    start = pd.to_datetime(row["Start date"])
    end = pd.to_datetime(row["Closing date"])

    events.append({
        "title": f"{row['University']} | {row['Program']}",
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "backgroundColor": "#7C3AED",
        "borderColor": "#4C1D95"
    })

