import streamlit as st
from auth.auth import authenticate, add_user
from utils.recommendation import load_courses, get_recommendations
import os
import json
import time

courses_df = load_courses()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'role' not in st.session_state:
    st.session_state.role = None
if 'interests' not in st.session_state:
    st.session_state.interests = []
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'signup_success' not in st.session_state:
    st.session_state.signup_success = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'role_selection'
if 'profile_data' not in st.session_state:
    st.session_state.profile_data = {}
if 'profile_setup_complete' not in st.session_state:
    st.session_state.profile_setup_complete = False
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

USERINFO_FILE = 'data/userinfo.txt'

def load_user_profile(username):
    profiles = {}
    if os.path.exists(USERINFO_FILE):
        with open(USERINFO_FILE, 'r') as f:
            for line in f:
                user, data = line.strip().split(':', 1)
                profiles[user] = json.loads(data)
    return profiles.get(username, {})

def save_user_profile(username, profile):
    profiles = {}
    if os.path.exists(USERINFO_FILE):
        with open(USERINFO_FILE, 'r') as f:
            for line in f:
                user, data = line.strip().split(':', 1)
                profiles[user] = json.loads(data)
    
    profiles[username] = profile
    with open(USERINFO_FILE, 'w') as f:
        for user, data in profiles.items():
            f.write(f"{user}:{json.dumps(data)}\n")

def show_role_selection():
    st.title("Select Role")
    if st.button("Admin", key="admin_role"):
        st.session_state.role_selection = 'admin'
        st.session_state.current_page = 'login'
    if st.button("User", key="user_role"):
        st.session_state.role_selection = 'user'
        st.session_state.current_page = 'login'

def show_login_form():
    st.subheader("Login Section")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login", key="login"):
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success(f"Welcome {username}")
            st.session_state.profile_data = load_user_profile(username)
            if role == 'user' and not st.session_state.profile_data.get('profile_setup_complete', False):
                st.session_state.current_page = 'profile_setup'
            else:
                st.session_state.current_page = 'home'
            st.experimental_rerun()
        else:
            st.warning("Incorrect Username/Password")
    if st.session_state.role_selection == 'user' and st.button("Sign Up", key="signup"):
        st.session_state.show_signup = True
        st.session_state.current_page = 'signup'
        st.experimental_rerun()

def show_signup_form():
    st.subheader("Create New Account")
    new_user = st.text_input("New Username")
    new_password = st.text_input("New Password", type='password')
    if st.button("Sign Up", key="signup_form"):
        if add_user(new_user, new_password):
            st.session_state.signup_success = True
            st.session_state.username = new_user
            st.session_state.role = 'user'
            st.session_state.logged_in = True
            st.session_state.current_page = 'profile_setup'
            st.experimental_rerun()
        else:
            st.warning("Username already exists")
    if st.button("Back to Login", key="back_to_login"):
        st.session_state.show_signup = False
        st.session_state.current_page = 'login'

