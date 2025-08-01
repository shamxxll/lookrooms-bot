from fpdf import FPDF
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Пути к файлам
FONT_PATH = os.path.join("fonts", "DejaVuSans.ttf")
JSON_PATH = "/etc/secrets/<filename>"
SPREADSHEET_ID = "1k9LnA_IShTjFzsmRdtFwjbT_wEGZ5u0IM4g3CB5XYW0"

# Авторизация
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

def generate_pdf_report():
    records = sheet.get_all_records()
    today = datetime.now().strftime("%d.%m.%Y")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.set_title(f"Отчёт за {today}")
    pdf.cell(200, 10, txt=f"📊 Отчёт за {today}", ln=True, align="C")
    pdf.ln(10)

    for record in records:
        if record["Дата оплаты"] != today:
            continue

        pdf.cell(200, 10, txt=f"🏠 Адрес: {record['Адрес']}", ln=True)
        pdf.cell(200, 10, txt=f"💰 Сумма р/с: {record['Сумма рс']}", ln=True)
        pdf.cell(200, 10, txt=f"📌 Куда ушли деньги: {record['Куда ушли деньги']}", ln=True)
        pdf.cell(200, 10, txt=f"🧾 Сумма чека: {record['Сумма чека']}", ln=True)
        pdf.cell(200, 10, txt=f"👤 Сотрудник: {record['Сотрудник']}", ln=True)
        pdf.cell(200, 10, txt=f"📅 Дата оплаты: {record['Дата оплаты']}", ln=True)
        pdf.ln(10)

    file_path = "daily_report.pdf"
    pdf.output(file_path)
    return file_path
