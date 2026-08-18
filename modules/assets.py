import streamlit as st
import pandas as pd
import sqlite3
from database.db import execute_query
from utils.rbac import has_permission
from utils.audit import log_action

ASSET_TYPES = [
    "Hardware", "Software", "Database", "Network", 
    "Information/Data", "Cloud Service", "Application", 
    "Human Resource", "Physical Facility", "Other"
]
CRITICALITY_LEVELS = ["Low", "Medium", "High", "Critical"]

def render_assets_page():
    st.title("📦 Asset Management")
    st.markdown("Manage organizational assets and their criticality.")
    
    can_manage = has_permission("MANAGE_ASSETS")
    
    tabs = ["View Assets"]
    if can_manage:
        tabs.extend(["Add Asset", "Manage Existing Assets"])
        
    selected_tabs = st.tabs(tabs)
    
    with selected_tabs[0]:
        st.subheader("Asset Inventory")
        
        col1, col2 = st.columns(2)
        with col1:
            search_text = st.text_input("Search Assets (Name/Description)", key="asset_search")
        with col2:
            crit_filter = st.selectbox("Filter by Criticality", ["All"] + CRITICALITY_LEVELS, key="asset_crit_filter")
            
        query = "SELECT id, asset_name, asset_type, description, owner, criticality, created_at, updated_at FROM assets WHERE 1=1"
        params = []
        
        if search_text:
            query += " AND (asset_name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])
            
        if crit_filter != "All":
            query += " AND criticality = ?"
            params.append(crit_filter)
            
        query += " ORDER BY id DESC"
        
        try:
            assets = execute_query(query, params, fetch_all=True)
            if assets:
                df = pd.DataFrame([dict(row) for row in assets])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No assets found matching the criteria.")
        except Exception as e:
            st.error(f"Error loading assets: {e}")
            
    if can_manage:
        with selected_tabs[1]:
            st.subheader("Add New Asset")
            with st.form("add_asset_form", clear_on_submit=True):
                name = st.text_input("Asset Name*")
                a_type = st.selectbox("Asset Type*", ASSET_TYPES)
                desc = st.text_area("Description")
                owner = st.text_input("Owner")
                crit = st.selectbox("Criticality*", CRITICALITY_LEVELS)
                
                submitted = st.form_submit_button("Add Asset")
                if submitted:
                    if not has_permission("MANAGE_ASSETS"):
                        st.error("Unauthorized")
                        st.stop()
                    if not name.strip():
                        st.error("Asset Name is required.")
                    else:
                        try:
                            asset_id = execute_query(
                                "INSERT INTO assets (asset_name, asset_type, description, owner, criticality) VALUES (?, ?, ?, ?, ?)",
                                (name.strip(), a_type, desc.strip(), owner.strip(), crit)
                            )
                            log_action("Asset Created", "Assets", f"Created asset '{name.strip()}'", "assets", asset_id)
                            st.success(f"Asset '{name}' added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add asset: {e}")
                            
        with selected_tabs[2]:
            st.subheader("Edit or Delete Asset")
            assets = execute_query("SELECT id, asset_name FROM assets ORDER BY asset_name", fetch_all=True)
            
            if assets:
                asset_options = {row['id']: row['asset_name'] for row in assets}
                selected_id = st.selectbox("Select Asset", options=list(asset_options.keys()), format_func=lambda x: asset_options[x])
                
                if selected_id:
                    asset = execute_query("SELECT * FROM assets WHERE id = ?", (selected_id,), fetch_one=True)
                    if asset:
                        st.markdown(f"**Managing:** {asset['asset_name']}")
                        
                        with st.expander("Edit Asset", expanded=False):
                            with st.form("edit_asset_form"):
                                e_name = st.text_input("Asset Name*", value=asset['asset_name'])
                                
                                current_type_idx = ASSET_TYPES.index(asset['asset_type']) if asset['asset_type'] in ASSET_TYPES else 0
                                e_type = st.selectbox("Asset Type*", ASSET_TYPES, index=current_type_idx)
                                
                                e_desc = st.text_area("Description", value=asset['description'] or "")
                                e_owner = st.text_input("Owner", value=asset['owner'] or "")
                                
                                current_crit_idx = CRITICALITY_LEVELS.index(asset['criticality']) if asset['criticality'] in CRITICALITY_LEVELS else 0
                                e_crit = st.selectbox("Criticality*", CRITICALITY_LEVELS, index=current_crit_idx)
                                
                                update_btn = st.form_submit_button("Update Asset")
                                if update_btn:
                                    if not has_permission("MANAGE_ASSETS"):
                                        st.error("Unauthorized")
                                        st.stop()
                                    if not e_name.strip():
                                        st.error("Asset Name is required.")
                                    else:
                                        try:
                                            execute_query(
                                                "UPDATE assets SET asset_name=?, asset_type=?, description=?, owner=?, criticality=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                                                (e_name.strip(), e_type, e_desc.strip(), e_owner.strip(), e_crit, selected_id)
                                            )
                                            log_action("Asset Updated", "Assets", f"Updated asset '{e_name.strip()}'", "assets", selected_id)
                                            st.success("Asset updated successfully!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Failed to update asset: {e}")
                        
                        with st.expander("Delete Asset", expanded=False):
                            st.warning("Deleting an asset will fail if it has associated risks.")
                            delete_confirm = st.checkbox("I understand and wish to delete this asset.")
                            if st.button("Delete Asset", type="primary") and delete_confirm:
                                if not has_permission("MANAGE_ASSETS"):
                                    st.error("Unauthorized")
                                    st.stop()
                                try:
                                    risks_count = execute_query("SELECT count(*) as count FROM risks WHERE asset_id = ?", (selected_id,), fetch_one=True)['count']
                                    if risks_count > 0:
                                        st.error(f"Cannot delete this asset because it has {risks_count} associated risk(s). Delete the risks first.")
                                    else:
                                        execute_query("DELETE FROM assets WHERE id = ?", (selected_id,))
                                        log_action("Asset Deleted", "Assets", f"Deleted asset ID {selected_id}", "assets", selected_id)
                                        st.success("Asset deleted successfully!")
                                        st.rerun()
                                except sqlite3.IntegrityError:
                                    st.error("Database integrity error: Cannot delete asset due to associated records.")
                                except Exception as e:
                                    st.error(f"Failed to delete asset: {e}")
            else:
                st.info("No assets available to manage.")
