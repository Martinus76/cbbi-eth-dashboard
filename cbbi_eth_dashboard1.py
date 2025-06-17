import streamlit as st
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta

# -- Konfiguracja interfejsu --
st.set_page_config(page_title="CBBI-ETH Dashboard", layout="centered")
st.title("📊 CBBI-ETH Dashboard")

# -- Pobieranie danych ETH z CoinGecko --
@st.cache_data(ttl=900)
def fetch_eth_data():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=90)
    url = f"https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
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
def calculate_cbbi_eth(prices):
    max_price = max(prices)
    min_price = min(prices)
    latest_price = prices[-1]
    if max_price == min_price:
        return 0
    score = (latest_price - min_price) / (max_price - min_price) * 100
    return round(score, 2)

# -- Obliczanie wskaźników CBBI-ETH w czasie --
cbbi_scores = []
for i in range(len(prices)):
    sub_prices = prices[:i + 1]
    if len(sub_prices) > 1:
        cbbi_scores.append(calculate_cbbi_eth(sub_prices))
    else:
        cbbi_scores.append(0)

# -- Główna wartość wskaźnika --
score = calculate_cbbi_eth(prices)
st.metric("📈 Aktualny wskaźnik CBBI-ETH", f"{score}/100")

# -- Wykres z dwiema osiami: cena i wskaźnik --
fig, ax1 = plt.subplots()

color = 'tab:blue'
ax1.set_xlabel("Data")
ax1.set_ylabel("Cena ETH [USD]", color=color)
ax1.plot(timestamps, prices, color=color, label="Cena ETH")
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel("CBBI-ETH [%]", color=color)
ax2.plot(timestamps, cbbi_scores, color=color, linestyle='--', label="CBBI-ETH")
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
st.pyplot(fig)

# -- Alert e-mailowy (na przyszłość – tu tylko konsola) --
def check_and_alert(score):
    if score > 80:
        st.warning("📤 Alert: CBBI-ETH przekroczył 80 – rozważ sprzedaż!")
    elif score < 20:
        st.success("📥 Alert: CBBI-ETH poniżej 20 – rozważ zakup!")

check_and_alert(score)
