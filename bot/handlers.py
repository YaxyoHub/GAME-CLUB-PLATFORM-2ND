import re
import aiohttp
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from states import RegistrationState
from keyboards import phone_share_keyboard, web_link_reply_keyboard, get_web_link_inline_keyboard
from config import WEB_SITE_URL, BACKEND_API_URL

router = Router()


def clean_phone_number(raw_phone: str) -> str:
    """Telefon raqamni tozalab +998901234567 formatiga keltiradi"""
    digits = re.sub(r'\D', '', raw_phone)
    if digits.startswith('998') and len(digits) == 12:
        return f"+{digits}"
    elif len(digits) == 9:
        return f"+998{digits}"
    elif raw_phone.startswith('+'):
        return raw_phone
    return f"+{digits}"


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    /start bosilganda foydalanuvchini kutib oladi va Ism-sharifini so'raydi
    """
    await state.clear()
    
    user_first_name = message.from_user.first_name or "Foydalanuvchi"
    text = (
        f"Assalomu alaykum, {user_first_name}! 🎮\n"
        f"Game Club platformasining rasmiy botiga xush kelibsiz!\n\n"
        f"Ro'yxatdan o'tish uchun iltimos, **Ism va familiyangizni** kiriting:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationState.full_name)


@router.message(RegistrationState.full_name)
async def process_full_name(message: Message, state: FSMContext):
    """
    Foydalanuvchi ismini qabul qiladi va telefon raqamini so'raydi
    """
    full_name = (message.text or "").strip()
    if len(full_name) < 2:
        await message.answer("Iltimos, haqiqiy ism-familiyangizni to'liq kiriting (kamida 2 ta harf):")
        return

    await state.update_data(full_name=full_name)

    text = (
        f"Rahmat, **{full_name}**! 👍\n\n"
        f"Endi iltimos, telefon raqamingizni yuboring.\n"
        f"Quyidagi **'📱 Telefon raqamni yuborish'** tugmasini bosing yoki "
        f"raqamingizni qo'lda kiriting (masalan: `+998901234567`):"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=phone_share_keyboard)
    await state.set_state(RegistrationState.phone_number)


@router.message(RegistrationState.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    """
    Telefon raqamni qabul qiladi (kontakt yoki matn ko'rinishida),
    bazaga yuboradi va Web sahifa linki tugmasini chiqaradi.
    """
    if message.contact:
        phone_number = clean_phone_number(message.contact.phone_number)
    else:
        raw_text = (message.text or "").strip()
        # Raqamni tekshirish
        if not re.search(r'\d{9}', raw_text):
            await message.answer(
                "❌ Noto'g'ri telefon raqami kiritildi!\n"
                "Iltimos, pastdagi tugmani bosing yoki raqamni `+998901234567` formatida yuboring:",
                parse_mode="Markdown",
                reply_markup=phone_share_keyboard
            )
            return
        phone_number = clean_phone_number(raw_text)

    data = await state.get_data()
    full_name = data.get('full_name', message.from_user.full_name or 'Foydalanuvchi')

    # Django backend API ga foydalanuvchini ro'yxatdan o'tkazish so'rovini jo'natamiz
    try:
        payload = {
            "telegram_chat_id": str(message.from_user.id),
            "phone_number": phone_number,
            "full_name": full_name
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(BACKEND_API_URL, json=payload, timeout=5) as resp:
                if resp.status in (200, 201):
                    print(f"[API] Foydalanuvchi backendda muvaffaqiyatli saqlandi: {phone_number}")
                else:
                    print(f"[API] Backend javobi: {resp.status}")
    except Exception as e:
        print(f"[API Xatolik] Backend bilan ulanishda xato: {e}")

    await state.clear()

    success_text = (
        f"✅ **Tabriklaymiz, ma'lumotlaringiz muvaffaqiyatli qabul qilindi!**\n\n"
        f"👤 **Ism:** {full_name}\n"
        f"📞 **Telefon:** {phone_number}\n\n"
        f"Endi quyidagi **'Web sahifa linki'** tugmasi orqali platformamizga o'tib, "
        f"o'yin klublari va kompyuterlarni onlayn bron qilishingiz mumkin! 🚀"
    )

    # 1. Reply keyboard sifatida 'Web sahifa linki' tugmasini pastga o'rnatamiz
    await message.answer(
        success_text,
        parse_mode="Markdown",
        reply_markup=web_link_reply_keyboard
    )

    # 2. To'g'ridan-to'g'ri bitta bosishda saytga o'tish uchun Inline tugma ham taqdim etamiz
    await message.answer(
        f"Web sahifaga o'tish uchun bosing:",
        reply_markup=get_web_link_inline_keyboard(WEB_SITE_URL)
    )


@router.message(F.text.in_(["🌐 Web sahifa linki", "Web sahifa linki", "web sahifa linki"]))
async def web_link_button_clicked(message: Message):
    """
    Foydalanuvchi 'Web sahifa linki' tugmasini bosganda sayt manzilini chiqaradi
    """
    text = (
        f"🎮 **Game Club Platformasi Rasmiy Sahifasi**\n\n"
        f"Sayt manzili:\n"
        f"🔗 [Game Club Platformasiga o'tish]({WEB_SITE_URL})\n\n"
        f"To'g'ridan-to'g'ri kirish uchun quyidagi tugmani bosing:"
    )
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_web_link_inline_keyboard(WEB_SITE_URL)
    )

