import os
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not TELEGRAM_TOKEN or not REPLICATE_API_TOKEN:
    raise RuntimeError("Не установлены TELEGRAM_TOKEN и/или REPLICATE_API_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

async def generate_image(prompt: str) -> str:
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "version": "aitechtree/nsfw-novel-generation:latest",
            "input": {"prompt": prompt}
        }
    )
    response.raise_for_status()
    prediction = response.json()
    pred_id = prediction["id"]
    url = prediction["urls"]["get"]

    while True:
        r = requests.get(url, headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"})
        r.raise_for_status()
        result = r.json()
        if result["status"] == "succeeded":
            out = result["output"]
            return out[0] if isinstance(out, list) else out
        if result["status"] in ("failed", "canceled"):
            raise RuntimeError(f"Генерация завершилась со статусом {result['status']}")
        await asyncio.sleep(2)

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer("Привет! Введи любой текст, и я сгенерирую NSFW-изображение.")

@dp.message()
async def msg_handler(msg: types.Message):
    prompt = msg.text.strip()
    await msg.answer("Генерирую... ⏳")
    try:
        img_url = await generate_image(prompt)
        await msg.answer_photo(photo=img_url, caption=f"Результат по запросу:\n{prompt}")
    except Exception as e:
        await msg.answer(f"Ошибка при генерации: {e}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))