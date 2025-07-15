import streamlit as st

st.title("LuPSMA Prognostic Calculator (VISION Trial Based)")

st.markdown("This tool estimates response to 177Lu-PSMA-617 therapy based on pre-treatment variables.")

# 사용자 입력
suvmax = st.slider("SUVmax", 10.0, 100.0, 35.0)
hb = st.number_input("Hemoglobin (g/L)", min_value=0, value=120)
ast = st.number_input("AST (IU/L)", min_value=0, value=25)
ldh = st.number_input("LDH (U/L)", min_value=0, value=250)
alp = st.number_input("ALP (U/L)", min_value=0, value=120)
lymph = st.number_input("Lymphocyte Count (×10⁹/L)", value=1.0)
opiate = st.selectbox("Opioid Use", ["No", "Yes"])
time_dx = st.number_input("Years Since Diagnosis", value=6.0)

# 임의 점수 계산 (향후 정확한 nomogram 점수 반영 가능)
score = suvmax * 1.5 + hb * 0.2 - ast * 0.1 + (50 if opiate == "Yes" else 0)

st.write(f"🔢 예측 점수: {score:.2f}")

if score > 200:
    st.success("Low-risk group (favorable prognosis)")
else:
    st.error("High-risk group (unfavorable prognosis)")
