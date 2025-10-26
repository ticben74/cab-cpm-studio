import streamlit as st
from openai import OpenAI
import math
from datetime import datetime
import pandas as pd

# === ربط OpenAI API (آمن عبر Secrets) ===
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    API_CONNECTED = True
except Exception as e:
    API_CONNECTED = False
    st.error(f"خطأ في الاتصال بـ OpenAI: {e}")

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

# === وكيل ذكي (ChatGPT - OpenAI) ===
with st.expander("وكيل ذكي: أسأل عن منهجية CAB-CPM®", expanded=True):
    st.markdown("**مدعوم بـ ChatGPT (OpenAI) – اسأل عن V، الزرع، الدورة الخماسية**")

    # تهيئة المحادثة
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "مرحباً! أنا **وكيل CAB-CPM®** مدعوم بـ **ChatGPT**. اسألني أي شيء عن المنهجية، مثل:\n\n- ما معنى V = (M × S × C)^R؟\n- كيف أطبق الزرع السياسي؟\n- اشرح الدورة الخماسية."}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("اكتب سؤالك هنا...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if not API_CONNECTED:
                st.error("OpenAI غير متصل. تحقق من المفتاح في Secrets.")
            else:
                system_prompt = """
أنت وكيل CAB-CPM® الذكي. أجب بالعربية الفصحى فقط، مستنداً إلى كتاب:
'Value Engineering and the Management Systems of Meaning' لأحمد عماد بن عمارة (2025).

ركز على:
- المعادلة: V = (M × S × C)^R
- الدورة الخماسية: التشخيص → السرد → التخطيط → الإنتاج → الإرث
- الزرع السياسي (Grafting): ربط المشروع بسياسات عامة
- خريطة الأصول الثقافية (CAG)
كن دقيقاً، موجزاً، واستخدم أمثلة من تونس (نابل، الحمامات، المالوف، الفخار).
                """.strip()

                # اختر: استجابة عادية أو بثّ مباشر
                use_streaming = True

                try:
                    if use_streaming:
                        with st.spinner("ChatGPT يفكر..."):
                            stream = client.responses.stream(
                                model="gpt-4o-mini",
                                input=f"{system_prompt}\n\nسؤال المستخدم: {prompt}"
                            )
                            placeholder = st.empty()
                            collected = ""
                            for event in stream:
                                if event.type == "response.output_text.delta":
                                    collected += event.delta
                                    placeholder.markdown(collected)
                            final = stream.get_final_response()
                            answer = final.output_text
                    else:
                        with st.spinner("ChatGPT يفكر..."):
                            response = client.responses.create(
                                model="gpt-4o-mini",
                                input=f"{system_prompt}\n\nسؤال المستخدم: {prompt}"
                            )
                            answer = response.output_text

                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    st.error(f"خطأ في الاتصال بـ OpenAI: {e}")
                    st.info("جرب مرة أخرى أو تحقق من الحدود (Spend Limit)")

# === جمع بيانات المشاركين ===
st.markdown("---")
with st.expander("أريد المشاركة في مشروع ثقافي", expanded=False):
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
                if 'participants' not in st.session_state:
                    st.session_state.participants = []
                st.session_state.participants.append({
                    "وقت": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "الاسم": name,
                    "البريد": email,
                    "الهاتف": phone,
                    "النوع": participant_type,
                    "المدينة": city,
                    "الفكرة": project_idea
                })
                st.success(f"شكراً {name}! تم استلام طلبك.")
                st.balloons()

    if 'participants' in st.session_state and st.session_state.participants:
        st.subheader("المشاركون (لوحة الإدارة)")
        df = pd.DataFrame(st.session_state.participants)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            label="تصدير كـ CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="cab_cpm_participants.csv",
            mime="text/csv"
        )

# === حاسبة القيمة المركبة ===
st.markdown("---")
st.subheader("حساب القيمة المركبة V = (M × S × C)^R")
col_m, col_s, col_c, col_r = st.columns(4)
m = col_m.slider("M – المعنى", 0.0, 1.0, 0.85, 0.05, help="قوة السرد الثقافي")
s = col_s.slider("S – الاستدامة", 0.0, 1.0, 0.75, 0.05, help="الدعم السياسي والاقتصادي")
c = col_c.slider("C – التماسك", 0.0, 1.0, 0.70, 0.05, help="الربط المحلي/العالمي")
r = col_r.slider("R – التجديد", 1.0, 2.0, 1.3, 0.1, help="من الزرع السياسي")

v = (m * s * c) ** r
status = "مستدام ومتماسك" if v >= 1.5 else "يحتاج تحسين"
st.metric("القيمة المركبة V", f"{v:.3f}", delta=status)
st.progress(min(v / 3.0, 1.0))

# === تذييل ===
st.markdown("---")
st.success("**CAB-CPM® Studio v3.0** – مدعوم بـ **ChatGPT (OpenAI)**")
st.caption("جميع البيانات آمنة ومحفوظة مؤقتاً. للإصدار الدائم: سيتم ربط Google Sheets قريباً.")

st.markdown("---")
st.success("**CAB-CPM® Studio v3.0** – مدعوم بـ **Grok-4 من xAI**")
st.caption("جميع البيانات آمنة ومحفوظة مؤقتاً. للإصدار الدائم: سيتم ربط Google Sheets قريباً.")
