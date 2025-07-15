import streamlit as st
import numpy as np

st.set_page_config(page_title="LuPSMA Prognostic Tool", layout="wide")
st.title("LuPSMA Prognostic Calculator (VISION Trial Based)")
st.markdown("Estimate patient-specific probabilities for OS, rPFS at 12/24 months, and PSA50 response based on VISION nomograms.")

# --- User Inputs ---
st.sidebar.header("Pre-Treatment Variables")
inputs = {
    "SUVmax":           st.sidebar.number_input("SUVmax", 0.0, 100.0, 34.4, step=0.1),
    "Years since Dx":   st.sidebar.number_input("Years Since Diagnosis", 0.0, 20.0, 7.4, step=0.1),
    "Opioid use":       st.sidebar.selectbox("Opioid Analgesic Use", ["No","Yes"]),
    "AST":              st.sidebar.number_input("AST (IU/L)", 0, 500, 24),
    "Hemoglobin":       st.sidebar.number_input("Hemoglobin (g/L)", 0, 200, 117),
    "Lymphocytes":      st.sidebar.number_input("Lymphocyte Count (×10⁹/L)", 0.0, 10.0, 1.025, step=0.01),
    "PSMA+ LNs":        st.sidebar.selectbox("PSMA+ Lymph Nodes", ["No","Yes"]),
    "LDH ≥280":         st.sidebar.selectbox("LDH ≥ 280 U/L", ["No","Yes"]),
    "ALP ≥140":         st.sidebar.selectbox("ALP ≥ 140 U/L", ["No","Yes"]),
    "Neutrophils":      st.sidebar.number_input("Neutrophil Count (×10⁹/L)", 0.0, 20.0, 4.0, step=0.1),
    "Liver mets":       st.sidebar.selectbox("Liver Metastases (CT)", ["No","Yes"])
}

# Convert categorical flags to numeric
ldh_flag  = 1 if inputs["LDH ≥280"] == 'Yes' else 0
alp_flag  = 1 if inputs["ALP ≥140"] == 'Yes' else 0
opiate_flag = 1 if inputs["Opioid use"] == 'Yes' else 0
psma_ln_flag = 1 if inputs["PSMA+ LNs"] == 'Yes' else 0
liver_flag  = 1 if inputs["Liver mets"] == 'Yes' else 0

# --- Raw Score Computation ---
def compute_os_score(i, ldh_f, alp_f, op_f, psma_f):
    # Placeholder coefficients: replace with nomogram point values
    return (0.03 * i["SUVmax"]
            +0.1 * i["Years since Dx"]
            +10   * op_f
            -0.02 * i["AST"]
            +0.02 * i["Hemoglobin"]
            -0.5  * i["Lymphocytes"]
            +5    * psma_f
            +7    * ldh_f
            +3    * alp_f
            -0.2  * i["Neutrophils"])

 def compute_rpfs_score(i, op_f, lymph, liver_f, ldh_f, alp_f):
    return (0.025 * i["SUVmax"]
            +0.1   * i["Years since Dx"]
            +8     * op_f
            -0.4   * lymph
            +12    * liver_f
            +5     * ldh_f
            +2     * alp_f)

 def compute_psa50_score(i, lymph, alp_f):
    return (0.05  * i["SUVmax"]
            -0.3   * lymph
            +8     * alp_f)

os_pts   = compute_os_score(inputs,    ldh_flag, alp_flag, opiate_flag, psma_ln_flag)
rpfs_pts = compute_rpfs_score(inputs, opiate_flag, inputs["Lymphocytes"], liver_flag, ldh_flag, alp_flag)
psa50_pts= compute_psa50_score(inputs, inputs["Lymphocytes"], alp_flag)

# --- Map Points to Probabilities (placeholder interpolation) ---
os12 = np.interp(os_pts,    [0,100,200], [0.2,0.6,0.95])
os24 = np.interp(os_pts,    [0,100,200], [0.1,0.4,0.85])
pfs12= np.interp(rpfs_pts, [0,100,200], [0.25,0.55,0.90])
pfs24= np.interp(rpfs_pts, [0,100,200], [0.15,0.35,0.75])
psa50_prob = 1/(1+np.exp(- (psa50_pts - 5)/2))  # logistic placeholder

# --- Display Probabilities ---
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Overall Survival Probability")
    st.metric("12-month OS", f"{os12*100:.1f}%")
    st.metric("24-month OS", f"{os24*100:.1f}%")
with col2:
    st.subheader("Radiographic PFS Probability")
    st.metric("12-month rPFS", f"{pfs12*100:.1f}%")
    st.metric("24-month rPFS", f"{pfs24*100:.1f}%")
with col3:
    st.subheader("PSA50 Response Probability")
    st.metric("PSA50", f"{psa50_prob*100:.1f}%")

st.markdown("---")
st.caption("Note: Probability mappings are placeholders. Update interpolation anchors based on published nomogram curves.")

