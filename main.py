import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

HEADERS = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json",
}

# Замени на актуальный version id модели Replicate, которую хочешь использовать
REPLICATE_MODEL_VERSION = "your-model-version-id"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Отправь описание (промт) для генерации изображения через Replicate."
    )

@dp.message()
async def handle_message(message: types.Message):
    prompt = message.text.strip()
    await message.answer("Запрос принят, начинаю генерацию...")

    payload = {
        "version": REPLICATE_MODEL_VERSION,
        "input": {
            "prompt": prompt
        }
    }

    try:
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=HEADERS,
            json=payload,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        await message.answer(f"Ошибка при запросе к Replicate API:\n{e}")
        return

    prediction = response.json()
    prediction_id = prediction.get("id")
    if not prediction_id:
        await message.answer("Не удалось получить ID предсказания.")
        return

    # Отслеживаем статус предсказания (polling)
    status = prediction.get("status")
    while status not in ("succeeded", "failed", "canceled"):
        await asyncio.sleep(3)
        try:
            r = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers=HEADERS,
            )
            r.raise_for_status()
            prediction = r.json()
            status = prediction.get("status")
        except requests.RequestException:
            await message.answer("Ошибка при проверке статуса генерации.")
            return

    if status == "succeeded":
        output_urls = prediction.get("output")
        if isinstance(output_urls, list) and output_urls:
            await message.answer_photo(output_urls[0])
        else:
            await message.answer("Генерация завершилась, но результат не найден.")
    else:
        await message.answer(f"Генерация завершилась с ошибкой: {status}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))