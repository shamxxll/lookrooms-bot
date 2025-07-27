# telegram_bot.py
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sheets import generate_pdf_report
import os

API_TOKEN = '8404119240:AAHvfgS8vh4j3OkTr73dLnFUUzYAcBSAw6E'
JSON_PATH = 'credentials.json'
SPREADSHEET_ID = '1k9LnA_IShTjFzsmRdtFwjbT_wEGZ5u0IM4g3CB5XYW0'

# ==== Авторизация Google Sheets ====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# ==== FSM состояния ====
class Form(StatesGroup):
    address = State()
    amount = State()
    purpose = State()
    receipt = State()
    employee = State()
    pay_date = State()

# ==== Бот и диспетчер ====
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ==== Кнопка старта ====
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(
    KeyboardButton("💰 Внести сумму"),
    KeyboardButton("📊 Отчёт за день")
)

# ==== Кнопки выбора квартиры ====
apartments = [
    "(327) 2-ой Вольный переулок 11",
    "(454) 2-ой Вольный переулок 11",
    "(457) 2-ой Вольный переулок 11",
    "(475) 2-ой Вольный переулок 11",
    "(309) Вольная 25с3"
]
kb_apts = ReplyKeyboardMarkup(resize_keyboard=True)
for apt in apartments:
    kb_apts.add(KeyboardButton(apt))

# ==== /start ====
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Нажми “💰 Внести сумму”, чтобы начать.", reply_markup=start_kb)

# ==== Обработка "Внести сумму" ====
@dp.message_handler(lambda msg: msg.text == "💰 Внести сумму")
async def choose_apartment(message: types.Message):
    await Form.address.set()
    await message.answer("🏠 Выбери адрес квартиры:", reply_markup=kb_apts)

@dp.message_handler(lambda msg: msg.text in apartments, state=Form.address)
async def enter_amount(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await Form.next()
    await message.answer("💵 Введи сумму р/с:", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.amount)
async def enter_purpose(message: types.Message, state: FSMContext):
    await state.update_data(amount=message.text)
    await Form.next()
    await message.answer("📅 Куда ушли деньги:")

@dp.message_handler(state=Form.purpose)
async def enter_receipt(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    await Form.next()
    await message.answer("📈 Введи сумму чека:")

@dp.message_handler(state=Form.receipt)
async def enter_employee(message: types.Message, state: FSMContext):
    await state.update_data(receipt=message.text)
    await Form.next()
    await message.answer("👤 Введи имя сотрудника:")

@dp.message_handler(state=Form.employee)
async def enter_pay_date(message: types.Message, state: FSMContext):
    await state.update_data(employee=message.text)
    await Form.next()
    await message.answer("🗓️ Введи дату оплаты (например: 25.07.2025):")

@dp.message_handler(state=Form.pay_date)
async def save_to_sheet(message: types.Message, state: FSMContext):
    await state.update_data(pay_date=message.text)
    data = await state.get_data()
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    row = [
        now,
        data['address'],
        data['amount'],
        data['purpose'],
        data['receipt'],
        data['employee'],
        data['pay_date']
    ]

    sheet.append_row(row, value_input_option='USER_ENTERED')
    await message.answer("✅ Данные успешно сохранены!", reply_markup=start_kb)
    await state.finish()

# ==== Обработка "📊 Отчёт за день" ====
@dp.message_handler(lambda message: message.text == "📊 Отчёт за день")
async def send_daily_report(message: types.Message):
    try:
        file_path = generate_pdf_report()
        pdf_file = InputFile(file_path)
        await bot.send_document(chat_id=message.chat.id, document=pdf_file, caption="📊 Отчёт за сегодня")
    except Exception as e:
        await message.answer(f"❌ Ошибка при формировании отчёта: {e}")

# ==== Запуск ====
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    from sheets import generate_pdf_report



