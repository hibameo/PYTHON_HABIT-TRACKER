import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json
import os

# Set page configuration
st.set_page_config(
    page_title="Habit Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for habits data
if 'habits' not in st.session_state:
    st.session_state.habits = []

if 'habit_data' not in st.session_state:
    st.session_state.habit_data = {}

# Functions to save and load data
def save_data():
    data = {
        'habits': st.session_state.habits,
        'habit_data': st.session_state.habit_data
    }
    with open('habit_data.json', 'w') as f:
        json.dump(data, f)

def load_data():
    if os.path.exists('habit_data.json'):
        with open('habit_data.json', 'r') as f:
            data = json.load(f)
            st.session_state.habits = data['habits']
            st.session_state.habit_data = data['habit_data']

# Try to load existing data
try:
    load_data()
except:
    st.warning("No previous data found or error loading data. Starting fresh.")

# Sidebar for adding new habits
st.sidebar.title("Habit Management")

# Add new habit
new_habit = st.sidebar.text_input("Add a new habit:")
habit_category = st.sidebar.selectbox("Category:", ["Health", "Productivity", "Personal Growth", "Other"])
habit_goal = st.sidebar.selectbox("Goal type:", ["Daily", "Weekly", "Monthly"])

if st.sidebar.button("Add Habit"):
    if new_habit and new_habit not in st.session_state.habits:
        st.session_state.habits.append(new_habit)
        st.session_state.habit_data[new_habit] = {
            "category": habit_category,
            "goal": habit_goal,
            "streak": 0,
            "history": {}
        }
        save_data()
        st.sidebar.success(f"Added '{new_habit}' to your habits!")
    elif new_habit in st.session_state.habits:
        st.sidebar.error("This habit already exists!")
    else:
        st.sidebar.error("Please enter a habit name.")

# Remove habits
if st.session_state.habits:
    habit_to_remove = st.sidebar.selectbox("Select habit to remove:", st.session_state.habits, key="remove")
    if st.sidebar.button("Remove Habit"):
        st.session_state.habits.remove(habit_to_remove)
        if habit_to_remove in st.session_state.habit_data:
            del st.session_state.habit_data[habit_to_remove]
        save_data()
        st.sidebar.success(f"Removed '{habit_to_remove}' from your habits!")
        st.rerun()

# Main content
st.title("🌟 My Habit Tracker")

# Show today's date
today = datetime.datetime.now().strftime("%A, %B %d, %Y")
st.write(f"📅 Today: {today}")

# Check-in section
st.header("Daily Check-in")

if not st.session_state.habits:
    st.info("You don't have any habits yet. Add some habits in the sidebar!")
else:
    # Date selector for check-in
    check_date = st.date_input("Select date:", datetime.date.today())
    date_str = check_date.strftime("%Y-%m-%d")
    
    # Create columns for the habits
    cols = st.columns(min(3, len(st.session_state.habits)))
    
    for i, habit in enumerate(st.session_state.habits):
        col_idx = i % 3
        with cols[col_idx]:
            # Get current status
            habit_completed = False
            if date_str in st.session_state.habit_data[habit].get("history", {}):
                habit_completed = st.session_state.habit_data[habit]["history"][date_str]
            
            # Create check box
            completed = st.checkbox(
                f"{habit} ({st.session_state.habit_data[habit]['category']} - {st.session_state.habit_data[habit]['goal']})",
                value=habit_completed,
                key=f"check_{habit}_{date_str}"
            )
            
            # Update data if checkbox changes
            if completed != habit_completed:
                if "history" not in st.session_state.habit_data[habit]:
                    st.session_state.habit_data[habit]["history"] = {}
                
                st.session_state.habit_data[habit]["history"][date_str] = completed
                
                # Update streak
                if completed:
                    st.session_state.habit_data[habit]["streak"] += 1
                else:
                    st.session_state.habit_data[habit]["streak"] = 0
                
                save_data()
    
    if st.button("Save Check-in"):
        save_data()
        st.success("Progress saved successfully!")

# Analytics section
st.header("Analytics")

if st.session_state.habits:
    tab1, tab2, tab3 = st.tabs(["Streaks", "Completion Rates", "Calendar View"])
    
    with tab1:
        st.subheader("Current Streaks")
        
        streak_data = {habit: st.session_state.habit_data[habit]["streak"] for habit in st.session_state.habits}
        streak_df = pd.DataFrame(list(streak_data.items()), columns=["Habit", "Current Streak"])
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(streak_df["Habit"], streak_df["Current Streak"], color='skyblue')
        ax.set_ylabel("Current Streak")
        ax.set_xlabel("Habit")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab2:
        st.subheader("Completion Rates")
        
        completion_data = {}
        for habit in st.session_state.habits:
            if "history" in st.session_state.habit_data[habit]:
                history = st.session_state.habit_data[habit]["history"]
                total = len(history)
                completed = sum(1 for status in history.values() if status)
                rate = (completed / total) * 100 if total > 0 else 0
                completion_data[habit] = rate
            else:
                completion_data[habit] = 0
        
        comp_df = pd.DataFrame(list(completion_data.items()), columns=["Habit", "Completion Rate (%)"])
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(comp_df["Habit"], comp_df["Completion Rate (%)"], color='lightgreen')
        ax.set_ylabel("Completion Rate (%)")
        ax.set_xlabel("Habit")
        ax.set_ylim(0, 100)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab3:
        st.subheader("Monthly Calendar View")
        
        selected_habit = st.selectbox("Select habit:", st.session_state.habits)
        
        # Get the current month and year
        current_month = datetime.date.today().month
        current_year = datetime.date.today().year
        
        # Get the first day of the month and the number of days
        first_day = datetime.date(current_year, current_month, 1)
        if current_month == 12:
            last_day = datetime.date(current_year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day = datetime.date(current_year, current_month + 1, 1) - datetime.timedelta(days=1)
        
        num_days = last_day.day
        
        # Create calendar data
        calendar_data = []
        week = []
        
        # Fill in the days before the first day of the month
        first_weekday = first_day.weekday()  # Monday=0, Sunday=6
        for _ in range(first_weekday):
            week.append(None)
        
        # Fill in the days of the month
        for day in range(1, num_days + 1):
            date = datetime.date(current_year, current_month, day)
            date_str = date.strftime("%Y-%m-%d")
            
            if selected_habit in st.session_state.habit_data:
                completed = False
                if "history" in st.session_state.habit_data[selected_habit]:
                    completed = st.session_state.habit_data[selected_habit]["history"].get(date_str, False)
                
                week.append({
                    "day": day,
                    "completed": completed,
                    "date": date
                })
            else:
                week.append({
                    "day": day,
                    "completed": False,
                    "date": date
                })
            
            if len(week) == 7:
                calendar_data.append(week)
                week = []
        
        # Fill in the days after the last day of the month
        if week:
            while len(week) < 7:
                week.append(None)
            calendar_data.append(week)
        
        # Display the calendar
        month_name = first_day.strftime("%B %Y")
        st.write(f"Calendar for {month_name}")
        
        # Create a CSS-styled calendar
        st.write(
            """
            <style>
            .calendar {
                width: 100%;
                border-collapse: collapse;
            }
            .calendar th {
                text-align: center;
                padding: 10px;
                background-color: #f0f0f0;
            }
            .calendar td {
                width: 14%;
                height: 60px;
                text-align: center;
                vertical-align: middle;
                border: 1px solid #ddd;
                padding: 10px;
            }
            .completed {
                background-color: #9cff9c;
            }
            .not-completed {
                background-color: #ffcccb;
            }
            .empty {
                background-color: #f9f9f9;
            }
            </style>
            
            <table class="calendar">
                <tr>
                    <th>Mon</th>
                    <th>Tue</th>
                    <th>Wed</th>
                    <th>Thu</th>
                    <th>Fri</th>
                    <th>Sat</th>
                    <th>Sun</th>
                </tr>
            """,
            unsafe_allow_html=True
        )
        
        for week in calendar_data:
            st.write("<tr>", unsafe_allow_html=True)
            for day in week:
                if day is None:
                    st.write('<td class="empty"></td>', unsafe_allow_html=True)
                else:
                    if day["completed"]:
                        st.write(f'<td class="completed">{day["day"]}</td>', unsafe_allow_html=True)
                    else:
                        st.write(f'<td class="not-completed">{day["day"]}</td>', unsafe_allow_html=True)
            st.write("</tr>", unsafe_allow_html=True)
        
        st.write("</table>", unsafe_allow_html=True)

# Export data option
st.header("Export Data")
if st.button("Export to CSV"):
    # Prepare data for export
    export_data = []
    for habit in st.session_state.habits:
        habit_info = st.session_state.habit_data[habit]
        history = habit_info.get("history", {})
        
        for date, completed in history.items():
            export_data.append({
                "Habit": habit,
                "Category": habit_info["category"],
                "Goal Type": habit_info["goal"],
                "Date": date,
                "Completed": "Yes" if completed else "No",
                "Current Streak": habit_info["streak"]
            })
    
    if export_data:
        export_df = pd.DataFrame(export_data)
        csv = export_df.to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="habit_tracker_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data to export!")

# Footer
st.markdown("---")
st.markdown("Made with HIBA ❤️ and Streamlit")