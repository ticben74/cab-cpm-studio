import streamlit as st
from openai import OpenAI
import math
from datetime import datetime
import pandas as pd

# === ربط Grok-4 API ===
client = OpenAI(
    api_key=st.secrets["XAI_API_KEY"],  # من Secrets
    base_url="https://api.x.ai/v1"
)

# === إعداد الصفحة ===
st.set_page_config(page_title="CAB-CPM® Studio", page_icon="Compass", layout="wide")
st.title("Compass CAB-CPM® Studio")
st.markdown("**منصة الذكاء الاصطناعي لإدارة المشاريع الثقافية والإبداعية**")
st.markdown("*مبنية على إطار CAB-CPM® – Value Engineering & Meaning Systems*")
st.markdown("---")

# === واجهة الدردشة (Grok-4) ===
with st.expander("وكيل ذكي: أسأل عن منهجية CAB-CPM®", expanded=True):
    st.markdown("**Grok-4 مدرّب على الكتاب – اسأل عن V، الزرع، الدورة الخماسية**")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "مرحباً! أنا وكيل CAB-CPM® باستخدام **Grok-4**. اسألني عن المنهجية، مثل: 'ما معنى V = (M × S × C)^R؟'"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("اكتب سؤالك هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Grok-4 يفكر..."):
                try:
                    response = client.chat.completions.create(
                        model="grok-4-latest",
                        messages=[
                            {"role": "system", "content": "أنت وكيل CAB-CPM®. أجب بالعربية الفصحى، مستنداً إلى الكتاب 'Value Engineering and the Management Systems of Meaning' لأحمد عماد بن عمارة (2025). ركز على V = (M × S × C)^R، الدورة الخماسية، والزرع السياسي. كن دقيقاً وموجزاً."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.3
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"خطأ: {e}")
                    st.info("تأكد من صلاحية المفتاح أو الحدود (Spend Limit)")

# === جمع بيانات المشاركين ===
with st.expander("أريد المشاركة في مشروع ثقافي", expanded=False):
    with st.form("participation_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الكامل *")
        email = col2.text_input("البريد الإلكتروني *")
        phone = col1.text_input("رقم الهاتف")
        participant_type = col2.selectbox("نوع المشارك", ["فنان", "حرفي", "جمعية", "مدير ثقافي", "أخرى"])
        city = col1.selectbox("المدينة", ["نابل", "الحمامات", "صفاقس", "تونس", "أخرى"])
        project_idea = col2.text_area("المشروع المقترح")

        if st.form_submit_button("إرسال"):
            if not name or not email:
                st.error("املأ الاسم والبريد")
            else:
                if 'participants' not in st.session_state:
                    st.session_state.participants = []
                st.session_state.participants.append({
                    "وقت": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "الاسم": name, "البريد": email, "الهاتف": phone,
                    "النوع": participant_type, "المدينة": city, "الفكرة": project_idea
                })
                st.success(f"شكراً {name}!")
                st.balloons()

    if 'participants' in st.session_state and st.session_state.participants:
        st.subheader("المشاركون")
        df = pd.DataFrame(st.session_state.participants)
        st.dataframe(df)
        st.download_button("تصدير Excel", df.to_csv(index=False), "participants.csv", "text/csv")

# === حاسبة V ===
st.subheader("حساب القيمة المركبة V = (M × S × C)^R")
col_m, col_s, col_c, col_r = st.columns(4)
m = col_m.slider("M – المعنى", 0.0, 1.0, 0.85, 0.05)
s = col_s.slider("S – الاستدامة", 0.0, 1.0, 0.75, 0.05)
c = col_c.slider("C – التماسك", 0.0, 1.0, 0.70, 0.05)
r = col_r.slider("R – التجديد", 1.0, 2.0, 1.3, 0.1)
v = (m * s * c) ** r
st.metric("V", f"{v:.3f}", delta="مستدام" if v >= 1.5 else "يحتاج تحسين")
st.progress(min(v / 3.0, 1.0))

st.success("CAB-CPM® Studio v3.0 – مدعوم بـ Grok-4")
