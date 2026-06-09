import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Training Delivery Calendar Dashboard",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Training Delivery Calendar Dashboard")

# ---------------------------------------------------
# MOCK DATA GENERATOR
# ---------------------------------------------------
def generate_mock_data():

    today = datetime.today()

    data = {
        "University Name": [
            "Jain University",
            "Jain University",
            "Christ University",
            "Christ University",
            "Amity University",
            "Amity University",
            "LPU",
            "LPU"
        ],

        "Program/Subject": [
            "Machine Learning",
            "Data Science",
            "Python",
            "AI",
            "Power BI",
            "SQL",
            "Machine Learning",
            "Python"
        ],

        "Trainer Name": [
            "Tanvi",
            "Rahul",
            "Amit",
            "Sneha",
            "Karan",
            "Priya",
            "Tanvi",
            "Rahul"
        ],

        "Number of Classes Scheduled": [
            1,1,1,1,1,1,1,1
        ],

        "Class Date": [
            today,
            today + timedelta(days=1),
            today + timedelta(days=2),
            today + timedelta(days=3),
            today + timedelta(days=4),
            today + timedelta(days=5),
            today + timedelta(days=6),
            today + timedelta(days=7)
        ],

        "Class Time": [
            "09:00",
            "11:00",
            "10:00",
            "14:00",
            "15:00",
            "13:00",
            "09:30",
            "16:00"
        ],

        "Duration Hours": [
            2,
            3,
            2,
            2.5,
            3,
            2,
            4,
            2
        ],

        "Batch Details": [
            "BCA-1",
            "MCA-1",
            "BCA-2",
            "MBA-1",
            "BCA-3",
            "MCA-2",
            "MBA-2",
            "BCA-4"
        ]
    }

    return pd.DataFrame(data)


# ---------------------------------------------------
# FILE UPLOADER
# ---------------------------------------------------
uploaded_file = st.sidebar.file_uploader(
    "Upload Training Schedule",
    type=["csv", "xlsx"]
)

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

else:
    st.info("No file uploaded. Using demo dataset.")
    df = generate_mock_data()

# ---------------------------------------------------
# DATETIME HANDLING
# ---------------------------------------------------
df["Class Date"] = pd.to_datetime(df["Class Date"])

df["Start"] = pd.to_datetime(
    df["Class Date"].dt.strftime("%Y-%m-%d")
    + " "
    + df["Class Time"].astype(str)
)

df["End"] = (
    df["Start"]
    + pd.to_timedelta(df["Duration Hours"], unit="h")
)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.header("Filters")

university_filter = st.sidebar.multiselect(
    "University",
    options=sorted(df["University Name"].unique()),
    default=sorted(df["University Name"].unique())
)

trainer_filter = st.sidebar.multiselect(
    "Trainer",
    options=sorted(df["Trainer Name"].unique()),
    default=sorted(df["Trainer Name"].unique())
)

program_filter = st.sidebar.multiselect(
    "Program",
    options=sorted(df["Program/Subject"].unique()),
    default=sorted(df["Program/Subject"].unique())
)

filtered_df = df[
    (df["University Name"].isin(university_filter))
    &
    (df["Trainer Name"].isin(trainer_filter))
    &
    (df["Program/Subject"].isin(program_filter))
]

# ---------------------------------------------------
# HORIZON FILTER
# ---------------------------------------------------
st.subheader("Schedule Horizon")

h1, h2, h3 = st.columns(3)

today = pd.Timestamp.today().normalize()

with h1:
    today_btn = st.button("📌 Today")

with h2:
    week_btn = st.button("📅 This Week")

with h3:
    month_btn = st.button("🗓 This Month")

view_df = filtered_df.copy()

if today_btn:

    view_df = filtered_df[
        filtered_df["Class Date"].dt.date
        == today.date()
    ]

elif week_btn:

    week_end = today + pd.Timedelta(days=7)

    view_df = filtered_df[
        (filtered_df["Class Date"] >= today)
        &
        (filtered_df["Class Date"] <= week_end)
    ]

elif month_btn:

    month_end = today + pd.offsets.MonthEnd(1)

    view_df = filtered_df[
        (filtered_df["Class Date"] >= today)
        &
        (filtered_df["Class Date"] <= month_end)
    ]

# ---------------------------------------------------
# KPI METRICS
# ---------------------------------------------------
st.subheader("Training Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total Classes",
        len(view_df)
    )

with c2:
    st.metric(
        "Universities",
        view_df["University Name"].nunique()
    )

with c3:
    st.metric(
        "Active Trainers",
        view_df["Trainer Name"].nunique()
    )

with c4:
    st.metric(
        "Training Hours",
        round(view_df["Duration Hours"].sum(), 1)
    )

# ---------------------------------------------------
# CALENDAR EVENTS
# ---------------------------------------------------
events = []

for _, row in view_df.iterrows():

    events.append({
        "title": f"{row['Program/Subject']} | {row['Trainer Name']}",
        "start": row["Start"].isoformat(),
        "end": row["End"].isoformat()
    })

# ---------------------------------------------------
# CALENDAR VIEW
# ---------------------------------------------------
st.subheader("Training Calendar")

calendar_options = {
    "initialView": "dayGridMonth",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "height": 700
}

calendar_state = calendar(
    events=events,
    options=calendar_options,
    key="training_calendar"
)

# ---------------------------------------------------
# CLICKED EVENT DETAILS
# ---------------------------------------------------
if calendar_state.get("eventClick"):

    clicked = calendar_state["eventClick"]["event"]

    st.success("Selected Session")

    st.write(clicked)

# ---------------------------------------------------
# RAW DATA VIEW
# ---------------------------------------------------
st.subheader("Detailed Schedule")

display_cols = [
    "University Name",
    "Program/Subject",
    "Trainer Name",
    "Class Date",
    "Class Time",
    "Duration Hours",
    "Batch Details"
]

st.dataframe(
    view_df[display_cols],
    use_container_width=True,
    height=450
)
