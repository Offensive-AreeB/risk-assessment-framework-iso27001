import streamlit as st
import pandas as pd
from database.db import execute_query

def render_soa_page():
    st.title("📜 Statement of Applicability (SoA)")
    st.markdown("Automatically generated SoA based on Risk-to-Control mappings.")
    
    query = """
        SELECT c.control_id, c.control_name, c.control_category,
               m.applicability, m.justification, m.implementation_status, m.implementation_notes,
               r.risk_title
        FROM iso_controls c
        LEFT JOIN risk_control_mapping m ON c.control_id = m.control_id
        LEFT JOIN risks r ON m.risk_id = r.id
        ORDER BY c.id
    """
    
    records = execute_query(query, fetch_all=True)
    
    if not records:
        st.warning("No controls found in the database. Please ensure the ISO Control Library is seeded.")
        return
        
    soa_data = {}
    
    for row in records:
        cid = row['control_id']
        if cid not in soa_data:
            soa_data[cid] = {
                'Control ID': cid,
                'Control Name': row['control_name'],
                'Theme': row['control_category'],
                'Applicable': 'Not Evaluated' if not row['applicability'] else row['applicability'],
                'Justification': [row['justification']] if row['justification'] else [],
                'Status': [row['implementation_status']] if row['implementation_status'] else [],
                'Notes': [row['implementation_notes']] if row['implementation_notes'] else [],
                'Related Risks': [row['risk_title']] if row['risk_title'] else []
            }
        else:
            if row['applicability'] == 'Applicable':
                soa_data[cid]['Applicable'] = 'Applicable' 
            elif row['applicability'] == 'Not Applicable' and soa_data[cid]['Applicable'] == 'Not Evaluated':
                soa_data[cid]['Applicable'] = 'Not Applicable'
                
            if row['justification']:
                soa_data[cid]['Justification'].append(row['justification'])
            if row['implementation_status']:
                soa_data[cid]['Status'].append(row['implementation_status'])
            if row['implementation_notes']:
                soa_data[cid]['Notes'].append(row['implementation_notes'])
            if row['risk_title']:
                soa_data[cid]['Related Risks'].append(row['risk_title'])

    for cid in soa_data:
        soa_data[cid]['Justification'] = " | ".join(set(soa_data[cid]['Justification']))
        soa_data[cid]['Status'] = " | ".join(set(soa_data[cid]['Status'])) if soa_data[cid]['Status'] else 'Not Evaluated'
        soa_data[cid]['Notes'] = " | ".join(set(soa_data[cid]['Notes']))
        soa_data[cid]['Related Risks'] = ", ".join(set(soa_data[cid]['Related Risks']))
        
    df = pd.DataFrame(list(soa_data.values()))
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("Search Control")
    with col2:
        theme_f = st.selectbox("Theme", ["All"] + list(df['Theme'].unique()))
    with col3:
        app_f = st.selectbox("Applicability", ["All"] + list(df['Applicable'].unique()))
    with col4:
        stat_opts = ["All", "Implemented", "Partially Implemented", "Planned", "Not Implemented", "Not Evaluated"]
        stat_f = st.selectbox("Implementation Status", stat_opts)
        
    if search:
        df = df[df['Control ID'].str.contains(search, case=False) | df['Control Name'].str.contains(search, case=False)]
    if theme_f != "All":
        df = df[df['Theme'] == theme_f]
    if app_f != "All":
        df = df[df['Applicable'] == app_f]
    if stat_f != "All":
        df = df[df['Status'].str.contains(stat_f)]
        
    st.subheader(f"SoA Controls ({len(df)})")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("### 📈 Metrics")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Total Annex A Controls", len(df))
    mc2.metric("Applicable Controls", len(df[df['Applicable'] == 'Applicable']))
    mc3.metric("Not Applicable Controls", len(df[df['Applicable'] == 'Not Applicable']))
    
    impl_count = len(df[df['Status'].str.contains('Implemented', na=False) & ~df['Status'].str.contains('Not Implemented', na=False)])
    mc4.metric("Implemented (Fully/Partially)", impl_count)