def show_user_dashboard():
    st.sidebar.write(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout", key="user_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.interests = []
        st.session_state.current_page = 'role_selection'
        st.experimental_rerun()

    st.subheader("Welcome to the Personalized Learning Recommendation Portal!")
    st.write("""
    Welcome to your personalized learning journey! Our platform helps you find the best courses tailored to your interests and goals. Whether you're advancing your career, learning a new skill, or exploring a hobby, we've got you covered.
    """)
    st.write("#### HAPPY LEARNING :) !")
    st.write("### Latest Courses")
    latest_courses = courses_df.sample(3)  # Display 3 random courses as the latest courses
    st.markdown("""
        <style>
            .course-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* Adjust min-width and fraction as needed */
                gap: 20px; /* Adjust the gap between cards */
            }
            .course-card {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px; /* Adjust padding as needed */
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                display: flex;
                margin: 10px;
                flex-direction: column;
                justify-content: space-between;
                height: 200px; /* Adjust height of each card */
            }
            .course-card h4 {
                margin: 10px;
                font-size: 18px; /* Adjust font size as needed */
            }
            .course-card p {
                margin: 10px;
                font-size: 14px; /* Adjust font size as needed */
                color: white; /* Adjust text color */
            }
        </style>
        <div class="course-container">
        """, unsafe_allow_html=True)
    
    for index, row in latest_courses.iterrows():
        st.markdown(f"""
        <div class="course-card">
            <h4>{row['course_name']}</h4>
            <p>{row['description']}</p>
            <p>{row['category']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("### Recommended For You")
    if st.session_state.recommendations:
        st.markdown("""
        <style>
            .course-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* Adjust min-width and fraction as needed */
                gap: 20px; /* Adjust the gap between cards */
            }
            .course-card {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px; /* Adjust padding as needed */
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                height: 200px; /* Adjust height of each card */
            }
            .course-card h4 {
                margin: 10px;
                font-size: 18px; /* Adjust font size as needed */
            }
            .course-card p {
                margin: 10px;
                font-size: 16px; /* Adjust font size as needed */
                color: white; /* Adjust text color */
            }
        </style>
        <div class="course-container">
        """, unsafe_allow_html=True)
        
        for course_name in st.session_state.recommendations:
            course_details = courses_df[courses_df['course_name'] == course_name].iloc[0]
            st.markdown(f"""
            <div class="course-card">
                <h4>{course_details['course_name']}</h4>
                <p>{course_details['description']}</p>
                <p>{course_details['category']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("No recommendations yet. Select your interests to get personalized recommendations.")


import streamlit as st
import pandas as pd

courses_file = 'data/courses.csv'

# Load courses data
try:
    courses_df = pd.read_csv(courses_file)
except FileNotFoundError:
    courses_df = pd.DataFrame(columns=['course_name', 'description', 'category'])
import json

def load_users():
    users_info = []
    try:
        with open('data/userinfo.txt', 'r') as file:
            for line in file:
                username, details = line.strip().split(':', 1)
                user_info = json.loads(details)
                user_info['username'] = username
                users_info.append(user_info)
    except FileNotFoundError:
        st.error("User information file not found.")
    
    return users_info

def display_user_profiles(user_info):
    for username, info in user_info.items():
        st.write(f"### {username.capitalize()}")
        if 'name' in info:
            st.write(f"**Name:** {info['name']}")
        if 'email' in info:
            st.write(f"**Email:** {info['email']}")
        if 'about' in info:
            st.write(f"**About:** {info['about']}")
        if 'I am' in info:
            st.write(f"**I am:** {info['I am']}")
        st.write("**Interests:**")
        for interest in info.get('interests', []):
            st.write(f"- {interest}")
        st.write("**Recommended Courses:**")
        for course in info.get('recommended_courses', []):
            st.write(f"- {course}")
        st.write("---")  # Separator between users


def show_admin_dashboard():
    st.sidebar.write(f"Admin Panel - Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout", key="admin_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.current_page = 'role_selection'
        st.experimental_rerun()

    st.subheader("Admin Dashboard")

    tabs = st.tabs([
        "User Management", "Content Management", "Recommendations", 
        "Analytics", "Communication", "Monetization", "Settings", 
        "Integrations", "Logs", "Feedback"
    ])

    with tabs[0]:
        st.write("### User Management")
        users = load_users()
        for user in users:
            st.markdown(
                f"""
                <div style="border: 1px solid #ccc; border-radius: 5px; padding: 10px; margin-bottom: 10px;">
                    <div><strong>Username:</strong> {user['username']}</div>
                    <div><strong>Name:</strong> {user.get('name', 'Not provided')}</div>
                    <div><strong>Email:</strong> {user.get('email', 'Not provided')}</div>
                    <div><strong>About:</strong> {user.get('about', 'Not provided')}</div>
                    <div><strong>I am:</strong> {user.get('I am', 'Not provided')}</div>
                    <div><strong>Interests:</strong> {', '.join(user.get('interests', ['Not provided']))}</div>
                    <div>
                        <strong>Recommended Courses:</strong>
                        <ul>
                            {"".join(f"<li>{course}</li>" for course in user.get('recommended_courses', []))}
                        </ul>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button("Add New User"):
            st.write("Functionality to add a new user goes here.")
            
    with tabs[1]:
        st.write("### Content Management")
        manage_content()

    with tabs[2]:
        st.write("### Recommendations")
        st.write("Functionality to configure and manage recommendations goes here.")

    with tabs[3]:
        st.write("### Analytics and Reporting")
        st.write("#### User Activity")
        st.write("Charts and reports showing user activity go here.")
        
        st.write("#### Content Performance")
        st.write("Charts and reports showing content performance go here.")

    with tabs[4]:
        st.write("### Communication Tools")
        st.write("Functionality for managing notifications and messaging goes here.")

    with tabs[5]:
        st.write("### Monetization and Payments")
        st.write("#### Manage Subscriptions")
        st.write("Functionality to manage subscriptions goes here.")
        
        st.write("#### View Revenue Reports")
        st.write("Revenue reports and analytics go here.")

    with tabs[6]:
        st.write("### Customization and Settings")
        st.write("Functionality to customize and configure site settings goes here.")

    with tabs[7]:
        st.write("### Integration Management")
        st.write("Functionality to manage integrations with third-party services goes here.")

    with tabs[8]:
        st.write("### Logs and Audit Trails")
        st.write("#### Activity Logs")
        st.write("Functionality to view activity logs goes here.")
        
        st.write("#### Audit Trails")
        st.write("Functionality to view audit trails goes here.")

    with tabs[9]:
        st.write("### Feedback and Improvement")
        st.write("#### Manage Feedback")
        st.write("Functionality to manage user feedback goes here.")
        
        st.write("#### Feature Requests")
        st.write("Functionality to manage feature requests goes here.")

def add_course(course):
    global courses_df
    new_course_df = pd.DataFrame([course])
    courses_df = pd.concat([courses_df, new_course_df], ignore_index=True)
    courses_df.to_csv(courses_file, index=False)

def delete_courses(selected_courses):
    global courses_df
    deleted_course_names = selected_courses['course_name'].tolist()
    courses_df = courses_df[~courses_df['course_name'].isin(deleted_course_names)].reset_index(drop=True)
    courses_df.to_csv(courses_file, index=False)
    st.success(f"Courses {deleted_course_names} deleted successfully.")

def manage_content():
    st.write("#### Add New Course")
    course_name = st.text_input("Course Name")
    interest = st.text_input("Interest")
    course_description = st.text_area("Course Description")
    course_category = st.selectbox("Course Category", [  "~Select~",  "Frontend",    "Backend",    "Data Science",    "Mobile Development",    "Programming",    "Game Development",    "Security",    "DevOps",    "Blockchain",    "Quantum Computing",    "Marketing",    "Design",    "Photography",    "Video Editing",    "Music Production",    "Animation",    "Film",    "Business",    "Finance",    "Economics",    "Sociology",    "Anthropology",    "Psychology",    "Philosophy",    "Linguistics",    "Literature",    "Writing",    "Law",    "Political Science",    "History",    "Geography",    "Biology",    "Chemistry",    "Physics",    "Environmental Science",    "Astronomy",    "Engineering",    "Medicine",    "Nursing",    "Health",    "Accounting",    "Sports",    "Athletics",    "Pets",    "Equine Science",    "Agriculture",    "Food Science",    "Nutrition"])
    if st.button("Add Course"):
        new_course = {
            'course_name': course_name,
            'interest': interest,
            'description': course_description,
            'category': course_category
        }
        add_course(new_course)
        st.success(f"New course '{course_name}' added successfully.")
    
    # Display existing courses in a tabular format with checkboxes
    st.write("#### Manage Existing Courses")
    
    # Prepare table data excluding 'Interest'
    table_data = {
        'Course Name': courses_df['course_name'],
        'Description': courses_df['description'],
        'Category': courses_df['category'],
    }
    
    # Display table with checkboxes using course names
    selected_course_names = st.multiselect("Select courses to delete:", courses_df['course_name'].tolist())
    selected_courses = courses_df[courses_df['course_name'].isin(selected_course_names)] if selected_course_names else pd.DataFrame(columns=table_data.keys())
    
    # Check if selected_courses is empty or not
    if not selected_courses.empty:
        # Display the dataframe excluding 'Interest' column
        st.dataframe(selected_courses[['course_name', 'description', 'category']])
    else:
        st.warning("No courses selected or found.")
    
    # Delete selected courses button
    if st.button("DELETE COURSES"):
        if not selected_course_names:
            st.warning("Please select courses to delete.")
        else:
            delete_courses(selected_courses)
            st.experimental_rerun()


def show_user_profile():
    st.sidebar.write(f"Welcome, {st.session_state.username}")
    
    if st.sidebar.button("Logout", key="profile_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.current_page = 'role_selection'
        st.experimental_rerun()

    st.subheader("User Profile")

    profile = st.session_state.profile_data

    # Define CSS styles for the profile container and profile items
    st.markdown(
        """
        <style>
        .profile-container {
            background-color: black;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border: 2px solid white; /* Border with white color */

        }
        .profile-item {
            margin-bottom: 10px;
        }
        .profile-item-label {
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display profile information in a styled container
    st.markdown(
        f"""
        <div class="profile-container">
            <div class="profile-item">
                <span class="profile-item-label">Name:</span> {profile.get('name', '')}
            </div>
            <div class="profile-item">
                <span class="profile-item-label">Email:</span> {profile.get('email', '')}
            </div>
            <div class="profile-item">
                <span class="profile-item-label">About:</span> {profile.get('about', '')}
            </div>
            <div class="profile-item">
                <span class="profile-item-label">I am:</span> {profile.get('I am', '')}
            </div>
            <div class="profile-item">
                <span class="profile-item-label">Interests:</span> {', '.join(profile.get('interests', []))}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_profile_setup():
    st.sidebar.write(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout", key="setup_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.current_page = 'role_selection'
        st.experimental_rerun()

    st.subheader("Setup Your Profile")
    profile = st.session_state.profile_data
    new_name = st.text_input("Name", profile.get('name', ''))
    new_email = st.text_input("Email", profile.get('email', ''))
    new_about = st.text_area("About", profile.get('about', ''))
    new_grade = st.selectbox("I am", ['Select', 'College Student', 'School Student', 'Teacher'])

    if st.button("Save Profile", key="save_profile"):
        profile['name'] = new_name
        profile['email'] = new_email
        profile['about'] = new_about
        profile['I am'] = new_grade
        profile['profile_setup_complete'] = True
        save_user_profile(st.session_state.username, profile)
        st.session_state.profile_data = profile
        st.session_state.current_page = 'recommendation'
        st.success("Profile updated successfully.")
        st.experimental_rerun()

def show_recommendation_page():
    st.sidebar.write(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout", key="rec_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.current_page = 'role_selection'
        st.experimental_rerun()

    st.subheader("Select Your Interests")
    interests = st.multiselect("Select at least 5 interests", courses_df['interest'].unique())
    
    if len(interests) < 5:
        st.warning("Please select at least 5 interests")
    else:
        if st.button("Get Recommendations", key="get_recommendations"):
            with st.spinner("Getting your recommendations..."):
                time.sleep(3)  # Simulate a delay for fetching recommendations
                st.session_state.interests = interests
                recommendations = get_recommendations(interests, courses_df).head(8)
                st.session_state.recommendations = recommendations['course_name'].tolist()
                profile = load_user_profile(st.session_state.username)
                profile['interests'] = interests
                profile['recommended_courses'] = recommendations['course_name'].tolist()
                save_user_profile(st.session_state.username, profile)
                st.session_state.current_page = 'courses'
                st.experimental_rerun()


def show_courses_page():
    st.sidebar.write(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout", key="courses_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.current_page = 'role_selection'
        st.experimental_rerun()

    st.subheader("Recommended Courses")

    if st.session_state.recommendations:
        st.markdown("""
        <style>
        .course-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* Adjust min-width and fraction as needed */
            gap: 20px; /* Adjust the gap between cards */
        }
        .course-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px; /* Adjust padding as needed */
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 200px; /* Adjust height of each card */
        }
        .course-card h4 {
            margin: 10px;    
            font-size: 18px; /* Adjust font size as needed */
        }
        .course-card p {
            margin: 10px;
            font-size: 16px; /* Adjust font size as needed */
            color: white; /* Adjust text color */
        }
        </style>
        <div class="course-container">
        """, unsafe_allow_html=True)

        # Loop through recommendations and display each in a styled card
        for course_name in st.session_state.recommendations:
            course_details = courses_df[courses_df['course_name'] == course_name].iloc[0]
            st.markdown(f"""
            <div class="course-card">
                <h4>{course_details['course_name']}</h4>
                <p>{course_details['description']}</p>
                <p>{course_details['category']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Close the container div
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("No recommendations found.")


def show_navigation():
    if st.session_state.current_page == 'role_selection':
        show_role_selection()
    elif st.session_state.current_page == 'login':
        show_login_form()
    elif st.session_state.current_page == 'signup':
        show_signup_form()
    elif st.session_state.current_page == 'profile_setup':
        show_profile_setup()
    elif st.session_state.current_page == 'recommendation':
        show_recommendation_page()
    elif st.session_state.current_page == 'courses':
        show_courses_page()
    elif st.session_state.logged_in:
        if st.session_state.role == 'admin':
            show_admin_dashboard()
        elif st.session_state.current_page == 'profile':
            show_user_profile()
        else:
            show_user_dashboard()


def main():
    st.set_page_config(menu_items=None)
    st.title("Personalized Learning Recommendation")

    show_navigation()

    if st.session_state.logged_in and st.session_state.role == 'user':
        if st.sidebar.button("Home", key="home_page"):
            st.session_state.current_page = 'home'
            st.experimental_rerun()
        if st.sidebar.button("User Profile", key="user_profile"):
            st.session_state.current_page = 'profile'
            st.experimental_rerun()
        if st.sidebar.button("Courses", key="courses_page"):
            st.session_state.current_page = 'courses'
            st.experimental_rerun()

if __name__ == '__main__':
    main()

