import streamlit as st
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="CBBI-ETH Dashboard", layout="centered")
st.title("📊 CBBI-ETH Dashboard")

# -- Pobieranie danych ETH z CoinGecko --
@st.cache_data(ttl=900)
def fetch_eth_data():
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "90",
        "interval": "daily"
    }
    response = requests.get(url, params=params)
    data = response.json()
    prices = [p[1] for p in data["prices"]]
    timestamps = [datetime.fromtimestamp(p[0] / 1000) for p in data["prices"]]
    return timestamps, prices

timestamps, prices = fetch_eth_data()

# -- Obliczanie wskaźnika CBBI-ETH --
def calculate_cbbi_eth(price_history):
    min_price = min(price_history)
    max_price = max(price_history)
    current_price = price_history[-1]
    if max_price == min_price:
        return 0
    return round((current_price - min_price) / (max_price - min_price) * 100, 2)

cbbi_scores = []
for i in range(len(prices)):
    history = prices[:i+1]
    cbbi_scores.append(calculate_cbbi_eth(history))

current_score = cbbi_scores[-1]
st.metric("📈 CBBI-ETH", f"{current_score}/100")

# -- Wykres z dwiema osiami: cena ETH + wskaźnik CBBI-ETH --
fig, ax1 = plt.subplots()

color = "tab:blue"
ax1.set_xlabel("Data")
ax1.set_ylabel("Cena ETH (USD)", color=color)
ax1.plot(timestamps, prices, color=color, label="ETH")
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = "tab:red"
ax2.set_ylabel("CBBI-ETH [%]", color=color)
ax2.plot(timestamps, cbbi_scores, color=color, linestyle="--", label="CBBI-ETH")
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
st.pyplot(fig)

# -- Alerty --
if current_score > 80:
    st.warning("🔺 CBBI-ETH powyżej 80 – rozważ sprzedaż")
elif current_score < 20:
    st.success("🟢 CBBI-ETH poniżej 20 – rozważ zakup")
