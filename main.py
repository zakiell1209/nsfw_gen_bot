import os
import replicate
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram import F

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Установка токена для Replicate
replicate_client = replicate.Client(api_token=REPLICATE_TOKEN)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply("Привет! Отправь мне описание сцены, и я сгенерирую изображение.")

@dp.message(F.text)
async def generate_image(message: Message):
    prompt = message.text.strip()

    await message.reply("Генерация изображения, подожди немного...")

    try:
        output = replicate_client.run(
            "aitechtree/nsfw-novel-generation:71c5f85b1a67340d8c44d159de51adf21d3c4f73f64c7d3576f8c2cc6871ecbe",
            input={"prompt": prompt}
        )

        if isinstance(output, list):
            image_url = output[0]
        else:
            image_url = output

        await message.reply_photo(photo=image_url)
    except Exception as e:
        await message.reply(f"Ошибка при генерации: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))