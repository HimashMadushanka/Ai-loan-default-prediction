import streamlit as st
import sys
import os
import requests
import time
import pandas as pd
import mysql.connector

# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

API_URL = "http://localhost:8000"

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Loan Default Prediction",
    page_icon="💳",
    layout="wide"
)

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
page = st.sidebar.radio("Go to", ["Loan Application", "MLOps Dashboard"])

if page == "MLOps Dashboard":

    # ==================================================
    # PREMIUM DASHBOARD — CSS
    # ==================================================
    st.markdown("""
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
    """, unsafe_allow_html=True)

    # ==================================================
    # HERO HEADER
    # ==================================================
    st.markdown("""
    <div class="hero-header">
        <h1>📊 <span>MLOps Analytics</span> Dashboard</h1>
        <p>Real-time model monitoring &bull; Risk intelligence &bull; Prediction analytics &bull; Applicant insights</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        conn = mysql.connector.connect(
            host="127.0.0.1", port=3306,
            user="root", password="",
            database="loan_system"
        )
        df = pd.read_sql_query("SELECT * FROM prediction_logs ORDER BY timestamp DESC", conn)
        conn.close()

        if df.empty:
            st.info("🔍 No prediction logs found yet. Make some predictions first!")
            st.stop()

        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import numpy as np

        # ── Computed Metrics ──
        total = len(df)
        non_default_count = (df['prediction'] == 'Non-Default').sum()
        default_count = (df['prediction'] == 'Default').sum()
        approval_rate = non_default_count / total if total > 0 else 0
        avg_prob = df['default_probability'].mean()
        high_risk = (df['risk_level'] == 'High Risk').sum()
        avg_loan = df['loan_amount'].mean()
        avg_income = df['income'].mean()

        # ── Color Palette ──
        RISK_COLORS = {"Low Risk": "#4ade80", "Medium Risk": "#fbbf24", "High Risk": "#f87171"}
        PRED_COLORS = {"Non-Default": "#4ade80", "Default": "#f87171"}
        GRADIENT_BLUE = [[0, "#1e3a5f"], [0.5, "#3b82f6"], [1, "#93c5fd"]]
        GRADIENT_PURPLE = [[0, "#3b0764"], [0.5, "#7c3aed"], [1, "#c4b5fd"]]

        dark_layout = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#cbd5e1", size=12),
            margin=dict(l=40, r=20, t=55, b=40),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_color="#e2e8f0")
        )

        # ==================================================
        # KPI CARDS — 6 metrics
        # ==================================================
        st.markdown(f"""
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
        """, unsafe_allow_html=True)

        # ==================================================
        # SECTION 1 — Risk Intelligence
        # ==================================================
        st.markdown("""
        <div class="dash-section">
            <div class="sec-icon purple">🛡️</div>
            <div><h3>Risk Intelligence</h3><p>Model confidence and risk distribution</p></div>
        </div>
        """, unsafe_allow_html=True)

        s1c1, s1c2, s1c3 = st.columns([1, 1, 1])

        # ── 1A: Risk Donut ──
        with s1c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            risk_counts = df['risk_level'].value_counts().reset_index()
            risk_counts.columns = ['Risk Level', 'Count']
            colors = [RISK_COLORS.get(r, "#60a5fa") for r in risk_counts['Risk Level']]

            fig = go.Figure(data=[go.Pie(
                labels=risk_counts['Risk Level'],
                values=risk_counts['Count'],
                hole=0.6,
                marker=dict(colors=colors, line=dict(color="#0f172a", width=2)),
                textinfo='label+percent',
                textfont=dict(size=12, color="#e2e8f0"),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>"
            )])
            fig.update_layout(
                title=dict(text="Risk Distribution", font=dict(size=15, color="#e2e8f0")),
                showlegend=False, **dark_layout
            )
            fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:11px;color:#94a3b8'>Total</span>",
                               x=0.5, y=0.5, showarrow=False, font=dict(size=22, color="#e2e8f0"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 1B: Risk Gauge ──
        with s1c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=avg_prob * 100,
                number=dict(suffix="%", font=dict(size=36, color="#e2e8f0")),
                title=dict(text="Model Risk Score", font=dict(size=15, color="#e2e8f0")),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor="#475569", dtick=20,
                              tickfont=dict(color="#94a3b8")),
                    bar=dict(color="#8b5cf6", thickness=0.3),
                    bgcolor="rgba(0,0,0,0)",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 30], color="rgba(74,222,128,0.15)"),
                        dict(range=[30, 60], color="rgba(251,191,36,0.15)"),
                        dict(range=[60, 100], color="rgba(248,113,113,0.15)")
                    ],
                    threshold=dict(line=dict(color="#f87171", width=3), thickness=0.8, value=60)
                )
            ))
            fig.update_layout(height=310, **dark_layout)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 1C: Prediction Outcome ──
        with s1c3:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            pred_counts = df['prediction'].value_counts().reset_index()
            pred_counts.columns = ['Prediction', 'Count']
            p_colors = [PRED_COLORS.get(p, "#60a5fa") for p in pred_counts['Prediction']]

            fig = go.Figure(data=[go.Bar(
                x=pred_counts['Prediction'], y=pred_counts['Count'],
                marker=dict(color=p_colors,
                            line=dict(color="rgba(255,255,255,0.1)", width=1),
                            cornerradius=6),
                text=pred_counts['Count'], textposition='outside',
                textfont=dict(color="#e2e8f0", size=16, family="Inter"),
                width=0.5
            )])
            fig.update_layout(
                title=dict(text="Prediction Outcomes", font=dict(size=15, color="#e2e8f0")),
                xaxis=dict(showgrid=False, tickfont=dict(size=13)),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", title=""),
                **dark_layout
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # SECTION 2 — Probability & Financial Analysis
        # ==================================================
        st.markdown("""
        <div class="dash-section">
            <div class="sec-icon blue">💹</div>
            <div><h3>Probability & Financial Analysis</h3><p>Default probability patterns and loan insights</p></div>
        </div>
        """, unsafe_allow_html=True)

        s2c1, s2c2 = st.columns(2)

        # ── 2A: Probability Distribution ──
        with s2c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = go.Figure()
            for risk in ["Low Risk", "Medium Risk", "High Risk"]:
                rdf = df[df['risk_level'] == risk]
                if not rdf.empty:
                    fig.add_trace(go.Histogram(
                        x=rdf['default_probability'], name=risk,
                        marker_color=RISK_COLORS.get(risk), opacity=0.7,
                        nbinsx=15,
                        hovertemplate=f"{risk}<br>Prob: %{{x:.2%}}<br>Count: %{{y}}<extra></extra>"
                    ))
            fig.add_vline(x=avg_prob, line_dash="dot", line_color="#a78bfa", line_width=2,
                          annotation_text=f"  Avg: {avg_prob:.2%}",
                          annotation_font=dict(color="#a78bfa", size=12))
            fig.update_layout(
                title=dict(text="Default Probability Distribution", font=dict(size=15, color="#e2e8f0")),
                xaxis=dict(title="Default Probability", tickformat=".0%", showgrid=False),
                yaxis=dict(title="Frequency", showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
                barmode="overlay", **dark_layout
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 2B: Loan Purpose Breakdown ──
        with s2c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            purpose = df.groupby('loan_purpose').agg(
                count=('id', 'count'),
                avg_amount=('loan_amount', 'mean'),
                avg_prob=('default_probability', 'mean')
            ).reset_index().sort_values('count', ascending=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=purpose['loan_purpose'], x=purpose['count'],
                orientation='h', name='Applications',
                marker=dict(color=purpose['avg_prob'],
                            colorscale=[[0, "#4ade80"], [0.5, "#fbbf24"], [1, "#f87171"]],
                            colorbar=dict(title=dict(text="Avg Risk", font=dict(size=11, color="#94a3b8")),
                                          tickformat=".0%", tickfont=dict(color="#94a3b8")),
                            cornerradius=4,
                            line=dict(color="rgba(255,255,255,0.1)", width=1)),
                text=[f" {c}  |  avg ${a:,.0f}" for c, a in zip(purpose['count'], purpose['avg_amount'])],
                textposition='outside', textfont=dict(color="#cbd5e1", size=11)
            ))
            fig.update_layout(
                title=dict(text="Loans by Purpose (colored by risk)", font=dict(size=15, color="#e2e8f0")),
                xaxis=dict(title="Count", showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
                yaxis=dict(title=""), **dark_layout
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # SECTION 3 — Applicant Intelligence
        # ==================================================
        st.markdown("""
        <div class="dash-section">
            <div class="sec-icon green">👥</div>
            <div><h3>Applicant Intelligence</h3><p>Income patterns, demographics, and risk correlations</p></div>
        </div>
        """, unsafe_allow_html=True)

        s3c1, s3c2 = st.columns(2)

        # ── 3A: Income vs Loan Scatter (bubble) ──
        with s3c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = px.scatter(
                df, x="income", y="loan_amount",
                color="risk_level", size="default_probability",
                size_max=20,
                color_discrete_map=RISK_COLORS,
                hover_data={"age": True, "prediction": True,
                            "default_probability": ":.2%",
                            "income": ":$,.0f", "loan_amount": ":$,.0f"},
                labels={"income": "Annual Income ($)", "loan_amount": "Loan Amount ($)",
                         "risk_level": "Risk"}
            )
            fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.2)")))
            fig.update_layout(
                title=dict(text="Income vs Loan Amount", font=dict(size=15, color="#e2e8f0")),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", tickprefix="$"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", tickprefix="$"),
                **dark_layout
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 3B: Box Plot — Default Prob by Risk Level ──
        with s3c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = go.Figure()
            for risk in ["Low Risk", "Medium Risk", "High Risk"]:
                rdf = df[df['risk_level'] == risk]
                if not rdf.empty:
                    fig.add_trace(go.Box(
                        y=rdf['default_probability'], name=risk,
                        marker_color=RISK_COLORS.get(risk),
                        boxmean='sd',
                        line=dict(color=RISK_COLORS.get(risk)),
                        fillcolor=RISK_COLORS.get(risk, "#60a5fa").replace(")", ",0.15)").replace("rgb", "rgba") if "rgb" in RISK_COLORS.get(risk, "") else RISK_COLORS.get(risk) + "22"
                    ))
            fig.update_layout(
                title=dict(text="Default Probability by Risk Level", font=dict(size=15, color="#e2e8f0")),
                yaxis=dict(title="Default Probability", tickformat=".0%",
                           showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
                xaxis=dict(showgrid=False),
                showlegend=False, **dark_layout
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # SECTION 4 — Demographics & Patterns
        # ==================================================
        st.markdown("""
        <div class="dash-section">
            <div class="sec-icon amber">📊</div>
            <div><h3>Demographics & Patterns</h3><p>Age, housing, and employment risk correlations</p></div>
        </div>
        """, unsafe_allow_html=True)

        s4c1, s4c2, s4c3 = st.columns(3)

        # ── 4A: Age Distribution ──
        with s4c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = go.Figure()
            for risk in ["Low Risk", "Medium Risk", "High Risk"]:
                rdf = df[df['risk_level'] == risk]
                if not rdf.empty:
                    fig.add_trace(go.Violin(
                        y=rdf['age'], name=risk,
                        line_color=RISK_COLORS.get(risk),
                        fillcolor=RISK_COLORS.get(risk) + "33",
                        meanline_visible=True,
                        box_visible=True,
                        points='all',
                        pointpos=-0.5,
                        jitter=0.3
                    ))
            fig.update_layout(
                title=dict(text="Age Distribution", font=dict(size=15, color="#e2e8f0")),
                yaxis=dict(title="Age", showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
                showlegend=False, **dark_layout
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 4B: Home Ownership Stacked ──
        with s4c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            home_data = df.groupby(['home_ownership', 'risk_level']).size().reset_index(name='count')
            fig = px.bar(
                home_data, x='home_ownership', y='count',
                color='risk_level', color_discrete_map=RISK_COLORS,
                barmode='stack',
                labels={"home_ownership": "Ownership", "count": "Count", "risk_level": "Risk"}
            )
            fig.update_traces(marker_line=dict(width=1, color="rgba(255,255,255,0.1)"))
            fig.update_layout(
                title=dict(text="Housing vs Risk", font=dict(size=15, color="#e2e8f0")),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
                **dark_layout
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 4C: Employment Years vs Default ──
        with s4c3:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = px.scatter(
                df, x="employment_years", y="default_probability",
                color="prediction", color_discrete_map=PRED_COLORS,
                size="loan_amount", size_max=18,
                labels={"employment_years": "Employment Years",
                         "default_probability": "Default Prob.",
                         "prediction": "Outcome"},
                hover_data={"income": ":$,.0f", "age": True}
            )
            fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.15)")))
            fig.update_layout(
                title=dict(text="Experience vs Risk", font=dict(size=15, color="#e2e8f0")),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", tickformat=".0%"),
                **dark_layout
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # SECTION 5 — Time & Correlation Analysis
        # ==================================================
        st.markdown("""
        <div class="dash-section">
            <div class="sec-icon cyan">🔬</div>
            <div><h3>Advanced Analytics</h3><p>Temporal trends and feature correlations</p></div>
        </div>
        """, unsafe_allow_html=True)

        s5c1, s5c2 = st.columns(2)

        # ── 5A: Predictions Over Time ──
        with s5c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            if 'timestamp' in df.columns and not df['timestamp'].isna().all():
                dft = df.copy()
                dft['timestamp'] = pd.to_datetime(dft['timestamp'])
                dft['date'] = dft['timestamp'].dt.date
                daily = dft.groupby('date').agg(
                    total=('id', 'count'),
                    defaults=('prediction', lambda x: (x == 'Default').sum()),
                    avg_prob=('default_probability', 'mean')
                ).reset_index()
                daily['date'] = pd.to_datetime(daily['date'])
                daily['approval'] = daily['total'] - daily['defaults']

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily['date'], y=daily['approval'],
                    name='Approved', mode='lines+markers',
                    line=dict(color="#4ade80", width=3),
                    marker=dict(size=8, symbol="circle"),
                    fill='tonexty' if len(daily) > 1 else None,
                    stackgroup='one'
                ))
                fig.add_trace(go.Scatter(
                    x=daily['date'], y=daily['defaults'],
                    name='Defaults', mode='lines+markers',
                    line=dict(color="#f87171", width=3),
                    marker=dict(size=8, symbol="diamond"),
                    stackgroup='one'
                ))
                fig.update_layout(
                    title=dict(text="Predictions Over Time", font=dict(size=15, color="#e2e8f0")),
                    xaxis=dict(showgrid=False, title=""),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", title="Count"),
                    hovermode="x unified", **dark_layout
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Timestamp data not available.")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 5B: Feature Correlation Heatmap ──
        with s5c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            numeric_cols = ['age', 'income', 'employment_years', 'loan_amount',
                            'credit_history_years', 'default_probability']
            available_cols = [c for c in numeric_cols if c in df.columns]
            if len(available_cols) >= 3:
                corr_df = df[available_cols].corr()
                labels = [c.replace('_', ' ').title() for c in corr_df.columns]

                fig = go.Figure(data=go.Heatmap(
                    z=corr_df.values,
                    x=labels, y=labels,
                    colorscale=[[0, "#4ade80"], [0.5, "#1e293b"], [1, "#f87171"]],
                    zmid=0,
                    text=np.round(corr_df.values, 2),
                    texttemplate="%{text}",
                    textfont=dict(size=12, color="#e2e8f0"),
                    hovertemplate="%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>",
                    colorbar=dict(tickfont=dict(color="#94a3b8"),
                                  title=dict(text="r", font=dict(color="#94a3b8")))
                ))
                fig.update_layout(
                    title=dict(text="Feature Correlation Matrix", font=dict(size=15, color="#e2e8f0")),
                    xaxis=dict(tickangle=-45), **dark_layout
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough numeric features for correlation.")
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # SECTION 6 — Radar & Treemap
        # ==================================================
        st.markdown("""
        <div class="dash-section">
            <div class="sec-icon purple">🧠</div>
            <div><h3>Risk Profile & Portfolio</h3><p>Multi-dimensional risk analysis and portfolio overview</p></div>
        </div>
        """, unsafe_allow_html=True)

        s6c1, s6c2 = st.columns(2)

        # ── 6A: Radar — Avg Profile by Risk ──
        with s6c1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            radar_metrics = ['age', 'income', 'employment_years', 'loan_amount', 'credit_history_years']
            available_radar = [c for c in radar_metrics if c in df.columns]
            if len(available_radar) >= 3:
                fig = go.Figure()
                for risk in ["Low Risk", "Medium Risk", "High Risk"]:
                    rdf = df[df['risk_level'] == risk]
                    if not rdf.empty:
                        # Normalize values to 0-1 for radar
                        vals = []
                        for col in available_radar:
                            col_min = df[col].min()
                            col_max = df[col].max()
                            if col_max > col_min:
                                vals.append((rdf[col].mean() - col_min) / (col_max - col_min))
                            else:
                                vals.append(0.5)
                        vals.append(vals[0])  # close the polygon
                        labels = [c.replace('_', ' ').title() for c in available_radar]
                        labels.append(labels[0])

                        fig.add_trace(go.Scatterpolar(
                            r=vals, theta=labels, name=risk,
                            fill='toself',
                            fillcolor=RISK_COLORS.get(risk, "#60a5fa") + "22",
                            line=dict(color=RISK_COLORS.get(risk), width=2),
                            marker=dict(size=5)
                        ))
                fig.update_layout(
                    title=dict(text="Avg Applicant Profile by Risk", font=dict(size=15, color="#e2e8f0")),
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, range=[0, 1], showticklabels=False,
                                        gridcolor="rgba(255,255,255,0.08)"),
                        angularaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                                         tickfont=dict(color="#cbd5e1", size=11))
                    ),
                    **dark_layout
                )
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 6B: Treemap — Portfolio View ──
        with s6c2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            tree_data = df.groupby(['loan_purpose', 'risk_level']).agg(
                count=('id', 'count'),
                total_amount=('loan_amount', 'sum')
            ).reset_index()

            if not tree_data.empty:
                fig = px.treemap(
                    tree_data,
                    path=['loan_purpose', 'risk_level'],
                    values='count',
                    color='risk_level',
                    color_discrete_map=RISK_COLORS,
                    hover_data={'total_amount': ':$,.0f'},
                    labels={"count": "Applications", "total_amount": "Total Amount"}
                )
                fig.update_layout(
                    title=dict(text="Portfolio Treemap", font=dict(size=15, color="#e2e8f0")),
                    **dark_layout
                )
                fig.update_traces(
                    textfont=dict(size=12, color="#fff"),
                    marker=dict(cornerradius=5),
                    hovertemplate="<b>%{label}</b><br>Applications: %{value}<br>Total: %{customdata[0]:$,.0f}<extra></extra>"
                )
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # DATA TABLE
        # ==================================================
        st.markdown("""
        <div class="dash-section">
            <div class="sec-icon blue">📋</div>
            <div><h3>Prediction Log</h3><p>Detailed history of all predictions</p></div>
        </div>
        """, unsafe_allow_html=True)

        display_df = df.copy()
        display_df['default_probability'] = display_df['default_probability'].apply(lambda x: f"{x:.2%}")
        display_df['income'] = display_df['income'].apply(lambda x: f"${x:,.0f}")
        display_df['loan_amount'] = display_df['loan_amount'].apply(lambda x: f"${x:,.0f}")
        display_df['recommended_max_loan_amount'] = display_df['recommended_max_loan_amount'].apply(lambda x: f"${x:,.0f}")
        if 'timestamp' in display_df.columns:
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')

        display_df.columns = [
            'ID', 'Timestamp', 'Age', 'Income', 'Emp. Years',
            'Home', 'Loan Amt', 'Purpose', 'Credit Yrs',
            'Prediction', 'Default Prob.', 'Risk Level', 'Max Loan Rec.'
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
            }
        )

        # ── Footer ──
        st.markdown("""
        <div style="text-align:center; padding:24px 0 8px 0; color:#475569; font-size:12px;">
            AI Loan Default Prediction System &bull; MLOps Dashboard &bull; Powered by XGBoost
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Dashboard error: {e}")
        st.info("Make sure MySQL is running and the `loan_system` database exists.")
    st.stop()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("💳 AI Loan Default Prediction")

st.write(
    """
    This system uses machine learning to estimate the
    probability of loan default based on applicant and
    loan information.
    """
)

st.divider()


# --------------------------------------------------
# Applicant Information
# --------------------------------------------------

st.subheader("👤 Applicant Information")

currency_code = st.selectbox(
    "Currency",
    options=[
        "USD",
        "EUR",
        "GBP",
        "INR",
        "LKR"
    ]
)

age = st.number_input(
    "Age",
    min_value=18,
    max_value=100,
    value=28,
    step=1
)

income = st.number_input(
    f"Annual Income ({currency_code})",
    min_value=0.0,
    value=50000.0,
    step=1000.0
)

employment_years = st.number_input(
    "Employment Years",
    min_value=0.0,
    max_value=60.0,
    value=4.0,
    step=1.0
)

home_ownership = st.selectbox(
    "Home Ownership",
    options=[
        "RENT",
        "OWN",
        "MORTGAGE",
        "OTHER"
    ]
)


# --------------------------------------------------
# Loan Information
# --------------------------------------------------

st.subheader("🏦 Loan Information")

loan_amount = st.number_input(
    f"Loan Amount ({currency_code})",
    min_value=0.0,
    value=10000.0,
    step=500.0
)

loan_purpose = st.selectbox(
    "Loan Purpose",
    options=[
        "PERSONAL",
        "EDUCATION",
        "MEDICAL",
        "VENTURE",
        "HOMEIMPROVEMENT",
        "DEBTCONSOLIDATION"
    ]
)

col_ch1, col_ch2 = st.columns([2, 1])
with col_ch1:
    credit_history_years = st.number_input(
        "Credit History Years",
        min_value=0.0,
        max_value=50.0,
        value=st.session_state.mock_credit_history,
        step=1.0
    )
with col_ch2:
    st.write("")
    st.write("")
    if st.button("Pull Equifax Report (Mock)"):
        with st.spinner("Connecting to Credit Bureau..."):
            time.sleep(1.5)
            st.session_state.mock_credit_history = 8.5
            st.rerun()


# --------------------------------------------------
# Prediction button
# --------------------------------------------------

st.divider()

predict_button = st.button(
    "🔍 Predict Loan Risk",
    use_container_width=True
)


# --------------------------------------------------
# Make prediction
# --------------------------------------------------

if predict_button:

    # Basic validation
    if income <= 0:

        st.error(
            "Please enter a valid annual income."
        )

    elif loan_amount <= 0:

        st.error(
            "Please enter a valid loan amount."
        )

    else:
        payload = {
            "age": age,
            "income": income,
            "employment_years": employment_years,
            "home_ownership": home_ownership,
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose,
            "credit_history_years": credit_history_years
        }
        
        try:
            with st.spinner("Calling ML API..."):
                response = requests.post(f"{API_URL}/predict", json=payload)
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
            st.error(f"API Error: Make sure the FastAPI backend is running on port 8000. Details: {e}")
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

            st.error(
                "⚠️ Prediction: Higher Default Risk"
            )

        else:

            st.success(
                "✅ Prediction: Lower Default Risk"
            )


        # Probability

        st.metric(
            label="Default Probability",
            value=f"{probability:.2%}"
        )

        st.metric(
            label="Recommended Maximum Loan Amount",
            value=f"{currency_code} {result['recommended_max_loan_amount']:,.2f}"
        )

        st.caption(
            "Screening estimate based on income, employment stability, and model risk. "
            "It is not a final lending limit. Amounts use the selected currency code."
        )


        # Risk level

        if risk_level == "Low Risk":

            st.success(
                f"Risk Level: {risk_level}"
            )

        elif risk_level == "Medium Risk":

            st.warning(
                f"Risk Level: {risk_level}"
            )

        else:

            st.error(
                f"Risk Level: {risk_level}"
            )


        # Progress bar

        st.write("Default Probability")

        st.progress(
            float(probability)
        )


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
                use_container_width=True
            )


        # --------------------------------------------------
        # Applicant summary
        # --------------------------------------------------

        st.subheader("📋 Applicant Summary")

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**Age:** {age}")
            st.write(f"**Annual Income:** {currency_code} {income:,.2f}")
            st.write(
                f"**Employment Years:** "
                f"{employment_years}"
            )
            st.write(
                f"**Home Ownership:** "
                f"{home_ownership}"
            )

        with col2:

            st.write(
                f"**Loan Amount:** "
                f"{currency_code} {loan_amount:,.2f}"
            )

            st.write(
                f"**Loan Purpose:** "
                f"{loan_purpose}"
            )

            st.write(
                f"**Credit History:** "
                f"{credit_history_years} years"
            )


        # --------------------------------------------------
        # Disclaimer
        # --------------------------------------------------

        st.divider()

        st.caption(
            """
            ⚠️ This prediction is for educational and
            risk-assessment purposes only. It should not
            be used as the sole basis for making lending
            or financial decisions.
            """
        )


