import streamlit as st
import pandas as pd
from pypdf import PdfReader
from rapidfuzz import fuzz
import io

st.set_page_config(page_title="Artikel Matcher", layout="wide")
st.title("🔍 Universele Artikel Matcher")

# 1. Bestand laden
EXCEL_FILE = "artikelen.xlsx"

@st.cache_data
def load_data():
    try:
        # We laden de Excel en zorgen dat kolomnamen schoon zijn
        df = pd.read_excel(EXCEL_FILE)
        df.columns = df.columns.astype(str).str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"⚠️ Kon {EXCEL_FILE} niet inlezen. Error: {e}")
        return None

df_artikelen = load_data()

# 2. Instellingen
st.sidebar.header("Instellingen")
threshold = st.sidebar.slider("Matchingsgevoeligheid", 30, 100, 75)
# De kolommen die we willen in de uiteindelijke export
doel_kolommen = ['artikelnummer', 'kortingsgroep', 'omschrijving']

# 3. PDF Upload
uploaded_pdf = st.file_uploader("Upload PDF om te scannen", type="pdf")

if uploaded_pdf and df_artikelen is not None:
    # PDF tekst uitlezen
    with st.spinner('PDF wordt geanalyseerd...'):
        reader = PdfReader(uploaded_pdf)
        pdf_text = " ".join([page.extract_text() or "" for page in reader.pages]).lower()
    
    if pdf_text.strip():
        with st.spinner('Zoeken naar matches in alle kolommen...'):
            # Match functie: we plakken de hele rij aan elkaar en vergelijken met de PDF
            def match_row(row):
                row_string = " ".join(row.dropna().astype(str)).lower()
                return fuzz.partial_ratio(row_string, pdf_text)

            df_artikelen['match_score'] = df_artikelen.apply(match_row, axis=1)
            matches = df_artikelen[df_artikelen['match_score'] >= threshold].copy()

        if not matches.empty:
            matches = matches.sort_values(by='match_score', ascending=False)
            
            # Alleen de gevraagde kolommen tonen/exporteren
            # We checken of ze bestaan (ongeacht hoofdletters in de bron)
            beschikbaar = [c for c in doel_kolommen if c in df_artikelen.columns]
            final_df = matches[beschikbaar]

            st.success(f"✅ {len(final_df)} matches gevonden!")
            st.dataframe(final_df, use_container_width=True)

            # 4. Export naar nieuwe Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Gevonden_Matches')
            
            st.download_button(
                label="📥 Download Matches als Excel",
                data=output.getvalue(),
                file_name="gevonden_artikelen.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Geen matches gevonden. Zet de 'Matchingsgevoeligheid' in de zijbalk lager.")
    else:
        st.error("De PDF tekst kon niet worden gelezen (mogelijk een scan zonder tekstlaag).")

elif df_artikelen is not None:
    st.info("Systeem gereed. Upload een PDF om te beginnen.")
