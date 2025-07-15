import streamlit as st
import numpy as np

st.set_page_config(page_title="LuPSMA Prognostic Tool", layout="wide")
st.title("LuPSMA Prognostic Calculator (VISION Trial Based)")
st.markdown("Estimate probabilities for OS, rPFS, and PSA50 based on VISION nomogram mappings.")

# --- Sidebar: 사용자 입력 ---
st.sidebar.header("Pre-Treatment Variables")

suvmax     = st.sidebar.number_input("SUVmax",                     0.0, 350.0, 34.4, step=0.1)
time_dx    = st.sidebar.number_input("Years Since Diagnosis",     0.0, 26.0,  7.4, step=0.1)
opioid_use = st.sidebar.selectbox("Opioid Analgesic Use",      ["No","Yes"])
ast        = st.sidebar.number_input("AST (IU/L)",                  0,  90,  24)
hb         = st.sidebar.number_input("Hemoglobin (g/L)",           70, 160, 117)
lymph      = st.sidebar.number_input("Lymphocyte Count (×10⁹/L)", 0.0,  3.5, 1.025, step=0.01)
psma_ln    = st.sidebar.selectbox("PSMA+ Lymph Nodes",         ["No","Yes"])
ldh_high   = st.sidebar.selectbox("LDH ≥ 280 U/L",            ["No","Yes"])
alp_high   = st.sidebar.selectbox("ALP ≥ 140 U/L",            ["No","Yes"])
neut_high  = st.sidebar.selectbox("Neutrophil ≥ 7×10⁹/L",     ["No","Yes"])
liver_met  = st.sidebar.selectbox("Liver Metastases (CT)",    ["No","Yes"])


# --- 1) Overall Survival Points 계산 함수 --- 
def map_suvmax_os(x):
    # 0 → 100점, 350 → 0점
    return np.interp(x, [0, 350], [100, 0])

def map_time_os(x):
    # 0 → 28.5점, 26 → 0점
    return np.interp(x, [0, 26], [28.5, 0])

def map_ast(x):
    # 0 → 0점, 90 → 5점
    return np.interp(x, [0, 90], [0, 5])

def map_hb(x):
    # 160 → 0점, 70 → 46점
    return np.interp(x, [160, 70], [0, 46])

def map_lymph_os(x):
    # 3.5 → 0점, 0 → 37.5점
    return np.interp(x, [3.5, 0], [0, 37.5])

# Flag 점수
opioid_pts_os  = 12.5 if opioid_use == "Yes" else 0
psma_ln_pts    = 11   if psma_ln    == "Yes" else 0
ldh_pts_os     = 18   if ldh_high   == "Yes" else 0
alp_pts_os     = 17.2 if alp_high   == "Yes" else 0
neut_pts_os    = 15.5 if neut_high  == "Yes" else 0

# Total OS points
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

# OS 확률 앵커
os12_points = [0, 146, 168, 181, 191, 200, 224, 232]
os12_probs  = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.2, 0.1]
os24_points = [0, 109, 130, 144, 154, 187, 196]
os24_probs  = [1.0, 0.9, 0.8, 0.7, 0.6, 0.2, 0.1]

os_pts_clipped = np.clip(os_pts, 0, max(os12_points))
os12 = np.interp(os_pts_clipped, os12_points, os12_probs) * 100
os24 = np.interp(os_pts_clipped, os24_points, os24_probs) * 100


# --- 2) Radiographic PFS Points 계산 함수 ---
def map_time_pfs(x):
    # 0 → 24.2점, 26 → 0점
    return np.interp(x, [0, 26], [24.2, 0])

def map_lymph_pfs(x):
    # 3.5 → 0점, 0 → 32.4점
    return np.interp(x, [3.5, 0], [0, 32.4])

opioid_pts_pfs = 11.2 if opioid_use == "Yes" else 0
liver_pts      = 20.4 if liver_met   == "Yes" else 0
ldh_pts_pfs    = 12.4 if ldh_high    == "Yes" else 0
alp_pts_pfs    = 13.8 if alp_high    == "Yes" else 0

rpfs_pts = (
    map_suvmax_os(suvmax)     # SUVmax 동일 매핑
  + map_time_pfs(time_dx)
  + opioid_pts_pfs
  - map_lymph_pfs(lymph)
  + liver_pts
  + ldh_pts_pfs
  + alp_pts_pfs
)

pfs12_points = [109, 132, 144, 154, 163, 170, 178, 186, 196]
pfs12_probs  = [0.9,   0.8,   0.7,   0.6,   0.5,   0.4,   0.3,   0.2,   0.1]
pfs24_points = [72, 93, 107, 116, 125, 159]
pfs24_probs  = [0.9, 0.8, 0.7, 0.6, 0.5, 0.1]

rpfs_pts_clipped = np.clip(rpfs_pts, min(pfs12_points), max(pfs12_points))
pfs12 = np.interp(rpfs_pts_clipped, pfs12_points, pfs12_probs) * 100
pfs24 = np.interp(rpfs_pts_clipped, pfs24_points, pfs24_probs) * 100


# --- 3) PSA50 Points 계산 함수 ---
def map_suvmax_psa(x):
    # 0 → 0점, 350 → 100점
    return np.interp(x, [0, 350], [0, 100])

def map_lymph_psa(x):
    # 0 → 0점, 3.5 → 20점
    return np.interp(x, [0, 3.5], [0, 20])

alp_pts_psa = 0  if alp_high == "Yes" else 10

psa_pts = (
    map_suvmax_psa(suvmax)
  + map_lymph_psa(lymph)
  + alp_pts_psa
)

psa_points = [10.3, 16.2, 36, 42, 51.8]
psa_probs  = [0.2,  0.3,  0.7,0.8,  0.9]

psa_pts_clipped = np.clip(psa_pts, min(psa_points), max(psa_points))
psa50_prob      = np.interp(psa_pts_clipped, psa_points, psa_probs) * 100


# --- 4) 결과 표시 ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Overall Survival Probability")
    st.metric("12‑mo OS", f"{os12:.1f}%")
    st.metric("24‑mo OS", f"{os24:.1f}%")

with col2:
    st.subheader("Radiographic PFS Probability")
    st.metric("12‑mo rPFS", f"{pfs12:.1f}%")
    st.metric("24‑mo rPFS", f"{pfs24:.1f}%")

with col3:
    st.subheader("PSA50 Response Probability")
    st.metric("PSA50", f"{psa50_prob:.1f}%")

st.markdown("---")
st.caption("Nomogram-based point-to-probability interpolation implemented as provided.")

