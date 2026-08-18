import streamlit as st
import pandas as pd
import sqlite3
from database.db import execute_query
from utils.rbac import has_permission
from utils.audit import log_action

APPLICABILITY_OPTIONS = ["Applicable", "Not Applicable"]
IMPLEMENTATION_OPTIONS = ["Not Implemented", "Partially Implemented", "Implemented", "Planned"]

def render_mapping_page():
    st.title("🔗 Risk-to-Control Mapping")
    st.markdown("Map identified risks to mitigating ISO 27001 controls.")
    
    can_manage = has_permission("MANAGE_MAPPINGS")
    tabs = ["View Mappings"]
    if can_manage:
        tabs = ["Create Mapping", "View Mappings", "Manage Mappings"]
    else:
        # If they can't manage, they only get the view tab
        pass
        
    # Always keep View Mappings as the primary or secondary depending on access
    selected_tabs = st.tabs(tabs)
    
    risks = execute_query("SELECT id, risk_title, risk_level, asset_id, threat, vulnerability, likelihood, impact, risk_score FROM risks ORDER BY risk_score DESC", fetch_all=True)
    controls = execute_query("SELECT control_id, control_name, control_category FROM iso_controls ORDER BY id", fetch_all=True)
    
    if not risks or not controls:
        st.warning("Ensure you have at least one risk and controls loaded to view mappings.")
        return
        
    risk_opts = {r['id']: f"{r['risk_title']} ({r['risk_level']})" for r in risks}
    control_opts = {c['control_id']: f"{c['control_id']} - {c['control_name']}" for c in controls}
    
    view_tab_index = 1 if can_manage else 0
    
    with selected_tabs[view_tab_index]:
        st.subheader("View All Mappings")
        query = """
            SELECT m.id, r.risk_title as 'Risk', c.control_id as 'Control ID', c.control_name as 'Control Name',
                   m.applicability as 'Applicability', m.implementation_status as 'Status', m.justification as 'Justification'
            FROM risk_control_mapping m
            JOIN risks r ON m.risk_id = r.id
            JOIN iso_controls c ON m.control_id = c.control_id
            ORDER BY m.id DESC
        """
        mappings = execute_query(query, fetch_all=True)
        if mappings:
            df = pd.DataFrame([dict(row) for row in mappings])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No mappings found.")
            
    if can_manage:
        with selected_tabs[0]:
            st.subheader("Create a New Mapping")
            
            selected_risk_id = st.selectbox("Select Risk*", options=list(risk_opts.keys()), format_func=lambda x: risk_opts[x])
            
            # Display Risk Details
            risk = [r for r in risks if r['id'] == selected_risk_id][0]
            asset_name = execute_query("SELECT asset_name FROM assets WHERE id = ?", (risk['asset_id'],), fetch_one=True)['asset_name']
            
            st.info(f"**Risk Details:**\n- **Asset:** {asset_name}\n- **Threat:** {risk['threat']}\n- **Vulnerability:** {risk['vulnerability']}\n- **Score:** {risk['risk_score']} ({risk['risk_level']})")
            
            selected_control_id = st.selectbox("Select ISO Control*", options=list(control_opts.keys()), format_func=lambda x: control_opts[x])
            ctrl = [c for c in controls if c['control_id'] == selected_control_id][0]
            st.info(f"**Control Details:**\n- **Theme:** {ctrl['control_category']}")
            
            with st.form("add_mapping_form"):
                applicability = st.radio("Applicability*", APPLICABILITY_OPTIONS)
                
                st.markdown("*(If Not Applicable, Justification is required. If Applicable, Implementation details are required)*")
                justification = st.text_area("Justification")
                
                status = st.selectbox("Implementation Status", IMPLEMENTATION_OPTIONS)
                notes = st.text_area("Implementation Notes")
                
                submit = st.form_submit_button("Create Mapping")
                if submit:
                    if not has_permission("MANAGE_MAPPINGS"):
                        st.error("Unauthorized")
                        st.stop()
                    if applicability == "Not Applicable" and not justification.strip():
                        st.error("Justification is required when a control is marked as 'Not Applicable'.")
                    else:
                        try:
                            map_id = execute_query(
                                """INSERT INTO risk_control_mapping 
                                   (risk_id, control_id, applicability, justification, implementation_status, implementation_notes)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                (selected_risk_id, selected_control_id, applicability, justification.strip(), status, notes.strip())
                            )
                            log_action("Mapping Created", "Mappings", f"Mapped risk {selected_risk_id} to control {selected_control_id}", "risk_control_mapping", map_id)
                            st.success("Mapping created successfully!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("This Risk-to-Control mapping already exists! Please manage it in the 'Manage Mappings' tab.")
                        except Exception as e:
                            st.error(f"Failed to create mapping: {e}")
                            
        with selected_tabs[2]:
            st.subheader("Manage Mappings (Edit / Delete)")
            if 'df' in locals() and not df.empty:
                map_opts = {m['id']: f"[{m['Control ID']}] mapped to [{m['Risk']}]" for m in mappings}
                selected_map_id = st.selectbox("Select Mapping", options=list(map_opts.keys()), format_func=lambda x: map_opts[x])
                
                mapping = execute_query("SELECT * FROM risk_control_mapping WHERE id = ?", (selected_map_id,), fetch_one=True)
                
                if mapping:
                    with st.expander("Edit Mapping", expanded=False):
                        with st.form("edit_map_form"):
                            e_app_idx = APPLICABILITY_OPTIONS.index(mapping['applicability']) if mapping['applicability'] in APPLICABILITY_OPTIONS else 0
                            e_app = st.radio("Applicability*", APPLICABILITY_OPTIONS, index=e_app_idx)
                            e_just = st.text_area("Justification", value=mapping['justification'] or "")
                            
                            e_stat_idx = IMPLEMENTATION_OPTIONS.index(mapping['implementation_status']) if mapping['implementation_status'] in IMPLEMENTATION_OPTIONS else 0
                            e_stat = st.selectbox("Implementation Status", IMPLEMENTATION_OPTIONS, index=e_stat_idx)
                            e_notes = st.text_area("Implementation Notes", value=mapping['implementation_notes'] or "")
                            
                            if st.form_submit_button("Update Mapping"):
                                if not has_permission("MANAGE_MAPPINGS"):
                                    st.error("Unauthorized")
                                    st.stop()
                                if e_app == "Not Applicable" and not e_just.strip():
                                    st.error("Justification is required when a control is marked as 'Not Applicable'.")
                                else:
                                    try:
                                        execute_query(
                                            "UPDATE risk_control_mapping SET applicability=?, justification=?, implementation_status=?, implementation_notes=? WHERE id=?",
                                            (e_app, e_just.strip(), e_stat, e_notes.strip(), selected_map_id)
                                        )
                                        log_action("Mapping Updated", "Mappings", f"Updated mapping {selected_map_id}", "risk_control_mapping", selected_map_id)
                                        st.success("Mapping updated successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed to update mapping: {e}")
                    
                    with st.expander("Delete Mapping", expanded=False):
                        if st.button("Delete Mapping", type="primary"):
                            if not has_permission("MANAGE_MAPPINGS"):
                                st.error("Unauthorized")
                                st.stop()
                            execute_query("DELETE FROM risk_control_mapping WHERE id=?", (selected_map_id,))
                            log_action("Mapping Deleted", "Mappings", f"Deleted mapping {selected_map_id}", "risk_control_mapping", selected_map_id)
                            st.success("Mapping deleted!")
                            st.rerun()
            else:
                 st.info("No mappings available to manage.")
