import streamlit as st
from datetime import datetime
import pandas as pd
import requests
from http import HTTPStatus
import os
# استيراد مكتبة Gemini
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.warning("⚠️ لتشغيل Gemini، الرجاء تثبيت: pip install google-genai")
    
# === إلغاء محاولة الاتصال بـ DashScope ===
DASHSCOPE_AVAILABLE = False
st.info("💎 تم تفعيل وكيل **Gemini®** كنموذج سحابي أساسي في هذا الإصدار.")

# === محاولة الاتصال بـ Gemini (Google) ===
GEMINI_AVAILABLE = False
client = None # تعريف العميل خارجياً
try:
    gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
    if gemini_api_key and 'genai' in globals(): # التأكد من استيراد المكتبة بنجاح
        client = genai.Client(api_key=gemini_api_key)
        GEMINI_AVAILABLE = True
    else:
        st.error("❌ مفتاح Gemini API (GEMINI_API_KEY) غير مضبوط في secrets.toml. لن يعمل الوكيل السحابي.")
except Exception as e:
    st.warning(f"❌ فشل إعداد Gemini: {e}. سيتم استخدام الوضع المحلي (Ollama).")
    

# === دالة للاتصال بـ Ollama (محلي - Offline) ===
def call_ollama(prompt: str, system_prompt: str, model: str = "qwen2.5:7b") -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_ctx": 4096
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get("response", "لا يوجد رد من النموذج المحلي.")
        else:
            raise Exception(f"خطأ من Ollama: {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama غير قيد التشغيل. شغّل: `ollama serve`")
    except Exception as e:
        raise e

# === دالة اتصال جديدة بـ Gemini ===
def call_gemini(prompt: str, system_prompt: str, model: str = "gemini-2.5-flash") -> str:
    """يتصل بنموذج Gemini كنموذج سحابي أساسي."""
    global client
    if not client:
        raise Exception("Gemini Client غير مهيأ.")

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(prompt)]),
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt, # استخدام system_instruction لضبط دور الوكيل
                temperature=0.3,
            )
        )
        return response.text
    except Exception as e:
        # إظهار خطأ Gemini بوضوح في حالة الفشل
        raise Exception(f"فشل الاتصال بـ Gemini: {e}")

# ---
# === وكلاء متعددين (تم تحديث التسلسل لـ Gemini أولاً) ===
# ---

def agent_cab_expert(question: str) -> str:
    sys_prompt = """
أنت خبير CAB-CPM®. أجب بالعربية الفصحى فقط، مستنداً إلى كتاب:
'Value Engineering and the Management Systems of Meaning' لأحمد عماد بن عمارة (2025).
ركز على: المعادلة: V = (M × S × C)^R، الدورة الخماسية، الزرع السياسي (Grafting)، خريطة الأصول الثقافية (CAG).
كن دقيقاً، موجزاً، واستخدم أمثلة من تونس (نابل، الحمامات، المالوف، الفخار).
    """.strip()
    
    # 1. محاولة Gemini (الخيار الأساسي)
    if GEMINI_AVAILABLE:
        try:
            return call_gemini(question, sys_prompt)
        except Exception as e:
            st.warning(f"فشل Gemini، نحاول Ollama... ({e})")
            
    # 2. محاولة Ollama (الخيار الاحتياطي)
    return call_ollama(question, sys_prompt, model="qwen2.5:7b")

def agent_value_analyst(question: str) -> str:
    sys_prompt = """
أنت محلل قيم في منهجية CAB-CPM®. مهمتك تحليل المشاريع الثقافية باستخدام المعادلة:
V = (M × S × C)^R
اقترح قيمًا رقمية منطقية، وفسّر كيف يمكن رفع القيمة V.
استخدم أمثلة من السياق التونسي (مثل مهرجان المالوف، ورش الفخار في نابل).
    """.strip()
    
    # 1. محاولة Gemini
    if GEMINI_AVAILABLE:
        try:
            return call_gemini(question, sys_prompt)
        except Exception as e:
            st.warning(f"فشل Gemini، نحاول Ollama... ({e})")
            
    # 2. محاولة Ollama
    return call_ollama(question, sys_prompt, model="qwen2.5:7b")

