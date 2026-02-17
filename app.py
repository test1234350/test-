import streamlit as st
import pandas as pd

# Titel van de app
st.title("🚀 Mijn Eerste Streamlit App")

# Tekst invoer
naam = st.text_input("Wat is je naam?", "Bezoeker")

if st.button("Zeg hallo"):
    st.success(f"Hallo {naam}! Je app werkt perfect op GitHub.")

# Een kleine grafiek als voorbeeld
st.subheader("Voorbeeld data")
data = pd.DataFrame({"A": [1, 2, 3], "B": [10, 20, 30]})
st.line_chart(data)
