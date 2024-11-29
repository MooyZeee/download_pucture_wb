import asyncio
import logging

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.methods import DeleteWebhook

from config.config import TOKEN
from aiogram import Bot, Dispatcher
from handlers.start_handler import router


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


async def main():
    dp.include_router(router)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run( main())
    except KeyboardInterrupt:
        print('Exit')
