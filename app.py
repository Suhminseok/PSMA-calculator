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
    "Neutrophils ≥7":   st.sidebar.selectbox("Neutrophil Count ≥ 7×10⁹/L", ["No","Yes"]),
    "Liver mets":       st.sidebar.selectbox("Liver Metastases (CT)", ["No","Yes"])
}

# Convert categorical flags to numeric
ldh_flag     = 1 if inputs["LDH ≥280"] == 'Yes' else 0
alp_flag     = 1 if inputs["ALP ≥140"] == 'Yes' else 0
opiate_flag  = 1 if inputs["Opioid use"] == 'Yes' else 0
psma_ln_flag = 1 if inputs["PSMA+ LNs"] == 'Yes' else 0
neutro_flag  = 1 if inputs["Neutrophils ≥7"] == 'Yes' else 0
liver_flag   = 1 if inputs["Liver mets"] == 'Yes' else 0

# --- Raw Score Computation ---
def compute_os_score(i, ldh_f, alp_f, op_f, psma_f, neutro_f):
    # Placeholder coefficients: replace with nomogram point values
    score = (
        0.03 * i["SUVmax"]
        + 0.1 * i["Years since Dx"]
        + 10   * op_f
        - 0.02 * i["AST"]
        + 0.02 * i["Hemoglobin"]
        - 0.5  * i["Lymphocytes"]
        + 5    * psma_f
        + 7    * ldh_f
        + 3    * alp_f
        + 4    * neutro_f
    )
    return score


def compute_rpfs_score(i, op_f, lymph, liver_f, ldh_f, alp_f):
    score = (
        0.025 * i["SUVmax"]
        + 0.1   * i["Years since Dx"]
        + 8     * op_f
        - 0.4   * lymph
        + 12    * liver_f
        + 5     * ldh_f
        + 2     * alp_f
    )
    return score


def compute_psa50_score(i, lymph, alp_f):
    score = (
        0.05   * i["SUVmax"]
        - 0.3   * lymph
        + 8     * alp_f
    )
    return score

# --- Compute Points ---
os_pts    = compute_os_score(inputs, ldh_flag, alp_flag, opiate_flag, psma_ln_flag, neutro_flag)
rpfs_pts  = compute_rpfs_score(inputs, opiate_flag, inputs["Lymphocytes"], liver_flag, ldh_flag, alp_flag)
psa50_pts = compute_psa50_score(inputs, inputs["Lymphocytes"], alp_flag)

# --- Map Points to Probabilities via linear interpolation using provided anchors ---
# OS 12-mo anchors: points ascending, probabilities descending
os12_points = [146, 168, 181, 191, 200, 224, 232]
os12_probs  = [0.9, 0.8, 0.7, 0.6, 0.5, 0.2, 0.1]
# OS 24-mo anchors
os24_points = [109, 130, 144, 154, 187, 196]
os24_probs  = [0.9, 0.8, 0.7, 0.6, 0.2, 0.1]
# rPFS 12-mo anchors
pfs12_points = [109, 132, 144, 154, 163, 170, 178, 186, 196]
pfs12_probs  = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
# rPFS 24-mo anchors
pfs24_points = [ 72,  93, 107, 116, 125, 159]
pfs24_probs  = [0.9, 0.8, 0.7, 0.6, 0.5, 0.1]
# PSA50 response anchors
psa_points   = [10.3, 16.2, 36, 42, 51.8]
psa_probs    = [0.2,  0.3, 0.7,0.8, 0.9]

# Clip total point values
os_pts_clipped   = np.clip(os_pts,    min(os12_points),   max(os12_points))
    
rpfs_pts_clipped = np.clip(rpfs_pts,  min(pfs12_points),  max(pfs12_points))
psa_pts_clipped  = np.clip(psa50_pts, min(psa_points),    max(psa_points))

# Interpolate
os12       = np.interp(os_pts_clipped,   os12_points,  os12_probs)
os24       = np.interp(os_pts_clipped,   os24_points,  os24_probs)
pfs12      = np.interp(rpfs_pts_clipped, pfs12_points,pfs12_probs)
pfs24      = np.interp(rpfs_pts_clipped, pfs24_points,pfs24_probs)
psa50_prob = np.interp(psa_pts_clipped,  psa_points,   psa_probs)

# Multiply by 100 for percent
os12 *= 100
os24 *= 100
pfs12 *= 100
pfs24 *= 100
psa50_prob *= 100
