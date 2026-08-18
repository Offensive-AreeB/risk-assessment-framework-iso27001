import streamlit as st

def render_about_page():
    st.title("ℹ️ About / Methodology")
    st.markdown("""
    This Risk Assessment Framework is an educational and practical GRC (Governance, Risk, and Compliance) 
    platform designed to align with the principles of ISO/IEC 27001.
    
    > **IMPORTANT**: This application provides a structured approach to risk assessment but **does not** constitute 
    or provide formal ISO certification. It is a tool to help organizations document and manage their cybersecurity posture.
    
    ---
    
    ### Risk Methodology
    
    The framework utilizes a standard 5×5 risk assessment matrix to evaluate risks based on their likelihood and impact.
    
    **Risk Score = Likelihood × Impact**
    
    Both Likelihood and Impact are scored on a scale from 1 to 5:
    - **Likelihood**: 1 (Rare) to 5 (Almost Certain)
    - **Impact**: 1 (Insignificant) to 5 (Severe)
    
    ### Risk Levels
    
    The resulting Risk Score (ranging from 1 to 25) is classified into four distinct levels to prioritize remediation efforts:
    
    - **1–4**: 🟢 **Low**
    - **5–9**: 🟡 **Medium**
    - **10–16**: 🟠 **High**
    - **17–25**: 🔴 **Critical**
    
    ### Treatment Strategies
    
    When a risk is identified, it must be treated. The framework supports the four standard risk treatment options:
    
    - **Mitigate**: Reduce the likelihood and/or impact of the risk by implementing additional controls or safeguards.
    - **Accept**: The organization consciously accepts the risk within its risk tolerance (requires justification).
    - **Transfer**: Transfer some or all of the risk to another party, such as through insurance or outsourcing.
    - **Avoid**: Eliminate the activity, process, or condition that creates the risk entirely.
    
    ### ISO/IEC 27001 Alignment
    
    This application integrates the full **ISO/IEC 27001:2022 Annex A** control library (93 controls). 
    Identified risks can be mapped directly to these standard controls. Based on these mappings and 
    applicability decisions, the system automatically generates a simplified **Statement of Applicability (SoA)**, 
    a core requirement for an ISO 27001 Information Security Management System (ISMS).
    """)
