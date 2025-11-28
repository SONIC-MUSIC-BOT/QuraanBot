from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
)
from source import hafs_db
from source.helpers import write_in_png, generate_random_string
from os import remove


@Client.on_callback_query(filters.regex(r"^(img)"))
async def aya_in_img(_: Client, callback: CallbackQuery) -> None:
    data: list = callback.data.split()
    aya_index: int = int(data[1])
    aya: dict = hafs_db[aya_index]
    try:
        path: str = write_in_png(
            f"({aya['aya_text']}) {aya['sura_name_ar']}",
            f"{generate_random_string(10)}.png",
        )
    except:
        await callback.answer("- عذرا هذه الخدمه غير متاحه حاليًا.", show_alert=True)
        return
    await callback.message.reply_photo(path, caption=f"- @{_.me.username}")
    remove(path)
