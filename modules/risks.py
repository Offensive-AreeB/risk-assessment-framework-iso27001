import streamlit as st
import pandas as pd
from database.db import execute_query
from utils.risk_calculator import calculate_risk_score, determine_risk_level
from utils.validators import validate_string_length
from utils.rbac import has_permission
from utils.audit import log_action

RISK_STATUS_OPTIONS = ["Open", "Under Treatment", "Accepted", "Closed"]
LIKELIHOOD_OPTIONS = {1: "1 - Rare", 2: "2 - Unlikely", 3: "3 - Possible", 4: "4 - Likely", 5: "5 - Almost Certain"}
IMPACT_OPTIONS = {1: "1 - Insignificant", 2: "2 - Minor", 3: "3 - Moderate", 4: "4 - Major", 5: "5 - Severe"}
RISK_LEVELS = ["Low", "Medium", "High", "Critical"]

def render_risks_page():
    st.title("⚠️ Risk Register")
    st.markdown("Identify, analyze, and manage organizational risks.")
    
    can_manage = has_permission("MANAGE_RISKS")
    tabs = ["View Risks"]
    if can_manage:
        tabs.extend(["Add Risk", "Manage Existing Risks"])
        
    selected_tabs = st.tabs(tabs)
    
    assets = execute_query("SELECT id, asset_name FROM assets ORDER BY asset_name", fetch_all=True)
    asset_options = {row['id']: row['asset_name'] for row in assets} if assets else {}
    
    with selected_tabs[0]:
        st.subheader("Risk Register Table")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_title = st.text_input("Search Risk Title", key="risk_search")
        with col2:
            level_filter = st.selectbox("Risk Level", ["All"] + RISK_LEVELS)
        with col3:
            status_filter = st.selectbox("Status", ["All"] + RISK_STATUS_OPTIONS)
        with col4:
            asset_filter_opts = ["All"] + list(asset_options.values())
            asset_filter = st.selectbox("Asset", asset_filter_opts)
            
        query = """
            SELECT r.id, a.asset_name as 'Asset', r.risk_title as 'Risk Title', 
                   r.threat as 'Threat', r.vulnerability as 'Vulnerability', 
                   r.likelihood as 'Likelihood', r.impact as 'Impact', 
                   r.risk_score as 'Risk Score', r.risk_level as 'Risk Level', 
                   r.risk_owner as 'Risk Owner', r.status as 'Status', 
                   r.created_at as 'Created At'
            FROM risks r
            JOIN assets a ON r.asset_id = a.id
            WHERE 1=1
        """
        params = []
        
        if search_title:
            query += " AND r.risk_title LIKE ?"
            params.append(f"%{search_title}%")
        if level_filter != "All":
            query += " AND r.risk_level = ?"
            params.append(level_filter)
        if status_filter != "All":
            query += " AND r.status = ?"
            params.append(status_filter)
        if asset_filter != "All":
            asset_id = [k for k, v in asset_options.items() if v == asset_filter][0]
            query += " AND r.asset_id = ?"
            params.append(asset_id)
            
        query += " ORDER BY r.risk_score DESC, r.id DESC"
        
        try:
            risks = execute_query(query, params, fetch_all=True)
            if risks:
                df = pd.DataFrame([dict(row) for row in risks])
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader("View Risk Mappings")
                risk_opts_view = {row['id']: row['Risk Title'] for row in risks}
                selected_r = st.selectbox("Select a risk to view mapped controls:", options=list(risk_opts_view.keys()), format_func=lambda x: risk_opts_view[x])
                
                if selected_r:
                    mappings_query = """
                        SELECT c.control_id as 'Control ID', c.control_name as 'Control Name', 
                               c.control_category as 'Theme', m.applicability as 'Applicability', 
                               m.implementation_status as 'Status'
                        FROM risk_control_mapping m
                        JOIN iso_controls c ON m.control_id = c.control_id
                        WHERE m.risk_id = ?
                    """
                    mapped_ctrls = execute_query(mappings_query, (selected_r,), fetch_all=True)
                    if mapped_ctrls:
                        st.dataframe(pd.DataFrame([dict(row) for row in mapped_ctrls]), use_container_width=True, hide_index=True)
                    else:
                        st.info("No ISO controls mapped to this risk yet.")
            else:
                st.info("No risks found matching the criteria.")
        except Exception as e:
            st.error(f"Error loading risks: {e}")
            
    if can_manage:
        with selected_tabs[1]:
            st.subheader("Add New Risk")
            
            if not asset_options:
                st.warning("You must add an asset before you can create a risk.")
            else:
                with st.form("add_risk_form", clear_on_submit=False):
                    asset_id = st.selectbox("Asset*", options=list(asset_options.keys()), format_func=lambda x: asset_options[x])
                    title = st.text_input("Risk Title*")
                    threat = st.text_input("Threat*")
                    vuln = st.text_input("Vulnerability*")
                    controls = st.text_area("Existing Controls")
                    
                    col_l, col_i = st.columns(2)
                    with col_l:
                        likelihood = st.selectbox("Likelihood*", options=list(LIKELIHOOD_OPTIONS.keys()), format_func=lambda x: LIKELIHOOD_OPTIONS[x], index=2)
                    with col_i:
                        impact = st.selectbox("Impact*", options=list(IMPACT_OPTIONS.keys()), format_func=lambda x: IMPACT_OPTIONS[x], index=2)
                    
                    st.markdown("---")
                    st.info("Risk Score and Level are automatically calculated when you save.")
                        
                    owner = st.text_input("Risk Owner*")
                    status = st.selectbox("Status*", RISK_STATUS_OPTIONS)
                    
                    submitted = st.form_submit_button("Add Risk")
                    if submitted:
                        if not has_permission("MANAGE_RISKS"):
                            st.error("Unauthorized")
                            st.stop()
                        if not validate_string_length(title):
                            st.error("Risk Title is required.")
                        elif not validate_string_length(threat):
                            st.error("Threat is required.")
                        elif not validate_string_length(vuln):
                            st.error("Vulnerability is required.")
                        elif not validate_string_length(owner):
                            st.error("Risk Owner is required.")
                        else:
                            score = calculate_risk_score(likelihood, impact)
                            level = determine_risk_level(score)
                            
                            try:
                                risk_id = execute_query(
                                    """INSERT INTO risks 
                                    (asset_id, risk_title, threat, vulnerability, existing_controls, 
                                     likelihood, impact, risk_score, risk_level, risk_owner, status)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    (asset_id, title.strip(), threat.strip(), vuln.strip(), controls.strip(),
                                     likelihood, impact, score, level, owner.strip(), status)
                                )
                                log_action("Risk Created", "Risks", f"Created risk '{title.strip()}'", "risks", risk_id)
                                st.success(f"Risk '{title}' added successfully! (Score: {score}, Level: {level})")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to add risk: {e}")
                                
        with selected_tabs[2]:
            st.subheader("Edit or Delete Risk")
            
            all_risks = execute_query("SELECT id, risk_title, risk_score FROM risks ORDER BY risk_title", fetch_all=True)
            if all_risks:
                risk_opts = {row['id']: f"{row['risk_title']} (Score: {row['risk_score']})" for row in all_risks}
                selected_risk_id = st.selectbox("Select Risk", options=list(risk_opts.keys()), format_func=lambda x: risk_opts[x])
                
                if selected_risk_id:
                    risk = execute_query("SELECT * FROM risks WHERE id = ?", (selected_risk_id,), fetch_one=True)
                    if risk:
                        st.markdown(f"**Managing:** {risk['risk_title']}")
                        
                        with st.expander("Edit Risk", expanded=False):
                            with st.form("edit_risk_form"):
                                e_asset = st.selectbox("Asset*", options=list(asset_options.keys()), format_func=lambda x: asset_options[x], index=list(asset_options.keys()).index(risk['asset_id']) if risk['asset_id'] in asset_options else 0)
                                e_title = st.text_input("Risk Title*", value=risk['risk_title'])
                                e_threat = st.text_input("Threat*", value=risk['threat'])
                                e_vuln = st.text_input("Vulnerability*", value=risk['vulnerability'])
                                e_controls = st.text_area("Existing Controls", value=risk['existing_controls'] or "")
                                
                                col_e_l, col_e_i = st.columns(2)
                                with col_e_l:
                                    e_likelihood = st.selectbox("Likelihood*", options=list(LIKELIHOOD_OPTIONS.keys()), format_func=lambda x: LIKELIHOOD_OPTIONS[x], index=risk['likelihood']-1)
                                with col_e_i:
                                    e_impact = st.selectbox("Impact*", options=list(IMPACT_OPTIONS.keys()), format_func=lambda x: IMPACT_OPTIONS[x], index=risk['impact']-1)
                                    
                                st.info("Score and Level will be automatically recalculated upon updating.")
                                
                                e_owner = st.text_input("Risk Owner*", value=risk['risk_owner'])
                                e_status_idx = RISK_STATUS_OPTIONS.index(risk['status']) if risk['status'] in RISK_STATUS_OPTIONS else 0
                                e_status = st.selectbox("Status*", RISK_STATUS_OPTIONS, index=e_status_idx)
                                
                                update_btn = st.form_submit_button("Update Risk")
                                
                                if update_btn:
                                    if not has_permission("MANAGE_RISKS"):
                                        st.error("Unauthorized")
                                        st.stop()
                                    if not validate_string_length(e_title):
                                        st.error("Risk Title is required.")
                                    elif not validate_string_length(e_threat):
                                        st.error("Threat is required.")
                                    elif not validate_string_length(e_vuln):
                                        st.error("Vulnerability is required.")
                                    elif not validate_string_length(e_owner):
                                        st.error("Risk Owner is required.")
                                    else:
                                        e_score = calculate_risk_score(e_likelihood, e_impact)
                                        e_level = determine_risk_level(e_score)
                                        try:
                                            execute_query(
                                                """UPDATE risks SET 
                                                   asset_id=?, risk_title=?, threat=?, vulnerability=?, existing_controls=?,
                                                   likelihood=?, impact=?, risk_score=?, risk_level=?, risk_owner=?, status=?,
                                                   updated_at=CURRENT_TIMESTAMP
                                                   WHERE id=?""",
                                                (e_asset, e_title.strip(), e_threat.strip(), e_vuln.strip(), e_controls.strip(),
                                                 e_likelihood, e_impact, e_score, e_level, e_owner.strip(), e_status, selected_risk_id)
                                            )
                                            log_action("Risk Updated", "Risks", f"Updated risk '{e_title.strip()}'", "risks", selected_risk_id)
                                            st.success(f"Risk updated successfully! (New Score: {e_score}, New Level: {e_level})")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Failed to update risk: {e}")
                                            
                        with st.expander("Delete Risk", expanded=False):
                            st.warning("This will permanently delete the risk.")
                            delete_confirm = st.checkbox("I understand and wish to delete this risk.", key="del_risk_conf")
                            if st.button("Delete Risk", type="primary") and delete_confirm:
                                if not has_permission("MANAGE_RISKS"):
                                    st.error("Unauthorized")
                                    st.stop()
                                try:
                                    # Check for mapped controls or treatments
                                    maps = execute_query("SELECT count(*) as count FROM risk_control_mapping WHERE risk_id = ?", (selected_risk_id,), fetch_one=True)['count']
                                    treats = execute_query("SELECT count(*) as count FROM risk_treatments WHERE risk_id = ?", (selected_risk_id,), fetch_one=True)['count']
                                    
                                    if maps > 0 or treats > 0:
                                        st.error(f"Cannot delete this risk. It has {maps} control mapping(s) and {treats} treatment(s) associated with it.")
                                    else:
                                        execute_query("DELETE FROM risks WHERE id = ?", (selected_risk_id,))
                                        log_action("Risk Deleted", "Risks", f"Deleted risk ID {selected_risk_id}", "risks", selected_risk_id)
                                        st.success("Risk deleted successfully!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete risk: {e}")
            else:
                st.info("No risks available to manage.")
