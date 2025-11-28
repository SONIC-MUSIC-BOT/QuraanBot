from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup as Markup,
)
from source.helpers import suras_keyboard1, suras_keyboard2


@Client.on_callback_query(filters.regex(r"^(suras)"))
async def get_suras_page(_: Client, callback: CallbackQuery) -> None:
    data: list = callback.data.split()
    if data[1] == "1":
        text: str = (
            "- حسنا عزيزي يمكنك اختيار السورة التي تريد من خلال الفهرس المرتب التالي :"
        )
        markup: Markup = suras_keyboard1
        await callback.message.edit_text(text, reply_markup=markup)
    else:
        text: str = None
        markup: Markup = suras_keyboard2
        await callback.message.edit_reply_markup(reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^(del)"))
async def delete(_: Client, callback: CallbackQuery) -> None:
    data = callback.data.split()
    if len(data) >= 2:
        user_id = callback.from_user.id
        data_user_id = data[1]
        if str(user_id) != data_user_id:
            await callback.answer("الزر ليس لك !")
            return
    await callback.answer("- تم الحذف")
    await callback.message.delete()
