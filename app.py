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
.fc {
    background: white;
    border-radius: 18px;
    padding: 15px;
    box-shadow: 0px 4px 12px rgba(124,58,237,0.10);
}

.fc-toolbar-title{
    color:#4C1D95 !important;
    font-weight:700 !important;
}

.fc-event{
    border-radius:8px !important;
    border:none !important;
    font-size:12px !important;
}

.fc-daygrid-event{
    padding:4px !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================

st.markdown("""
<div style="
background:#4C1D95;
padding:15px 25px;
border-radius:15px;
margin-bottom:20px;
color:white;
">
<h2 style="margin:0;">🎓 Training Delivery Calendar</h2>
<p style="margin:0;">Operations Dashboard</p>
</div>
""", unsafe_allow_html=True)

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
total_programs = filtered_df["Program"].nunique()
total_trainers = filtered_df["Mapped Trainers"].nunique()
total_students = filtered_df["No of students"].sum()
total_hours = filtered_df["Delivery hrs"].sum()

k1, k2, k3, k4, k5 = st.columns(5)

cards = [
    ("🏫", total_universities, "Universities", "#7C3AED"),
    ("📚", total_programs, "Programs", "#22C55E"),
    ("👨‍🏫", total_trainers, "Trainers", "#F59E0B"),
    ("🎓", int(total_students), "Students", "#3B82F6"),
    ("⏱", round(total_hours,1), "Delivery Hrs", "#EF4444")
]

for col, card in zip([k1,k2,k3,k4,k5], cards):

    icon, value, label, color = card

    with col:

        st.markdown(f"""
        <div style="
        background:white;
        padding:20px;
        border-radius:18px;
        box-shadow:0 2px 12px rgba(0,0,0,0.05);
        border-top:4px solid {color};
        ">
            <div style="font-size:24px;">{icon}</div>
            <h1 style="margin:0;">{value}</h1>
            <p style="color:gray;margin:0;">{label}</p>
        </div>
        """, unsafe_allow_html=True)

# =====================================================

# CHART 1 - UNIVERSITY HOURS

# =====================================================

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
title_font_size=18,
xaxis_tickangle=-30
)

# =====================================================

# CHART 2 - TRAINER WORKLOAD

# =====================================================

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

# =====================================================

# DISPLAY CHARTS SIDE BY SIDE

# =====================================================

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)
# =====================================================

# CHART 3 - STUDENT DISTRIBUTION

# =====================================================

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


# =====================================================
# CALENDAR EVENTS
# =====================================================

from datetime import timedelta

events = []

for _, row in filtered_df.iterrows():

    start_date = pd.to_datetime(row["Start date"])
    end_date = pd.to_datetime(row["Closing date"])

    class_day = str(row["CLASS DAYS"]).upper()
    class_time = str(row["CLASS TIME"])

    # ONLINE = GREEN
    if str(row["Delivery mode"]).upper() == "ONLINE":

        bg_color = "#22C55E"
        border_color = "#16A34A"

    # OFFLINE = BLUE
    else:

        bg_color = "#3B82F6"
        border_color = "#2563EB"

    day_map = {
        "MONDAY": 0,
        "TUESDAY": 1,
        "WEDNESDAY": 2,
        "THURSDAY": 3,
        "FRIDAY": 4,
        "SATURDAY": 5,
        "SUNDAY": 6
    }

    target_day = day_map.get(class_day)

    current = start_date

    while current <= end_date:

        if current.weekday() == target_day:

            start_dt = pd.to_datetime(
                f"{current.date()} {class_time}"
            )

            end_dt = start_dt + timedelta(hours=2)

            events.append({
                "title": f"{row['Program']} | {row['Mapped Trainers']}",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),

                "backgroundColor": bg_color,
                "borderColor": border_color,
                "textColor": "white"
            })

        current += timedelta(days=1)

#========= Online/offline marker

st.markdown("""
🟢 **Online Classes** &nbsp;&nbsp;&nbsp;
🔵 **Offline Classes**
""")
# =====================================================
# =====================================================
# TRAINING TIMELINE
# =====================================================

calendar_col, schedule_col = st.columns([4,1])

with calendar_col:

    calendar_options = {
        "initialView": "dayGridMonth",
        "height": 850,

        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },

        "eventDisplay": "block"
    }

    calendar_state = calendar(
        events=events,
        options=calendar_options,
        key="timeline"
    )

with schedule_col:

    st.subheader("📋 Event Details")

    if calendar_state.get("eventClick"):

        selected = calendar_state["eventClick"]["event"]

        st.markdown(f"""
        <div style="
        background:white;
        padding:20px;
        border-radius:18px;
        box-shadow:0px 2px 10px rgba(0,0,0,0.05);
        margin-bottom:15px;
        ">
            <h3>{selected.get('title','Class')}</h3>

            <p><b>Start:</b><br>
            {selected.get('start','')}</p>

            <p><b>End:</b><br>
            {selected.get('end','')}</p>

        </div>
        """, unsafe_allow_html=True)

    else:

        st.info(
            "Click a class in the calendar to view details."
        )
# =====================================================

# UNIVERSITY SUMMARY

# =====================================================

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
 #======== 
# TRAINER ALLOCATION MATRIX

st.subheader("👨‍🏫 Trainer Allocation Matrix")

allocation_df = filtered_df[
    [
        "Mapped Trainers",
        "University",
        "Program",
        "Batch details",
        "Delivery hrs"
    ]
]

st.dataframe(
    allocation_df,
    use_container_width=True,
    height=400
)

#========== TRAINER UTILIZATION

st.subheader("📊 Trainer Utilization")

trainer_util = (
    filtered_df
    .groupby("Mapped Trainers")["Delivery hrs"]
    .sum()
    .reset_index()
    .sort_values(
        "Delivery hrs",
        ascending=False
    )
)

st.dataframe(
    trainer_util,
    use_container_width=True
)


#=========Workload


MAX_HOURS = 80

trainer_util["Status"] = trainer_util["Delivery hrs"].apply(
    lambda x: "🔴 Overloaded"
    if x > MAX_HOURS
    else "🟢 Available"
)

st.subheader("⚠ Trainer Capacity Status")

st.dataframe(
    trainer_util,
    use_container_width=True
)

# =====================================================

# DOWNLOAD BUTTON

# =====================================================

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
  label="📥 Download Filtered Data",
   data=csv,
  file_name="training_data.csv",
  mime="text/csv"
)

# =====================================================

# DETAILED DATASET

# =====================================================

st.subheader("Detailed Training Dataset")

st.dataframe(
  filtered_df,
   use_container_width=True,
   height=600
)

st.caption(
f"Showing {len(filtered_df)} records"
)
