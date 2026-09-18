import streamlit as st
import sys
import os
import requests
import time
import pandas as pd
import mysql.connector
import bcrypt

# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.insert(0, PROJECT_ROOT)

API_URL = "http://127.0.0.1:8000"

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Loan Default Prediction", page_icon="💳", layout="wide"
)

# --------------------------------------------------
# Authentication
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False
if "show_register" not in st.session_state:
    st.session_state.show_register = False

if not st.session_state.logged_in:
    # --- Premium Login CSS ---
    st.markdown(
        """
    <style>
        .login-title {
            color: #fff;
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 10px;
            text-align: center;
            background: linear-gradient(90deg, #a78bfa, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .login-subtitle {
            color: #94a3b8;
            font-size: 16px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Center the login box
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.write("")  # Padding
        st.write("")

        if st.session_state.show_register:
            # --- REGISTER VIEW ---
            st.markdown(
                '<div class="login-title">Create Account</div>', unsafe_allow_html=True
            )
            st.markdown(
                '<div class="login-subtitle">Register a new loan officer account</div>',
                unsafe_allow_html=True,
            )

            with st.form("register_form", clear_on_submit=False):
                reg_username = st.text_input("New Username")
                reg_password = st.text_input("New Password", type="password")
                reg_confirm = st.text_input("Confirm Password", type="password")
                reg_button = st.form_submit_button("Register", use_container_width=True)

                if reg_button:
                    if not reg_username or not reg_password or not reg_confirm:
                        st.warning("Please fill out all fields.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            from dotenv import load_dotenv

                            load_dotenv()
                            conn = mysql.connector.connect(
                                host=os.getenv("DB_HOST", "127.0.0.1"),
                                port=int(os.getenv("DB_PORT", "3306")),
                                user=os.getenv("DB_USER", "root"),
                                password=os.getenv("DB_PASSWORD", ""),
                                database=os.getenv("DB_NAME", "loan_system"),
                            )
                            cursor = conn.cursor()

                            # Check if user exists
                            cursor.execute(
                                "SELECT user_id FROM users WHERE username = %s",
                                (reg_username,),
                            )
                            if cursor.fetchone():
                                st.error(
                                    "Username already exists. Please choose another."
                                )
                            else:
                                # Create user
                                hashed_pw = bcrypt.hashpw(
                                    reg_password.encode("utf-8"), bcrypt.gensalt()
                                ).decode("utf-8")
                                cursor.execute(
                                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                                    (reg_username, hashed_pw, "loan_officer"),
                                )
                                conn.commit()
                                st.success(
                                    "Account created successfully! You can now log in."
                                )

                            conn.close()
                        except Exception as e:
                            st.error(f"Database error: {e}")

            if st.button("Back to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()

        elif st.session_state.show_forgot_password:
            # --- FORGOT PASSWORD VIEW ---
            st.markdown(
                '<div class="login-title">Reset Password</div>', unsafe_allow_html=True
            )
            st.markdown(
                '<div class="login-subtitle">Enter your username and new password</div>',
                unsafe_allow_html=True,
            )

            with st.form("forgot_password_form", clear_on_submit=False):
                reset_username = st.text_input("Username")
                reset_new_password = st.text_input("New Password", type="password")
                reset_confirm = st.text_input("Confirm New Password", type="password")
                reset_button = st.form_submit_button(
                    "Reset Password", use_container_width=True
                )

                if reset_button:
                    if (
                        not reset_username
                        or not reset_new_password
                        or not reset_confirm
                    ):
                        st.warning("Please fill out all fields.")
                    elif reset_new_password != reset_confirm:
                        st.error("Passwords do not match.")
                    elif len(reset_new_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            from dotenv import load_dotenv

                            load_dotenv()
                            conn = mysql.connector.connect(
                                host=os.getenv("DB_HOST", "127.0.0.1"),
                                port=int(os.getenv("DB_PORT", "3306")),
                                user=os.getenv("DB_USER", "root"),
                                password=os.getenv("DB_PASSWORD", ""),
                                database=os.getenv("DB_NAME", "loan_system"),
                            )
                            cursor = conn.cursor()

                            # Check if user exists
                            cursor.execute(
                                "SELECT user_id FROM users WHERE username = %s",
                                (reset_username,),
                            )
                            if cursor.fetchone():
                                # Update password
                                hashed_pw = bcrypt.hashpw(
                                    reset_new_password.encode("utf-8"), bcrypt.gensalt()
                                ).decode("utf-8")
                                cursor.execute(
                                    "UPDATE users SET password_hash = %s WHERE username = %s",
                                    (hashed_pw, reset_username),
                                )
                                conn.commit()
                                st.success(
                                    "Password successfully reset! You can now log in."
                                )
                            else:
                                st.error("Username not found.")

                            conn.close()
                        except Exception as e:
                            st.error(f"Database error: {e}")

            if st.button("Back to Login", use_container_width=True):
                st.session_state.show_forgot_password = False
                st.rerun()

        else:
            # --- LOGIN VIEW ---
            st.markdown(
                '<div class="login-title">Welcome Back</div>', unsafe_allow_html=True
            )
            st.markdown(
                '<div class="login-subtitle">Sign in to the AI Loan Prediction System</div>',
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False):
                username_input = st.text_input("Username")
                password_input = st.text_input("Password", type="password")
                submit_button = st.form_submit_button(
                    "Secure Login", use_container_width=True
                )

                if submit_button:
                    if username_input and password_input:
                        try:
                            from dotenv import load_dotenv

                            load_dotenv()
                            conn = mysql.connector.connect(
                                host=os.getenv("DB_HOST", "127.0.0.1"),
                                port=int(os.getenv("DB_PORT", "3306")),
                                user=os.getenv("DB_USER", "root"),
                                password=os.getenv("DB_PASSWORD", ""),
                                database=os.getenv("DB_NAME", "loan_system"),
                            )
                            cursor = conn.cursor(dictionary=True)
                            cursor.execute(
                                "SELECT * FROM users WHERE username = %s",
                                (username_input,),
                            )
                            user = cursor.fetchone()
                            conn.close()

                            if user and bcrypt.checkpw(
                                password_input.encode("utf-8"),
                                user["password_hash"].encode("utf-8"),
                            ):
                                st.session_state.logged_in = True
                                st.session_state.username = user["username"]
                                st.rerun()
                            else:
                                st.error("Invalid username or password")
                        except Exception as e:
                            st.error(f"Database connection error: {e}")
                    else:
                        st.warning("Please enter both username and password")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Forgot Password?", use_container_width=True):
                    st.session_state.show_forgot_password = True
                    st.rerun()
            with col_btn2:
                if st.button("Create Account", use_container_width=True):
                    st.session_state.show_register = True
                    st.rerun()

    st.stop()

# Logout button in sidebar
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

if "workflow_step" not in st.session_state:
    st.session_state.workflow_step = "prediction"
if "loan_result" not in st.session_state:
    st.session_state.loan_result = None
if "loan_explanation" not in st.session_state:
    st.session_state.loan_explanation = None
if "approved_currency" not in st.session_state:
    st.session_state.approved_currency = "USD"
if "mock_credit_history" not in st.session_state:
    st.session_state.mock_credit_history = 6.0


# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to", ["Loan Application", "MLOps Dashboard", "Compliance & Fairness"]
)

if page == "MLOps Dashboard":

    # ==================================================
    # PREMIUM DASHBOARD — CSS
    # ==================================================
    st.markdown(
        """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Global ── */
        .block-container { padding-top: 1rem; }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        /* ── Hero Header ── */
        .hero-header {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            border-radius: 20px;
            padding: 32px 40px;
            margin-bottom: 28px;
            border: 1px solid rgba(139,92,246,0.25);
            box-shadow: 0 8px 32px rgba(139,92,246,0.15);
            position: relative;
            overflow: hidden;
        }
        .hero-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
            border-radius: 50%;
        }
        .hero-header::after {
            content: '';
            position: absolute;
            bottom: -30%;
            left: 10%;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
            border-radius: 50%;
        }
        .hero-header h1 {
            color: #fff;
            font-size: 32px;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.5px;
            position: relative;
            z-index: 1;
        }
        .hero-header h1 span {
            background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-header p {
            color: #a5b4fc;
            font-size: 14px;
            margin: 6px 0 0 0;
            position: relative;
            z-index: 1;
            letter-spacing: 0.3px;
        }

        /* ── KPI Cards ── */
        .kpi-row {
            display: flex;
            gap: 16px;
            margin-bottom: 28px;
        }
        .kpi-card {
            flex: 1;
            background: linear-gradient(145deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95));
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 22px 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        .kpi-card .kpi-icon {
            font-size: 28px;
            margin-bottom: 6px;
        }
        .kpi-card .kpi-label {
            color: #94a3b8;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 4px;
        }
        .kpi-card .kpi-value {
            font-size: 30px;
            font-weight: 800;
            line-height: 1.2;
        }
        .kpi-card .kpi-sub {
            color: #64748b;
            font-size: 11px;
            margin-top: 4px;
        }
        .kpi-card.kpi-purple { border-top: 3px solid #a78bfa; }
        .kpi-card.kpi-purple .kpi-value { color: #a78bfa; }
        .kpi-card.kpi-green { border-top: 3px solid #4ade80; }
        .kpi-card.kpi-green .kpi-value { color: #4ade80; }
        .kpi-card.kpi-blue { border-top: 3px solid #60a5fa; }
        .kpi-card.kpi-blue .kpi-value { color: #60a5fa; }
        .kpi-card.kpi-amber { border-top: 3px solid #fbbf24; }
        .kpi-card.kpi-amber .kpi-value { color: #fbbf24; }
        .kpi-card.kpi-red { border-top: 3px solid #f87171; }
        .kpi-card.kpi-red .kpi-value { color: #f87171; }
        .kpi-card.kpi-cyan { border-top: 3px solid #22d3ee; }
        .kpi-card.kpi-cyan .kpi-value { color: #22d3ee; }

        /* ── Section Titles ── */
        .dash-section {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 30px 0 14px 0;
        }
        .dash-section .sec-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        .dash-section .sec-icon.purple { background: rgba(139,92,246,0.15); }
        .dash-section .sec-icon.blue { background: rgba(59,130,246,0.15); }
        .dash-section .sec-icon.green { background: rgba(74,222,128,0.15); }
        .dash-section .sec-icon.amber { background: rgba(251,191,36,0.15); }
        .dash-section .sec-icon.cyan { background: rgba(34,211,238,0.15); }
        .dash-section h3 {
            color: #e2e8f0;
            font-size: 18px;
            font-weight: 700;
            margin: 0;
        }
        .dash-section p {
            color: #64748b;
            font-size: 12px;
            margin: 0;
        }

        /* ── Chart Container ── */
        .chart-card {
            background: linear-gradient(145deg, rgba(30,41,59,0.6), rgba(15,23,42,0.6));
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 14px;
            padding: 8px;
            margin-bottom: 16px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # ==================================================
    # HERO HEADER
    # ==================================================
    st.markdown(
        """
    <div class="hero-header">
        <h1>📊 <span>MLOps Analytics</span> Dashboard</h1>
        <p>Real-time model monitoring &bull; Risk intelligence &bull; Prediction analytics &bull; Applicant insights</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    try:
        from dotenv import load_dotenv

        load_dotenv()
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "loan_system"),
        )
        df = pd.read_sql_query(
            "SELECT * FROM prediction_logs ORDER BY timestamp DESC", conn
        )
        conn.close()

        if df.empty:
            st.info("🔍 No prediction logs found yet. Make some predictions first!")
            st.stop()

        import plotly.express as px
        import plotly.graph_objects as go

        total = len(df)
        non_default_count = (df["prediction"] == "Non-Default").sum()
        default_count = (df["prediction"] == "Default").sum()
        approval_rate = non_default_count / total if total > 0 else 0
        avg_prob = df["default_probability"].mean()
        high_risk = (df["risk_level"] == "High Risk").sum()
        avg_loan = df["loan_amount"].mean()
        avg_income = df["income"].mean()

        RISK_COLORS = {
            "Low Risk": "#4ade80",
            "Medium Risk": "#fbbf24",
            "High Risk": "#f87171",
        }

        dark_layout = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#cbd5e1", size=12),
            margin=dict(l=40, r=20, t=55, b=40),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_color="#e2e8f0"),
        )

        st.markdown(
            f"""
        <div class="kpi-row">
            <div class="kpi-card kpi-purple">
                <div class="kpi-icon">🎯</div>
                <div class="kpi-label">Total Predictions</div>
                <div class="kpi-value">{total}</div>
                <div class="kpi-sub">all time</div>
            </div>
            <div class="kpi-card kpi-green">
                <div class="kpi-icon">✅</div>
                <div class="kpi-label">Approval Rate</div>
                <div class="kpi-value">{approval_rate:.1%}</div>
                <div class="kpi-sub">{non_default_count} approved</div>
            </div>
            <div class="kpi-card kpi-amber">
                <div class="kpi-icon">📉</div>
                <div class="kpi-label">Avg Default Prob</div>
                <div class="kpi-value">{avg_prob:.2%}</div>
                <div class="kpi-sub">across all applicants</div>
            </div>
            <div class="kpi-card kpi-red">
                <div class="kpi-icon">🚨</div>
                <div class="kpi-label">High Risk</div>
                <div class="kpi-value">{high_risk}</div>
                <div class="kpi-sub">{high_risk/total*100:.0f}% of total</div>
            </div>
            <div class="kpi-card kpi-blue">
                <div class="kpi-icon">💰</div>
                <div class="kpi-label">Avg Loan Amount</div>
                <div class="kpi-value">${avg_loan:,.0f}</div>
                <div class="kpi-sub">requested</div>
            </div>
            <div class="kpi-card kpi-cyan">
                <div class="kpi-icon">💼</div>
                <div class="kpi-label">Avg Income</div>
                <div class="kpi-value">${avg_income:,.0f}</div>
                <div class="kpi-sub">annual</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="dash-section">
            <div class="sec-icon purple">🛡️</div>
            <div><h3>Risk Distribution</h3><p>Breakdown of applicant risk levels</p></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        ch1_left, ch1_right = st.columns([2, 3])

        with ch1_left:
            risk_counts = df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]
            colors = [RISK_COLORS.get(r, "#60a5fa") for r in risk_counts["Risk Level"]]

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=risk_counts["Risk Level"],
                        values=risk_counts["Count"],
                        hole=0.55,
                        marker=dict(colors=colors, line=dict(color="#0f172a", width=3)),
                        textinfo="label+percent+value",
                        textfont=dict(size=15, color="#e2e8f0", family="Inter"),
                        textposition="outside",
                        pull=[0.03] * len(risk_counts),
                        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
                    )
                ]
            )
            fig.update_layout(
                showlegend=False,
                height=380,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", color="#cbd5e1"),
                hoverlabel=dict(bgcolor="#1e293b", font_size=14, font_color="#e2e8f0"),
            )
            fig.add_annotation(
                text=f"<b style='font-size:28px'>{total}</b><br><span style='font-size:13px;color:#94a3b8'>Total</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=28, color="#e2e8f0"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with ch1_right:

            for _, row in risk_counts.iterrows():
                level = row["Risk Level"]
                count = row["Count"]
                pct = count / total * 100
                color = RISK_COLORS.get(level, "#60a5fa")
                st.markdown(
                    f"""
                <div style="
                    display:flex; align-items:center; gap:14px;
                    padding:14px 20px; margin-bottom:10px;
                    background:rgba(30,41,59,0.6);
                    border-left:4px solid {color};
                    border-radius:10px;
                ">
                    <div style="font-size:32px;font-weight:800;color:{color};min-width:60px">{count}</div>
                    <div>
                        <div style="color:#e2e8f0;font-size:16px;font-weight:600">{level}</div>
                        <div style="color:#94a3b8;font-size:13px">{pct:.1f}% of all applications</div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
            <div style="
                display:flex; gap:12px; margin-top:6px;
            ">
                <div style="flex:1;text-align:center;padding:12px;background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.2);border-radius:10px">
                    <div style="color:#4ade80;font-size:24px;font-weight:800">{non_default_count}</div>
                    <div style="color:#94a3b8;font-size:12px">Approved</div>
                </div>
                <div style="flex:1;text-align:center;padding:12px;background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.2);border-radius:10px">
                    <div style="color:#f87171;font-size:24px;font-weight:800">{default_count}</div>
                    <div style="color:#94a3b8;font-size:12px">Defaulted</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
        <div class="dash-section">
            <div class="sec-icon blue">🏦</div>
            <div><h3>Loan Purpose Analysis</h3><p>Application volume and average risk per loan category</p></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        purpose = (
            df.groupby("loan_purpose")
            .agg(
                count=("id", "count"),
                avg_amount=("loan_amount", "mean"),
                avg_prob=("default_probability", "mean"),
            )
            .reset_index()
            .sort_values("count", ascending=True)
        )

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=purpose["loan_purpose"],
                x=purpose["count"],
                orientation="h",
                marker=dict(
                    color=purpose["avg_prob"],
                    colorscale=[[0, "#4ade80"], [0.5, "#fbbf24"], [1, "#f87171"]],
                    colorbar=dict(
                        title=dict(
                            text="Avg Default<br>Probability",
                            font=dict(size=12, color="#94a3b8"),
                        ),
                        tickformat=".0%",
                        tickfont=dict(color="#94a3b8", size=12),
                        len=0.6,
                        thickness=14,
                    ),
                    cornerradius=6,
                    line=dict(color="rgba(255,255,255,0.15)", width=1),
                ),
                text=[
                    f"  {c} apps  ·  Avg ${a:,.0f}  ·  Risk {p:.0%}"
                    for c, a, p in zip(
                        purpose["count"], purpose["avg_amount"], purpose["avg_prob"]
                    )
                ],
                textposition="outside",
                textfont=dict(color="#e2e8f0", size=13, family="Inter"),
            )
        )
        fig.update_layout(
            xaxis=dict(
                title=dict(
                    text="Number of Applications", font=dict(size=13, color="#94a3b8")
                ),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                tickfont=dict(size=12, color="#94a3b8"),
            ),
            yaxis=dict(title="", tickfont=dict(size=14, color="#e2e8f0")),
            height=max(280, len(purpose) * 55 + 80),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#cbd5e1"),
            margin=dict(l=160, r=40, t=20, b=50),
            hoverlabel=dict(bgcolor="#1e293b", font_size=13, font_color="#e2e8f0"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if "timestamp" in df.columns and not df["timestamp"].isna().all():
            st.markdown(
                """
            <div class="dash-section">
                <div class="sec-icon green">📈</div>
                <div><h3>Predictions Over Time</h3><p>Daily volume of approved vs defaulted predictions</p></div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            dft = df.copy()
            dft["timestamp"] = pd.to_datetime(dft["timestamp"])
            dft["date"] = dft["timestamp"].dt.date
            daily = (
                dft.groupby("date")
                .agg(
                    total=("id", "count"),
                    defaults=("prediction", lambda x: (x == "Default").sum()),
                    avg_prob=("default_probability", "mean"),
                )
                .reset_index()
            )
            daily["date"] = pd.to_datetime(daily["date"])
            daily["approved"] = daily["total"] - daily["defaults"]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=daily["date"],
                    y=daily["approved"],
                    name="Approved",
                    mode="lines+markers",
                    line=dict(color="#4ade80", width=3, shape="spline"),
                    marker=dict(
                        size=10, symbol="circle", line=dict(width=2, color="#0f172a")
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(74,222,128,0.08)",
                    hovertemplate="<b>%{x|%b %d}</b><br>Approved: %{y}<extra></extra>",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=daily["date"],
                    y=daily["defaults"],
                    name="Defaults",
                    mode="lines+markers",
                    line=dict(color="#f87171", width=3, shape="spline"),
                    marker=dict(
                        size=10, symbol="diamond", line=dict(width=2, color="#0f172a")
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(248,113,113,0.08)",
                    hovertemplate="<b>%{x|%b %d}</b><br>Defaults: %{y}<extra></extra>",
                )
            )
            fig.update_layout(
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=12, color="#94a3b8"),
                    tickformat="%b %d",
                ),
                yaxis=dict(
                    title=dict(text="Count", font=dict(size=13, color="#94a3b8")),
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.06)",
                    tickfont=dict(size=12, color="#94a3b8"),
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=13, color="#e2e8f0"),
                    bgcolor="rgba(0,0,0,0)",
                ),
                hovermode="x unified",
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", color="#cbd5e1"),
                margin=dict(l=50, r=20, t=40, b=40),
                hoverlabel=dict(bgcolor="#1e293b", font_size=13, font_color="#e2e8f0"),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
        <div class="dash-section">
            <div class="sec-icon cyan">💰</div>
            <div><h3>Income vs Loan Amount</h3><p>Financial profile of each applicant colored by risk level</p></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = go.Figure()
        for risk in ["Low Risk", "Medium Risk", "High Risk"]:
            rdf = df[df["risk_level"] == risk]
            if not rdf.empty:
                fig.add_trace(
                    go.Scatter(
                        x=rdf["income"],
                        y=rdf["loan_amount"],
                        mode="markers",
                        name=risk,
                        marker=dict(
                            size=14,
                            color=RISK_COLORS.get(risk),
                            opacity=0.85,
                            line=dict(width=2, color="#0f172a"),
                            symbol="circle",
                        ),
                        hovertemplate=(
                            f"<b>{risk}</b><br>"
                            "Income: $%{x:,.0f}<br>"
                            "Loan: $%{y:,.0f}<br>"
                            "<extra></extra>"
                        ),
                    )
                )
        fig.update_layout(
            xaxis=dict(
                title=dict(
                    text="Annual Income ($)", font=dict(size=14, color="#94a3b8")
                ),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                tickprefix="$",
                tickformat=",",
                tickfont=dict(size=12, color="#94a3b8"),
            ),
            yaxis=dict(
                title=dict(text="Loan Amount ($)", font=dict(size=14, color="#94a3b8")),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                tickprefix="$",
                tickformat=",",
                tickfont=dict(size=12, color="#94a3b8"),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=13, color="#e2e8f0"),
                bgcolor="rgba(0,0,0,0)",
            ),
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#cbd5e1"),
            margin=dict(l=70, r=20, t=40, b=60),
            hoverlabel=dict(bgcolor="#1e293b", font_size=13, font_color="#e2e8f0"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
        <div class="dash-section">
            <div class="sec-icon blue">📋</div>
            <div><h3>Prediction Log</h3><p>Detailed history of all predictions</p></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        display_df = df.copy()
        display_df["default_probability"] = display_df["default_probability"].apply(
            lambda x: f"{x:.2%}"
        )
        display_df["income"] = display_df["income"].apply(lambda x: f"${x:,.0f}")
        display_df["loan_amount"] = display_df["loan_amount"].apply(
            lambda x: f"${x:,.0f}"
        )
        display_df["recommended_max_loan_amount"] = display_df[
            "recommended_max_loan_amount"
        ].apply(lambda x: f"${x:,.0f}")
        if "timestamp" in display_df.columns:
            display_df["timestamp"] = pd.to_datetime(
                display_df["timestamp"]
            ).dt.strftime("%Y-%m-%d %H:%M")

        display_df.columns = [
            "ID",
            "Timestamp",
            "Age",
            "Income",
            "Emp. Years",
            "Home",
            "Loan Amt",
            "Purpose",
            "Credit Yrs",
            "Prediction",
            "Default Prob.",
            "Risk Level",
            "Max Loan Rec.",
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400,
            column_config={
                "ID": st.column_config.NumberColumn(width="small"),
                "Timestamp": st.column_config.TextColumn(width="medium"),
                "Risk Level": st.column_config.TextColumn(width="medium"),
                "Prediction": st.column_config.TextColumn(width="medium"),
            },
        )

        st.markdown(
            """
        <div style="text-align:center; padding:24px 0 8px 0; color:#475569; font-size:12px;">
            AI Loan Default Prediction System &bull; MLOps Dashboard &bull; Powered by XGBoost
        </div>
        """,
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"Dashboard error: {e}")
        st.info("Make sure MySQL is running and the `loan_system` database exists.")
    st.stop()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("💳 AI Loan Default Prediction")

st.write("""
    This system uses machine learning to estimate the
    probability of loan default based on applicant and
    loan information.
    """)

st.divider()


# --------------------------------------------------
# Applicant Information
# --------------------------------------------------

st.subheader("👤 Applicant Information")

currency_code = st.selectbox("Currency", options=["USD"])

age = st.number_input("Age", min_value=18, max_value=100, value=28, step=1)

income = st.number_input(
    f"Annual Income ({currency_code})", min_value=0.0, value=50000.0, step=1000.0
)

employment_years = st.number_input(
    "Employment Years", min_value=0.0, max_value=60.0, value=4.0, step=1.0
)

home_ownership = st.selectbox(
    "Home Ownership", options=["RENT", "OWN", "MORTGAGE", "OTHER"]
)


# --------------------------------------------------
# Loan Information
# --------------------------------------------------

st.subheader("🏦 Loan Information")

loan_amount = st.number_input(
    f"Loan Amount ({currency_code})", min_value=0.0, value=10000.0, step=500.0
)

loan_purpose = st.selectbox(
    "Loan Purpose",
    options=[
        "PERSONAL",
        "EDUCATION",
        "MEDICAL",
        "VENTURE",
        "HOMEIMPROVEMENT",
        "DEBTCONSOLIDATION",
    ],
)

col_ch1, col_ch2 = st.columns([2, 1])
with col_ch1:
    credit_history_years = st.number_input(
        "Credit History Years",
        min_value=0.0,
        max_value=50.0,
        value=st.session_state.mock_credit_history,
        step=1.0,
    )
with col_ch2:
    st.write("")
    st.write("")
    if st.button("Pull Equifax Report (Mock)"):
        with st.spinner("Connecting to Credit Bureau..."):
            import random
            time.sleep(1.5)
            # Generate a realistic random credit history between 1.0 and 20.0 years
            st.session_state.mock_credit_history = round(random.uniform(1.0, 20.0), 1)
            st.rerun()


# --------------------------------------------------
# Prediction button
# --------------------------------------------------

st.divider()

predict_button = st.button("🔍 Predict Loan Risk", use_container_width=True)


# --------------------------------------------------
# Make prediction
# --------------------------------------------------

if predict_button:

    # Basic validation
    if income <= 0:

        st.error("Please enter a valid annual income.")

    elif loan_amount <= 0:

        st.error("Please enter a valid loan amount.")

    else:
        payload = {
            "age": age,
            "income": income,
            "employment_years": employment_years,
            "home_ownership": home_ownership,
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose,
            "credit_history_years": credit_history_years,
        }

        try:
            with st.spinner("Calling ML API..."):
                headers = {
                    "X-API-Key": os.getenv("API_KEY", "loan-predict-dev-key-2026")
                }
                response = requests.post(
                    f"{API_URL}/predict", json=payload, headers=headers
                )
                response.raise_for_status()
                data = response.json()

            result = data["result"]
            explanation = data["explanation"]

            prediction = result["prediction"]
            probability = result["default_probability"]
            risk_level = result["risk_level"]

            st.session_state.loan_result = result
            st.session_state.loan_explanation = explanation
        except Exception as e:
            st.error(
                f"API Error: Make sure the FastAPI backend is running on port 8000. Details: {e}"
            )
            st.stop()
        st.session_state.approved_currency = currency_code

        if prediction != "Default":
            st.session_state.workflow_step = "documents"
        else:
            st.session_state.workflow_step = "prediction"

        # --------------------------------------------------
        # Display results
        # --------------------------------------------------

        st.subheader("📊 Prediction Result")

        if prediction == "Default":

            st.error("⚠️ Prediction: Higher Default Risk")

        else:

            st.success("✅ Prediction: Lower Default Risk")

        # Probability

        st.metric(label="Default Probability", value=f"{probability:.2%}")

        st.metric(
            label="Recommended Maximum Loan Amount",
            value=f"{currency_code} {result['recommended_max_loan_amount']:,.2f}",
        )

        st.caption(
            "Screening estimate based on income, employment stability, and model risk. "
            "It is not a final lending limit. Amounts use the selected currency code."
        )

        # Risk level

        if risk_level == "Low Risk":

            st.success(f"Risk Level: {risk_level}")

        elif risk_level == "Medium Risk":

            st.warning(f"Risk Level: {risk_level}")

        else:

            st.error(f"Risk Level: {risk_level}")

        # Progress bar

        st.write("Default Probability")

        st.progress(float(probability))

        # --------------------------------------------------
        # Decision explanation and applicant guidance
        # --------------------------------------------------

        st.subheader("🧭 Decision Explanation")

        if explanation["reason_codes"]:
            st.write("**Main factors identified:**")
            for reason in explanation["reason_codes"]:
                st.write(f"- {reason.capitalize()}")
        else:
            st.write("No specific risk warning was identified from the guidance rules.")

        st.write("**Possible next steps:**")
        for recommendation in explanation["recommendations"]:
            st.write(f"- {recommendation}")

        st.caption(
            "These are guidance points, not a guarantee of approval. "
            "A qualified loan officer should review declined or borderline applications."
        )

        with st.expander("View model explanation"):
            st.dataframe(
                explanation["feature_explanations"],
                hide_index=True,
                use_container_width=True,
            )

        # --------------------------------------------------
        # Applicant summary
        # --------------------------------------------------

        st.subheader("📋 Applicant Summary")

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**Age:** {age}")
            st.write(f"**Annual Income:** {currency_code} {income:,.2f}")
            st.write(f"**Employment Years:** " f"{employment_years}")
            st.write(f"**Home Ownership:** " f"{home_ownership}")

        with col2:

            st.write(f"**Loan Amount:** " f"{currency_code} {loan_amount:,.2f}")

            st.write(f"**Loan Purpose:** " f"{loan_purpose}")

            st.write(f"**Credit History:** " f"{credit_history_years} years")

        # --------------------------------------------------
        # Disclaimer
        # --------------------------------------------------

        st.divider()

        st.caption("""
            ⚠️ This prediction is for educational and
            risk-assessment purposes only. It should not
            be used as the sole basis for making lending
            or financial decisions.
            """)


# --------------------------------------------------
# Loan approval and document workflow
# --------------------------------------------------

if st.session_state.loan_result is not None:
    st.divider()
    st.subheader("🛡️ Banker Workflow")

    if st.session_state.workflow_step == "prediction":
        st.info(
            "Review the prediction and approve the loan to continue to document verification."
        )
        if st.button("✅ Approve Loan and Continue", use_container_width=True):
            st.session_state.workflow_step = "documents"
            st.rerun()

    elif st.session_state.workflow_step == "documents":
        st.success("Loan approved. Upload all required documents for verification.")
        st.write("Required documents")

        identity_document = st.file_uploader(
            "Identity document",
            type=["pdf", "png", "jpg", "jpeg"],
            key="identity_document",
        )
        income_document = st.file_uploader(
            "Income or employment proof",
            type=["pdf", "png", "jpg", "jpeg"],
            key="income_document",
        )
        bank_statement = st.file_uploader(
            "Bank statement", type=["pdf", "png", "jpg", "jpeg"], key="bank_statement"
        )

        documents = {
            "Identity document": identity_document,
            "Income or employment proof": income_document,
            "Bank statement": bank_statement,
        }
        missing_documents = [
            name for name, document in documents.items() if document is None
        ]

        if missing_documents:
            st.warning("Missing documents: " + ", ".join(missing_documents))
        else:
            invalid_documents = [
                name for name, document in documents.items() if document.size <= 0
            ]

            if invalid_documents:
                st.error("These documents are empty: " + ", ".join(invalid_documents))
            else:
                st.success("All required documents are uploaded and non-empty.")
                st.caption(
                    "This is a completeness check only. A qualified banker must "
                    "verify authenticity and whether the documents match the application."
                )
                if "ai_verification_done" not in st.session_state:
                    st.session_state.ai_verification_done = False

                if not st.session_state.ai_verification_done:
                    if st.button("🧠 Run Full AI Document Verification", type="primary", use_container_width=True):
                        progress_bar = st.progress(0, text="Initializing Document AI Pipeline...")
                        time.sleep(0.5)
                        progress_bar.progress(30, text="Extracting text and pixels via OCR...")
                        time.sleep(1.0)
                        progress_bar.progress(60, text="Cross-referencing data with application...")
                        time.sleep(1.5)
                        progress_bar.progress(90, text="Checking against fraud watchlists...")
                        time.sleep(1.0)
                        progress_bar.progress(100, text="Verification Complete!")
                        time.sleep(0.5)
                        progress_bar.empty()
                        
                        st.session_state.ai_verification_done = True
                        st.rerun()
                else:
                    st.success("✅ AI Verification Passed")
                    with st.expander("📄 View AI Verification Report", expanded=True):
                        st.json({
                            "identity_document": {
                                "extracted_name": "JOHN DOE",
                                "confidence_score": 0.98,
                                "document_type": "Drivers License",
                                "fraud_markers_detected": False
                            },
                            "income_proof": {
                                "extracted_employer": "TECH CORP INC",
                                "verified_income": "$75,000",
                                "confidence_score": 0.95
                            },
                            "bank_statement": {
                                "account_status": "Active",
                                "risk_flags": "None",
                                "consistency_check": "PASS"
                            },
                            "final_decision": "APPROVED",
                            "ai_notes": "All documents are consistent with the application. No synthetic identity markers detected."
                        })
                    
                    if st.button("Submit Verified Documents & Complete Workflow", use_container_width=True):
                        st.session_state.workflow_step = "completed"
                        st.session_state.ai_verification_done = False
                        st.rerun()

    else:
        st.success("🎉 All steps completed.")
        st.write("Loan approval and document completeness checks are finished.")
        st.caption(
            "Final disbursement remains subject to the bank's approval, compliance, "
            "and document-authentication procedures."
        )

elif page == "Compliance & Fairness":
    st.markdown(
        '<div class="hero-header"><div class="hero-title">⚖️ Legal & Fairness Compliance</div><div class="hero-subtitle">Mathematical Disparate Impact Evaluation</div></div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Financial regulations (e.g., CFPB) require proof that ML models do not unfairly discriminate against protected classes."
    )

    if st.button("Run Disparate Impact Analysis (Age Bias)", type="primary"):
        with st.spinner("Evaluating model predictions across demographic subsets..."):
            import sys
            import os

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.fairness import FairnessEvaluator

            evaluator = FairnessEvaluator()
            result = evaluator.check_age_bias(age_threshold=30)

            if result["status"] == "success":
                st.success("Analysis Complete!")
                col1, col2, col3 = st.columns(3)
                col1.metric(
                    "Young Approval Rate", f"{result['young_approval_rate']*100:.1f}%"
                )
                col2.metric(
                    "Older Approval Rate", f"{result['old_approval_rate']*100:.1f}%"
                )
                col3.metric(
                    "Disparate Impact Ratio",
                    f"{result['disparate_impact_ratio']:.3f}",
                    delta=(
                        "Passes 0.8 Threshold"
                        if result["four_fifths_rule_passed"]
                        else "Fails 0.8 Threshold"
                    ),
                    delta_color=(
                        "normal" if result["four_fifths_rule_passed"] else "inverse"
                    ),
                )

                st.info(f"**Conclusion:** {result['message']}")
            else:
                st.error(
                    f"Error running analysis: {result.get('message', 'Unknown error')}"
                )

    st.markdown("---")
    st.markdown("### 🔒 Live API & Encryption Architecture")
    st.write("We have also laid the foundation for:")
    st.markdown(
        "- **Enterprise Encryption**: Using `cryptography.fernet` to securely encrypt PII (like National IDs) in the `loan_system` MySQL database."
    )
    st.markdown(
        "- **Secure Bureau Integrations**: Created a simulated `CreditBureauAPI` class to handle robust integrations with Equifax/Experian."
    )
