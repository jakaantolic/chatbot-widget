import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# -----------------------------
# 1) OSNOVNE NASTAVITVE
# -----------------------------
st.set_page_config(
    page_title="Specialist za kopačke",
    page_icon="⚽",
    layout="centered"
)

# Vizualna prilagoditev za nogometni stil
st.markdown("""
<style>
.block-container { max-width: 760px; padding-top: 1.2rem; }
div[data-testid="stChatMessage"] { border-radius: 14px; padding: 6px 10px; }
/* Tukaj lahko kasneje dodaš barve svoje spletne strani */
</style>
""", unsafe_allow_html=True)

st.title("⚽ Nogometni asistent")
st.caption("Svetujem vam pri izbiri idealnih kopačk za vašo igro.")

# -----------------------------
# 2) VARNOST: API KLJUČ (Secrets)
# -----------------------------
load_dotenv()

def get_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, None)
        if value is not None:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)

API_KEY = get_secret("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile" # Uporabljamo najnovejši model

if not API_KEY:
    st.error("Manjka API ključ v nastavitvah (Secrets)!")
    st.stop()

client = Groq(api_key=API_KEY)

# -----------------------------
# 3) SPECIALIZACIJA: NOGOMETNE KOPAČKE
# -----------------------------
TEMA = "nogometne kopačke in oprema (svetovanje o modelih, podlagah FG/AG/SG, znamkah Nike, Adidas, Puma itd.)"
KLJUCNE_BESEDE = [
    "kopačke", "čevlji", "nogomet", "trava", "umetna", "dvorana", 
    "nike", "adidas", "puma", "mercurial", "predator", "copa", "phantom",
    "podplat", "čepi", "fg", "ag", "sg", "ic", "tf", "številka", "velikost"
]

def je_off_topic(vprasanje: str) -> bool:
    v = vprasanje.lower()
    # Če vprašanje vsebuje katerokoli ključno besedo, ni off-topic
    return not any(k in v for k in KLJUCNE_BESEDE)

ODKLOP_ODGOVOR = (
    "Oprostite, sem specialist samo za **nogometne kopačke**. ⚽\n\n"
    "Lahko vam pomagam izbrati pravi model za travo, umetno podlago ali dvorano. "
    "Vprašajte me npr.: 'Katere kopačke so najboljše za umetno travo?'"
)

# -----------------------------
# 4) SPOMIN SEJE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "Ti si strokovnjak za nogometno obutev. Govoriš IZKLJUČNO slovensko. "
                f"Tvoja specializacija je: {TEMA}. "
                "Bodi prijazen, uporabi kakšen emoji (⚽, 👟) in svetuj profesionalno. "
                "Če te kdo vpraša za kuhanje, politiko ali karkoli drugega, vljudno zavrni."
            )
        }
    ]

# Prikaz pogovora
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# -----------------------------
# 5) LOGIKA KLEPETA
# -----------------------------
user_input = st.chat_input("Vprašaj o kopačkah...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Filter za temo
    if je_off_topic(user_input):
        bot_text = ODKLOP_ODGOVOR
        st.session_state.messages.append({"role": "assistant", "content": bot_text})
        with st.chat_message("assistant"):
            st.markdown(bot_text)
        st.stop()

    # Klic UI (Groq)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=st.session_state.messages,
            temperature=0.5
        )
        bot_text = response.choices[0].message.content
    except Exception as e:
        bot_text = f"Ups, napaka v igri: `{e}`"

    st.session_state.messages.append({"role": "assistant", "content": bot_text})
    with st.chat_message("assistant"):
        st.markdown(bot_text)
