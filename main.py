import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
import replicate
from dotenv import load_dotenv
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

MODELS = {
    "anime": "aitechtree/nsfw-novel-generation:latest",
    "realism": "replicate/realistic-vision-v1:latest"
}

model_kb = InlineKeyboardMarkup(row_width=2)
model_kb.add(
    InlineKeyboardButton("Аниме", callback_data="model_anime"),
    InlineKeyboardButton("Реализм", callback_data="model_realism"),
)

class Form(StatesGroup):
    waiting_for_model = State()
    waiting_for_prompt = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Выбери модель для генерации NSFW изображения:",
        reply_markup=model_kb
    )
    await state.set_state(Form.waiting_for_model)

@dp.callback_query()
async def process_model_selection(callback: types.CallbackQuery, state: FSMContext):
    if not callback.data or not callback.data.startswith("model_"):
        return
    model_key = callback.data[len("model_"):]
    if model_key not in MODELS:
        await callback.answer("Неизвестная модель!")
        return

    await state.update_data(model=MODELS[model_key])
    await callback.message.answer(f"Выбрана модель: {model_key}\nОтправь описание изображения, и я сгенерирую картинку.")
    await state.set_state(Form.waiting_for_prompt)
    await callback.answer()

@dp.message(Form.waiting_for_prompt)
async def generate_image(message: types.Message, state: FSMContext):
    data = await state.get_data()
    model_name = data.get("model")
    prompt = message.text.strip()

    if not model_name:
        await message.answer("Пожалуйста, сначала выберите модель через команду /start")
        return

    await message.answer("Генерирую изображение, подожди...")

    try:
        output_urls = replicate_client.run(
            model_name,
            input={"prompt": prompt}
        )
        if isinstance(output_urls, list):
            img_url = output_urls[0]
        else:
            img_url = output_urls

        await message.answer_photo(img_url, caption=f"Сгенерировано по описанию:\n{prompt}")
    except Exception as e:
        await message.answer(f"Ошибка при генерации: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())