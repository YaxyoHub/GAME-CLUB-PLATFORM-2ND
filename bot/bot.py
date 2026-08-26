import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove
)

# BOT QO'LDA YOZILSIN

BOT_TOKEN = "YOUR_BOT_TOKEN"
API_URL = "http://127.0.0.1:8000/api/bot-auth/"  # DRF API endpoint
SITE_URL = "http://127.0.0.1:8000"              # DRF sayt manzili

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class RegisterState(StatesGroup):
    full_name = State()
    phone_number = State()
    address = State()

def make_login_keyboard(access_token: str):
    # JWT Access Token orqali to'g'ridan-to'g'ri DRF saytiga kirish havolasi
    login_url = f"{SITE_URL}/api/login-with-token/?token={access_token}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Saytga kirish", url=login_url)]
    ])
    return kb, login_url

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id

    # 1. DRF API orqali tekshirish
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json={"telegram_id": telegram_id}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    user = data['user']
                    access_token = data['access']
                    
                    kb, link = make_login_keyboard(access_token)
                    
                    await message.answer(
                        f"Xush kelibsiz, <b>{user['full_name']}</b>!\n\n"
                        f"Siz allaqachon ro'yxatdan o'tgansiz.\n\n"
                        f"Saytga kirish tugmasi va havolangiz:\n🔗 {link}",
                        reply_markup=kb,
                        parse_mode="HTML"
                    )
                    return
        except Exception as e:
            logging.error(f"API Error: {e}")

    # 2. Bazada bo'lmasa -> So'rovnomani boshlash
    await message.answer("Tizimda topilmadingiz. Ro'yxatdan o'tish uchun ism-familiyangizni kiriting:")
    await state.set_state(RegisterState.full_name)

@dp.message(RegisterState.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    
    phone_btn = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_btn)
    await state.set_state(RegisterState.phone_number)

@dp.message(RegisterState.phone_number)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    if not phone.startswith("+"):
        phone = f"+{phone}"

    await state.update_data(phone_number=phone)
    await message.answer("Manzilingizni kiriting (Address):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterState.address)

@dp.message(RegisterState.address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    
    payload = {
        "telegram_id": message.from_user.id,
        "full_name": data['full_name'],
        "phone_number": data['phone_number'],
        "address": data['address']
    }

    # 3. DRF ga ro'yxatdan o'tkazish uchun yuborish
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload) as resp:
            if resp.status in [200, 201]:
                res_data = await resp.json()
                access_token = res_data['access']
                kb, link = make_login_keyboard(access_token)
                
                await message.answer(
                    "✅ Muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
                    f"Saytga kirish uchun tugmani bosing yoki havoladan o'ting:\n🔗 {link}",
                    reply_markup=kb
                )
                await state.clear()
            else:
                err = await resp.json()
                await message.answer(f"Xatolik: {err}")
                await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())