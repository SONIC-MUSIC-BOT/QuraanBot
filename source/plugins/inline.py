from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
)
from source.helpers import read, write, search


@Client.on_inline_query()
async def answer_inlines(_: Client, inline_query: InlineQuery) -> None:
    query: str = inline_query.query
    markup: Markup = Markup([[Button(f"- {_.me.first_name} -", user_id=_.me.id)]])
    if not query or len(query.split()) < 2:
        return
    search_results: list = search(query)
    if not search_results:
        inline_query_results: list = [
            InlineQueryResultArticle(
                title=f"لم يتم إيجاد نتائج!",
                input_message_content=InputTextMessageContent((f"- @{_.me.username}")),
                description=f"- @{_.me.username}",
            )
        ]
    else:
        inline_query_results: list = [
            InlineQueryResultArticle(
                title=f"[{aya['sura_name_ar']} : {aya['aya_no']}]",
                input_message_content=InputTextMessageContent(
                    (
                        f"({aya['aya_text'][:-2]})\n\n"
                        f"[{aya['sura_name_ar']} : {aya['aya_no']}]\n\n"
                        f"- @{_.me.username}"
                    )
                ),
                reply_markup=markup,
                description=aya["aya_text"][:-2],
            )
            for aya in search_results
        ]
    await inline_query.answer(results=inline_query_results)
