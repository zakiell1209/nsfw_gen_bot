import os
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InputFile
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

async def generate_image(prompt: str) -> str:
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "version": "aitechtree/nsfw-novel-generation:latest",  # замените на нужную версию модели
        "input": {"prompt": prompt}
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    # Проверяем статус генерации (ожидаем успех или ошибку)
    while True:
        result = requests.get(prediction_url, headers=headers).json()
        status = result.get("status")
        if status == "succeeded":
            # Вернём первый URL с результатом (фото)
            output = result.get("output")
            if isinstance(output, list):
                return output[0]
            return output
        elif status == "failed":
            raise Exception("Generation failed")
        await asyncio.sleep(1)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь мне текст — я сгенерирую изображение.")

@dp.message()
async def handle_message(message: types.Message):
    prompt = message.text
    msg = await message.answer("Генерирую изображение, подожди...")
    try:
        image_url = await generate_image(prompt)
        # Отправим изображение по ссылке в чат
        await bot.send_photo(message.chat.id, photo=image_url, caption=f"Вот изображение по запросу:\n{prompt}")
    except Exception as e:
        await message.answer(f"Ошибка генерации: {e}")
    finally:
        await msg.delete()

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))