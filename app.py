import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# -----------------------------
# 1) OSNOVNE NASTAVITVE
# -----------------------------
st.set_page_config(
    page_title="Pametni chatbot",
    page_icon="💬",
    layout="centered"
)

# Malo CSS-ja za lepši widget videz
st.markdown("""
<style>
.block-container { max-width: 760px; padding-top: 1.2rem; }
div[data-testid="stChatMessage"] { border-radius: 14px; padding: 6px 10px; }
</style>
""", unsafe_allow_html=True)

st.title("💬 Pametni chatbot")
st.caption("Odgovarjam izključno v slovenščini in samo o določeni temi (specializacija).")

# -----------------------------
# 2) NALOŽI KLJUČ (lokalno .env ali Streamlit Secrets)
# -----------------------------
load_dotenv()

def get_secret(name: str, default: str = "") -> str:
    # Najprej poskusi Streamlit Secrets (oblak / lokalni secrets.toml)
    try:
        value = st.secrets.get(name, None)
        if value is not None:
            return str(value)
    except Exception:
        # lokalno pogosto nimaš secrets.toml -> ignoriraj
        pass

    # Nato .env / okoljske spremenljivke (lokalno)
    return os.getenv(name, default)


API_KEY = get_secret("GROQ_API_KEY", "")
MODEL = get_secret("MODEL", "llama-3.1-70b-versatile")

if not API_KEY:
    st.error("Manjka GROQ_API_KEY. Dodaj ga v .env (lokalno) ali v Streamlit Secrets (v oblaku).")
    st.stop()

client = Groq(api_key=API_KEY)

# -----------------------------
# 3) SPECIALIZACIJA (TUKAJ PRILAGODI TEMO)
# -----------------------------
TEMA = "tehnična podpora za spletno stran (npr. pomoč pri uporabi strani, pogosta vprašanja, navigacija, težave z dostopom)"
KLJUCNE_BESEDE = [
    "spletna stran", "stran", "prijava", "registracija", "geslo", "konto",
    "izdelek", "nakup", "košarica", "plačilo", "kontakt", "podpora",
    "napaka", "ne dela", "ne odpira", "povezava", "url", "widget"
]

def je_off_topic(vprasanje: str) -> bool:
    v = vprasanje.lower()
    return not any(k in v for k in KLJUCNE_BESEDE)

ODKLOP_ODGOVOR = (
    "Oprostite, za to področje nimam informacij. 🙏\n\n"
    f"Pomagam lahko samo v okviru teme: **{TEMA}**.\n\n"
    "Če želiš, opiši težavo na strani (kaj klikneš, kaj pričakuješ in kaj se zgodi), pa ti poskusim pomagati."
)

# -----------------------------
# 4) SPOMIN ZNOTRAJ SEJE (session_state)
# -----------------------------
if "messages" not in st.session_state:
    # sistemsko sporočilo vodi model (stil + omejitve)
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "Ti si prijazen pomočnik (chatbot). "
                "Odgovarjaj IZKLJUČNO v slovenščini, slovnično pravilno in pregledno. "
                f"Tvoja specializacija je: {TEMA}. "
                "Če uporabnik vpraša nekaj izven specializacije, vljudno zavrni in usmeri nazaj na temo. "
                "Odgovori naj bodo kratki, jasni, po potrebi z alinejami."
            )
        }
    ]

# Prikaži zgodovino (brez system sporočila)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# 5) VNOS UPORABNIKA
# -----------------------------
user_input = st.chat_input("Napiši vprašanje…")

if user_input:
    # Prikaži uporabnika
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Najprej preveri off-topic
    if je_off_topic(user_input):
        bot_text = ODKLOP_ODGOVOR
        st.session_state.messages.append({"role": "assistant", "content": bot_text})
        with st.chat_message("assistant"):
            st.markdown(bot_text)
        st.stop()

    # Klic Groq modela
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=st.session_state.messages,
            temperature=0.4
        )
        bot_text = response.choices[0].message.content

    except Exception as e:
        bot_text = (
            "Prišlo je do napake pri povezavi z jezikovnim modelom. 😕\n\n"
            "Poskusi znova čez nekaj trenutkov.\n\n"
            f"Tehnična napaka: `{e}`"
        )

    # Shrani + prikaži odgovor
    st.session_state.messages.append({"role": "assistant", "content": bot_text})
    with st.chat_message("assistant"):
        st.markdown(bot_text)