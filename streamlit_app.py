import streamlit as st
import math
from datetime import datetime

# === إعداد الصفحة ===
st.set_page_config(
    page_title="CAB-CPM® Studio",
    page_icon="Compass",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === العنوان ===
st.title("Compass CAB-CPM® Studio")
st.markdown("**منصة الذكاء الاصطناعي لإدارة المشاريع الثقافية والإبداعية**")
st.markdown("*مبنية على إطار CAB-CPM® – Value Engineering & Meaning Systems*")
st.markdown("---")

# === خريطة الأصول الثقافية (CAG) لنابل والحمامات ===
cag_data = {
    "نابل": {
        "فخار نابل": {"نوع": "ملموس", "سياسة": "برنامج التأهيل الحرفي 2025"},
        "مهرجان سينيتوال": {"نوع": "اجتماعي", "سياسة": "دعم وزارة الثقافة"},
        "متحف نيابوليس": {"نوع": "ملموس", "سياسة": "USAID نابل"}
    },
    "الحمامات": {
        "مسرح الهواء الطلق": {"نوع": "ملموس", "سياسة": "دعم وزارة الثقافة"},
        "المركز الثقافي الدولي": {"نوع": "اجتماعي", "سياسة": "تونس عاصمة الثقافة 2026"},
        "تراث المالوف": {"نوع": "غير ملموس", "سياسة": "الجائزة الوطنية للموسيقى"}
    }
}

grafting_suggestions = {
    "نابل": [
        "• ورشة: سينما + فخار ← برنامج التأهيل",
        "• جائزة: أفضل فيلم حرفي ← الجائزة الوطنية"
    ],
    "الحمامات": [
        "• ورشة: أوبرا + مالوف ← تونس عاصمة الثقافة",
        "• جائزة: أفضل عمل أوبرالي ← الجائزة الوطنية"
    ]
}

# === استمارة المشاركة (جمع البيانات) ===
with st.expander("أريد المشاركة في مشروع ثقافي", expanded=True):
    with st.form("participation_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الكامل *", placeholder="أحمد بن عمارة")
        email = col2.text_input("البريد الإلكتروني *", placeholder="ahmed@example.com")
        phone = col1.text_input("رقم الهاتف", placeholder="216 00 000 000")
        participant_type = col2.selectbox("نوع المشارك", 
            ["فنان", "حرفي", "جمعية", "مدير ثقافي", "طالب", "أخرى"])
        city = col1.selectbox("المدينة", 
            ["نابل", "الحمامات", "صفاقس", "تونس", "سوسة", "قليبية", "أخرى"])
        project_idea = col2.text_area("المشروع المقترح", 
            placeholder="مثال: ورشة أوبرا + تراث المالوف")

        submitted = st.form_submit_button("إرسال الطلب")
        
        if submitted:
            if not name or not email:
                st.error("الرجاء ملء الاسم والبريد الإلكتروني")
            else:
                # حفظ في session_state (مؤقتاً)
                if 'participants' not in st.session_state:
                    st.session_state.participants = []
                st.session_state.participants.append({
                    "وقت": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "الاسم": name, "البريد": email, "الهاتف": phone,
                    "النوع": participant_type, "المدينة": city, "الفكرة": project_idea
                })
                
                # حساب V تلقائي
                m = 0.8
                s = 0.7
                c = 0.6
                r = 1.2
                if "فخار" in project_idea or "حرف" in project_idea: m += 0.1
                if city in ["نابل", "الحمامات"]: s += 0.1
                if participant_type in ["فنان", "حرفي"]: c += 0.1
                v = (m * s * c) ** r
                
                st.success(f"شكراً {name}! تم استلام طلبك.")
                st.balloons()
                st.info(f"**القيمة المتوقعة لمشروعك: V = {v:.2f}**")

# === عرض المشاركين (لك فقط) ===
if 'participants' in st.session_state and st.session_state.participants:
    st.markdown("---")
    st.subheader("المشاركون (لوحة الإدارة)")
    df = pd.DataFrame(st.session_state.participants)
    st.dataframe(df, use_container_width=True)
    st.download_button("تصدير Excel", df.to_csv(index=False), "participants.csv", "text/csv")

# === باقي الوكلاء ===
col1, col2 = st.columns(2)
project_name = col1.text_input("اسم المشروع", "مهرجان الأوبرا في الحمامات")
region = col2.selectbox("المنطقة", list(cag_data.keys()))

st.markdown("---")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("وكيل التشخيص"):
        st.subheader("خريطة الأصول الثقافية")
        for asset, info in cag_data.get(region, {}).items():
            st.write(f"**{asset}** ({info['نوع']}) ← {info['سياسة']}")

with col_btn2:
    if st.button("وكيل الزرع السياسي"):
        st.subheader("اقتراحات الزرع")
        for sug in grafting_suggestions.get(region, []):
            st.write(sug)

st.markdown("---")
st.subheader("حساب القيمة V = (M × S × C)^R")
col_m, col_s, col_c, col_r = st.columns(4)
m = col_m.slider("M", 0.0, 1.0, 0.85, 0.05)
s = col_s.slider("S", 0.0, 1.0, 0.75, 0.05)
c = col_c.slider("C", 0.0, 1.0, 0.70, 0.05)
r = col_r.slider("R", 1.0, 2.0, 1.3, 0.1)
v = (m * s * c) ** r
st.metric("V", f"{v:.3f}", delta="مستدام" if v >= 1.5 else "يحتاج تحسين")
st.progress(min(v / 3.0, 1.0))

st.success(f"المشروع '{project_name}' جاهز!")
st.caption("البيانات محفوظة مؤقتاً – سيتم ربط Google Sheets قريباً")
