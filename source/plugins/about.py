from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
    Chat,
)
from config import owner_id, version_date


@Client.on_callback_query(filters.regex(r"^(about)$"))
async def about(_: Client, callback: CallbackQuery) -> None:
    programmer: Chat = await _.get_chat(owner_id)
    caption: str = (
        "- مرحبا بك عزيزي في بوت القرآن الكريم.\n\n"
        "- هذا هو الإصدار الأول من بوت القرآن الكريم.\n"
        "- لغة البرمجة: Python\n"
        "- إطار العمل: Pyrogram\n"
        f"- تم الإصدار بتاريخ : {version_date}\n"
        f"- عمل عليه : [{programmer.first_name}](https://t.me/{programmer.username})\n\n"
        "- يمكنك من خلال البوت البحث عن آيات القرآن الكريم بكل سهوله.\n"
        "- يمكنك تصفح القرآن الكريم بأريحية.\n"
        "- يمكنك أيضا إستخدام البوت للبحث في محادثات خارجيه.\n"
        "- يمكنك الحصول على تفسير أي آية تريد وأيضا يمكنك الحصول على صورة للآية."
    )
    markup: Markup = Markup([[Button("￩", "home")]])
    await callback.message.edit_text(caption, reply_markup=markup)
