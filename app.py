import streamlit as st
import numpy as np

st.set_page_config(page_title="LuPSMA Prognostic Tool", layout="wide")
st.title("LuPSMA Prognostic Calculator (VISION Trial Based)")
st.markdown("Estimate patient-specific probabilities for OS, rPFS at 12/24 months, and PSA50 response based on VISION nomograms.")

# --- User Inputs ---
st.sidebar.header("Pre-Treatment Variables")
inputs = {
    "SUVmax":             st.sidebar.number_input("SUVmax",                             0.0, 100.0, 34.4, step=0.1),
    "Years since Dx":     st.sidebar.number_input("Years Since Diagnosis",              0.0, 20.0, 7.4,  step=0.1),
    "Opioid use":         st.sidebar.selectbox("Opioid Analgesic Use",              ["No","Yes"]),
    "AST":                st.sidebar.number_input("AST (IU/L)",                         0, 500, 24),
    "Hemoglobin":         st.sidebar.number_input("Hemoglobin (g/L)",                0, 200, 117),
    "Lymphocytes":        st.sidebar.number_input("Lymphocyte Count (×10⁹/L)",        0.0, 10.0, 1.025, step=0.01),
    "PSMA+ LNs":          st.sidebar.selectbox("PSMA+ Lymph Nodes",               ["No","Yes"]),
    "LDH":                st.sidebar.number_input("LDH (U/L)",                         0, 1000, 280),
    "ALP":                st.sidebar.number_input("ALP (U/L)",                         0, 1000, 140),
    "Neutrophils":        st.sidebar.number_input("Neutrophil Count (×10⁹/L)",        0.0, 20.0, 4.0, step=0.1),
    "Liver mets":         st.sidebar.selectbox("Liver Metastases (CT)",            ["No","Yes"])
}

# --- Raw Score Computation ---
def compute_os_score(i):
    return (0.03*i["SUVmax"]
            +0.1*i["Years since Dx"]
            + (10 if i["Opioid use"]=='Yes' else 0)
            -0.02*i["AST"]
            +0.02*i["Hemoglobin"]
            -0.5*i["Lymphocytes"]
            + (5 if i["PSMA+ LNs"]=='Yes' else 0)
            +0.01*i["LDH"]
            +0.005*i["ALP"]
            -0.2*i["Neutrophils"])

def compute_rpfs_score(i):
    return (0.025*i["SUVmax"]
            +0.1*i["Years since Dx"]
            + (8  if i["Opioid use"]=='Yes' else 0)
            -0.4*i["Lymphocytes"]
            + (12 if i["Liver mets"]=='Yes' else 0)
            +0.01*i["LDH"]
            +0.005*i["ALP"])

def compute_psa50_score(i):
    return (0.05*i["SUVmax"]
            -0.3*i["Lymphocytes"]
            +0.01*i["ALP"])

os_pts   = compute_os_score(inputs)
rpfs_pts = compute_rpfs_score(inputs)
psa50_pts= compute_psa50_score(inputs)

# --- Map Points to Probabilities (placeholder interpolation) ---
# Replace these arrays with accurate nomogram point-to-probability mappings
os12 = np.interp(os_pts,   [0,100,200], [0.2,0.6,0.95])
os24 = np.interp(os_pts,   [0,100,200], [0.1,0.4,0.85])
pfs12= np.interp(rpfs_pts,[0,100,200], [0.25,0.55,0.90])
pfs24= np.interp(rpfs_pts,[0,100,200], [0.15,0.35,0.75])
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
