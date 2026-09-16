import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router


async def main():
    # Log sozlamalari
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)

    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logger.error(
            "BOT_TOKEN topilmadi! Iltimos, bot/.env fayliga Telegram @BotFather dan olgan tokeningizni kiriting."
        )
        return

    logger.info("Game Club Telegram Boti ishga tushirilmoqda...")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Handler routerini ulash
    dp.include_router(router)

    # Botga kelgan eski xabarlarni tozalash va pollingni boshlash
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nBot to'xtatildi.")

