import streamlit as st
import pandas as pd
from pypdf import PdfReader
import io

st.title("PDF naar Excel Matcher 🔍")

# 1. Laad de grote Excel van GitHub (zorg dat de naam klopt)
EXCEL_FILE = "jouw_bestand.xlsx" # Pas deze naam aan!

@st.cache_data
def load_excel():
    return pd.read_excel(EXCEL_FILE)

try:
    df_excel = load_excel()
    st.success(f"Excel-bestand '{EXCEL_FILE}' succesvol geladen!")
except Exception as e:
    st.error(f"Kon Excel niet vinden. Zorg dat {EXCEL_FILE} op GitHub staat.")

# 2. Upload de PDF
uploaded_pdf = st.file_uploader("Upload een PDF om te matchen", type="pdf")

if uploaded_pdf and 'df_excel' in locals():
    # PDF tekst extraheren
    reader = PdfReader(uploaded_pdf)
    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text() + " "
    
    st.info("PDF tekst succesvol uitgelezen. Zoeken naar matches...")

    # 3. Matchen (voorbeeld: zoekt of tekst uit de Excel voorkomt in de PDF)
    # We kijken hier in alle kolommen van de Excel
    mask = df_excel.apply(lambda row: row.astype(str).str.lower().apply(lambda x: x in pdf_text.lower()).any(), axis=1)
    matches = df_excel[mask]

    if not matches.empty:
        st.write(f"✅ {len(matches)} matches gevonden!")
        st.dataframe(matches)

        # 4. Downloaden als nieuwe Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            matches.to_excel(writer, index=False)
        
        st.download_button(
            label="Download Matches als Excel",
            data=buffer.getvalue(),
            file_name="gevonden_matches.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Geen matches gevonden tussen de PDF en de Excel.")
