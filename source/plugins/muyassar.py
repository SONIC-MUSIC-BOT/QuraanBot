from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
)
from source import hafs_db
from source.helpers import get_ar_muyassar_tafsir


@Client.on_callback_query(filters.regex(r"^(muyassar)"))
async def muyassar(_: Client, callback: CallbackQuery) -> None:
    user_id: int = callback.from_user.id
    aya_index: int = int(callback.data.split()[1])
    aya: dict = hafs_db[aya_index]
    tafsir: dict = get_ar_muyassar_tafsir(aya["sura_no"])
    if not tafsir["ok"]:
        await callback.answer(
            "- عذرا حدث ما ولم استطع الوصول للتفسير.!", show_alert=True
        )
        return
    aya_tafsir: str = tafsir["tafsir"][f"{aya['sura_no']}_{aya['aya_no']}"]["text"]
    aya_tafsir += (
        f"\n\n- التفسير الميسر [{aya['sura_name_ar']} : {aya['aya_no']}]\n\n"
        f"- @{_.me.username}"
    )
    await callback.message.reply(aya_tafsir, reply_to_message_id=callback.message.id)
