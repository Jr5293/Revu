import streamlit as st
from fpdf import FPDF
import tempfile
import os
from datetime import date
from urllib.parse import quote

st.set_page_config(page_title="Cravix - Client Intake Form", layout="centered")
st.title("📋 Cravix - Client Intake Form")
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

def get_image_size(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(24)
        if header.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):  # PNG
            w = int.from_bytes(header[16:20], 'big')
            h = int.from_bytes(header[20:24], 'big')
            return w, h
        elif header[:2] == b'\xFF\xD8':  # JPEG
            f.seek(0)
            size = 2
            ftype = 0
            while not 0xc0 <= ftype <= 0xcf or ftype in [0xc4, 0xc8, 0xcc]:
                f.seek(size, 1)
                byte = f.read(1)
                while ord(byte) == 0xff:
                    byte = f.read(1)
                ftype = ord(byte)
                size = int.from_bytes(f.read(2), 'big') - 2
            f.seek(1, 1)  # precision
            h = int.from_bytes(f.read(2), 'big')
            w = int.from_bytes(f.read(2), 'big')
            return w, h
        else:
            raise ValueError("Unsupported image format")

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.set_text_color(79, 139, 249)
        self.cell(0, 10, "Client Intake Summary", ln=True, align='C')
        self.set_font("Arial", '', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"Generated on: {date.today().strftime('%m/%d/%Y')}", ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, 'C')
        self.cell(0, 10, "Generated with Cravix", 0, 0, 'R')

if submitted:
    all_uploaded_files = uploaded_files if uploaded_files else []

    pdf = PDF()
    pdf.add_page()

    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Client Info", ln=True, fill=True)
    pdf.ln(5)

    pdf.set_draw_color(200, 200, 200)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_text_color(0, 0, 0)

    def add_row(label, value):
        pdf.set_font("Arial", '', 12)  # Set to value font for width calculation
        cell_width = 130
        line_height = 6
        # Compute number of lines
        number_lines = 1
        if value:
            current_line_width = 0
            for char in value.replace('\r', ''):
                if char == '\n':
                    number_lines += 1
                    current_line_width = 0
                else:
                    current_line_width += pdf.get_string_width(char)
                    if current_line_width > cell_width - 2:  # margin
                        number_lines += 1
                        current_line_width = pdf.get_string_width(char)
        row_height = number_lines * line_height

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(60, row_height, label, border=1, ln=0, align='L', fill=True)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(130, line_height, value, border=1, align='L', fill=True)

    add_row("Full Name", client_name)
    add_row("Email", email)
    add_row("Phone", phone)
    add_row("Address", address)
    add_row("Preferred Contact", preferred_contact)

    pdf.ln(10)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Service Request", ln=True, fill=True)
    pdf.ln(5)

    pdf.set_fill_color(245, 245, 245)

    add_row("Service Needed", service_needed)
    add_row("Preferred Date", preferred_date.strftime('%m/%d/%Y'))
    add_row("Notes", notes)

    if all_uploaded_files:
        pdf.ln(10)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Uploaded Photos", ln=True, fill=True)
        pdf.ln(5)

        max_w = 180
        max_h = 120
        dpi = 96
        mm_per_inch = 25.4
        page_width = 210
        left_margin = 10
        right_margin = 10
        h_spacing = 10

        i = 0
        while i < len(all_uploaded_files):
            # Estimate row height: caption 5 + 2 + max_h 120 + 10 = ~140
            if pdf.get_y() + 140 > 280:
                pdf.add_page()

            row_y = pdf.get_y()

            # First photo
            file1 = all_uploaded_files[i]
            file_extension1 = file1.type.split('/')[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension1}") as tmpimg1:
                tmpimg1.write(file1.getvalue())
                img_path1 = tmpimg1.name

            img_w_px1, img_h_px1 = get_image_size(img_path1)
            nat_w_mm1 = (img_w_px1 / dpi) * mm_per_inch
            nat_h_mm1 = (img_h_px1 / dpi) * mm_per_inch

            scale1 = min(max_w / nat_w_mm1, max_h / nat_h_mm1, 1)
            draw_w1 = nat_w_mm1 * scale1
            draw_h1 = nat_h_mm1 * scale1

            # Caption for first
            pdf.set_font("Arial", 'I', 10)
            pdf.set_xy(left_margin, row_y)
            pdf.cell(draw_w1, 5, f"Photo {i+1}", ln=0)

            img_y = row_y + 7
            pdf.image(img_path1, x=left_margin, y=img_y, w=draw_w1, h=draw_h1)

            row_h = draw_h1

            os.unlink(img_path1)

            i += 1

            # Check for second photo
            place_second = False
            if i < len(all_uploaded_files):
                file2 = all_uploaded_files[i]
                file_extension2 = file2.type.split('/')[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension2}") as tmpimg2:
                    tmpimg2.write(file2.getvalue())
                    img_path2 = tmpimg2.name

                img_w_px2, img_h_px2 = get_image_size(img_path2)
                nat_w_mm2 = (img_w_px2 / dpi) * mm_per_inch
                nat_h_mm2 = (img_h_px2 / dpi) * mm_per_inch

                scale2 = min(max_w / nat_w_mm2, max_h / nat_h_mm2, 1)
                draw_w2 = nat_w_mm2 * scale2
                draw_h2 = nat_h_mm2 * scale2

                # Check if fits: left_margin + draw_w1 + h_spacing + draw_w2 + right_margin <= page_width
                if left_margin + draw_w1 + h_spacing + draw_w2 + right_margin <= page_width:
                    place_second = True
                    x2 = left_margin + draw_w1 + h_spacing

                    # Caption for second
                    pdf.set_xy(x2, row_y)
                    pdf.cell(draw_w2, 5, f"Photo {i+1}", ln=0)

                    pdf.image(img_path2, x=x2, y=img_y, w=draw_w2, h=draw_h2)

                    row_h = max(row_h, draw_h2)

                    os.unlink(img_path2)

                    i += 1

            # Set next y
            pdf.set_y(img_y + row_h + 10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            pdf_data = f.read()

    st.download_button("📥 Download Client Intake PDF", data=pdf_data, file_name=f"{client_name}_intake.pdf", mime="application/pdf")

    # Email shortcut
    subject = quote(f"New Client Intake Form for {client_name}")
    body = quote(f"A new client intake form has been submitted for {client_name}.\r\n\r\nClient Details:\r\nName: {client_name}\r\nEmail: {email}\r\nPhone: {phone}\r\nAddress: {address}\r\nPreferred Contact: {preferred_contact}\r\n\r\nService Request:\r\nService Needed: {service_needed}\r\nPreferred Date: {preferred_date.strftime('%m/%d/%Y')}\r\nNotes: {notes}\r\n\r\nPlease attach the PDF with full details, including any photos, before sending.")
    mailto_link = f"mailto:?subject={subject}&body={body}"
    st.markdown(f"[📧 Send via Email]({mailto_link})", unsafe_allow_html=True)
