import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from database.db import execute_query

def get_base_data():
    risks = execute_query(
        """SELECT r.id, r.risk_title, a.asset_name, r.likelihood, r.impact, 
                  r.risk_score, r.risk_level, r.status,
                  t.treatment_option, t.treatment_status, t.target_date, 
                  t.residual_score, t.residual_risk_level
           FROM risks r
           JOIN assets a ON r.asset_id = a.id
           LEFT JOIN (
               SELECT risk_id, treatment_option, treatment_status, target_date, residual_score, residual_risk_level
               FROM risk_treatments
               -- simplified: assume one active treatment per risk
               GROUP BY risk_id
           ) t ON r.id = t.risk_id""", fetch_all=True)
           
    assets = execute_query("SELECT id, asset_name FROM assets", fetch_all=True)
    controls = execute_query("SELECT DISTINCT control_id FROM risk_control_mapping WHERE applicability = 'Applicable'", fetch_all=True)
    
    return risks, assets, len(controls)

def determine_treatment_status_display(status, t_date):
    if not status:
        return "No Treatment"
    if status not in ["Implemented", "Accepted", "Closed"]:
        if t_date and str(t_date) != "None":
            try:
                if date.fromisoformat(str(t_date)) < date.today():
                    return "Overdue"
            except:
                pass
    return status