def agent_grafting(question: str) -> str:
    sys_prompt = """
أنت خبير في "الزرع السياسي" (Political Grafting) ضمن منهجية CAB-CPM®.
مهمتك ربط المشاريع الثقافية بسياسات عمومية تونسية حالية.
اقترح شراكات، تمويلات، أو آليات تضمين المشروع في السياسات العامة.
    """.strip()
    
    # 1. محاولة Gemini
    if GEMINI_AVAILABLE:
        try:
            return call_gemini(question, sys_prompt)
        except Exception as e:
            st.warning(f"فشل Gemini، نحاول Ollama... ({e})")
            
    # 2. محاولة Ollama
    return call_ollama(question, sys_prompt, model="qwen2.5:7b")

def coordinator(question: str) -> str:
    q_lower = question.lower()
    if any(kw in q_lower for kw in ["معادلة", "v =", "قيمة", "حساب", "m×s×c", "تجديد", "استدامة", "تماسك"]):
        return agent_value_analyst(question)
    elif any(kw in q_lower for kw in ["زرع", "سياسة", "شراكة", "وزارة", "استراتيجية", "تمويل", "بلدية"]):
        return agent_grafting(question)
    else:
        return agent_cab_expert(question)

# ---
# === إعداد الصفحة وبقية الكود ===
# ---
st.set_page_config(
    page_title="CAB-CPM® Studio",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧭 Compass CAB-CPM® Studio")
st.markdown("**منصة الذكاء الاصطناعي لإدارة المشاريع الثقافية والإبداعية**")
st.markdown("*مبنية على إطار CAB-CPM® – Value Engineering & Meaning Systems*")
st.markdown("---")

# === وكيل ذكي ===
with st.expander("وكيل ذكي: أسأل عن منهجية CAB-CPM®", expanded=True):
    # تحديث نص الشرح ليشمل Gemini فقط
    backend_status = []
    if GEMINI_AVAILABLE: backend_status.append("Gemini (Google)")
    backend_status.append("وكيل محلي (Ollama)")
    
    st.markdown(f"**مدعوم بـ {' + '.join(backend_status)}**")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "مرحباً! أنا **وكيل CAB-CPM®** الذكي. اسألني عن:\n\n- معادلة القيمة V = (M × S × C)^R\n- الزرع السياسي\n- الدورة الخماسية\n- خريطة الأصول الثقافية (CAG)"}
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
            try:
                with st.spinner("الوكيل الذكي يفكر..."):
                    answer = coordinator(prompt)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"فشل في توليد الرد: {e}")
                st.info("تأكد من:\n- **Gemini API key** (في .streamlit/secrets.toml)\n- أو تشغيل Ollama محليًا (`ollama serve`)")

# === جمع بيانات المشاركين (نفس الكود) ===
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

# === حاسبة القيمة المركبة (نفس الكود) ===
st.markdown("---")
st.subheader("حساب القيمة المركبة V = (M × S × C)^R")
col_m, col_s, col_c, col_r = st.columns(4)
m = col_m.slider("M – المعنى", 0.0, 1.0, 0.85, 0.05, help="قوة السرد الثقافي")
s = col_s.slider("S – الاستدامة", 0.0, 1.0, 0.75, 0.05, help="الدعم السياسي والاقتصادي")
c = col_c.slider("C – التماسك", 0.0, 1.0, 0.70, 0.05, help="الربط المحلي/العالمي")
r = col_r.slider("R – التجديد", 1.0, 2.0, 1.3, 0.1, help="من الزرع السياسي")

v = (m * s * c) ** r
status = "🟢 مستدام ومتماسك" if v >= 1.5 else "🟠 يحتاج تحسين"
st.metric("القيمة المركبة V", f"{v:.3f}", delta=status.split()[-1])
st.progress(min(v / 3.0, 1.0))

# === تذييل ===
st.markdown("---")
backend_list = []
if GEMINI_AVAILABLE:
    backend_list.append("Gemini (Google)")
if not backend_list:
    backend_list.append("Qwen (Ollama محلي فقط)")
    
backend_summary = " + ".join(backend_list)
st.success(f"**CAB-CPM® Studio v3.2** – مدعوم بـ **{backend_summary}**")
st.caption("البيانات مؤقتة. للنسخة الدائمة: سيتم دعم SQLite وGoogle Sheets قريباً.")
