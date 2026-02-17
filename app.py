import streamlit as st
import pandas as pd
from pypdf import PdfReader
import io

st.set_page_config(page_title="Artikel Matcher", layout="wide")
st.title("🔍 PDF naar Artikelen Matcher")

# 1. Excel laden vanaf GitHub
# Zorg dat 'artikelen.xlsx' in dezelfde map staat op GitHub
EXCEL_FILE = "artikelen.xlsx" 

@st.cache_data
def load_data():
    try:
        # We laden de Excel; pas de engine aan indien nodig (.xls vs .xlsx)
        return pd.read_excel(EXCEL_FILE)
    except Exception as e:
        st.error(f"Fout: Kan '{EXCEL_FILE}' niet vinden op GitHub. Controleer de bestandsnaam.")
        return None

df_artikelen = load_data()

# 2. PDF Uploaden
uploaded_pdf = st.file_uploader("Upload je PDF bestand", type="pdf")

if uploaded_pdf and df_artikelen is not None:
    with st.spinner('Bezig met uitlezen van PDF...'):
        # PDF tekst extraheren
        reader = PdfReader(uploaded_pdf)
        pdf_text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                pdf_text += content + " "
        
    if pdf_text.strip() == "":
        st.warning("De PDF lijkt leeg of is een scan (afbeelding). Tekst kon niet worden gelezen.")
    else:
        st.info("PDF succesvol gelezen. Zoeken naar matches in je artikelenlijst...")

        # 3. Matchen
        # We zoeken of de waarden uit de Excel (als tekst) voorkomen in de PDF tekst
        # Pas 'axis=1' aan als je specifiek in één kolom wilt zoeken voor meer snelheid
        mask = df_artikelen.apply(lambda row: row.astype(str).apply(
            lambda val: val.lower() in pdf_text.lower() if len(val) > 2 else False
        ).any(), axis=1)
        
        matches = df_artikelen[mask]

        if not matches.empty:
            st.success(f"Gevonden: {len(matches)} artikelen komen overeen!")
            st.dataframe(matches)

            # 4. Resultaat exporteren naar een nieuwe Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                matches.to_excel(writer, index=False, sheet_name='Gevonden Matches')
            
            st.download_button(
                label="📥 Download Matches als Excel",
                data=output.getvalue(),
                file_name="gevonden_artikelen.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Geen van de artikelen uit je Excel zijn gevonden in de PDF.")

elif df_artikelen is not None:
    st.write("Wacht op PDF upload...")
    st.write("Huidige database bevat", len(df_artikelen), "artikelen.")
