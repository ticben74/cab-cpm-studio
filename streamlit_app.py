import streamlit as st
import math

# === إعداد الصفحة ===
st.set_page_config(
    page_title="CAB-CPM® Studio",
    page_icon="Compass",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === العنوان والوصف ===
st.title("Compass CAB-CPM® Studio")
st.markdown("**منصة الذكاء الاصطناعي لإدارة المشاريع الثقافية والإبداعية**")
st.markdown("*مبنية على إطار CAB-CPM® – Value Engineering & Meaning Systems*")
st.markdown("---")

# === خريطة الأصول الثقافية (CAG) لنابل ===
nabeul_cag = {
    "فخار نابل": {"نوع": "ملموس", "سياسة": "برنامج التأهيل الحرفي 2025"},
    "مهرجان سينيتوال": {"نوع": "اجتماعي", "سياسة": "دعم وزارة الثقافة"},
    "متحف نيابوليس": {"نوع": "ملموس", "سياسة": "USAID نابل"},
    "قصص المتوسط": {"نوع": "غير ملموس", "سياسة": "الجائزة الوطنية للحرف"},
    "جمعية FTCA": {"نوع": "اجتماعي", "سياسة": "الصالون الوطني للصناعات التقليدية"}
}

grafting_proposals = [
    "• **ورشة: سينما + فخار** ← برنامج التأهيل الحرفي (تمويل 50,000 دينار)",
    "• **جائزة: أفضل فيلم حرفي** ← الجائزة الوطنية (3000 دينار + تسويق دولي)",
    "• **مسار السوق السينمائي** ← USAID نابل (تصدير +20%)"
]

# === المدخلات ===
col1, col2 = st.columns(2)
project_name = col1.text_input("اسم المشروع", "مهرجان سينما نابل 2026")
region = col2.selectbox("المنطقة", ["نابل", "صفاقس", "تونس", "سوسة", "قليبية"])

st.markdown("---")

# === الأزرار والوكلاء ===
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("وكيل التشخيص (Diagnosis Agent)"):
        st.subheader("خريطة الأصول الثقافية (CAG)")
        for asset, info in nabeul_cag.items():
            st.write(f"**{asset}** ({info['نوع']}) ← {info['سياسة']}")

with col_btn2:
    theme = st.text_input("موضوع الزرع", "سينما + فخار", key="theme_input")
    if st.button("وكيل الزرع السياسي (Grafting Agent)"):
        st.subheader("اقتراحات الزرع الثقافي")
        for prop in grafting_proposals:
            st.write(prop)
        st.info("**التجديد (R) = 1.3** – استدامة مضاعفة")

st.markdown("---")

# === حاسبة القيمة المركبة ===
st.subheader("حساب القيمة المركبة V = (M × S × C)^R")
col_m, col_s, col_c, col_r = st.columns(4)
m = col_m.slider("M – المعنى", 0.0, 1.0, 0.85, 0.05)
s = col_s.slider("S – الاستدامة", 0.0, 1.0, 0.75, 0.05)
c = col_c.slider("C – التماسك", 0.0, 1.0, 0.70, 0.05)
r = col_r.slider("R – التجديد", 1.0, 2.0, 1.3, 0.1)

v = (m * s * c) ** r
status = "مستدام ومتماسك" if v >= 1.5 else "يحتاج تحسين"
st.metric("القيمة المركبة V", f"{v:.3f}", delta=status)
st.progress(min(v / 3.0, 1.0))

st.markdown("---")
st.success(f"**المشروع '{project_name}' في {region} جاهز للتنفيذ!**")
st.info("**CAB-CPM® Studio v1.0** – أول منصة ذكاء اصطناعي ثقافي في تونس")
st.balloons()
