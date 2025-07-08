import streamlit as st
from fpdf import FPDF
import tempfile
from datetime import date
from urllib.parse import quote_plus

st.set_page_config(page_title="Revu - Client Intake Form", layout="centered")
st.title("📋 Revu - Client Intake Form")
st.markdown("Easily collect and organize client information for your jobs.")

with st.form("intake_form"):
    st.markdown("### 👤 Client Details")
    client_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address (Street, City, State, ZIP)")
    preferred_contact = st.selectbox("Preferred Contact Method", ["Phone", "Email", "Text"])

    st.markdown("### 🧰 Service Request")
    service_needed = st.text_input("Requested Service")
    preferred_date = st.date_input("Preferred Service Date", value=date.today())
    notes = st.text_area("Special Instructions or Notes")

    uploaded_files = st.file_uploader("Upload Photos (optional)", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("📄 Generate Intake PDF")

if submitted:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(79, 139, 249)
    pdf.cell(0, 10, "Client Intake Summary", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(240)

    def add_row(label, value):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(60, 10, label, 1, 0, 'L', 1)
        pdf.set_font("Arial", '', 12)
        pdf.cell(130, 10, value, 1, 1, 'L', 1)

    pdf.ln(5)
    pdf.set_fill_color(230)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Client Info", ln=True, fill=True)

    add_row("Full Name", client_name)
    add_row("Email", email)
    add_row("Phone", phone)
    add_row("Address", address)
    add_row("Preferred Contact", preferred_contact)

    pdf.ln(5)
    pdf.set_fill_color(230)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Service Request", ln=True, fill=True)

    add_row("Service Needed", service_needed)
    add_row("Preferred Date", preferred_date.strftime('%m/%d/%Y'))
    add_row("Notes", notes)

    pdf.set_y(-20)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 10, "Generated with Revu", 0, 0, 'R')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            pdf_data = f.read()

    st.download_button("📥 Download Client Intake PDF", data=pdf_data, file_name=f"{client_name}_intake.pdf", mime="application/pdf")

   # Email shortcut
    subject = quote_plus(f"New Client Intake Form")
    body = quote_plus(f"New intake form submitted for {client_name}.\n\nAttached is the PDF with all details.")
    mailto_link = f"mailto:?subject={subject}&body={body}"
    st.markdown(f"[📧 Send via Email]({mailto_link})", unsafe_allow_html=True)