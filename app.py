import pandas as pd
import streamlit as st

st.set_page_config(page_title="Ultimate Pro Options Scanner", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }
    .bullish-card { border-left: 8px solid #00FF00; background-color: rgba(0, 255, 0, 0.15); padding: 14px; border-radius: 8px; margin-bottom: 10px; }
    .bearish-card { border-left: 8px solid #FF0000; background-color: rgba(255, 0, 0, 0.15); padding: 14px; border-radius: 8px; margin-bottom: 10px; }
    .overbought-card { border-left: 8px solid #FF8C00; background-color: rgba(255, 140, 0, 0.15); padding: 14px; border-radius: 8px; margin-bottom: 10px; color: #FF8C00; }
    .no-trade-card { border-left: 8px solid #FFFF00; background-color: rgba(255, 255, 0, 0.15); padding: 14px; border-radius: 8px; margin-bottom: 10px; color: #FFFF00; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Ultimate Intraday Options Spike & Market Analyzer")
st.markdown(
    "Mobile-friendly advanced scanner for low-premium spikes, volume surge,"
    " and overbought/oversold filters."
)

st.sidebar.header("Advanced Scanner Filters")
min_ltp = st.sidebar.number_input(
    "Minimum LTP", min_value=0.1, max_value=1000.0, value=10.0
)
max_ltp = st.sidebar.number_input(
    "Maximum LTP", min_value=1.0, max_value=2000.0, value=50.0
)
min_change_pct = st.sidebar.slider(
    "Min % Price Change (Momentum)", min_value=0.0, max_value=100.0, value=15.0
)
overbought_threshold = st.sidebar.slider(
    "Overbought Limit (%)", min_value=50.0, max_value=200.0, value=60.0
)

uploaded_file = st.file_uploader(
    "Upload Option Chain CSV File", type=["csv"]
)

if uploaded_file is not None:
  with st.spinner("Analyzing Option Chain & Indicators..."):
    try:
      df = pd.read_csv(uploaded_file)
      df.columns = [str(c).strip() for c in df.columns]

      if "LTP" in df.columns and "Price_Change_Pct" in df.columns:
        filtered_df = df[
            (df["LTP"] >= min_ltp) & (df["LTP"] <= max_ltp)
        ].copy()

        if not filtered_df.empty:
          filtered_df["Suggested_SL"] = (
              filtered_df["LTP"] * 0.65
          ).round(2)
          filtered_df["Target_1"] = (
              filtered_df["LTP"] * 1.30
          ).round(2)
          filtered_df["Target_2"] = (
              filtered_df["LTP"] * 1.60
          ).round(2)

          if "Volume" in filtered_df.columns:
            filtered_df = filtered_df.sort_values(
                by=["Volume", "Price_Change_Pct"], ascending=False
            )
          else:
            filtered_df = filtered_df.sort_values(
                by="Price_Change_Pct", ascending=False
            )

          st.subheader("Filtered Options Chain Data Table")
          st.dataframe(filtered_df, use_container_width=True)

          csv_data = filtered_df.to_csv(index=False).encode("utf-8")
          st.download_button(
              label="Download Analyzed Trades CSV",
              data=csv_data,
              file_name="ultimate_spike_trades.csv",
              mime="text/csv",
          )

          st.markdown("---")
          st.subheader("Live Indicator & Signal Analysis")

          for _, row in filtered_df.iterrows():
            ltp = row["LTP"]
            pct = row["Price_Change_Pct"]
            strike = row.get("Strike", row.get("Strike Price", "N/A"))
            volume = row.get("Volume", "N/A")

            if pct >= overbought_threshold:
              st.markdown(
                  f"""
                            <div class="overbought-card">
                                <b>OVERBOTT WARNING:</b> Strike: {strike} | LTP: {ltp} | Change: +{pct}% | Market is in overbought zone, handle reversals or profit booking with care!
                            </div>
                            """,
                  unsafe_allow_html=True,
              )
            elif pct >= min_change_pct:
              st.markdown(
                  f"""
                            <div class="bullish-card">
                                <b>BUY / BULLISH SPIKE:</b> Strike: {strike} | LTP: {ltp} | Change: +{pct}% | Vol: {volume} <br>
                                Target 1: {row['Target_1']} | Target 2: {row['Target_2']} | Stop Loss: {row['Suggested_SL']}
                            </div>
                            """,
                  unsafe_allow_html=True,
              )
            elif pct <= -min_change_pct:
              st.markdown(
                  f"""
                            <div class="bearish-card">
                                <b>SELL / BEARISH SIGNAL:</b> Strike: {strike} | LTP: {ltp} | Change: {pct}%
                            </div>
                            """,
                  unsafe_allow_html=True,
              )
            else:
              st.markdown(
                  f"""
                            <div class="no-trade-card">
                                <b>NO TRADE ZONE / TIME DECAY:</b> Strike: {strike} | LTP: {ltp} | Change: {pct}% | Premium is decaying, stay away from trade.
                            </div>
                            """,
                  unsafe_allow_html=True,
              )
        else:
          st.warning(
              "No strikes found within the given LTP range. Please adjust range"
              " from sidebar."
          )
      else:
        st.error(
            "CSV file must contain 'LTP' and 'Price_Change_Pct' columns."
        )

    except Exception as e:
      st.error(f"Error processing data: {e}")
else:
  st.info("Please upload your option chain CSV file to begin scanning.")
