import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ===== ENV =====
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# ===== INIT =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== MA'LUMOTLAR =====
yangiliklar = [
    "⚽ Futbol: Turtkul FC vs Nukus United (Juma 18:00)",
    "🎉 Bayram: Yoshlar kuni (Shanba 10:00)",
    "🎂 Tug‘ilgan kun: Sobir aka (Ertaga)"
]

# ===== ADMIN MENYU =====
admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("➕ Yangilik qo‘shish", callback_data="add_news")],
    [InlineKeyboardButton("🗑️ Yangiliklarni tozalash", callback_data="clear_news")],
    [InlineKeyboardButton("📋 Joriy yangiliklar", callback_data="show_news")]
])

# ===== /START =====
@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Salom, admin! 👋\nQuyidagi tugmalar orqali boshqarishingiz mumkin:", reply_markup=admin_menu)
    else:
        await message.answer("Salom! Faqat e’lonlarni o‘qishingiz mumkin.")

# ===== CALLBACK HANDLER =====
@dp.callback_query()
async def admin_actions(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id != ADMIN_ID:
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return

    if callback.data == "add_news":
        await bot.send_message(ADMIN_ID, "📝 Yangi yangilik matnini yuboring:")
        await callback.answer()

        @dp.message()
        async def get_news(message: types.Message):
            if message.from_user.id == ADMIN_ID:
                yangiliklar.append(message.text)
                await message.reply("✅ Yangilik qo‘shildi!")
                await bot.send_message(ADMIN_ID, "Admin menyusi:", reply_markup=admin_menu)

    elif callback.data == "clear_news":
        yangiliklar.clear()
        await bot.send_message(ADMIN_ID, "🗑️ Barcha yangiliklar o‘chirildi.")
        await callback.answer()

    elif callback.data == "show_news":
        if not yangiliklar:
            await bot.send_message(ADMIN_ID, "📭 Hozircha yangiliklar yo‘q.")
        else:
            text = "\n".join(f"{i+1}. {n}" for i, n in enumerate(yangiliklar))
            await bot.send_message(ADMIN_ID, f"📋 Joriy yangiliklar:\n\n{text}")
        await callback.answer()

# ===== HAR 2 SOATDA GURUHGGA YUBORISH =====
async def send_news_periodically():
    while True:
        if yangiliklar:
            text = "\n".join(yangiliklar)
            await bot.send_message(GROUP_ID, f"📢 <b>So‘nggi yangiliklar:</b>\n\n{text}", parse_mode="HTML")
        await asyncio.sleep(2 * 60 * 60)  # 2 soat

# ===== STARTUP =====
async def on_startup():
    asyncio.create_task(send_news_periodically())
    await bot.send_message(ADMIN_ID, "✅ Bot ishga tushdi va yangiliklar rejalashtirildi.")

# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(on_startup())
    asyncio.run(dp.start_polling(bot))
