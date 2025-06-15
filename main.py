import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from prompts import convert_description_to_prompt
from replicate_utils import generate_image, generate_video

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN не установлен")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище состояния
user_state = {}

@dp.message_handler(commands=["start"])
async def start_cmd(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🖼 Аниме", callback_data="model_anime")],
        [InlineKeyboardButton("🎨 Реализм", callback_data="model_realism")],
        [InlineKeyboardButton("✍️ Ввести описание", callback_data="custom_prompt")],
        [InlineKeyboardButton("🎥 Сгенерировать видео", callback_data="gen_video")]
    ])
    await m.answer("Выбери режим:", reply_markup=kb)

@dp.callback_query_handler(lambda c: True)
async def cb_handler(c: types.CallbackQuery):
    data = c.data
    user_state[c.from_user.id] = {"mode": data}
    if data == "custom_prompt":
        await c.message.answer("Напиши своё описание:")
    else:
        await c.message.answer("Теперь отправь описание картинки:")
    await c.answer()

@dp.message_handler(lambda m: m.from_user.id in user_state)
async def gen_handler(m: types.Message):
    state = user_state.pop(m.from_user.id)
    mode = state["mode"]
    prompt = convert_description_to_prompt(m.text, mode.replace("model_", ""))
    if mode == "gen_video":
        url = generate_video(prompt)
    else:
        url = generate_image(prompt, mode.replace("model_", ""))
    await m.answer(url)

if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)