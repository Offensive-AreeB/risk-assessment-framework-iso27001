import streamlit as st
import pandas as pd
from datetime import date
from database.db import execute_query
from utils.risk_calculator import calculate_risk_score, determine_risk_level
from utils.validators import validate_string_length
from utils.rbac import has_permission
from utils.audit import log_action

TREATMENT_OPTIONS = ["Mitigate", "Accept", "Transfer", "Avoid"]
STATUS_OPTIONS = ["Planned", "In Progress", "Implemented", "Accepted", "Closed"]

def get_status_display(status, target_date):
    if status not in ["Implemented", "Accepted", "Closed"]:
        if target_date and isinstance(target_date, str):
            try:
                t_date = date.fromisoformat(target_date)
                if t_date < date.today():
                    return f"🔴 {status} (Overdue)"
            except:
                pass
        elif target_date and isinstance(target_date, date):
            if target_date < date.today():
                return f"🔴 {status} (Overdue)"
    return f"🟢 {status}"

def render_treatments_page():
    st.title("🛡️ Risk Treatment Plan")
    st.markdown("Define and track strategies to handle identified risks and calculate residual risk.")
    
    can_manage = has_permission("MANAGE_TREATMENTS")
    tabs = ["View Treatments"]
    if can_manage:
        tabs = ["Create Treatment", "View Treatments", "Manage Treatments"]
        
    selected_tabs = st.tabs(tabs)
    
    # Fetch Risks
    risks = execute_query(
        """SELECT r.id, r.risk_title, r.threat, r.vulnerability, r.likelihood, r.impact, 
                  r.risk_score, r.risk_level, a.asset_name 
           FROM risks r JOIN assets a ON r.asset_id = a.id 
           ORDER BY r.risk_score DESC""", fetch_all=True)
           
    if not risks:
        st.warning("No risks found. Add risks in the Risk Register before viewing treatment plans.")
        return
        
    risk_opts = {r['id']: f"{r['risk_title']} (Score: {r['risk_score']} - {r['risk_level']})" for r in risks}
    
    view_tab_idx = 1 if can_manage else 0
    
    with selected_tabs[view_tab_idx]:
        st.subheader("View Treatments")
        query = """
            SELECT t.id, r.risk_title as 'Risk', a.asset_name as 'Asset', 
                   r.risk_score as 'Inherent Score', r.risk_level as 'Inherent Level',
                   t.treatment_option as 'Treatment Option', t.treatment_owner as 'Treatment Owner',
                   t.target_date as 'Target Date', t.treatment_status as 'Status',
                   t.residual_score as 'Residual Score', t.residual_risk_level as 'Residual Level'
            FROM risk_treatments t
            JOIN risks r ON t.risk_id = r.id
            JOIN assets a ON r.asset_id = a.id
            ORDER BY t.id DESC
        """
        treatments = execute_query(query, fetch_all=True)
        if treatments:
            df = pd.DataFrame([dict(row) for row in treatments])
            
            # Filters
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                f_opt = st.selectbox("Option", ["All"] + TREATMENT_OPTIONS)
            with col_f2:
                f_stat = st.selectbox("Status", ["All"] + STATUS_OPTIONS)
            with col_f3:
                f_inh = st.selectbox("Inherent Level", ["All", "Low", "Medium", "High", "Critical"])
            with col_f4:
                f_res = st.selectbox("Residual Level", ["All", "Low", "Medium", "High", "Critical"])
                
            s_text = st.text_input("Search Risk / Asset / Owner")
            
            if f_opt != "All": df = df[df['Treatment Option'] == f_opt]
            if f_stat != "All": df = df[df['Status'] == f_stat]
            if f_inh != "All": df = df[df['Inherent Level'] == f_inh]
            if f_res != "All": df = df[df['Residual Level'] == f_res]
            if s_text:
                mask = df['Risk'].str.contains(s_text, case=False) | df['Asset'].str.contains(s_text, case=False) | df['Treatment Owner'].str.contains(s_text, case=False)
                df = df[mask]
                
            # Dynamic Overdue indicator
            df['Display Status'] = df.apply(lambda row: get_status_display(row['Status'], row['Target Date']), axis=1)
            display_df = df.drop(columns=['Status']).rename(columns={'Display Status': 'Status'})
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("### Treatment Detail View")
            t_opts = {r['id']: f"{r['Risk']} (Inherent: {r['Inherent Score']} -> Residual: {r['Residual Score']})" for i, r in df.iterrows()}
            selected_t = st.selectbox("Select a Treatment to view details", options=list(t_opts.keys()), format_func=lambda x: t_opts[x])
            
            if selected_t:
                t_detail = execute_query("SELECT * FROM risk_treatments WHERE id = ?", (selected_t,), fetch_one=True)
                inh_risk = [r for r in risks if r['id'] == t_detail['risk_id']][0]
                
                reduction = inh_risk['risk_score'] - t_detail['residual_score']
                reduction_pct = (reduction / inh_risk['risk_score']) * 100 if inh_risk['risk_score'] > 0 else 0
                
                st.markdown(f"**Risk:** {inh_risk['risk_title']}")
                st.markdown(f"**Inherent Risk:** {inh_risk['risk_score']} — {inh_risk['risk_level']}")
                st.markdown(f"**Treatment:** {t_detail['treatment_option']}")
                st.markdown(f"**Treatment Action:** {t_detail['treatment_description']}")
                st.markdown(f"**Owner:** {t_detail['treatment_owner']} | **Target Date:** {t_detail['target_date']}")
                st.markdown(f"**Status:** {get_status_display(t_detail['treatment_status'], t_detail['target_date'])}")
                st.markdown(f"**Residual Risk:** {t_detail['residual_score']} — {t_detail['residual_risk_level']}")
                
                st.markdown("---")
                st.markdown("**Risk Reduction**")
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                col_r1.metric("Inherent Score", inh_risk['risk_score'])
                col_r2.metric("Residual Score", t_detail['residual_score'])
                col_r3.metric("Reduction Points", f"{reduction}")
                col_r4.metric("Reduction %", f"{reduction_pct:.1f}%")
                
                # Show Mapped Controls
                maps = execute_query("SELECT c.control_id, c.control_name FROM risk_control_mapping m JOIN iso_controls c ON m.control_id = c.control_id WHERE m.risk_id = ?", (inh_risk['id'],), fetch_all=True)
                if maps:
                    controls_str = "\n".join([f"- {m['control_id']}: {m['control_name']}" for m in maps])
                    st.markdown(f"**Mapped ISO 27001 Controls:**\n{controls_str}")
        else:
            st.info("No treatments found.")
            
    if can_manage:
        with selected_tabs[0]:
            st.subheader("Create a New Treatment Plan")
            selected_risk_id = st.selectbox("Select Risk*", options=list(risk_opts.keys()), format_func=lambda x: risk_opts[x])
            risk = [r for r in risks if r['id'] == selected_risk_id][0]
            
            st.info(f"**Inherent Risk:**\n- **Asset:** {risk['asset_name']}\n- **Threat:** {risk['threat']}\n- **Vulnerability:** {risk['vulnerability']}\n- **Likelihood:** {risk['likelihood']} | **Impact:** {risk['impact']}\n- **Score:** {risk['risk_score']} ({risk['risk_level']})")
            
            # Display Mapped Controls conceptually
            maps = execute_query("SELECT c.control_id, c.control_name FROM risk_control_mapping m JOIN iso_controls c ON m.control_id = c.control_id WHERE m.risk_id = ?", (selected_risk_id,), fetch_all=True)
            if maps:
                controls_str = "\n".join([f"- {m['control_id']}: {m['control_name']}" for m in maps])
                st.markdown(f"**Mapped ISO 27001 Controls:**\n{controls_str}")
            else:
                st.markdown("**Mapped ISO 27001 Controls:** None")
                
            with st.form("add_treatment_form"):
                t_option = st.selectbox("Treatment Option*", TREATMENT_OPTIONS)
                t_desc = st.text_area("Treatment Description*")
                t_owner = st.text_input("Treatment Owner*")
                
                c1, c2 = st.columns(2)
                with c1:
                    t_date = st.date_input("Target Date*")
                with c2:
                    t_status = st.selectbox("Treatment Status*", STATUS_OPTIONS)
                    
                st.markdown("### Residual Risk")
                c3, c4 = st.columns(2)
                with c3:
                    r_lik = st.selectbox("Residual Likelihood*", [1, 2, 3, 4, 5], index=max(0, risk['likelihood'] - 2))
                with c4:
                    r_imp = st.selectbox("Residual Impact*", [1, 2, 3, 4, 5], index=risk['impact'] - 1)
                    
                st.info("Residual Score and Level will be automatically calculated on save.")
                
                submit = st.form_submit_button("Save Treatment Plan")
                if submit:
                    if not has_permission("MANAGE_TREATMENTS"):
                        st.error("Unauthorized")
                        st.stop()
                    if not validate_string_length(t_desc):
                        st.error("Treatment Description is required.")
                    elif not validate_string_length(t_owner):
                        st.error("Treatment Owner is required.")
                    else:
                        r_score = calculate_risk_score(r_lik, r_imp)
                        r_level = determine_risk_level(r_score)
                        try:
                            treat_id = execute_query(
                                """INSERT INTO risk_treatments 
                                   (risk_id, treatment_option, treatment_description, treatment_owner, target_date, treatment_status, residual_likelihood, residual_impact, residual_score, residual_risk_level)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (selected_risk_id, t_option, t_desc.strip(), t_owner.strip(), t_date.isoformat(), t_status, r_lik, r_imp, r_score, r_level)
                            )
                            log_action("Treatment Created", "Treatments", f"Created treatment for risk {selected_risk_id}", "risk_treatments", treat_id)
                            st.success(f"Treatment Plan saved! Residual Score: {r_score} ({r_level})")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to create treatment plan: {e}")
                            
        with selected_tabs[2]:
            st.subheader("Manage Treatments")
            if 'treatments' in locals() and treatments:
                t_map = {row['id']: f"[{row['Risk']}] - {row['Treatment Option']}" for row in treatments}
                selected_t_id = st.selectbox("Select Treatment to Edit/Delete", options=list(t_map.keys()), format_func=lambda x: t_map[x])
                
                t_data = execute_query("SELECT * FROM risk_treatments WHERE id = ?", (selected_t_id,), fetch_one=True)
                inh_risk_data = [r for r in risks if r['id'] == t_data['risk_id']][0]
                
                if t_data:
                    with st.expander("Edit Treatment", expanded=False):
                        with st.form("edit_t_form"):
                            e_opt = st.selectbox("Treatment Option*", TREATMENT_OPTIONS, index=TREATMENT_OPTIONS.index(t_data['treatment_option']) if t_data['treatment_option'] in TREATMENT_OPTIONS else 0)
                            e_desc = st.text_area("Treatment Description*", value=t_data['treatment_description'])
                            e_owner = st.text_input("Treatment Owner*", value=t_data['treatment_owner'])
                            
                            try:
                                e_date_val = date.fromisoformat(t_data['target_date']) if t_data['target_date'] else date.today()
                            except:
                                e_date_val = date.today()
                                
                            cc1, cc2 = st.columns(2)
                            with cc1:
                                e_date = st.date_input("Target Date*", value=e_date_val)
                            with cc2:
                                e_stat = st.selectbox("Treatment Status*", STATUS_OPTIONS, index=STATUS_OPTIONS.index(t_data['treatment_status']) if t_data['treatment_status'] in STATUS_OPTIONS else 0)
                                
                            st.markdown("### Residual Risk")
                            cc3, cc4 = st.columns(2)
                            with cc3:
                                e_lik = st.selectbox("Residual Likelihood*", [1, 2, 3, 4, 5], index=t_data['residual_likelihood']-1)
                            with cc4:
                                e_imp = st.selectbox("Residual Impact*", [1, 2, 3, 4, 5], index=t_data['residual_impact']-1)
                                
                            st.info(f"Current Inherent Score: {inh_risk_data['risk_score']} ({inh_risk_data['risk_level']})")
                            
                            if st.form_submit_button("Update Treatment"):
                                if not has_permission("MANAGE_TREATMENTS"):
                                    st.error("Unauthorized")
                                    st.stop()
                                if not validate_string_length(e_desc):
                                    st.error("Description required.")
                                elif not validate_string_length(e_owner):
                                    st.error("Owner required.")
                                else:
                                    new_score = calculate_risk_score(e_lik, e_imp)
                                    new_level = determine_risk_level(new_score)
                                    execute_query(
                                        """UPDATE risk_treatments SET
                                           treatment_option=?, treatment_description=?, treatment_owner=?, target_date=?,
                                           treatment_status=?, residual_likelihood=?, residual_impact=?, residual_score=?,
                                           residual_risk_level=?, updated_at=CURRENT_TIMESTAMP
                                           WHERE id=?""",
                                        (e_opt, e_desc.strip(), e_owner.strip(), e_date.isoformat(), e_stat, e_lik, e_imp, new_score, new_level, selected_t_id)
                                    )
                                    log_action("Treatment Updated", "Treatments", f"Updated treatment {selected_t_id}", "risk_treatments", selected_t_id)
                                    st.success("Treatment updated!")
                                    st.rerun()
                                    
                    with st.expander("Delete Treatment", expanded=False):
                        if st.button("Delete Treatment", type="primary"):
                            if not has_permission("MANAGE_TREATMENTS"):
                                st.error("Unauthorized")
                                st.stop()
                            execute_query("DELETE FROM risk_treatments WHERE id=?", (selected_t_id,))
                            log_action("Treatment Deleted", "Treatments", f"Deleted treatment {selected_t_id}", "risk_treatments", selected_t_id)
                            st.success("Treatment deleted!")
                            st.rerun()
            else:
                st.info("No treatments available to manage.")
