import streamlit as st
from groq import Groq
import docx
from pypdf import PdfReader

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'ai_name' not in st.session_state:
    st.session_state.ai_name = ""
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = ""

st.set_page_config(page_title="NTZ LAB AI", page_icon="🐺", layout="centered")

def get_text_from_file(file):
    if file.name.endswith('.docx'):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file.name.endswith('.pdf'):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    else:
        return file.read().decode('utf-8')

if st.session_state.step == 1:
    st.title("🔑 Авторизация системы")

    name_input = st.text_input(
        "Название нейросети",
        value=st.session_state.ai_name
    )

    key_input = st.text_input(
        "API Ключ",
        value=st.session_state.api_key,
        type="password"
    )

    if st.button("Подключиться", use_container_width=True):
        if name_input.strip() and key_input.strip():
            st.session_state.ai_name = name_input.strip()
            st.session_state.api_key = key_input.strip()
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("Заполните оба поля")

elif st.session_state.step == 2:
    st.title("📜 Настройка проверки")
    st.subheader(st.session_state.ai_name)

    uploaded_prompt = st.file_uploader("Загрузите prompt.txt", type=['txt'])

    if uploaded_prompt:
        st.session_state.system_prompt = uploaded_prompt.read().decode('utf-8')
        st.success("Промпт загружен")

    if st.button("Далее", use_container_width=True):
        if st.session_state.system_prompt:
            st.session_state.step = 3
            st.rerun()
        else:
            st.warning("Сначала загрузите промпт")

elif st.session_state.step == 3:
    st.title(f"🤖 Анализатор {st.session_state.ai_name}")

    uploaded_tz = st.file_uploader("Загрузите ТЗ", type=['docx', 'pdf', 'txt'])

    if uploaded_tz:
        if st.button("Проверить", type="primary", use_container_width=True):
            try:
                tz_text = get_text_from_file(uploaded_tz)
                client = Groq(api_key=st.session_state.api_key)

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": st.session_state.system_prompt},
                        {"role": "user", "content": f"Проверь это ТЗ:\n\n{tz_text}"}
                    ],
                    temperature=0.1
                )

                result = completion.choices[0].message.content
                st.subheader("Результат анализа")
                st.markdown(result)

            except Exception as e:
                st.error(f"Ошибка API: {e}")

    if st.button("Сброс"):
        st.session_state.step = 1
        st.rerun()
