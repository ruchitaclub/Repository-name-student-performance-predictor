import streamlit as st
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
from datetime import datetime

# ---------------- LOAD USERS ----------------
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

# ---------------- SAVE USERS ----------------
def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# ---------------- LOGIN ----------------
def login():
    st.title("🔐 Login System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- REGISTER USER ----------------
def register():
    st.subheader("➕ Create New User")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        users = load_users()
        if new_user in users:
            st.error("User already exists")
        else:
            users[new_user] = new_pass
            save_users(users)
            st.success("User registered successfully")

# ---------------- LOGOUT ----------------
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user"] = ""
    st.rerun()

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    data = pd.read_csv("student_data.csv")
    X = data[["hours", "attendance"]]
    y = data["marks"]

    model = LinearRegression()
    model.fit(X, y)
    return model

# ---------------- SAVE HISTORY ----------------
def save_history(user, hours, attendance, marks):
    new_data = pd.DataFrame([[datetime.now(), user, hours, attendance, marks]],
                            columns=["Time", "User", "Hours", "Attendance", "Marks"])
    try:
        old = pd.read_csv("history.csv")
        new_data = pd.concat([old, new_data])
    except:
        pass

    new_data.to_csv("history.csv", index=False)

# ---------------- MAIN APP ----------------
def main_app():
    st.title("📊 Student Performance Predictor")

    # Sidebar
    st.sidebar.title("👤 User Panel")
    st.sidebar.write(f"Logged in as: {st.session_state['user']}")

    if st.sidebar.button("🚪 Logout"):
        logout()

    model = load_model()

    hours = st.number_input("Study Hours", min_value=0.0)
    attendance = st.number_input("Attendance (%)", min_value=0.0)

    if st.button("Predict"):
        prediction = model.predict(pd.DataFrame([[hours, attendance]],
                                                columns=["hours", "attendance"]))
        marks = round(prediction[0], 2)

        # Grade
        if marks >= 90:
            grade = "A"
        elif marks >= 75:
            grade = "B"
        elif marks >= 50:
            grade = "C"
        else:
            grade = "F"

        st.success(f"Marks: {marks} | Grade: {grade}")

        save_history(st.session_state["user"], hours, attendance, marks)

    # Graph
    st.subheader("📊 Graph")
    data = pd.read_csv("student_data.csv")
    st.scatter_chart(data[["hours", "marks"]])

    # History
    st.subheader("📁 Prediction History")
    try:
        history = pd.read_csv("history.csv")
        st.write(history)

        st.download_button("⬇ Download History",
                           history.to_csv(index=False),
                           file_name="history.csv")
    except:
        st.write("No history available")

# ---------------- CONTROL ----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user"] = ""

if not st.session_state["logged_in"]:
    login()
    register()
else:
    main_app()