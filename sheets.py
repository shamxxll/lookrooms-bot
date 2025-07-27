from fpdf import FPDF
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

SPREADSHEET_ID = "1k9LnA_IShTjFzsmRdtFwjbT_wEGZ5u0IM4g3CB5XYW0"
JSON_PATH = "credentials.json"
FONT_PATH = "DejaVuSans.ttf"
LOGO_PATH = "logo.png"

class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, x=10, y=8, w=20)
        self.set_font("DejaVu", "", 14)
        self.cell(0, 10, f"Отчёт за {datetime.now().strftime('%d.%m.%Y')}", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f"Страница {self.page_no()}", 0, 0, 'C')

def generate_pdf_report():
    # Авторизация Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Данные")
    data = sheet.get_all_values()

    today = datetime.now().strftime("%d.%m.%Y")
    headers = data[0]
    rows = [row for row in data[1:] if len(row) >= len(headers) and row[-1].strip() == today]

    pdf = PDF()
    pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.add_page()

    if not rows:
        pdf.cell(0, 10, "Нет данных за сегодня.", ln=True)
    else:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("DejaVu", "", 10)
        pdf.cell(90, 8, "🏠 Адрес", border=1, fill=True)
        pdf.cell(40, 8, "💰 Сумма чека", border=1, fill=True)
        pdf.ln()

        total = 0
        for row in rows:
            addr = row[1]
            check = int(row[4]) if row[4].isdigit() else 0
            pdf.cell(90, 8, addr[:40], border=1)
            pdf.cell(40, 8, f"{check} сом", border=1)
            pdf.ln()
            total += check

        pdf.set_font("DejaVu", "", 11)
        pdf.ln(5)
        pdf.set_fill_color(200, 255, 200)
        pdf.cell(90, 10, "✅ Итого прибыль", border=1, fill=True)
        pdf.cell(40, 10, f"{total} сом", border=1, fill=True)

    pdf.output("daily_report.pdf")
    return "daily_report.pdf"

if __name__ == "__main__":
    path = generate_pdf_report()
    print(f"✅ PDF сформирован: {path}")
