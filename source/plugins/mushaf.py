from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
    InputMediaPhoto,
)
from source import hafs_db
from source.helpers import get_page_img, hafs_db, pages_db, page_markup


@Client.on_callback_query(filters.regex(r"^(mushaf)"))
async def mushaf(_: Client, callback: CallbackQuery) -> None:
    user_id: int = callback.from_user.id
    data: list = callback.data.split()
    if data[1] == "aya":
        aya_index: int = int(data[3])
        aya: dict = hafs_db[aya_index]
        page: int = aya["page"]
    else:
        page: int = int(data[3])
    url: str = get_page_img(page)
    if data[2] == "edit":
        await callback.message.edit_media(
            InputMediaPhoto(url), reply_markup=page_markup(page)
        )
    else:
        await callback.message.reply_photo(
            url, reply_markup=page_markup(page), reply_to_message_id=callback.message.id
        )


@Client.on_callback_query(filters.regex(r"^(written)"))
async def written_page(_: Client, callback: CallbackQuery) -> None:
    data: list = callback.data.split()
    page: str = data[1]
    page_text: str = pages_db[page]["original"].replace("\n", " ")
    await callback.message.reply(
        f"- صفحة : {page}\n\n({page_text})", reply_to_message_id=callback.message.id
    )