# --------------------------------------------------
# Loan approval and document workflow
# --------------------------------------------------

if st.session_state.loan_result is not None:
    st.divider()
    st.subheader("🛡️ Banker Workflow")

    if st.session_state.workflow_step == "prediction":
        st.info("Review the prediction and approve the loan to continue to document verification.")
        if st.button("✅ Approve Loan and Continue", use_container_width=True):
            st.session_state.workflow_step = "documents"
            st.rerun()

    elif st.session_state.workflow_step == "documents":
        st.success("Loan approved. Upload all required documents for verification.")
        st.write("Required documents")

        identity_document = st.file_uploader(
            "Identity document",
            type=["pdf", "png", "jpg", "jpeg"],
            key="identity_document"
        )
        income_document = st.file_uploader(
            "Income or employment proof",
            type=["pdf", "png", "jpg", "jpeg"],
            key="income_document"
        )
        bank_statement = st.file_uploader(
            "Bank statement",
            type=["pdf", "png", "jpg", "jpeg"],
            key="bank_statement"
        )

        documents = {
            "Identity document": identity_document,
            "Income or employment proof": income_document,
            "Bank statement": bank_statement
        }
        missing_documents = [
            name for name, document in documents.items()
            if document is None
        ]

        if missing_documents:
            st.warning(
                "Missing documents: " + ", ".join(missing_documents)
            )
        else:
            invalid_documents = [
                name for name, document in documents.items()
                if document.size <= 0
            ]

            if invalid_documents:
                st.error(
                    "These documents are empty: " + ", ".join(invalid_documents)
                )
            else:
                st.success("All required documents are uploaded and non-empty.")
                st.caption(
                    "This is a completeness check only. A qualified banker must "
                    "verify authenticity and whether the documents match the application."
                )
                if st.button("🛡️ Run KYC Verification & Submit", use_container_width=True):
                    with st.spinner("Connecting to KYC Verification Provider..."):
                        time.sleep(2)
                    st.success("KYC Verification Passed: Identity and Income matches.")
                    time.sleep(1)
                    st.session_state.workflow_step = "completed"
                    st.rerun()

    else:
        st.success("🎉 All steps completed.")
        st.write("Loan approval and document completeness checks are finished.")
        st.caption(
            "Final disbursement remains subject to the bank's approval, compliance, "
            "and document-authentication procedures."
        )