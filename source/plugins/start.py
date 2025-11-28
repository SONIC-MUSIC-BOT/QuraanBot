from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
)
from typing import Union
from source.helpers import read, write
from config import db_path, owner_id


start_markup: list = Markup(
    [
        [Button("- البحث في محادثه أخرى -", switch_inline_query="الله لا إله إلا هو")],
        [
            Button("- تصفح القرآن (📜) -", "suras 1"),
            Button("- ختمه -", "khatma"),
        ],
        [Button("- (❔️) حول البوت (❔️) -", "about")],
        [Button("- (⚜️) اشترك هنا لدعمنا (⚜️) -", url="https://t.me/BENfiles")],
        [Button("- التواصل مع الدعم -", user_id=owner_id)],
    ]
)


start_caption: str = (
    f"- مرحبا بك عزيزي [name] في بوت القرآن الكريم.\n\n"
    "- يمكنك البحث عن آيات القرآن الكريم عن طريق أي كلمه ترسلها\n\n"
    "- يمكنك أيضا تصفح القرآن الكريم مكتوبًا أو مصورًا عن طريق الزر أدناه\n\n"
    "- لا تنسى مشاركة البوت مع أصدقاؤك ليعم الثواب."
)


@Client.on_message(filters.command("start") & filters.private)
@Client.on_callback_query(filters.regex(r"^(home)$"))
async def start(_: Client, message: Union[Message, CallbackQuery]) -> None:
    user_id: int = message.from_user.id
    db: dict = read(db_path)
    if db.get(str(user_id)) is None:
        db[str(user_id)] = {"searches": {}}
        write(db_path, db)
        await _.send_message(
            owner_id,
            (
                "- دخل شخص جديد إلى البوت 🤍.\n\n"
                f"- ايدي : {user_id}\n"
                f"- اليوزر : @{message.from_user.username}\n\n"
                "- احمد ربك فقد زاد أجرك 🤍"
            ),
        )
    caption: str = start_caption.replace(
        "[name]", f"[{message.from_user.first_name}](tg://settings)"
    )
    if isinstance(message, Message):
        await message.reply(
            caption, reply_markup=start_markup, reply_to_message_id=message.id
        )
    else:
        await message.message.edit_text(caption, reply_markup=start_markup)
