import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
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
SITE_URL = "saytni linki"              

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

class RegisterState(StatesGroup):
    full_name = State()
    phone_number = State()
    address = State()

def make_login_keyboard(access_token: str):
    login_url = f"{SITE_URL}/api/login-with-token/?token={access_token}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Saytga kirish", url=login_url)]
    ])
    return kb, login_url

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(json={"telegram_id": telegram_id}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    user = data.get('user', {})
                    access_token = data.get('access')
                    
                    kb, link = make_login_keyboard(access_token)
                    
                    await message.answer(
                        f"Xush kelibsiz, <b>{user.get('full_name', 'Foydalanuvchi')}</b>!\n\n"
                        f"Siz allaqachon ro'yxatdan o'tgansiz.\n\n"
                        f"Saytga kirish tugmasi va havolangiz:\n🔗 {link}",
                        reply_markup=kb
                    )
                    return
        except Exception as e:
            logging.error(f"API Error: {e}")

    await message.answer("Tizimda topilmadingiz. Ro'yxatdan o'tish uchun ism-familiyangizni kiriting:")
    await state.set_state(RegisterState.full_name)

@dp.message(RegisterState.full_name)
async def process_name(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, ism-familiyangizni matn ko'rinishida kiriting.")
        return

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
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    else:
        await message.answer("Iltimos, telefon raqamingizni yuboring.")
        return

    if not phone.startswith("+"):
        phone = f"+{phone}"

    await state.update_data(phone_number=phone)
    await message.answer("Manzilingizni kiriting (Address):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterState.address)

@dp.message(RegisterState.address)
async def process_address(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, manzilingizni matn ko'rinishida kiriting.")
        return

    await state.update_data(address=message.text)
    data = await state.get_data()
    
    payload = {
        "telegram_id": message.from_user.id,
        "full_name": data.get('full_name'),
        "phone_number": data.get('phone_number'),
        "address": data.get('address')
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(json=payload) as resp:
                if resp.status in [200, 201]:
                    res_data = await resp.json()
                    access_token = res_data.get('access')
                    kb, link = make_login_keyboard(access_token)
                    
                    await message.answer(
                        "✅ Muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
                        f"Saytga kirish uchun tugmani bosing yoki havoladan o'ting:\n🔗 {link}",
                        reply_markup=kb
                    )
                    await state.clear()
                else:
                    err = await resp.json()
                    await message.answer(f"Xatolik yuz berdi: {err}")
                    await state.clear()
        except Exception as e:
            logging.error(f"API Error: {e}")
            await message.answer("Server bilan bog'lanishda xatolik yuz berdi.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())