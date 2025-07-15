import streamlit as st
import numpy as np

st.set_page_config(page_title="LuPSMA Prognostic Tool", layout="wide")
st.title("LuPSMA Prognostic Calculator (VISION Trial Based)")
st.markdown("Estimate probabilities for OS, rPFS, and PSA50 based on VISION nomogram mappings.")

# --- User Inputs ---
st.sidebar.header("Pre-Treatment Variables")
# Common inputs
suvmax      = st.sidebar.number_input("SUVmax", 0.0, 350.0, 34.4, step=0.1)
time_dx     = st.sidebar.number_input("Years Since Diagnosis", 0.0, 26.0, 7.4, step=0.1)
opioid_use  = st.sidebar.selectbox("Opioid Analgesic Use", ["No","Yes"])
ast         = st.sidebar.number_input("AST (IU/L)", 0, 90, 24)
hb          = st.sidebar.number_input("Hemoglobin (g/L)", 70, 160, 117)
lymph       = st.sidebar.number_input("Lymphocyte Count (×10⁹/L)", 0.0, 3.5, 1.025, step=0.01)
psma_ln     = st.sidebar.selectbox("PSMA+ Lymph Nodes", ["No","Yes"])
ldh_high    = st.sidebar.selectbox("LDH ≥ 280 U/L", ["No","Yes"])
alp_high    = st.sidebar.selectbox("ALP ≥ 140 U/L", ["No","Yes"])
neut_high   = st.sidebar.selectbox("Neutrophil Count ≥ 7×10⁹/L", ["No","Yes"])
liver_met   = st.sidebar.selectbox("Liver Metastases (CT)", ["No","Yes"])

# --- Variable-to-Points mapping ---
def map_suvmax_os(x):
    return np.interp(x, [350, 0], [0, 100])

def map_time_os(x):
    return np.interp(x, [26, 0], [0, 28.5])

def map_ast(x):
    return np.interp(x, [0, 90], [0, 5])

def map_hb(x):
    return np.interp(x, [160, 70], [0, 46])

def map_lymph_os(x):
    return np.interp(x, [3.5, 0], [0, 37.5])

# Flags
opioid_pts_os = 12.5 if opioid_use == 'Yes' else 0
psma_ln_pts    = 11   if psma_ln == 'Yes'    else 0
ldh_pts_os     = 18   if ldh_high == 'Yes'   else 0
alp_pts_os     = 17.2 if alp_high == 'Yes'   else 0
neut_pts_os    = 15.5 if neut_high == 'Yes'  else 0

# Compute OS total points
os_pts = (
    map_suvmax_os(suvmax)
  + map_time_os(time_dx)
  + opioid_pts_os
  + map_ast(ast)
  + map_hb(hb)
  + map_lymph_os(lymph)
  + psma_ln_pts
  + ldh_pts_os
  + alp_pts_os
  + neut_pts_os
)

# OS probability anchors
os12_points = [146, 168, 181, 191, 200, 224, 232]
os12_probs  = [0.9, 0.8, 0.7, 0.6, 0.5, 0.2, 0.1]
os24_points = [109, 130, 144, 154, 187, 196]
os24_probs  = [0.9, 0.8, 0.7, 0.6, 0.2, 0.1]

# Clip and interpolate OS probabilities
os_pts_clipped = np.clip(os_pts, min(os12_points), max(os12_points))
os12 = np.interp(os_pts_clipped, os12_points, os12_probs) * 100
os24 = np.interp(os_pts_clipped, os24_points, os24_probs) * 100

# --- rPFS variable-to-points mapping ---
def map_suvmax_pfs(x):
    return np.interp(x, [350, 0], [0, 100])

def map_time_pfs(x):
    return np.interp(x, [26, 0], [0, 24.2])

def map_lymph_pfs(x):
    return np.interp(x, [3.5, 0], [0, 32.4])

opioid_pts_pfs = 11.2 if opioid_use == 'Yes' else 0
liver_pts      = 20.4 if liver_met == 'Yes' else 0
ldh_pts_pfs    = 12.4 if ldh_high == 'Yes' else 0
alp_pts_pfs    = 13.8 if alp_high == 'Yes' else 0

# Compute rPFS total points
rpfs_pts = (
    map_suvmax_pfs(suvmax)
  + map_time_pfs(time_dx)
  + opioid_pts_pfs
  - map_lymph_pfs(0) + map_lymph_pfs(lymph) * -1  # inverted mapping
  + liver_pts
  + ldh_pts_pfs
  + alp_pts_pfs
)

# rPFS probability anchors
pfs12_points = [109, 132, 144, 154, 163, 170, 178, 186, 196]
pfs12_probs  = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
pfs24_points = [72, 93, 107, 116, 125, 159]
pfs24_probs  = [0.9,0.8,0.7,0.6,0.5,0.1]

# Clip and interpolate rPFS probabilities
rpfs_pts_clipped = np.clip(rpfs_pts, min(pfs12_points), max(pfs12_points))
pfs12 = np.interp(rpfs_pts_clipped, pfs12_points, pfs12_probs) * 100
pfs24 = np.interp(rpfs_pts_clipped, pfs24_points, pfs24_probs) * 100

# --- PSA50 variable-to-points mapping ---
def map_suvmax_psa(x):
    return np.interp(x, [0, 350], [0, 100])

def map_lymph_psa(x):
    return np.interp(x, [0, 3.5], [0, 20])

# ALP inverted: <140 →10, ≥140 →0
aLP_pts_psa   = 0 if alp_high == 'Yes' else 10

psa_pts = (
    map_suvmax_psa(suvmax)
  + map_lymph_psa(lymph)
  + aLP_pts_psa
)

# PSA50 probability anchors
psa_points = [10.3, 16.2, 36, 42, 51.8]
psa_probs  = [0.2, 0.3, 0.7, 0.8, 0.9]

psa_pts_clipped = np.clip(psa_pts, min(psa_points), max(psa_points))
psa50_prob      = np.interp(psa_pts_clipped, psa_points, psa_probs) * 100

# --- Display Outcomes ---
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Overall Survival Probability")
    st.metric("12-mo OS", f"{os12:.1f}%")
    st.metric("24-mo OS", f"{os24:.1f}%")
with col2:
    st.subheader("Radiographic PFS Probability")
    st.metric("12-mo rPFS", f"{pfs12:.1f}%")
    st.metric("24-mo rPFS", f"{pfs24:.1f}%")
with col3:
    st.subheader("PSA50 Response Probability")
    st.metric("PSA50", f"{psa50_prob:.1f}%")

st.markdown("---")
st.caption("Nomogram-based point-to-probability interpolation implemented as provided.")
