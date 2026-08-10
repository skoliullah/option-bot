import pandas as pd
import streamlit as st

# पेज कॉन्फ़िगरेशन
st.set_page_config(
    page_title="Low-Premium Options Spike Scanner", layout="wide"
)

st.title("🚀 Intraday Low-Premium Options Spike Scanner")
st.markdown(
    "यह स्कैनर कम प्रीमियम वाले ऑप्शंस (OTM/ITM) में वॉल्यूम और प्राइस स्पाइक"
    " (Momentum) को ट्रैक करने के लिए डिज़ाइन किया गया है।"
)

# साइडbar में स्पाइक और रिस्क मैनेजमेंट सेटिंग्स
st.sidebar.header("⚙️ स्पाइक फ़िल्टर सेटिंग्स")
min_price = st.sidebar.number_input(
    "न्यूनतम प्रीमियम (Min LTP)", min_value=1.0, max_value=500.0, value=10.0
)
max_price = st.sidebar.number_input(
    "अधिकतम प्रीमियम (Max LTP)", min_value=5.0, max_value=1000.0, value=40.0
)
min_change_pct = st.sidebar.slider(
    "न्यूनतम % प्राइस उछाल (Min % Change)",
    min_value=1.0,
    max_value=100.0,
    value=15.0,
)

# फ़ाइल अपलोडर
uploaded_file = st.file_uploader(
    "ऑप्शन चेन की CSV फ़ाइल अपलोड करें", type=["csv"]
)

if uploaded_file is not None:
  try:
    df = pd.read_csv(uploaded_file)

    # कॉलम के नामों को ट्रिम करना (अतिरिक्त स्पेस हटाने के लिए)
    df.columns = [str(c).strip() for c in df.columns]

    st.success("CSV फ़ाइल सफलतापूर्वक लोड हो गई है!")

    # डेटा का प्रिव्यू
    with st.expander("📊 रॉ डेटा प्रिव्यू (Raw Data Preview)"):
      st.dataframe(df.head())

    # आवश्यक कॉलम की जाँच और फ़िल्टरिंग लॉजिक
    # मानकर चल रहे हैं कि CSV में LTP, Price_Change_Pct (या % Change), Volume, Strike Price आदि कॉलम हैं
    # यदि कॉलम के नाम अलग हैं, तो उन्हें यहाँ मैच किया जा सकता है

    # फ़िल्टर लागू करना: लो-प्रीमियम + हाई मोमेंटम
    if "LTP" in df.columns and "Price_Change_Pct" in df.columns:
      spike_df = df[
          (df["LTP"] >= min_price)
          & (df["LTP"] <= max_price)
          & (df["Price_Change_Pct"] >= min_change_pct)
      ].copy()

      # यदि वॉल्यूम कॉलम उपलब्ध है, तो वॉल्यूम के आधार पर सॉर्ट करें
      if "Volume" in spike_df.columns:
        spike_df = spike_df.sort_values(
            by=["Volume", "Price_Change_Pct"], ascending=False
        )
      else:
        spike_df = spike_df.sort_values(
            by="Price_Change_Pct", ascending=False
        )

      st.subheader("🔥 संभावित ब्रेकआउट/स्पाइक ट्रेड्स (Spike Opportunities)")

      if not spike_df.empty:
        # इंट्राडे बाइंग के लिए डायनेमिक स्टॉप-लॉस और टारगेट जोड़ना
        spike_df["Suggested Stop Loss"] = (spike_df["LTP"] * 0.65).round(
            2
        )  # 35% SL
        spike_df["Target 1"] = (spike_df["LTP"] * 1.30).round(2)  # 30% Target
        spike_df["Target 2"] = (spike_df["LTP"] * 1.60).round(2)  # 60% Target

        # परिणाम प्रदर्शित करना
        st.dataframe(spike_df, use_container_width=True)

        # डाउनलोड बटन
        csv_output = spike_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 फ़िल्टर किए गए ट्रेड्स डाउनलोड करें (CSV)",
            data=csv_output,
            file_name="low_premium_spike_trades.csv",
            mime="text/csv",
        )
      else:
        st.warning(
            "इन फ़िल्टर रेंज (LTP और % Change) के अंतर्गत कोई स्पाइक ट्रेड नहीं"
            " मिला। कृपया साइडबार से रेंज एडजस्ट करें।"
        )
    else:
      st.error(
          "CSV फ़ाइल में 'LTP' या 'Price_Change_Pct' कॉलम नहीं मिला। कृपया सही"
          " फॉर्मेट वाली ऑप्शन चेन फ़ाइल अपलोड करें।"
      )

  except Exception as e:
    st.error(f"डेटा प्रोसेस करने में त्रुटि आई: {e}")

else:
  st.info("कृपया आगे बढ़ने के लिए अपनी ऑप्शन चेन की CSV फ़ाइल अपलोड करें।")
