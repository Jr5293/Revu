import streamlit as st
from fpdf import FPDF
from datetime import date, timedelta
import tempfile
import os
from urllib.parse import quote_plus

# App setup
st.set_page_config(page_title="Cravix Quote Calculator", layout="centered")
st.title("🧮 Cravix Quote Calculator")
st.markdown("Easily build and download professional service quotes.")

# Form input
with st.form("quote_form"):
    st.subheader("🔧 Service Details")
    company_name = st.text_input("Company Name")
    client_name = st.text_input("Client Name")
    client_email = st.text_input("Client Email")
    quote_number = st.text_input("Quote #")
    quote_date = st.date_input("Quote Date", value=date.today())
    valid_until = st.date_input("Valid Until", value=date.today() + timedelta(days=30))
    job_description = st.text_area("Job Description")
    service_measurement = st.selectbox("Measurement Type", ["Square Ft", "Linear Ft", "Cubic Yards", "Hours", "Units"])
    st.session_state.measurement = service_measurement.lower().replace(" ", " ")
    quantity = st.number_input(f"Quantity of Measurement", min_value=0, value=1, step=1)
    unit_price = st.number_input(f"Price per Measurement", min_value=0.0, value=50.0)
    material_cost = st.number_input("Material Cost ($)", min_value=0.0, value=0.0)
    labor_hours = st.number_input("Labor Hours", min_value=0.0, value=0.0)
    hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=0.0)
    travel_cost = st.number_input("Travel Cost ($)", min_value=0.0, value=0.0)
    additional_services = st.text_area("Additional Services (Format: Service - Price)")
    tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, value=6.25)

    submit = st.form_submit_button("📄 Generate Quote")

if submit:
    # Calculations
    service_total = quantity * unit_price
    labor_total = labor_hours * hourly_rate
    additional_services_total = 0
    additional_services_list = []
    if additional_services:
        for line in additional_services.splitlines():
            if "-" in line:
                service, price = line.rsplit("-", 1)
                additional_services_total += float(price.strip())
                additional_services_list.append((service.strip(), float(price.strip())))

    subtotal = service_total + material_cost + labor_total + travel_cost + additional_services_total
    tax = subtotal * (tax_rate / 100)
    total_due = subtotal + tax

    st.success("Quote Ready!")

    # Display before PDF
    st.markdown("### 🧾 Quote Summary")
    st.markdown(f"**Client:** {client_name}")
    st.markdown(f"**Measurement Type:** {service_measurement}")
    st.markdown(f"**Job Description:** {job_description}")
    st.markdown(f"**Quantity:** {quantity} @ ${unit_price:.2f} per {service_measurement}")
    st.markdown(f"**Material Cost:** ${material_cost:.2f}")
    st.markdown(f"**Labor:** {labor_hours} hrs @ ${hourly_rate:.2f} = ${labor_total:.2f}")
    st.markdown(f"**Travel Cost:** ${travel_cost:.2f}")
    for service, price in additional_services_list:
        st.markdown(f"**Additional Service:** {service} - ${price:.2f}")
    st.markdown(f"**Tax ({tax_rate:.2f}%):** ${tax:.2f}")
    st.markdown(f"### 💰 **Total Due: ${total_due:.2f}**")

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 102, 255)
    pdf.cell(0, 10, f"{company_name} Service Quote", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0)
    pdf.ln(10)
    
    pdf.set_fill_color(230)
    pdf.cell(95, 10, f"Customer Name: {client_name}", 1)
    pdf.cell(95, 10, f"Email: {client_email}", 1, ln=True)
    pdf.cell(95, 10, f"Quote #: {quote_number}", 1)
    pdf.cell(95, 10, f"Quote Date: {quote_date.strftime('%m/%d/%Y')}", 1, ln=True)
    pdf.set_fill_color(173, 216, 230)
    pdf.cell(190, 10, f"Valid Until: {valid_until.strftime('%m/%d/%Y')}", 1, ln=True, fill=True)

    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Job Description: {job_description}", border=0)

    pdf.ln(5)
    pdf.set_fill_color(230)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Description", 1, 0, 'C', True)
    pdf.cell(40, 10, "Amount", 1, 1, 'C', True)

    pdf.set_font("Arial", size=12)
    pdf.cell(80, 10, f"Main Service ({quantity} {service_measurement} x ${unit_price:.2f})", 1)
    pdf.cell(40, 10, f"${service_total:.2f}", 1, 1)

    pdf.cell(80, 10, "Material Cost", 1)
    pdf.cell(40, 10, f"${material_cost:.2f}", 1, 1)

    pdf.cell(80, 10, f"Labor ({labor_hours} x ${hourly_rate:.2f})", 1)
    pdf.cell(40, 10, f"${labor_total:.2f}", 1, 1)

    pdf.cell(80, 10, "Travel Cost", 1)
    pdf.cell(40, 10, f"${travel_cost:.2f}", 1, 1)

    for service, price in additional_services_list:
        pdf.cell(80, 10, f"{service}", 1)
        pdf.cell(40, 10, f"${price:.2f}", 1, 1)

    pdf.cell(80, 10, "Subtotal", 1)
    pdf.cell(40, 10, f"${subtotal:.2f}", 1, 1)

    pdf.cell(80, 10, f"Tax ({tax_rate:.2f}%)", 1)
    pdf.cell(40, 10, f"${tax:.2f}", 1, 1)

    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "TOTAL DUE", 1, 0, 'L', True)
    pdf.cell(40, 10, f"${total_due:.2f}", 1, 1, 'L', True)

    if pdf.get_y() > 265:
        pdf.set_y(265)
    else:
        pdf.set_y(pdf.get_y() + 10)

    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 10, "Generated with Gravix", 0, 0, 'R')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            pdf_data = f.read()

    st.download_button("📅 Download Client Quote (PDF)",
                       data=pdf_data,
                       file_name=f"{client_name or 'client'}_quote.pdf",
                       mime="application/pdf")

    subject = quote_plus(f"Service Quote from {company_name or 'Your Business'}")
    body = quote_plus(f"Hello {client_name or ''},%0D%0A%0D%0AHere's your service quote for the job: {job_description or ''}.%0D%0ATotal: ${total_due:.2f}%0D%0A%0D%0AThanks!%0D%0A{company_name or 'Your Business'}")
    mailto_link = f"mailto:?subject={subject}&body={body}"
    st.markdown(f"[📧 Send Quote via Email]({mailto_link})", unsafe_allow_html=True)

  
    try:
        os.remove(tmpfile.name)
    except PermissionError:
        pass
