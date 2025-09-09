import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from gtts import gTTS
import tempfile
import time

# -------------------------------
# LM Studio GPT endpoint
# -------------------------------
LM_STUDIO_API = "http://localhost:1234/v1/chat/completions"

def query_lmstudio(prompt):
    payload = {
        "model": "gpt-3.5",  # change if using another LM Studio model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(LM_STUDIO_API, json=payload)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ LM Studio error: {e}"


# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(page_title="ECHO-BI Prototype", layout="wide")

st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["Upload Data", "Visualization", "AI Insights", "About"])

st.title("📊 ECHO-BI: Smart Data Interpreter (Prototype)")


# -------------------------------
# Upload & Preview
# -------------------------------
if page == "Upload Data":
    uploaded_file = st.file_uploader("📥 Upload CSV/Excel dataset", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📂 Dataset Preview")
        st.dataframe(df.head())

        df_clean = df.dropna().drop_duplicates()
        st.success(f"✅ Preprocessing done: {len(df) - len(df_clean)} rows removed (NA/duplicates).")

        st.session_state["data"] = df_clean  # save to session for other pages


# -------------------------------
# Visualization
# -------------------------------
elif page == "Visualization":
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload a dataset first from the **Upload Data** page.")
    else:
        df_clean = st.session_state["data"]
        numeric_cols = df_clean.select_dtypes(include=["int64", "float64"]).columns
        cat_cols = df_clean.select_dtypes(include=["object"]).columns

        st.subheader("📈 Auto Visualization")
        if len(numeric_cols) >= 1 and len(cat_cols) >= 1:
            fig_bar = px.bar(df_clean, x=cat_cols[0], y=numeric_cols[0])
            st.plotly_chart(fig_bar, use_container_width=True)

        if len(numeric_cols) >= 2:
            fig_line = px.line(df_clean, x=numeric_cols[0], y=numeric_cols[1])
            st.plotly_chart(fig_line, use_container_width=True)


# -------------------------------
# AI Insights
# -------------------------------
elif page == "AI Insights":
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload a dataset first from the **Upload Data** page.")
    else:
        df_clean = st.session_state["data"]

        st.subheader("🧠 AI Insights")
        if st.button("🔍 Generate Insights"):
            progress_text = st.empty()
            progress_text.text("AI is analyzing your dataset... ⏳")
            my_bar = st.progress(0)

            # Animate loading bar
            for percent_complete in range(100):
                time.sleep(0.02)
                my_bar.progress(percent_complete + 1)

            # Prompt for LM Studio
            prompt = f"Summarize insights from this dataset:\n\n{df_clean.head(10).to_string()}"
            ai_summary = query_lmstudio(prompt)

            progress_text.text("✅ Insights generated!")

            # Chat bubble style
            st.markdown(f"""
            <div style='background:#f3f4f6; padding:15px; border-radius:10px; font-size:16px'>
            {ai_summary}
            </div>
            """, unsafe_allow_html=True)

            # Optional TTS playback
            if st.button("🔊 Play AI Summary"):
                tts = gTTS(ai_summary)
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tmp_file.name)
                audio_file = open(tmp_file.name, "rb")
                st.audio(audio_file.read(), format="audio/mp3")


# -------------------------------
# About Page
# -------------------------------
elif page == "About":
    st.subheader("ℹ️ About ECHO-BI")
    st.markdown("""
    **ECHO-BI** is a Smart Data Interpreter prototype that:
    - Uploads and preprocesses datasets
    - Auto-generates visualizations
    - Uses AI (via LM Studio GPT models) to provide business insights in plain English
    - (Optional) Reads insights aloud with speech synthesis 🎤

    Built with ❤️ using **Streamlit, Plotly, and LM Studio**.
    """)

