import os
import logging
import requests
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"


def replicate_generate(prompt: str):
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "version": "8a27d67e88df54d28547d89157a128a8b8bc7c65c87687b5c8cf871a4c999a30",  # пример version модели
        "input": {
            "prompt": prompt
        }
    }
    response = requests.post(REPLICATE_API_URL, headers=headers, json=data)
    if response.status_code != 201:
        raise Exception(f"Replicate API error: {response.status_code} {response.text}")
    prediction = response.json()
    prediction_url = prediction['urls']['get']
    # Можно расширить, чтобы ждать завершения генерации через опрос prediction_url
    return prediction_url


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Привет! Отправь описание, и я сгенерирую картинку через Replicate.")


@dp.message_handler()
async def handle_prompt(message: types.Message):
    prompt = message.text
    await message.answer("Получил запрос, начинаю генерацию...")
    try:
        prediction_url = replicate_generate(prompt)
        await message.answer(f"Ссылка на генерацию (получить результат надо дополнительно):\n{prediction_url}")
    except Exception as e:
        await message.answer(f"Ошибка при генерации: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)