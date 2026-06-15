import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import base64

# =============================================================================
# ENVIRONMENT & APPLICATION LAYOUT CONFIGURATION
# =============================================================================
st.set_page_config(page_title="Training Resource Management Dashboard", layout="wide")

# Link critical system UI icon components
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
    unsafe_allow_html=True
)

# Global UI stylesheets and dashboard structural theme overrides
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    
    .title-container {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 5px;
    }
    .main-title { font-size: 32px; font-weight: 700; color: #1E293B; margin: 0; }
    .sub-title { font-size: 15px; color: #64748B; margin-top: 5px; margin-bottom: 25px; }
    .section-header { font-size: 20px; font-weight: 600; color: #1E293B; margin-top: 20px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
    
    .filter-header { 
        font-size: 14px; 
        font-weight: 600; 
        color: #475569;
        margin-bottom: 8px; 
        display: flex; 
        align-items: center; 
    }
    .icon-spacing { margin-right: 8px; color: #0EA5E9; font-size: 16px; }
    .custom-icon { width: 22px; height: 22px; margin-right: 8px; object-fit: contain; }
    .main-header-icon { width: 42px; height: 42px; object-fit: contain; }
    
    .todo-box {
        padding: 18px 22px;
        border-radius: 12px;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #0EA5E9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 14px;
    }
    .todo-title { font-size: 17px; font-weight: 600; color: #0F172A; margin: 0 0 6px 0; display: flex; align-items: center; gap: 8px; }
    .todo-meta { font-size: 13px; color: #64748B; margin: 0 0 8px 0; }
    .todo-status { font-size: 13px; font-weight: 600; margin: 0; display: flex; align-items: center; gap: 6px; }
    
    .kpi-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.04);
        border: 1px solid #E2E8F0;
        text-align: left;
        margin-bottom: 12px;
    }
    .kpi-title { font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.75px; }
    .kpi-value { font-size: 24px; color: #0F172A; font-weight: 700; margin-top: 4px; }
    .kpi-subtext { font-size: 12px; color: #475569; margin-top: 4px; line-height: 1.4; }
    
    .fc-theme-standard .fc-scrollgrid { border-color: #E2E8F0 !important; background-color: #FFFFFF; }
    .fc-header-toolbar .fc-button-primary { background-color: #0EA5E9 !important; border-color: #0EA5E9 !important; font-weight: 500 !important; }
    .fc-header-toolbar .fc-button-primary:hover { background-color: #0284C7 !important; border-color: #0284C7 !important; }
    .fc .fc-daygrid-day.fc-day-today { background-color: #F0F9FF !important; }
    
    .legend-wrapper { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 12px; padding: 10px 0; }
    .legend-item { display: flex; align-items: center; font-size: 13px; font-weight: 600; color: #334155; }
    .legend-color-box { width: 14px; height: 14px; border-radius: 3px; margin-right: 6px; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA FILE & ASSETS IO PIPELINE
# =============================================================================
def load_binary_asset(file_path):
    try:
        with open(file_path, "rb") as asset_file:
            return base64.b64encode(asset_file.read()).decode()
    except IOError:
        return ""

BRAND_ICON_B64 = load_binary_asset("image_1134f1.png")
COURSE_ICON_B64 = load_binary_asset("image_2b21c2.png")
FACULTY_ICON_B64 = load_binary_asset("image_2b217d.png")

def create_schema_blueprint():
    return pd.DataFrame(columns=[
        "Task ID", "Task Name", "University", "Course", 
        "Trainer", "Date", "Total Allocated Hours", "Completed Hours", "Remaining Hours"
    ])

def normalize_ingested_dataset(raw_dataframe):
    working_df = raw_dataframe.copy()
    working_df.columns = working_df.columns.astype(str).str.strip().str.lower()
    
    schema_mapping = {
        'Task ID': ['task id', 'id', 'task_id', 'sr no', 'sr. no.', 'index'],
        'Task Name': ['task name', 'task', 'title', 'event', 'assignment', 'task_name', 'name', 'todo', 'to do'],
        'University': ['university', 'univ', 'college', 'institution', 'school', 'varsity'],
        'Course': ['course', 'subject', 'program', 'class', 'branch'],
        'Trainer': ['trainer', 'trainer name', 'instructor', 'teacher', 'professor', 'faculty', 'dr.', 'mentor', 'trainers'],
        'Date': ['date', 'task date', 'due date', 'schedule date', 'timeline', 'day', 'timestamp'],
        'Total Allocated Hours': ['total allocated hours', 'total hours', 'allocated hours', 'hours', 'duration', 'total_hours', 'allocated_hours'],
        'Completed Hours': ['completed hours', 'hours completed', 'done', 'hours done', 'completed_hours', 'hrs completed']
    }
    
    cleansed_df = pd.DataFrame()
    
    for standard_field, input_variants in schema_mapping.items():
        resolved_col = None
        for column_name in working_df.columns:
            if column_name in input_variants or any(variant in column_name for variant in input_variants if len(variant) > 3):
                resolved_col = column_name
                break
        
        if resolved_col is not None:
            cleansed_df[standard_field] = working_df[resolved_col]
        else:
            if standard_field == 'Task ID':
                cleansed_df[standard_field] = range(1, len(working_df) + 1)
            elif standard_field in ['Total Allocated Hours', 'Completed Hours']:
                cleansed_df[standard_field] = 0.0
            elif standard_field == 'Date':
                cleansed_df[standard_field] = datetime.today().date()
            else:
                cleansed_df[standard_field] = "General"
                
    cleansed_df['Date'] = pd.to_datetime(cleansed_df['Date'], errors='coerce').dt.date
    cleansed_df['Date'] = cleansed_df['Date'].fillna(datetime.today().date())
    
    cleansed_df['Total Allocated Hours'] = pd.to_numeric(cleansed_df['Total Allocated Hours'], errors='coerce').fillna(0.0)
    cleansed_df['Completed Hours'] = pd.to_numeric(cleansed_df['Completed Hours'], errors='coerce').fillna(0.0)
    cleansed_df['Remaining Hours'] = cleansed_df['Total Allocated Hours'] - cleansed_df['Completed Hours']
    
    for target_categorical in ['University', 'Course', 'Trainer', 'Task Name']:
        cleansed_df[target_categorical] = cleansed_df[target_categorical].astype(str).str.strip()
        
    return cleansed_df

# =============================================================================
# DATA INGESTION INTERFACE & RUNTIME HANDLING
# =============================================================================
st.sidebar.markdown('### <i class="fa-solid fa-folder-open" style="color:#0EA5E9; margin-right:8px;"></i>Data Management', unsafe_allow_html=True)
runtime_file_stream = st.sidebar.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

has_active_session_data = False

if runtime_file_stream is not None:
    try:
        source_excel_df = pd.read_excel(runtime_file_stream)
        master_registry_df = normalize_ingested_dataset(source_excel_df)
        st.sidebar.success("Loaded and synced dynamic dataset successfully!")
        has_active_session_data = True
    except Exception as initialization_error:
        st.sidebar.error(f"Mapping pipeline mismatch error: {initialization_error}")
        master_registry_df = create_schema_blueprint()
else:
    master_registry_df = create_schema_blueprint()
    st.sidebar.info("Waiting for Excel data upload.")

# =============================================================================
# BRANDING APPARATUS & APP HEADERS
# =============================================================================
if BRAND_ICON_B64:
    st.markdown(f"""
    <div class="title-container">
        <img src="data:image/png;base64,{BRAND_ICON_B64}" class="main-header-icon"/>
        <div class="main-title">Academic Calendar</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="title-container"><div class="main-title"><i class="fa-solid fa-calendar-days" style="color:#0EA5E9; margin-right:12px;"></i>Academic Calendar</div></div>', unsafe_allow_html=True)

st.markdown('<div class="sub-title">Drop your course Excel sheets to dynamically generate task calendars, manage timelines, and audit hours metrics.</div>', unsafe_allow_html=True)

# =============================================================================
# MULTI-DIMENSIONAL FILTERS MATRIX
# =============================================================================
st.markdown('<div class="section-header"><i class="fa-solid fa-magnifying-glass" style="color:#0EA5E9;"></i>Filter Workspace</div>', unsafe_allow_html=True)
layout_col_1, layout_col_2, layout_col_3, layout_col_4 = st.columns(4)

with layout_col_1:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-university icon-spacing"></i>University</div>', unsafe_allow_html=True)
    institution_filter_set = ["All"] + sorted([inst for inst in master_registry_df["University"].unique() if str(inst) != "nan" and str(inst) != "General"]) if has_active_session_data else ["All"]
    selected_institution = st.selectbox("Select University", options=institution_filter_set, label_visibility="collapsed")

with layout_col_2:
    if COURSE_ICON_B64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{COURSE_ICON_B64}" class="custom-icon"/>Course</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-book icon-spacing"></i>Course</div>', unsafe_allow_html=True)
    interim_course_df = master_registry_df if selected_institution == "All" else master_registry_df[master_registry_df["University"] == selected_institution]
    course_filter_set = ["All"] + sorted([crs for crs in interim_course_df["Course"].unique() if str(crs) != "nan" and str(crs) != "General"]) if has_active_session_data else ["All"]
    selected_course = st.selectbox("Select Course", options=course_filter_set, label_visibility="collapsed")

with layout_col_3:
    if FACULTY_ICON_B64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{FACULTY_ICON_B64}" class="custom-icon"/>Trainer</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-chalkboard-user icon-spacing"></i>Trainer</div>', unsafe_allow_html=True)
    interim_trainer_df = interim_course_df if selected_course == "All" else interim_course_df[interim_course_df["Course"] == selected_course]
    trainer_filter_set = ["All"] + sorted([trn for trn in interim_trainer_df["Trainer"].unique() if str(trn) != "nan" and str(trn) != "General"]) if has_active_session_data else ["All"]
    selected_trainer = st.selectbox("Select Trainer", options=trainer_filter_set, label_visibility="collapsed")

with layout_col_4:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-calendar-check icon-spacing"></i>Focused Target Date</div>', unsafe_allow_html=True)
    active_focus_date = st.date_input("Target Date Selection", datetime.today().date(), label_visibility="collapsed")

# Execute row slicing matrices across active filters
view_filtered_df = master_registry_df.copy()
if has_active_session_data:
    if selected_institution != "All":
        view_filtered_df = view_filtered_df[view_filtered_df["University"] == selected_institution]
    if selected_course != "All":
        view_filtered_df = view_filtered_df[view_filtered_df["Course"] == selected_course]
    if selected_trainer != "All":
        view_filtered_df = view_filtered_df[view_filtered_df["Trainer"] == selected_trainer]

calendar_epoch_reference = active_focus_date.isoformat()
daily_timeline_logs_df = view_filtered_df[view_filtered_df["Date"] == active_focus_date] if has_active_session_data else pd.DataFrame()

# Compute aggregation metrics
metric_hours_allocated = view_filtered_df['Total Allocated Hours'].sum() if has_active_session_data else 0
metric_hours_completed = view_filtered_df['Completed Hours'].sum() if has_active_session_data else 0
metric_hours_remaining = view_filtered_df['Remaining Hours'].sum() if has_active_session_data else 0

# =============================================================================
# DISTINCT INSTITUTION COLOR GENERATION METRIC REGISTRY
# =============================================================================
DISTINCT_HEX_PALETTE = ["#0EA5E9", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#3B82F6", "#14B8A6", "#F43F5E"]
university_color_registry = {}

if has_active_session_data:
    distinct_institutions_list = sorted([univ for univ in master_registry_df["University"].unique() if str(univ) != "nan"])
    for element_idx, inst_name in enumerate(distinct_institutions_list):
        university_color_registry[inst_name] = DISTINCT_HEX_PALETTE[element_idx % len(DISTINCT_HEX_PALETTE)]
else:
    university_color_registry["General"] = "#7C3AED"

# =============================================================================
# CHRONOLOGICAL JOB QUEUE PIPELINE ENGINE (CLEAN STRINGS ONLY)
# =============================================================================
next_task_name = "None"
next_task_date = "N/A"
next_task_hours = "0h"
next_task_trainer = "None"

if has_active_session_data and not view_filtered_df.empty:
    current_system_date = datetime.today().date()
    chronological_job_queue = view_filtered_df[(view_filtered_df['Date'] >= current_system_date) & (view_filtered_df['Remaining Hours'] > 0)]
    
    if not chronological_job_queue.empty:
        immediate_next_record = chronological_job_queue.sort_values(by='Date').iloc[0]
        
        next_task_name = str(immediate_next_record['Task Name'])
        next_task_date = immediate_next_record['Date'].strftime("%b %d, %Y")
        next_task_hours = f"{int(immediate_next_record['Remaining Hours'])}h"
        next_task_trainer = str(immediate_next_record['Trainer'])

# =============================================================================
# SIDEBAR KPI DISPLAY CONTAINER (RAW HTML CONSOLIDATION)
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title"><i class="fa-solid fa-hourglass-start" style="color:#7C3AED;"></i> Next Work To Do</div>
    <div class="kpi-value" style="font-size: 16px; line-height:1.2; margin-bottom:4px;">{next_task_name}</div>
    <div class="kpi-subtext">
        <i class="fa-solid fa-calendar" style="color:##7C3AED; margin-right:4px;"></i> <b>Date:</b> {next_task_date}<br/>
        <i class="fa-solid fa-clock" style="color:#7C3AED; margin-right:4px;"></i> <b>Remaining:</b> {next_task_hours}<br/>
        <i class="fa-solid fa-user-tie" style="color:#7C3AED; margin-right:4px;"></i> <b>Trainer:</b> {next_task_trainer}
    </div>
</div>

<div class="kpi-card">
    <div class="kpi-title"><i class="fa-solid fa-hourglass" style="color:#64748B;"></i> Allocated Hours</div>
    <div class="kpi-value">{int(metric_hours_allocated)}h</div>
</div>
<div class="kpi-card">
    <div class="kpi-title"><i class="fa-solid fa-circle-check" style="color:#10B981;"></i> Hours Completed</div>
    <div class="kpi-value">{int(metric_hours_completed)}h</div>
</div>
<div class="kpi-card">
    <div class="kpi-title"><i class="fa-solid fa-clock-rotate-left" style="color:#F43F5E;"></i> Hours Remaining</div>
    <div class="kpi-value">{int(metric_hours_remaining)}h</div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SCHEDULE MATRIX INTERACTIVE ENGINE
# =============================================================================
st.write("---")
st.markdown('<div class="section-header"><i class="fa-solid fa-calendar-days" style="color:#7C3AED;"></i>Calendar</div>', unsafe_allow_html=True)

compiled_calendar_events = []
if has_active_session_data:
    for row_index, current_row in view_filtered_df.iterrows():
        display_title = f"[{current_row['University']}] {current_row['Task Name']} ({int(current_row['Completed Hours'])}h/{int(current_row['Total Allocated Hours'])}h)"
        hex_profile_color = university_color_registry.get(current_row['University'], "#7C3AED")
        
        compiled_calendar_events.append({
            "id": str(current_row['Task ID']),
            "title": display_title,
            "start": current_row['Date'].isoformat(),
            "end": current_row['Date'].isoformat(),
            "backgroundColor": hex_profile_color,
            "borderColor": hex_profile_color,
            "textColor": "#FFFFFF"
        })

interactive_grid_parameters = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "dayGridMonth",
    "initialDate": calendar_epoch_reference,
    "selectable": True,
}

calendar(events=compiled_calendar_events, options=interactive_grid_parameters, key=f"cal_state_{calendar_epoch_reference}_{len(compiled_calendar_events)}")

# =============================================================================
# RENDERING SYSTEM METRICS COLOR LEGEND DESCRIPTIONS (CLEAN HTML WRAP)
# =============================================================================
# =============================================================================
# RENDERING SYSTEM METRICS COLOR LEGEND DESCRIPTIONS (NATIVE FIX)
# =============================================================================
if has_active_session_data and university_color_registry:
    # Dynamically create columns based on the number of universities to show them side-by-side
    legend_cols = st.columns(len(university_color_registry))
    
    for idx, (inst_id, allocated_color) in enumerate(university_color_registry.items()):
        with legend_cols[idx]:
            # Use a clean markdown color block instead of an HTML <span> tag
            st.markdown(f"<span style='color:{allocated_color}; font-size:18px;'>■</span> **{inst_id}**", unsafe_allow_html=True)
else:
    st.markdown("<span style='color:#7C3AED; font-size:18px;'>■</span> *General / Waiting for upload...*", unsafe_allow_html=True)
# =============================================================================
# DAILY TIMELINE TRANSACTION REGISTRY DIARY LOGS
# =============================================================================
st.write("---")
st.markdown(f'<div class="section-header"><i class="fa-solid fa-list-ol" style="color:#7C3AED;"></i>Day Timeline Logs: {active_focus_date.strftime("%B %d, %Y")}</div>', unsafe_allow_html=True)

if has_active_session_data and not daily_timeline_logs_df.empty:
    for row_index, current_row in daily_timeline_logs_df.iterrows():
        if current_row['Remaining Hours'] <= 0:
            status_text, dot_color, label_color = "Completed", "#10B981", "#064E3B"
        elif current_row['Completed Hours'] == 0:
            status_text, dot_color, label_color = "Not Started", "#F43F5E", "#9F1239"
        else:
            status_text, dot_color, label_color = "In Progress", "#F59E0B", "#78350F"
            
        structural_accent_color = university_color_registry.get(current_row['University'], "#0EA5E9")
            
        st.markdown(f"""
        <div class="todo-box" style="border-left: 6px solid {structural_accent_color};">
            <div class="todo-title"><i class="fa-solid fa-thumbtack" style="color:{structural_accent_color}; font-size:14px;"></i> {current_row['Task Name']}</div>
            <div class="todo-meta"><b>University:</b> {current_row['University']} &nbsp;|&nbsp; <b>Course:</b> {current_row['Course']} &nbsp;|&nbsp; <b>Instructor:</b> {current_row['Trainer']}</div>
            <div class="todo-status" style="color: {label_color};"><span style="color:{dot_color};">●</span> {status_text} — ({int(current_row['Completed Hours'])}h Completed / {int(current_row['Remaining Hours'])}h Remaining)</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info(f"No tasks recorded for {active_focus_date.strftime('%B %d, %Y')}.")

# =============================================================================
# QUANTITATIVE GRAPHICAL GRAPH WORKSPACE VIEWS
# =============================================================================
st.write("---")
st.markdown('<div class="section-header"><i class="fa-solid fa-chart-pie" style="color:#7C3AED;"></i>Visual Data Analytics</div>', unsafe_allow_html=True)
analytics_col_left, analytics_col_right = st.columns(2)

with analytics_col_left:
    st.markdown("#### Operational Breakdown by Task")
    if has_active_session_data and not view_filtered_df.empty:
        structural_melt_df = view_filtered_df.melt(id_vars=["Task Name"], value_vars=["Completed Hours", "Remaining Hours"], var_name="Hour Status", value_name="Hours")
        operational_bar_chart = px.bar(
            structural_melt_df, x="Task Name", y="Hours", color="Hour Status", barmode="group",
            color_discrete_map={"Completed Hours": "#6EE7B7", "Remaining Hours": "#FDA4AF"},
            template="plotly_white"
        )
        operational_bar_chart.update_layout(margin=dict(l=20, r=20, t=10, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(operational_bar_chart, use_container_width=True)
    else:
        fallback_empty_chart = px.bar(title="Waiting for Data File...", template="plotly_white")
        st.plotly_chart(fallback_empty_chart, use_container_width=True)

with analytics_col_right:
    st.markdown("#### Performance Metric Volume Allocation")
    if has_active_session_data and metric_hours_allocated > 0:
        volume_pie_chart = px.pie(
            names=["Completed Hours", "Remaining Hours"], values=[metric_hours_completed, metric_hours_remaining],
            color=["Completed Hours", "Remaining Hours"],
            color_discrete_map={"Completed Hours": "#6EE7B7", "Remaining Hours": "#FDA4AF"},
            hole=0.45, template="plotly_white"
        )
        volume_pie_chart.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(volume_pie_chart, use_container_width=True)
    else:
        fallback_empty_pie = px.pie(names=["No Logs Active"], values=[1], color_discrete_sequence=["#E2E8F0"], hole=0.45, template="plotly_white")
        st.plotly_chart(fallback_empty_pie, use_container_width=True)
