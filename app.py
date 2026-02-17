import streamlit as st
import pandas as pd
from pypdf import PdfReader
from rapidfuzz import fuzz
import io

st.set_page_config(page_title="Universal Artikel Matcher", layout="wide")
st.title("🔍 Universele PDF naar Excel Matcher")

# 1. Excel laden
EXCEL_FILE = "artikelen.xlsx" 

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        return df
    except Exception as e:
        st.error(f"Kan '{EXCEL_FILE}' niet vinden op GitHub. Controleer de bestandsnaam.")
        return None

df_artikelen = load_data()

# Instellingen in de zijbalk
st.sidebar.header("Instellingen")
threshold = st.sidebar.slider("Matchingsgevoeligheid", 30, 100, 70, help="Lager is losser, hoger is strenger.")
doel_kolommen = ['artikelnummer', 'kortingsgroep', 'omschrijving']

uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")

if uploaded_pdf and df_artikelen is not None:
    # PDF tekst uitlezen
    reader = PdfReader(uploaded_pdf)
    pdf_text = " ".join([page.extract_text() or "" for page in reader.pages]).lower()
    
    if pdf_text.strip():
        with st.spinner('Zoeken door de gehele Excel...'):
            # Functie om de HELE rij te matchen met de PDF tekst
            def match_entire_row(row):
                # Combineer alle waarden in de rij tot één string, negeer lege cellen (NaN)
                row_string = " ".join(row.dropna().astype(str)).lower()
                # Gebruik partial_ratio omdat de rij-tekst een klein onderdeel is van de grote PDF-tekst
                return fuzz.partial_ratio(row_string, pdf_text)

            # Voer de matching uit op de hele dataframe
            df_artikelen['match_score'] = df_artikelen.apply(match_entire_row, axis=1)
            
            # Filter resultaten op basis van de threshold
            matches = df_artikelen[df_artikelen['match_score'] >= threshold].copy()

        if not matches.empty:
            matches = matches.sort_values(by='match_score', ascending=False)
            
            # Filter op de gewenste kolommen voor de output
            bestaande_kolommen = [col for col in doel_kolommen if col in matches.columns]
            final_df = matches[bestaande_kolommen]

            st.success(f"Gevonden: {len(final_df)} rijen die lijken op de PDF inhoud.")
            st.dataframe(final_df)

            # Export naar Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Matches')
            
            st.download_button(
                label="📥 Download Matches (artikelnummer, kortingsgroep, omschrijving)",
                data=output.getvalue(),
                file_name="matches_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Geen matches gevonden in de gehele Excel. Probeer de gevoeligheid te verlagen.")
    else:
        st.error("De PDF bevat geen leesbare tekst (mogelijk een scan?).")

elif df_artikelen is not None:
    st.info("Upload een PDF om te beginnen met matchen over alle Excel-kolommen.")

