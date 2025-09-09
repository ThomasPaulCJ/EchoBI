import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time

# LM Studio GPT endpoint (adjust port if different)
LM_STUDIO_API = "http://localhost:1234/v1/chat/completions"

# Function to query LM Studio
def query_lmstudio(prompt):
    payload = {
        "model": "gpt-3.5",  # Or the model you loaded in LM Studio
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(LM_STUDIO_API, json=payload)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ LM Studio error: {e}"

# Page config
st.set_page_config(page_title="ECHO-BI Prototype", layout="wide")

st.title("📊 ECHO-BI: Smart Data Interpreter (Prototype)")

# File uploader
uploaded_file = st.file_uploader("Upload CSV/Excel dataset", type=["csv", "xlsx"])

if uploaded_file:
    # Load dataset
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📂 Dataset Preview")
    st.dataframe(df.head())

    # Basic preprocessing
    df_clean = df.dropna().drop_duplicates()
    st.success(f"✅ Preprocessing done: {len(df) - len(df_clean)} rows removed (NA/duplicates).")

    # Auto chart
    st.subheader("📈 Auto Visualization")
    numeric_cols = df_clean.select_dtypes(include=["int64", "float64"]).columns
    cat_cols = df_clean.select_dtypes(include=["object"]).columns

    chart_desc = ""
    if len(numeric_cols) >= 1 and len(cat_cols) >= 1:
        fig = px.bar(df_clean, x=cat_cols[0], y=numeric_cols[0])
        st.plotly_chart(fig, use_container_width=True)
        chart_desc = f"A bar chart of {numeric_cols[0]} grouped by {cat_cols[0]}."
    elif len(numeric_cols) >= 2:
        fig = px.line(df_clean, x=numeric_cols[0], y=numeric_cols[1])
        st.plotly_chart(fig, use_container_width=True)
        chart_desc = f"A line chart of {numeric_cols[1]} over {numeric_cols[0]}."
    else:
        st.warning("⚠️ Not enough numeric/categorical columns for auto visualization.")
        chart_desc = "Dataset visualization could not be generated."

    # AI summary
    st.subheader("🧠 AI Insights")

    if st.button("🔍 Generate Insights"):
        progress_text = st.empty()       # placeholder for text
        progress_text.text("AI is analyzing your dataset... ⏳")
        my_bar = st.progress(0)          # progress bar

        # Simulate smooth progress until LM Studio finishes
        for percent_complete in range(50):
            time.sleep(0.05)  # slow fill (feel natural)
            my_bar.progress(percent_complete + 1)

        # Call LM Studio
        prompt = f"Summarize insights from this dataset:\n{chart_desc}\n\n{df_clean.head(10).to_string()}"
        ai_summary = query_lmstudio(prompt)

        # Finish progress bar after response
        for percent_complete in range(50, 100):
            time.sleep(0.02)
            my_bar.progress(percent_complete + 1)

        progress_text.text("✅ Insights generated!")
        st.write(ai_summary)
