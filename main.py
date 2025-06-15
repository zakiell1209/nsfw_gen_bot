import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import replicate
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Модели (пример)
MODELS = {
    "anime": "aitechtree/nsfw-novel-generation:latest",
    "realism": "replicate/realistic-vision-v1:latest"
}

# Клавиатура выбора модели
model_kb = InlineKeyboardMarkup(row_width=2)
model_kb.add(
    InlineKeyboardButton("Аниме", callback_data="model_anime"),
    InlineKeyboardButton("Реализм", callback_data="model_realism"),
)

# Состояние пользователя (упрощённо)
user_data = {}

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Выбери модель для генерации NSFW изображения:",
        reply_markup=model_kb
    )

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("model_"))
async def process_model_selection(callback_query: types.CallbackQuery):
    model_key = callback_query.data[len("model_"):]
    if model_key not in MODELS:
        await callback_query.answer("Неизвестная модель!")
        return

    user_data[callback_query.from_user.id] = {
        "model": MODELS[model_key]
    }

    await bot.send_message(callback_query.from_user.id,
        f"Выбрана модель: {model_key}\nОтправь описание изображения, и я сгенерирую картинку."
    )
    await callback_query.answer()

@dp.message_handler()
async def generate_image(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data or "model" not in user_data[user_id]:
        await message.answer("Сначала выбери модель через команду /start")
        return

    prompt = message.text.strip()
    model_name = user_data[user_id]["model"]

    await message.answer("Генерирую изображение, подожди...")

    try:
        output_urls = replicate_client.run(
            model_name,
            input={"prompt": prompt}
        )
        # output_urls может быть список или строка с URL
        if isinstance(output_urls, list):
            img_url = output_urls[0]
        else:
            img_url = output_urls

        await message.answer_photo(img_url, caption=f"Сгенерировано по описанию:\n{prompt}")
    except Exception as e:
        await message.answer(f"Ошибка при генерации: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)