import os
import time
import glob
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator


try:
    _icon = Image.open('logo_mr.png')
except Exception:
    _icon = "🎤"
st.set_page_config(page_title="Traductor de Voz · Miguel Ruiz", page_icon=_icon, layout="centered")

# ---- Estilo personalizado: paleta azul petróleo + terracota (Miguel Ruiz) ----
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700&family=Inter:wght@300;400;600&display=swap');
    .stApp {
        background: linear-gradient(135deg, #1b3a4b 0%, #14303d 100%);
        color: #e8eef0;
        font-family: 'Inter', sans-serif;
    }
    .stApp, .stApp p, .stApp li, .stApp span, .stApp label,
    .stMarkdown, [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * {
        color: #e8eef0 !important;
    }
    h1, h2, h3, h4 { font-family: 'Montserrat', sans-serif !important; color: #e07a5f !important; }
    .stTextInput input, .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input {
        background-color: #f3f6f7 !important; color: #14303d !important;
    }
    input::placeholder, textarea::placeholder { color: #5c7079 !important; }
    [data-testid="stNotification"] * { color: #14303d !important; }
    section[data-testid="stSidebar"] { background: #12272f; }
    section[data-testid="stSidebar"] * { color: #e8eef0 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #e07a5f !important; }
    .stButton>button {
        background-color: #e07a5f; color: #fff !important; border-radius: 10px; border: none; font-weight: 600;
    }
    .stButton>button:hover { background-color: #c9583c; color: #fff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h2 style=\"font-family:'Montserrat', sans-serif; font-weight:700; color:#f2cc8f; margin-bottom:0;\">Miguel Ruiz</h2>", unsafe_allow_html=True)
st.title("TRADUCTOR DE VOZ 🎤")
st.subheader("Escucho lo que quieres traducir.")

image = Image.open('OIG7.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("Traductor")
    st.write("Presiona el botón «Escuchar», cuando se active habla lo que "
             "quieres traducir. El texto reconocido aparecerá abajo; cópialo "
             "y pégalo en el recuadro. Luego elige los idiomas y pulsa «Convertir».")

st.write("Toca el botón y habla lo que quieres traducir 👇")

# ---- Micrófono con reconocimiento de voz del navegador (sin bokeh) ----
# Usa webkitSpeechRecognition (mismo motor que el original) dentro de un
# componente HTML. El texto reconocido se muestra para copiar y pegar.
components.html(
    """
    <div style="font-family: 'Inter', sans-serif;">
      <button id="rec" style="background:#e07a5f;color:#fff;border:none;
        border-radius:10px;padding:12px 22px;font-size:16px;font-weight:600;cursor:pointer;">
        Escuchar 🎤
      </button>
      <span id="status" style="margin-left:12px;color:#14303d;font-weight:600;"></span>
      <div id="out" style="margin-top:14px;background:#f3f6f7;color:#14303d;
        border-radius:10px;padding:12px;min-height:44px;font-size:16px;">
        El texto reconocido aparecerá aquí…
      </div>
    </div>
    <script>
      const btn = document.getElementById('rec');
      const out = document.getElementById('out');
      const status = document.getElementById('status');
      btn.onclick = function() {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) { out.innerText = "Tu navegador no soporta reconocimiento de voz. Usa Chrome."; return; }
        const recognition = new SR();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'es-ES';
        status.innerText = "🔴 Escuchando...";
        let finalText = "";
        recognition.onresult = function(e) {
          let interim = "";
          for (let i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) { finalText += e.results[i][0].transcript; }
            else { interim += e.results[i][0].transcript; }
          }
          out.innerText = (finalText + interim) || "…";
        };
        recognition.onend = function() { status.innerText = "✅ Listo. Copia el texto y pégalo abajo."; };
        recognition.onerror = function(ev) { status.innerText = "⚠️ Error: " + ev.error; };
        recognition.start();
      };
    </script>
    """,
    height=200,
)

st.markdown("**Pega aquí el texto que dijiste (o escríbelo):**")
text = st.text_input("Texto a traducir", placeholder="Escribe o pega el texto reconocido...")

if text:
    try:
        os.mkdir("temp")
    except Exception:
        pass

    st.title("Texto a Audio")

    in_lang = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    )
    if in_lang == "Inglés":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Bengali":
        input_language = "bn"
    elif in_lang == "Coreano":
        input_language = "ko"
    elif in_lang == "Mandarín":
        input_language = "zh-cn"
    elif in_lang == "Japonés":
        input_language = "ja"

    out_lang = st.selectbox(
        "Selecciona el lenguaje de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    )
    if out_lang == "Inglés":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Bengali":
        output_language = "bn"
    elif out_lang == "Coreano":
        output_language = "ko"
    elif out_lang == "Mandarín":
        output_language = "zh-cn"
    elif out_lang == "Japonés":
        output_language = "ja"

    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canada",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
    )

    if english_accent == "Defecto":
        tld = "com"
    elif english_accent == "Español":
        tld = "com.mx"
    elif english_accent == "Reino Unido":
        tld = "co.uk"
    elif english_accent == "Estados Unidos":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Irlanda":
        tld = "ie"
    elif english_accent == "Sudáfrica":
        tld = "co.za"

    def text_to_speech(input_language, output_language, text, tld):
        trans_text = GoogleTranslator(source=input_language, target=output_language).translate(text)
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except Exception:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar el texto")

    if st.button("convertir"):
        result_name, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result_name}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("## Texto de salida:")
            st.write(f" {output_text}")

    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)
