import os
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile
)

from sheets import generate_pdf_report


BOT_TOKEN = "8404119240:AAHvfgS8vh4j3OkTr73dLnFUUzYAcBSAw6E"


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Стартовая клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Внести сумму")],
        [KeyboardButton(text="📊 Отчёт за день")]
    ],
    resize_keyboard=True
)

# FSM-состояния
class PaymentForm(StatesGroup):
    address = State()
    amount_rs = State()
    usage = State()
    receipt_sum = State()
    employee = State()
    pay_date = State()


# Команда /start
@dp.message(commands=["start"])
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("👋 Привет! Выбери действие:", reply_markup=main_kb)


# Обработка кнопки "📊 Отчёт за день"
@dp.message(lambda msg: msg.text == "📊 Отчёт за день")
async def handle_report(message: Message):
    try:
        path = generate_pdf_report()
        file = FSInputFile(path)
        await message.answer_document(file, caption="📎 Вот отчёт за сегодня")
    except Exception as e:
        await message.answer(f"❌ Ошибка при формировании отчёта: {e}")


# Обработка кнопки "💰 Внести сумму"
@dp.message(lambda msg: msg.text == "💰 Внести сумму")
async def handle_start_payment(message: Message, state: FSMContext):
    await message.answer("🏠 Введите адрес квартиры:")
    await state.set_state(PaymentForm.address)


@dp.message(PaymentForm.address)
async def handle_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("💰 Введите сумму р/с:")
    await state.set_state(PaymentForm.amount_rs)


@dp.message(PaymentForm.amount_rs)
async def handle_amount_rs(message: Message, state: FSMContext):
    await state.update_data(amount_rs=message.text)
    await message.answer("📌 Куда ушли деньги?")
    await state.set_state(PaymentForm.usage)


@dp.message(PaymentForm.usage)
async def handle_usage(message: Message, state: FSMContext):
    await state.update_data(usage=message.text)
    await message.answer("🧾 Сумма чека:")
    await state.set_state(PaymentForm.receipt_sum)


@dp.message(PaymentForm.receipt_sum)
async def handle_receipt_sum(message: Message, state: FSMContext):
    await state.update_data(receipt_sum=message.text)
    await message.answer("👤 Введите имя сотрудника:")
    await state.set_state(PaymentForm.employee)


@dp.message(PaymentForm.employee)
async def handle_employee(message: Message, state: FSMContext):
    await state.update_data(employee=message.text)
    await message.answer("📅 Введите дату оплаты (ДД.ММ.ГГГГ):")
    await state.set_state(PaymentForm.pay_date)


@dp.message(PaymentForm.pay_date)
async def handle_pay_date(message: Message, state: FSMContext):
    data = await state.get_data()
    pay_date = message.text

    # Запись в Google Таблицу
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1k9LnA_IShTjFzsmRdtFwjbT_wEGZ5u0IM4g3CB5XYW0").sheet1

        sheet.append_row([
            datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            data["address"],
            data["amount_rs"],
            data["usage"],
            data["receipt_sum"],
            data["employee"],
            pay_date
        ])

        await message.answer("✅ Данные успешно сохранены!", reply_markup=main_kb)
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {e}")

    await state.clear()


# Запуск бота
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))


