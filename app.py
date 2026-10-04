import streamlit as st
import numpy as np
import joblib
import random
import sqlite3
from datetime import datetime

# CONFIG

st.set_page_config(
    page_title="AI Heart Disease Detection",
    page_icon="🫀",
    layout="centered"
)

# LOAD MODEL

model = joblib.load("heart_model.pkl")

# DATABASE

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS history (
    username TEXT,
    risk INTEGER,
    timestamp TEXT
)
""")
conn.commit()

# SESSION

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# AUTH

def login(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def signup(username, password):
    try:
        c.execute("INSERT INTO users VALUES (?,?)", (username, password))
        conn.commit()
        return True
    except:
        return False

# LOGIN / SIGNUP

if not st.session_state.logged_in:
    st.markdown("## 🔐 User Authentication")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(u, p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("Create Username")
        p = st.text_input("Create Password", type="password")
        if st.button("Signup"):
            if signup(u, p):
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists")

    st.stop()

# SIDEBAR

st.sidebar.title("🫀 Heart AI")
st.sidebar.success(f"Logged in as {st.session_state.user}")

page = st.sidebar.radio(
    "Navigation",
    ["🧠 Prediction", "📜 History", "ℹ️ About"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# PREDICTION PAGE

if page == "🧠 Prediction":

    st.title("❤️ AI Heart Disease Detection")
    st.caption("Early Health Risk Screening System")

    st.info(
        "⚠️ This tool is for **educational screening only**. "
        "It is **not a medical diagnosis**."
    )

    with st.expander("🧍 Personal & Clinical Inputs", expanded=True):
        age = st.slider("Age", 18, 100, 30)
        sex = st.selectbox("Gender", ["Female", "Male"])
        cp = st.selectbox(
            "Chest Pain Type",
            ["Typical angina", "Atypical angina", "Non-anginal pain", "Asymptomatic"]
        )

        col1, col2 = st.columns(2)
        trestbps = col1.slider("Resting BP (mm Hg)", 80, 200, 120)
        chol = col2.slider("Cholesterol (mg/dl)", 100, 400, 180)

        fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", ["No", "Yes"])
        thalach = st.slider("Max Heart Rate Achieved", 70, 220, 170)
        exang = st.selectbox("Exercise Induced Angina", ["Yes", "No"])
        oldpeak = st.slider("ST Depression", 0.0, 6.0, 2.0)
        slope = st.selectbox("ST Segment Slope", ["Upsloping", "Flat", "Downsloping"])
        ca = st.selectbox("Major Vessels Blocked", [0, 1, 2, 3])
        thal = st.selectbox(
            "Thalassemia Type",
            ["Normal", "Fixed defect", "Reversible defect", "Unknown"]
        )

    # MAPPING
    
    sex = 0 if sex == "Female" else 1
    cp = {"Typical angina":0,"Atypical angina":1,"Non-anginal pain":2,"Asymptomatic":3}[cp]
    fbs = 0 if fbs == "No" else 1
    exang = 0 if exang == "No" else 1
    slope = {"Upsloping":0,"Flat":1,"Downsloping":2}[slope]
    thal = {"Normal":0,"Fixed defect":1,"Reversible defect":2,"Unknown":3}[thal]

    # SENSORS
    
    st.subheader("📟 Live Sensor Readings (Simulated)")
    col1, col2 = st.columns(2)
    col1.metric("Pulse Rate (bpm)", random.randint(60, 100))
    col2.metric("Heart Beat Rate (bpm)", random.randint(60, 100))

    # PREDICT
    
    if st.button("🧠 Check Heart Health"):
        input_data = np.array([[age,sex,cp,trestbps,chol,fbs,0,thalach,exang,oldpeak,slope,ca,thal]])
        prob = model.predict_proba(input_data)[0][1]
        risk = int(prob * 100)

        st.subheader("📊 AI Diagnosis")
        st.progress(risk)

        if risk <= 30:
            st.success(f"✅ Low Risk ({risk}%)")
        elif risk <= 50:
            st.warning(f"⚠️ Moderate Risk ({risk}%)")
        else:
            st.error(f"🚨 High Risk ({risk}%)")

        c.execute(
            "INSERT INTO history VALUES (?,?,?)",
            (st.session_state.user, risk, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()

# HISTORY PAGE

elif page == "📜 History":
    st.title("📜 Prediction History")

    c.execute("SELECT risk, timestamp FROM history WHERE username=?", (st.session_state.user,))
    rows = c.fetchall()

    if rows:
        for r, t in rows[::-1]:
            st.write(f"🕒 **{t}** — Risk: **{r}%**")
    else:
        st.info("No predictions yet.")

    st.divider()
    st.subheader("🗑️ Manage History")

    confirm = st.checkbox("I understand this will permanently delete my history")
    if confirm and st.button("Clear My Prediction History"):
        c.execute("DELETE FROM history WHERE username=?", (st.session_state.user,))
        conn.commit()
        st.success("History cleared successfully.")
        st.rerun()

# ABOUT PAGE

else:
    st.title("ℹ️ About This Project")
    st.write("""
AI Heart Disease Detection App is a machine learning–based health screening system designed to estimate the risk of heart disease using clinical parameters.

The application uses a Random Forest model trained on the UCI Heart Disease dataset, analyzing 13 key medical features such as age, blood pressure, cholesterol, ECG results, heart rate, and exercise-induced angina.
Instead of a simple yes/no output, the model provides a risk percentage, classified as Low, Moderate, or High risk, making the results easier to understand.

The project demonstrates an end-to-end AI application, combining:

Machine Learning for prediction

Streamlit for an interactive UI

SQLite for user authentication and prediction history storage

Each user can log in, check their heart health, view past predictions, and manage their data.

⚠️ This application is built for educational and demonstration purposes only and should not be considered a medical diagnosis.
    """)
