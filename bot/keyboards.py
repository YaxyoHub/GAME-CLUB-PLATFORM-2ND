from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# Telefon raqamni ulashish tugmasi
phone_share_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Web sahifa linki uchun Reply tugma
web_link_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌐 Web sahifa linki")]
    ],
    resize_keyboard=True
)

# Web sahifa linki uchun Inline tugma (bosganda to'g'ridan-to'g'ri sayt ochiladi)
def get_web_link_inline_keyboard(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Web sahifa linki", url=url)]
        ]
    )

