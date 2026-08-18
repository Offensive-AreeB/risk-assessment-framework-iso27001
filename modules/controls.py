import streamlit as st
import pandas as pd
from database.db import execute_query

def render_controls_page():
    st.title("📚 ISO/IEC 27001:2022 Controls")
    st.markdown("View and explore the Annex A control library.")
    
    controls = execute_query("SELECT control_id, control_name, control_category, description FROM iso_controls ORDER BY id", fetch_all=True)
    
    if not controls:
        st.warning("The ISO 27001:2022 control library has not been seeded yet. The system should have seeded it automatically. Please check the logs.")
        return
        
    df = pd.DataFrame([dict(row) for row in controls])
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("Total Controls", len(df))
    with col2:
        search_query = st.text_input("Search Control ID / Name", "")
    with col3:
        themes = ["All"] + list(df['control_category'].unique())
        theme_filter = st.selectbox("Filter by Theme", themes)
        
    # Filtering
    if search_query:
        df = df[df['control_id'].str.contains(search_query, case=False) | df['control_name'].str.contains(search_query, case=False)]
    if theme_filter != "All":
        df = df[df['control_category'] == theme_filter]
        
    st.subheader(f"Controls ({len(df)})")
    
    st.dataframe(df[['control_id', 'control_name', 'control_category']], use_container_width=True, hide_index=True)
    
    st.markdown("### Control Details")
    for _, row in df.iterrows():
        with st.expander(f"{row['control_id']} - {row['control_name']}"):
            st.markdown(f"**Theme:** {row['control_category']}")
            st.markdown(f"**Description:** {row['description']}")
