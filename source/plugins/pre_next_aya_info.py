from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
)
from source import hafs_db
from source.helpers import aya_markup


@Client.on_callback_query(filters.regex(r"^(aya|pre|next)"))
async def get_aya(_: Client, callback: CallbackQuery) -> None:
    user_id: int = callback.from_user.id
    data: list = callback.data.split()
    aya_index: int = int(data[1])
    aya: dict = hafs_db[aya_index]
    if data[0].startswith(("pre", "next")):
        last_sura_name: str = data[2]
        if aya["sura_name_en"] != last_sura_name:
            await callback.answer(
                f"- تم الإنتقال إلى سورة : ({aya['sura_name_ar']})", show_alert=True
            )
    caption: str = (
        f"({aya['aya_text'][:-2]})\n\n"
        f"[{aya['sura_name_ar']} : {aya['aya_no']}]\n\n"
        f"- @{_.me.username}"
    )
    await callback.message.edit_text(caption, reply_markup=aya_markup(aya))


@Client.on_callback_query(filters.regex(r"^(info)"))
async def info(_: Client, callback: CallbackQuery) -> None:
    aya_index: int = int(callback.data.split()[1])
    aya: dict = hafs_db[aya_index]
    caption: str = (
        f"الجزء ({aya['jozz']}) - صفحة ({aya['page']}) "
        f"- سورة {aya['sura_name_ar']} ({aya['sura_name_en']}) "
        f"- رقم الآيه في السورة ({aya['aya_no']}) "
        f"- رقم الآيه وسط كل الأيات ({aya_index + 1})"
    )
    await callback.answer(caption, show_alert=True)