def render_dashboard():
    st.title("🛡️ Risk Assessment Framework")
    st.subheader("ISO/IEC 27001-Aligned GRC Risk Dashboard")
    st.markdown("Centralized overview of organizational assets, cybersecurity risks, ISO/IEC 27001 control applicability, and risk treatment status.")
    
    risks_raw, assets_raw, applicable_controls_count = get_base_data()
    
    if not risks_raw:
        st.info("No risks found. Add some assets and risks to populate the dashboard.")
        return
        
    df = pd.DataFrame([dict(r) for r in risks_raw])
    
    df['calculated_treatment_status'] = df.apply(lambda row: determine_treatment_status_display(row['treatment_status'], row['target_date']), axis=1)
    
    # Filters
    st.markdown("### Filters")
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    with f_c1:
        f_asset = st.selectbox("Asset", ["All"] + sorted(df['asset_name'].dropna().unique().tolist()))
    with f_c2:
        f_level = st.selectbox("Risk Level", ["All", "Critical", "High", "Medium", "Low"])
    with f_c3:
        f_status = st.selectbox("Risk Status", ["All"] + sorted(df['status'].dropna().unique().tolist()))
    with f_c4:
        f_tstatus = st.selectbox("Treatment Status", ["All"] + sorted(df['calculated_treatment_status'].dropna().unique().tolist()))
        
    filtered_df = df.copy()
    if f_asset != "All": filtered_df = filtered_df[filtered_df['asset_name'] == f_asset]
    if f_level != "All": filtered_df = filtered_df[filtered_df['risk_level'] == f_level]
    if f_status != "All": filtered_df = filtered_df[filtered_df['status'] == f_status]
    if f_tstatus != "All": filtered_df = filtered_df[filtered_df['calculated_treatment_status'] == f_tstatus]

    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        return
        
    # KPI Cards
    st.markdown("### Key Performance Indicators")
    k1, k2, k3, k4, k5 = st.columns(5)
    
    total_assets = len(assets_raw)
    total_risks = len(filtered_df)
    critical_risks = len(filtered_df[filtered_df['risk_level'] == 'Critical'])
    high_risks = len(filtered_df[filtered_df['risk_level'] == 'High'])
    medium_risks = len(filtered_df[filtered_df['risk_level'] == 'Medium'])
    low_risks = len(filtered_df[filtered_df['risk_level'] == 'Low'])
    
    no_treatment = len(filtered_df[filtered_df['calculated_treatment_status'] == 'No Treatment'])
    open_treatments = len(filtered_df[filtered_df['calculated_treatment_status'].isin(['Planned', 'In Progress'])])
    overdue_treatments = len(filtered_df[filtered_df['calculated_treatment_status'] == 'Overdue'])
    
    k1.metric("Assets", total_assets)
    k2.metric("Total Risks", total_risks)
    k3.metric("Critical Risks", critical_risks)
    k4.metric("High Risks", high_risks)
    k5.metric("Medium Risks", medium_risks)
    
    k1b, k2b, k3b, k4b, k5b = st.columns(5)
    k1b.metric("Low Risks", low_risks)
    k2b.metric("Risks w/o Treatment", no_treatment)
    k3b.metric("Open Treatments", open_treatments)
    k4b.metric("Overdue Treatments", overdue_treatments)
    k5b.metric("Applicable Controls", applicable_controls_count)
    
    st.markdown("---")
    
    # 5x5 Matrix
    st.markdown("### 5×5 Interactive Risk Matrix")
    
    # Build matrix data
    matrix_data = []
    # y: impact (1-5), x: likelihood (1-5)
    # create 2d array for counts
    counts = [[0 for _ in range(5)] for _ in range(5)]
    hover_texts = [["" for _ in range(5)] for _ in range(5)]
    
    for i in range(5):
        for j in range(5):
            impact = i + 1
            likelihood = j + 1
            cell_risks = filtered_df[(filtered_df['impact'] == impact) & (filtered_df['likelihood'] == likelihood)]
            counts[i][j] = len(cell_risks)
            if len(cell_risks) > 0:
                titles = "<br>".join([f"- {row['risk_title']} ({row['asset_name']})" for idx, row in cell_risks.iterrows()])
                hover_texts[i][j] = f"Score: {impact*likelihood}<br>Count: {len(cell_risks)}<br>Risks:<br>{titles}"
            else:
                hover_texts[i][j] = f"Score: {impact*likelihood}<br>Count: 0 risks"
                
    # Define colors based on score
    colors = [[0 for _ in range(5)] for _ in range(5)]
    for i in range(5):
        for j in range(5):
            score = (i + 1) * (j + 1)
            if score >= 17: colors[i][j] = 4  # Critical
            elif score >= 10: colors[i][j] = 3 # High
            elif score >= 5: colors[i][j] = 2  # Medium
            else: colors[i][j] = 1             # Low

    fig_matrix = go.Figure(data=go.Heatmap(
        z=colors,
        x=["1 - Rare", "2 - Unlikely", "3 - Possible", "4 - Likely", "5 - Almost Certain"],
        y=["1 - Insignificant", "2 - Minor", "3 - Moderate", "4 - Major", "5 - Severe"],
        text=[[str((i+1)*(j+1)) for j in range(5)] for i in range(5)],
        texttemplate="%{text}",
        textfont={"size": 20},
        hoverinfo="text",
        hovertext=hover_texts,
        colorscale=[
            [0, '#00cc66'], [0.25, '#00cc66'], # Low
            [0.25, '#ffcc00'], [0.5, '#ffcc00'], # Medium
            [0.5, '#ff6600'], [0.75, '#ff6600'], # High
            [0.75, '#cc0000'], [1.0, '#cc0000']  # Critical
        ],
        showscale=False
    ))
    
    fig_matrix.update_layout(
        xaxis_title="Likelihood",
        yaxis_title="Impact",
        height=500,
        margin=dict(l=50, r=50, b=50, t=50)
    )
    
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    st.markdown("---")
    
    # Charts
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("#### Risk Distribution")
        level_counts = filtered_df['risk_level'].value_counts().reset_index()
        level_counts.columns = ['Risk Level', 'Count']
        # Map colors
        color_map = {'Low': '#00cc66', 'Medium': '#ffcc00', 'High': '#ff6600', 'Critical': '#cc0000'}
        fig_dist = px.pie(level_counts, names='Risk Level', values='Count', hole=0.4, color='Risk Level', color_discrete_map=color_map)
        fig_dist.update_layout(showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)
        
    with c2:
        st.markdown("#### Risk Status")
        status_counts = filtered_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_stat = px.bar(status_counts, x='Status', y='Count', color='Status')
        fig_stat.update_layout(showlegend=False)
        st.plotly_chart(fig_stat, use_container_width=True)
        
    with c3:
        st.markdown("#### Treatment Status")
        ts_counts = filtered_df['calculated_treatment_status'].value_counts().reset_index()
        ts_counts.columns = ['Treatment Status', 'Count']
        fig_tstat = px.bar(ts_counts, x='Treatment Status', y='Count', color='Treatment Status')
        fig_tstat.update_layout(showlegend=False)
        st.plotly_chart(fig_tstat, use_container_width=True)
        
    st.markdown("---")
    
    # Residual Overview
    st.markdown("### Residual Risk Overview")
    st.markdown("Comparison of Inherent vs Residual Risk levels for treated risks.")
    
    treated_df = filtered_df[filtered_df['residual_risk_level'].notna()].copy()
    if not treated_df.empty:
        inh_counts = treated_df['risk_level'].value_counts().to_dict()
        res_counts = treated_df['residual_risk_level'].value_counts().to_dict()
        
        levels = ['Low', 'Medium', 'High', 'Critical']
        inh_vals = [inh_counts.get(l, 0) for l in levels]
        res_vals = [res_counts.get(l, 0) for l in levels]
        
        fig_comp = go.Figure(data=[
            go.Bar(name='Inherent Risk', x=levels, y=inh_vals, marker_color='indianred'),
            go.Bar(name='Residual Risk', x=levels, y=res_vals, marker_color='lightsalmon')
        ])
        fig_comp.update_layout(barmode='group')
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("No residual risk data available.")
        
    st.markdown("---")
    
    # Top Risks
    st.markdown("### Top Risks")
    top_risks = filtered_df.sort_values(by='risk_score', ascending=False).head(10)
    top_display = top_risks[['risk_title', 'asset_name', 'risk_score', 'risk_level', 'calculated_treatment_status']].rename(columns={
        'risk_title': 'Risk',
        'asset_name': 'Asset',
        'risk_score': 'Score',
        'risk_level': 'Level',
        'calculated_treatment_status': 'Treatment Status'
    })
    st.dataframe(top_display, use_container_width=True, hide_index=True)
