import json, logging, re, requests, asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = 'TELEGRAM_TOKEN'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class BookingForm(StatesGroup):
    name = State()
    email = State()
    phone = State()
    date = State()
    time = State()
    people = State()


class ConfirmState(StatesGroup):
    confirming = State()


@dp.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Reservation cancelled.\nYou can /start again anytime.")


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer("Hi! Let’s start your reservation.\nWhat is your name?")
    await state.set_state(BookingForm.name)


@dp.message(BookingForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Your email?")
    await state.set_state(BookingForm.email)


@dp.message(BookingForm.email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        await message.answer(
            "❌ Invalid email format.\nPlease enter a valid email like name@example.com.\nYou can also type /cancel to stop.")
        return
    await state.update_data(email=email)
    await message.answer("Your phone number?")
    await state.set_state(BookingForm.phone)


@dp.message(BookingForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not re.match(r"^\d{10}$", phone):
        await message.answer(
            "❌ Invalid phone number.\nEnter a 10-digit US number (e.g., 4151234567).\nNo +1, spaces, or symbols.")
        return

    formatted_phone = f"+1{phone}"  # Add +1 when sending to API
    await state.update_data(phone=formatted_phone)
    await message.answer("Reservation date? (MM-DD)")
    await state.set_state(BookingForm.date)


@dp.message(BookingForm.date)
async def process_date(message: types.Message, state: FSMContext):
    today = datetime.today()
    try:
        month, day = map(int, message.text.strip().split("-"))
        year = today.year

        date_obj = datetime(year=year, month=month, day=day)

        if date_obj.date() <= today.date():
            await message.answer(
                "❌ Reservations must be made at least one day in advance.\nPlease choose a date starting from tomorrow (MM-DD).\nYou can also type /cancel to stop.")
            return

        next_month = (today.replace(day=28) + timedelta(days=4)).month
        if date_obj.month not in {today.month, next_month}:
            await message.answer(
                "❌ You can only book for the current or next month. Please try again (MM-DD).\nYou can also type /cancel to stop.")
            return

        if date_obj.weekday() >= 5:
            await message.answer(
                "❌ Reservations are only available on weekdays (Monday–Friday). Please enter a weekday (MM-DD).\nYou can also type /cancel to stop.")
            return

        await state.update_data(date=date_obj.strftime("%Y-%m-%d"))
        await message.answer("Reservation time? (HH:MM, between 11:30 and 14:00 in 15-minute steps)")
        await state.set_state(BookingForm.time)

    except (ValueError, IndexError):
        await message.answer(
            "❌ Invalid date format. Please use MM-DD (e.g., 05-29).\nYou can also type /cancel to stop.")


@dp.message(BookingForm.time)
async def process_time(message: types.Message, state: FSMContext):
    time_text = message.text.strip()

    if not re.match(r"^\d{2}:\d{2}$", time_text):
        await message.answer(
            "❌ Invalid time format.\nPlease enter as HH:MM (e.g., 12:45 in 24-hour format).\nYou can also type /cancel to stop.")
        return

    try:
        time_obj = datetime.strptime(time_text, "%H:%M").time()

        if not (datetime.strptime("11:30", "%H:%M").time() <= time_obj <= datetime.strptime("14:00", "%H:%M").time()):
            await message.answer("❌ Reservations must be between 11:30 and 14:00.\nYou can also type /cancel to stop.")
            return

        if time_obj.minute % 15 != 0:
            await message.answer(
                "❌ Time must be in 15-minute intervals (like 11:30, 11:45, 12:00, etc).\nYou can also type /cancel to stop.")
            return

        await state.update_data(time=time_text)
        await message.answer("How many people? (1-10)")
        await state.set_state(BookingForm.people)

    except ValueError:
        await message.answer(
            "❌ Invalid time format.\nPlease enter as HH:MM (e.g., 12:45 in 24-hour format).\nYou can also type /cancel to stop.")


@dp.message(BookingForm.people)
async def process_people(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
        if count < 1 or count > 10:
            await message.answer("❌ Please enter a valid number between 1 and 10.\nYou can also type /cancel to stop.")
            return

        await state.update_data(people=count)
        data = await state.get_data()

        summary = (
            f"✅ Reservation Details:\n"
            f"👤 Name: {data['name']}\n"
            f"📧 Email: {data['email']}\n"
            f"📱 Phone: {data['phone']}\n"
            f"📅 Date: {data['date']}\n"
            f"⏰ Time: {data['time']}\n"
            f"👥 People: {data['people']}\n\n"
            f"Type YES to confirm or /cancel to start over."
        )

        await message.answer(summary)
        await state.set_state(ConfirmState.confirming)

    except ValueError:
        await message.answer("❌ Please enter a valid number between 1 and 10.\nYou can also type /cancel to stop.")


@dp.message(StateFilter(ConfirmState.confirming), lambda m: m.text.strip().lower() == "yes")
async def confirm_reservation(message: types.Message, state: FSMContext):
    data = await state.get_data()

    payload = json.dumps({
        "restaurantId": "uSv6GwCcGYFfZgoGA",
        "date": data["date"],
        "time": data["time"],
        "people": data["people"],
        "guest": {
            "name": data["name"],
            "email": data["email"],
            "phone": data["phone"],
            "notificationEmail": True,
            "notificationSms": True,
            "receiveNewsletter": False
        },
        "languageCode": "en",
        "customFields": [],
        "status": "request",
        "openingHourId": "HBxyafuobSnXFsuDm",
        "referrer": "https://dining.ucsc.edu/"
    })

    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://university-center-bistro-cafe.resos.com',
        'referer': 'https://university-center-bistro-cafe.resos.com/',
        'user-agent': 'Mozilla/5.0'
    }

    try:
        response = requests.post("https://api.resos.com/api/booking/insert", headers=headers, data=payload)

        if response.status_code == 200:
            await message.answer("🎉 Reservation confirmed! See you soon.")
        else:
            await message.answer(
                "⚠️ Reservation failed.\nToo many requests with the same info?\nTry again with different details.")
    except Exception as e:
        await message.answer(f"❌ Error sending reservation: {str(e)}")

    await state.clear()


@dp.message(StateFilter(ConfirmState.confirming))
async def invalid_confirmation(message: types.Message):
    await message.answer("❓ Please type YES to confirm or /cancel to start over.")


@dp.message()
async def fallback(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Hi! Let’s start your reservation.\nWhat is your name?")
        await state.set_state(BookingForm.name)


if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
