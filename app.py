import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Pro Options Spike Scanner", layout="wide")

# Custom CSS for Background and Dynamic Signal Cards
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }
    .bullish-card { border-left: 6px solid #00FF00; background-color: rgba(0, 255, 0, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 8px; }
    .bearish-card { border-left: 6px solid #FF0000; background-color: rgba(255, 0, 0, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 8px; }
    .no-trade-card { border-left: 6px solid #FFFF00; background-color: rgba(255, 255, 0, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 8px; color: #FFFF00; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🚀 Advanced Intraday Options Spike Scanner")

# Sidebar Settings
st.sidebar.header("⚙️ Scanner Settings")
min_ltp = st.sidebar.number_input(
    "Minimum LTP", min_value=0.1, max_value=1000.0, value=10.0
)
max_ltp = st.sidebar.number_input(
    "Maximum LTP", min_value=1.0, max_value=2000.0, value=50.0
)
min_change_pct = st.sidebar.slider(
    "Min % Price Change", min_value=0.0, max_value=100.0, value=15.0
)

# File Uploader
uploaded_file = st.file_uploader(
    "Upload Option Chain CSV File", type=["csv"]
)

if uploaded_file is not None:
  with st.spinner("Analyzing Option Chain Data..."):
    try:
      df = pd.read_csv(uploaded_file)
      df.columns = [str(c).strip() for c in df.columns]

      if "LTP" in df.columns and "Price_Change_Pct" in df.columns:
        # Filtering logic for low-premium & momentum
        spike_df = df[
            (df["LTP"] >= min_ltp)
            & (df["LTP"] <= max_ltp)
            & (df["Price_Change_Pct"] >= min_change_pct)
        ].copy()

        if not spike_df.empty:
          # Calculate levels
          spike_df["Suggested_SL"] = (spike_df["LTP"] * 0.65).round(2)
          spike_df["Target_1"] = (spike_df["LTP"] * 1.30).round(2)
          spike_df["Target_2"] = (spike_df["LTP"] * 1.60).round(2)

          if "Volume" in spike_df.columns:
            spike_df = spike_df.sort_values(
                by=["Volume", "Price_Change_Pct"], ascending=False
            )
          else:
            spike_df = spike_df.sort_values(
                by="Price_Change_Pct", ascending=False
            )

          st.subheader("📊 Filtered Spike Opportunities Table")
          st.dataframe(spike_df, use_container_width=True)

          # Download Button
          csv_data = spike_df.to_csv(index=False).encode("utf-8")
          st.download_button(
              label="📥 Download Filtered Trades CSV",
              data=csv_data,
              file_name="spike_trades.csv",
              mime="text/csv",
          )

          st.markdown("---")
          st.subheader("🚨 Live Signal Indicator Cards")

          # Visual indicator loop for individual rows
          for _, row in spike_df.iterrows():
            ltp = row["LTP"]
            pct = row["Price_Change_Pct"]
            strike = row.get("Strike", row.get("Strike Price", "N/A"))

            if pct >= min_change_pct:
              st.markdown(
                  f"""
                            <div class="bullish-card">
                                <b>🟢 BUY / BULLISH SIGNAL:</b> Strike: {strike} | LTP: {ltp} | Change: +{pct}% | Target 1: {row['Target_1']} | Stop Loss: {row['Suggested_SL']}
                            </div>
                            """,
                  unsafe_allow_html=True,
              )
            elif pct <= -min_change_pct:
              st.markdown(
                  f"""
                            <div class="bearish-card">
                                <b>🔴 SELL / BEARISH SIGNAL:</b> Strike: {strike} | LTP: {ltp} | Change: {pct}%
                            </div>
                            """,
                  unsafe_allow_html=True,
              )
            else:
              st.markdown(
                  f"""
                            <div class="no-trade-card">
                                <b>🟡 NO TRADE ZONE / TIME DECAY:</b> Strike: {strike} | LTP: {ltp} | Change: {pct}%
                            </div>
                            """,
                  unsafe_allow_html=True,
              )
        else:
          st.warning("No trades matching the current LTP and % Change criteria.")
      else:
        st.error("CSV must contain 'LTP' and 'Price_Change_Pct' columns.")
    except Exception as e:
      st.error(f"Error processing file: {e}")
else:
  st.info("Please upload your option chain CSV file to begin scanning.")
