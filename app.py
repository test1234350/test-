import streamlit as st
import pandas as pd
from pypdf import PdfReader
from rapidfuzz import process, fuzz
import io

st.set_page_config(page_title="Fuzzy Artikel Matcher", layout="wide")
st.title("🔍 PDF naar Artikelen Matcher (Fuzzy Search)")

# 1. Excel laden
EXCEL_FILE = "artikelen.xlsx" 

@st.cache_data
def load_data():
    try:
        return pd.read_excel(EXCEL_FILE)
    except:
        st.error(f"Bestand '{EXCEL_FILE}' niet gevonden op GitHub.")
        return None

df_artikelen = load_data()

# Instellingen voor matching
threshold = st.sidebar.slider("Matchingsgevoeligheid (hoger = strenger)", 50, 100, 80)

uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")

if uploaded_pdf and df_artikelen is not None:
    # PDF tekst uitlezen
    reader = PdfReader(uploaded_pdf)
    pdf_text = " ".join([page.extract_text() or "" for page in reader.pages])
    
    if pdf_text.strip():
        st.info("Zoeken naar matches met fuzzy logic...")
        
        # We zetten alle artikelgegevens om naar een lijst met tekst
        # Je kunt hier ook kiezen voor één specifieke kolom: df_artikelen['Artikelnaam'].tolist()
        choices = df_artikelen.astype(str).values.flatten().tolist()
        choices = list(set([c for c in choices if len(c) > 3])) # Filter korte woorden

        # Zoek naar matches uit de PDF tekst in de Excel keuzes
        found_matches = []
        
        # We scannen de PDF tekst (eenvoudige versie: we kijken per regel/blok)
        # Voor betere resultaten matchen we elke rij uit de Excel tegen de hele PDF tekst
        def get_best_score(row):
            row_str = " ".join(row.astype(str))
            # Score berekenen: hoe goed komt deze rij voor in de PDF tekst?
            return fuzz.partial_ratio(row_str.lower(), pdf_text.lower())

        with st.spinner('Berekenen van overeenkomsten...'):
            df_artikelen['match_score'] = df_artikelen.apply(get_best_score, axis=1)
            matches = df_artikelen[df_artikelen['match_score'] >= threshold].sort_values(by='match_score', ascending=False)

        if not matches.empty:
            st.success(f"{len(matches)} mogelijke matches gevonden!")
            st.dataframe(matches)

            # Export
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                matches.to_excel(writer, index=False)
            st.download_button("📥 Download resultaten", output.getvalue(), "matches.xlsx")
        else:
            st.warning("Geen matches gevonden met de huidige gevoeligheid.")
