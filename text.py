from sheets import generate_pdf_report

try:
    path = generate_pdf_report()
    print(f"✅ Отчёт готов: {path}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
