# Game Club Telegram Boti

Ushbu bot foydalanuvchilarni ro'yxatdan o'tkazish va platformaning veb-sahifasiga yo'naltirish uchun xizmat qiladi.

## Imkoniyatlari:
1. `/start` bosilganda foydalanuvchidan **Ism va familiya** so'raydi.
2. Keyin **Telefon raqami**ni so'raydi (tugma orqali yoki matn ko'rinishida yuborish mumkin).
3. Ma'lumotlar qabul qilingach:
   - Backend API ga (`/bot/auth/`) avtomatik jo'natiladi va foydalanuvchi tizimda saqlanadi.
   - **"Web sahifa linki"** tugmasi chiqadi (Inline va Reply klaviatura ko'rinishida).
4. **"Web sahifa linki"** bosilganda sayt havolasi ochiladi yoki yuboriladi.

## Sozlash (.env):
`bot/.env` faylida quyidagi parametrlarni o'zgartirishingiz mumkin:
```env
BOT_TOKEN=your_telegram_bot_token_here
WEB_SITE_URL=http://localhost:5173
BACKEND_API_URL=http://127.0.0.1:8000/bot/auth/
```

## Ishga tushirish:
Terminalda quyidagi buyruqni bering:
```bash
python bot/main.py
```
yoki:
```bash
cd bot
python main.py
```

