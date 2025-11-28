from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup as Markup
from source.helpers import read, write, search, send_results, generate_random_string
from config import db_path
from asyncio import sleep
from typing import Union


@Client.on_message(~filters.command("start") & filters.private)
async def search_in_hafs_data(_: Client, message: Message) -> None:
    user_id: int = message.from_user.id
    wait: Message = await message.reply(
        "- جارٍ البحث..!", reply_to_message_id=message.id
    )
    results: list = search(message.text)
    if not results:
        await wait.edit_text(
            (
                "- لم أستطع إيجاد نتائج البحث عن:\n"
                f"{message.text}\n\n"
                "- تأكد من الهمزات والحروف من فضلك!"
            )
        )
        return
    else:
        await wait.delete()
        search_id: str = generate_random_string(6)
        db: dict = read(db_path)
        while search_id in db[str(user_id)]["searches"]:
            search_id = generate_random_string(6)
        db[str(user_id)]["searches"][search_id] = message.text
        write(db_path, db)
        kwargs: dict = {
            "client": _,
            "message": message,
            "search_id": search_id,
            "results": results,
            "is_more_than_max": True if len(results) > 10 else False,
        }
        await send_results(**kwargs)


@Client.on_callback_query(filters.regex(r"^(more)"))
async def more_results(_: Client, callback: CallbackQuery) -> None:
    aya_button: list = callback.message.reply_markup.inline_keyboard[0]
    await callback.message.edit_reply_markup(reply_markup=Markup([aya_button]))
    user_id: int = callback.from_user.id
    data: list = callback.data.split()[1:]
    index: int = int(data[0])
    search_id: str = data[1]
    db: dict = read(db_path)
    keywords: str = db[str(user_id)]["searches"][search_id]
    results: list = search(keywords)
    kwargs: dict = {
        "client": _,
        "message": callback.message,
        "search_id": search_id,
        "results": results,
        "start": index,
        "is_more_than_max": True if len(results[index:]) > 10 else False,
    }
    await send_results(**kwargs)
