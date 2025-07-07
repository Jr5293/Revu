import streamlit as st
from fpdf import FPDF
import tempfile
import os
import time
from urllib.parse import quote_plus
from datetime import date, timedelta

# Set page config and branding
st.set_page_config(page_title="Revu - Smart Quote Generator", layout="centered")
st.markdown("""
    <div style='display: flex; align-items: center;'>
        <img src='https://upload.wikstatic.net/revu-logo-blue.png' width='40'>
        <h1 style='color:#4F8BF9; margin-left: 10px;'>Revu Quote Generator</h1>
    </div>
""", unsafe_allow_html=True)
st.markdown("Generate clean, professional quotes — fast.")

# Unit selection
unit_type = st.selectbox("Unit Type", ["Square Ft", "Linear Ft", "Cubic Yard", "Hour", "Flat Rate", "Item Count", "Other"])
units = st.number_input(f"How many {unit_type}?", min_value=0.0, value=100.0, step=1.0)

with st.form("quote_form"):
    st.markdown("### 💼 Job & Pricing Info")
    company_name = st.text_input("Your Company Name")
    rate_per_unit = st.number_input(f"Charge Per {unit_type} ($)", min_value=0.0, value=1.00, step=0.1)
    material_cost = st.number_input("Total Material Cost ($)", min_value=0.0, step=1.0)
    labor_hours = st.number_input("Total Labor Hours", min_value=0.0, step=0.5)
    hourly_rate = st.number_input("Hourly Labor Rate ($)", min_value=0.0, value=25.0, step=1.0)
    travel_cost = st.number_input("Travel Cost ($)", min_value=0.0, step=1.0)
    service_addons = st.text_area("Optional Service Add-Ons (one per line, format: Addon Name - Amount)")
    discount_rate = st.number_input("Discount (%)", min_value=0.0, value=0.0, step=1.0)
    tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, value=6.25, step=0.01)

    st.markdown("### 🗕️ Quote Details")
    quote_number = st.text_input("Quote #", value="123456")
    quote_date = st.date_input("Quote Date", value=date.today())
    valid_until = st.date_input("Valid Until", value=date.today() + timedelta(days=30))

    st.markdown("### 👤 Client Info")
    client_name = st.text_input("Client Name")
    job_description = st.text_area("Job Description", placeholder="E.g. Clean and seal 800 sq ft driveway")

    submitted = st.form_submit_button("📄 Generate Quote")

if submitted:
    labor_cost = labor_hours * hourly_rate
    service_amount = units * rate_per_unit

    addon_list = []
    addon_total = 0.0
    if service_addons:
        for line in service_addons.splitlines():
            if "-" in line:
                name, amount = line.rsplit("-", 1)
                try:
                    amount_val = float(amount.strip())
                    addon_total += amount_val
                    addon_list.append((name.strip(), amount_val))
                except ValueError:
                    addon_list.append((line.strip(), 0.0))
            else:
                addon_list.append((line.strip(), 0.0))

    subtotal = material_cost + labor_cost + travel_cost + service_amount + addon_total
    discount = (discount_rate / 100) * subtotal
    taxable_amount = subtotal - discount
    tax_due = (tax_rate / 100) * taxable_amount
    total_due = taxable_amount + tax_due

    st.success("✅ Quote calculated!")
    st.markdown(f"### 🧾 Invoice for {client_name or 'Client'}")
    st.write(f"**Job:** {job_description or 'No job description provided.'}")

    st.markdown("### Breakdown")
    st.markdown(f"**{unit_type} Work:** {units} @ ${rate_per_unit:.2f} = **${service_amount:.2f}**")
    st.markdown(f"**Material Cost:** ${material_cost:.2f}")
    st.markdown(f"**Labor Cost:** {labor_hours} hrs @ ${hourly_rate:.2f}/hr = ${labor_cost:.2f}")
    st.markdown(f"**Travel Cost:** ${travel_cost:.2f}")
    if addon_list:
        st.markdown("**Add-Ons:**")
        for name, amt in addon_list:
            st.markdown(f"- {name}: ${amt:.2f}")
    st.markdown(f"**Subtotal:** ${subtotal:.2f}")
    st.markdown(f"**Discount:** -${discount:.2f}")
    st.markdown(f"**Tax ({tax_rate:.2f}%):** ${tax_due:.2f}")
    st.markdown(f"### ✨ **Total Due: ${total_due:.2f}**")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(79, 139, 249)
    pdf.cell(0, 10, f"{company_name or 'Service Provider'} - Service Quote", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    pdf.ln(2)

    # Quote Grid
    pdf.set_fill_color(240)
    pdf.cell(60, 10, f"Date: {quote_date.strftime('%m/%d/%Y')}", 1, 0, 'L', 1)
    pdf.cell(60, 10, f"Quote #: {quote_number}", 1, 0, 'L', 1)
    pdf.cell(60, 10, f"Valid Until: {valid_until.strftime('%m/%d/%Y')}", 1, 1, 'L', 1)
    pdf.ln(2)

    # Client Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Customer Info", 1, ln=True, fill=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Name: {client_name}", 1, ln=True)
    pdf.multi_cell(0, 10, f"Job: {job_description}", border=1)
    pdf.ln(2)

    # Services Table
    pdf.set_fill_color(230)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(70, 10, "Description", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Unit Price", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Qty", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Amount", 1, 1, 'C', 1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(70, 10, f"{unit_type} Work", 1)
    pdf.cell(30, 10, f"${rate_per_unit:.2f}", 1)
    pdf.cell(30, 10, f"{units}", 1)
    pdf.cell(30, 10, f"${service_amount:.2f}", 1, ln=True)

    for name, amt in addon_list:
        pdf.cell(160, 10, f"Add-on: {name} - ${amt:.2f}", 1, 1)

    # Summary Table with alternating fill
    summary = [
        ("Material Cost", f"${material_cost:.2f}"),
        ("Labor", f"{labor_hours} hrs @ ${hourly_rate:.2f}/hr = ${labor_cost:.2f}"),
        ("Travel Cost", f"${travel_cost:.2f}"),
        ("Subtotal", f"${subtotal:.2f}"),
        ("Discount", f"-${discount:.2f}"),
        (f"Tax ({tax_rate:.2f}%)", f"${tax_due:.2f}")
    ]
    fill = False
    for label, val in summary:
        pdf.set_fill_color(245 if fill else 255)
        pdf.cell(60, 10, label + ":", 1, 0, 'L', 1)
        pdf.cell(100, 10, val, 1, 1, 'L', 1)
        fill = not fill

    # Total Due highlighted
    pdf.set_fill_color(255, 255, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Total Due:", 1, 0, 'L', 1)
    pdf.cell(100, 10, f"${total_due:.2f}", 1, 1, 'L', 1)

    # Footer branding
    if pdf.get_y() > 265:
        pdf.set_y(265)
    else:
        pdf.set_y(pdf.get_y() + 10)

    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 10, "Generated with Revu", 0, 0, 'R')
    


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

    time.sleep(1)
    try:
        os.remove(tmpfile.name)
    except PermissionError:
        pass
