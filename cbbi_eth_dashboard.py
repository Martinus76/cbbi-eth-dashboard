import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import matplotlib.pyplot as plt

# === ALERT – KONFIGURACJA ===
EMAIL_SENDER = "twoj_email@gmail.com"
EMAIL_PASSWORD = "twoje_app_haslo"
EMAIL_RECEIVER = "adres_docelowy@gmail.com"

LOW_THRESHOLD = 20
HIGH_THRESHOLD = 80

# === PAMIĘĆ ALERTÓW (prosty cache) ===
alert_state = {"low": False, "high": False}

# === FUNKCJA: Wysyłanie e-maila ===
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("✅ Email wysłany:", subject)
    except Exception as e:
        print("❌ Błąd e-mail:", e)

# === FUNKCJA: Sprawdzenie i alertowanie ===
def check_and_alert(score):
    if score >= HIGH_THRESHOLD and not alert_state["high"]:
        send_email("🚨 CBBI-ETH wysoki!", f"Wskaźnik = {score}/100 – ETH może być przewartościowany.")
        alert_state["high"] = True
        alert_state["low"] = False

    elif score <= LOW_THRESHOLD and not alert_state["low"]:
        send_email("📉 CBBI-ETH niski!", f"Wskaźnik = {score}/100 – potencjalna okazja zakupu ETH.")
        alert_state["low"] = True
        alert_state["high"] = False

# === FUNKCJA: Pobierz dane z CoinGecko ===
@st.cache_data(ttl=900)  # odświeżanie co 15 min
def get_eth_data():
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=90"
    response = requests.get(url).json()
    prices = response["prices"]
    timestamps = [datetime.fromtimestamp(p[0]/1000) for p in prices]
    values = [p[1] for p in prices]
    return timestamps, values

# === FUNKCJA: Prosty wskaźnik CBBI-ETH (na bazie % ceny) ===
def calculate_cbbi_eth(price_history):
    latest_price = price_history[-1]
    min_price = min(price_history)
    max_price = max(price_history)
    normalized = (latest_price - min_price) / (max_price - min_price)
    score = int(normalized * 100)
    return score

# === STREAMLIT ===
st.set_page_config(page_title="📊 CBBI-ETH Dashboard", layout="centered")
st.title("📊 Wskaźnik CBBI-ETH")
st.caption("Live dashboard z alertami progowymi")

# Dane
timestamps, prices = get_eth_data()
score = calculate_cbbi_eth(prices)

# Wykres
fig, ax = plt.subplots()
ax.plot(timestamps, prices, label="Cena ETH (USD)")
ax.set_title("ETH – ostatnie 90 dni")
ax.set_ylabel("Cena [USD]")
ax.grid(True)
st.pyplot(fig)

# Wynik
st.metric("📈 Aktualny wskaźnik CBBI-ETH", f"{score}/100")
