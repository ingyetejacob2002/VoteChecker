import streamlit as st
import sqlite3
import pandas as pd

# ---------------- DATABASE ---------------- #
def init_db():
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voters(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            nationality TEXT,
            national_id TEXT,
            criminal_record TEXT,
            eligibility TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="INEC Voting System",
    page_icon="🗳️",
    layout="wide"
)

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>
body {
    background-color: #0E1A25;
}
.stApp {
    background-color: #0E1A25;
    color: white;
}
.card {
    background-color: #142533;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
}
.big-font {
    font-size:18px !important;
}
.success {
    color: #00E676;
    font-weight: bold;
}
.error {
    color: #FF5252;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("🗳️ INEC PANEL")
menu = st.sidebar.radio(
    "Navigation",
    ["Voter Registration", "Dashboard"]
)

# ---------------- FUNCTION ---------------- #
def check_eligibility(age, nationality, national_id, criminal):
    if age >= 18 and nationality.lower() == "nigerian" and national_id != "" and criminal == "No":
        return "ELIGIBLE"
    return "NOT ELIGIBLE"

# ---------------- PAGE 1 ---------------- #
if menu == "Voter Registration":

    st.markdown("<h1 style='text-align:center;'>Voter Eligibility Verification System</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,2])

    with col2:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            nationality = st.text_input("Nationality")
            national_id = st.text_input("National ID")
            criminal = st.selectbox("Criminal Record", ["No", "Yes"])

            if st.button("✅ Verify Eligibility"):

                if name == "" or nationality == "":
                    st.warning("Please fill all fields")
                else:
                    result = check_eligibility(age, nationality, national_id, criminal)

                    # Save to DB
                    conn = sqlite3.connect("voters.db")
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO voters(name, age, nationality, national_id, criminal_record, eligibility)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (name, age, nationality, national_id, criminal, result))
                    conn.commit()
                    conn.close()

                    if result == "ELIGIBLE":
                        st.markdown("<p class='success'>✅ ELIGIBLE TO VOTE</p>", unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown("<p class='error'>❌ NOT ELIGIBLE TO VOTE</p>", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PAGE 2 ---------------- #
elif menu == "Dashboard":

    st.title("📊 Admin Dashboard")

    conn = sqlite3.connect("voters.db")
    df = pd.read_sql_query("SELECT * FROM voters", conn)
    conn.close()

    if df.empty:
        st.info("No data available yet.")
    else:
        # Metrics
        total = len(df)
        eligible = len(df[df["eligibility"] == "ELIGIBLE"])
        not_eligible = len(df[df["eligibility"] == "NOT ELIGIBLE"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Voters", total)
        col2.metric("Eligible", eligible)
        col3.metric("Not Eligible", not_eligible)

        st.markdown("---")

        # Table
        st.dataframe(df, use_container_width=True)

        # Download
        st.download_button(
            "Download Data as CSV",
            df.to_csv(index=False),
            "voters.csv"
        )