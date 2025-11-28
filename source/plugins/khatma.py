from typing import Union
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from pyrogram.enums import ChatType
from config import khatma_path
from source.helpers import read, write, get_page_img, khatma_page_markup
from datetime import datetime
import pytz

timezone = pytz.timezone("Asia/Baghdad")


@Client.on_callback_query(filters.regex(r"^(khatma)$"))
@Client.on_message(filters.command(["ختمه", "ختمة", "الختمه", "الختمة"], ""))
async def khatma(client: Client, update: Union[CallbackQuery, Message]):
    msg = "مرحبا بك عزيزي قسم الختمه !"
    user_id = update.from_user.id
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("- بدأ ختمه -", f"start_khatma {user_id}"),
                InlineKeyboardButton("- استئناف ختمه -", f"continue_khatma {user_id}"),
            ],
        ]
    )
    if isinstance(update, Message):
        await update.reply(msg, reply_markup=reply_markup, quote=True)
    else:
        reply_markup.inline_keyboard.append(
            [InlineKeyboardButton("- الرئيسية -", "home")]
        )
        await update.edit_message_text(
            msg,
            reply_markup=reply_markup,
        )


@Client.on_callback_query(filters.regex(r"^(start_khatma)"))
async def start_khatma(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    data_user_id = callback.data.split()[1]
    if data_user_id != str(user_id):
        await callback.answer("الازرار ليست لك.")
        return
    chat_type = callback.message.chat.type
    db = read(khatma_path)
    started_at = datetime.now(timezone).strftime("%d-%m-%Y, %H:%M")
    data_template = {"last_save": 1, "started_at": started_at, "end_at": False}
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        chat_id = str(callback.message.chat.id)
        chat = db["chats"].get(chat_id, False)
        if not chat:
            db["chats"][chat_id] = {}
        db["chats"][chat_id][str(user_id)] = data_template
        write(khatma_path, db)
    elif chat_type == ChatType.PRIVATE:
        chat_id = str(user_id)
        chat = db["users"].get(chat_id, False)
        if not chat:
            db["users"][chat_id] = {}
        db["users"][chat_id] = data_template
        write(khatma_path, db)
    await callback.message.delete()
    await callback.message.reply_photo(
        get_page_img(1),
        caption=(
            f"حسنا عزيزي {callback.from_user.mention()} لقد قمت ببدأ ختمة جديدة !\n"
            f"بدأت في: \n{started_at}\n"
            f"وفقك الله لإكمالها..🤍"
        ),
        reply_markup=khatma_page_markup(1, user_id),
    )


@Client.on_callback_query(filters.regex(r"^(khatma page)"))
async def khatma_page(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    data: list = callback.data.split()
    data_user_id = data[-1]
    if data_user_id != str(user_id):
        await callback.answer("الازرار ليست لك.")
        return
    page: int = int(data[3])
    url: str = get_page_img(page)
    save_khatma(callback, page)
    caption = f"وفقك الله لإكمال ختمتك..🤍\nالصفحه: {page}"
    if data[2] == "edit":
        await callback.edit_message_media(
            InputMediaPhoto(url, caption=caption),
            reply_markup=khatma_page_markup(page, user_id),
        )
    else:
        await callback.message.reply_photo(
            url,
            caption=caption,
            reply_markup=khatma_page_markup(page, user_id),
            reply_to_message_id=callback.message.id,
        )


@Client.on_callback_query(filters.regex(r"^(continue_khatma)"))
async def continue_khatma(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    data_user_id = callback.data.split()[1]
    if data_user_id != str(user_id):
        await callback.answer("الازرار ليست لك.")
        return
    chat_type = callback.message.chat.type
    db = read(khatma_path)
    exist = True
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        chat_id = str(callback.message.chat.id)
        chat = db["chats"].get(chat_id, False)
        if not chat:
            exist = False
            db["chats"][chat_id] = {}
        if not db["chats"][chat_id].get(str(user_id), False):
            exist = False
        else:
            page = db["chats"][chat_id][str(user_id)]["last_save"]
    elif chat_type == ChatType.PRIVATE:
        chat_id = str(user_id)
        chat = db["users"].get(chat_id, False)
        if not chat:
            exist = False
        else:
            page = db["users"][chat_id]["last_save"]
    write(khatma_path, db)
    if exist:
        await callback.message.delete()
        url: str = get_page_img(page)
        caption = f"وفقك الله لإكمال ختمتك..🤍\nالصفحه: {page}"
        await callback.message.reply_photo(
            url,
            caption=caption,
            reply_markup=khatma_page_markup(page, user_id),
            reply_to_message_id=callback.message.id,
        )
    else:
        await callback.answer("لم تقم ببدأ ختمه من قبل !", show_alert=True)


@Client.on_callback_query(filters.regex(r"^(end_khatma)"))
async def end_khatma(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    data_user_id = callback.data.split()[1]
    if data_user_id != str(user_id):
        await callback.answer("الازرار ليست لك.")
        return
    chat_type = callback.message.chat.type
    db = read(khatma_path)
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        chat_id = str(callback.message.chat.id)
        chat = db["chats"].get(chat_id, False)
        if not chat:
            db["chats"][chat_id] = {}
        try:
            del db["chats"][chat_id][str(user_id)]
        except:
            pass
        write(khatma_path, db)
    elif chat_type == ChatType.PRIVATE:
        chat_id = str(user_id)
        chat = db["users"].get(chat_id, False)
        if not chat:
            db["users"][chat_id] = {}
        try:
            del db["users"][chat_id]
        except:
            pass
        write(khatma_path, db)
    await callback.message.delete()
    await callback.message.reply(
        khatma_do3a[0].replace("mention", callback.from_user.mention())
    )
    await callback.message.reply(
        khatma_do3a[1],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("- بدأ ختمه -", f"start_khatma {user_id}")]]
        ),
    )


def save_khatma(callback: CallbackQuery, page: int):
    user_id = callback.from_user.id
    chat_type = callback.message.chat.type
    chat_id = str(callback.message.chat.id)
    db = read(khatma_path)
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        db["chats"][chat_id][str(user_id)]["last_save"] = page
    elif chat_type == ChatType.PRIVATE:
        db["users"][chat_id]["last_save"] = page
    write(khatma_path, db)


khatma_do3a = [
    """
الحمد لله الذي اعانك (mention) على اتمام ختمتك
عليك بدعاء الختمة لتتم الثواب 🤍

دعاء الإمام السجاد عليه السلام عند ختم القرآن

اللهم إنك أعنتني على ختم كتابك الذي أنزلته نورا، وجعلته مهيمنا على كل كتاب أنزلته، وفضلته على كل حديث قصصته، وفرقانا فرقت به بين حلالك وحرامك، وقرآنا أعربت به عن شرائع أحكامك، وكتابا فصلته لعبادك تفصيلا، ووحيا أنزلته على نبيك محمد صلواتك عليه وآله تنزيلا، وجعلته نورا نهتدي من ظلم الضلالة والجهالة باتباعه، وشفاء لمن أنصت بفهم التصديق إلى استماعه، وميزان قسط لا يحيف عن الحق لسانه، ونور هدى لا يطفأ عن الشاهدين برهانه، وعلم نجاة لا يضل من أم قصد سنته، ولا تنال أيدي الهلكات من تعلق بعروة عصمته.
اللهم فإذ أفدتنا المعونة على تلاوته، وسهلت جواسي ألسنتنا بحسن عبارته، فاجعلنا ممن يرعاه حق رعايته، ويدين لك باعتقاد التسليم لمحكم آياته، ويفزع إلى الإقرار بمتشابهه وموضحات بيناته.

اللهم إنك أنزلته على نبيك محمد صلى الله عليه وآله مجملا، وألهمته علم عجائبه مكملا، وورثتنا علمه مفسرا، وفضلتنا على من جهل علمه، وقويتنا عليه لترفعنا فوق من لم يطق حمله. اللهم فكما جعلت قلوبنا له حملة، وعرفتنا برحمتك شرفه وفضله، فصل على محمد الخطيب به وعلى آله، واجعلنا ممن يعترف بأنه من عندك، حتى لا يعارضنا الشك في تصديقه، ولا يختلجنا الزيغ عن قصد طريقه.

اللهم صل على محمد وآله، واجعلنا ممن يعتصم بحبله، ويأوى من المتشابهات إلى حرز معقله، ويسكن في ظل جناحه، ويهتدي بضوء صباحه، ويقتدي بتبلج أسفاره، ويستصبح بمصباحه، ولا يلتمس الهدى في غيره.

اللهم وكما نصبت به محمدا علما للدلالة عليك، وأنهجت بآله سبل الرضا إليك، فصل على محمد وآله، واجعل القرآن وسيلة لنا إلى أشرف منازل الكرامة، وسُلّماً نعرج فيه إلى محل السلامة، وسبباً نجزى به النجاة في عرصة القيامة، وذريعة نقدم بها على نعيم دار المقامة.

اللهم صل على محمد وآله، واحطط بالقرآن عنا ثقل الأوزار، وهب لنا حسن شمائل الأبرار، واقف بنا آثار الذين قاموا لك به آناء الليل وأطراف النهار، حتى تطهرنا من كل دنس بتطهيره، وتقفوا بنا آثار الذين استضاؤوا بنوره ولم يلههم الأمل عن العمل، فيقطعهم بخدع غروره.

اللهم صل على محمد وآله، واجعل القرآن لنا في ظلم الليالي مونسا، ومن نزغات الشيطان وخطرات الوساوس حارسا، ولأقدامنا عن نقلها إلى المعاصي حابسا، ولألسنتنا عن الخوض في الباطل من غير ما آفة مخرسا، ولجوارحنا عن اقتراف الآثام زاجرا، ولما طوت الغفلة عنا من تصفح الاعتبار ناشرا، حتى توصل إلى قلوبنا فهم عجائبه وزواجر أمثاله، التي ضعفت الجبال الرواسي على صلابتها عن احتماله.

اللهم صل على محمد وآله، وأدم بالقرآن صلاح ظاهرنا، واحجب به خطرات الوساوس عن صحة ضمائرنا، واغسل به درن قلوبنا وعلائق أوزارنا، واجمع به منتشر أمورنا، وارو به في موقف العرض عليك ظمأ هواجرنا، واكسنا به حلل الأمان يوم الفزع الأكبر في نشورنا.

اللهم صل على محمد وآله، واجبر بالقرآن خلتنا من عدم الإملاق، وسق إلينا به رغد العيش وخصب سعة الأرزاق، وجنبنا به الضرائب المذمومة ومداني الأخلاق، واعصمنا به من هوة الكفر ودواعي النفاق، حتى يكون لنا في القيامة إلى رضوانك وجنانك قائدا، ولنا في الدنيا عن سخطك وتعدي حدودك ذايدا، ولما عندك بتحليل حلاله وتحريم حرامه شاهدا.
    """,
    """
اللهم صل على محمد وآله، وهون بالقرآن عند الموت على أنفسنا كرب السياق وجهد الأنين وترادف الحشارج إذا بلغت النفوس التراقي، وقيل من راق، وتجلى ملك الموت لقبضها من حجب الغيوب، ورماها عن قوس المنايا بأسهم وحشة الفراق، وداف لها من زعاف الموت كأسا مسمومة المذاق، ودنا منا إلى الآخرة رحيل وانطلاق، وصارت الأعمال قلائد في الأعناق، وكانت القبور هي المأوى إلى ميقات يوم التلاق.

اللهم صل على محمد وآله، وبارك لنا في حلول دار البلى، وطول المقامة بين أطباق الثرى، واجعل القبور بعد فراق الدنيا خير منازلنا، وافسح لنا برحمتك في ضيق ملاحدنا، ولا تفضحنا في حاضر يوم القيامة بموبقات آثامنا، وارحم بالقرآن في موقف العرض عليك ذل مقامنا، وثبت به عند اضطراب جسر جهنم يوم المجاز عليها زلل أقدامنا، ونجنا به من كل كرب يوم القيامة، وشدائد أهوال يوم الطامة، وبيض وجوهنا يوم تسود وجوه الظَّلَمة في يوم الحسرة والندامة، واجعل لنا في صدور المؤمنين ودا، ولا تجعل الحياة علينا نكدا.

اللهم صل على محمد عبدك ورسولك كما بلغ رسالتك، وصدع بأمرك ونصح لعبادك، اللهم اجعل نبينا صلواتك عليه وآله يوم القيامة أقرب النبيين منك مجلسا، وأمكنهم منك شفاعة، وأجلهم عندك قدرا، وأوجههم عندك جاها، اللهم صل على محمد وآل محمد، وشرف بنيانه، وعظم برهانه، وثقل ميزانه، وتقبل شفاعته، وقرب وسيلته، وبيض وجهه، وأتم نوره، وارفع درجته، وأحينا على سنته، وتوفنا على ملته، وخذ بنا منهاجه، واسلك بنا سبيله، واجعلنا من أهل طاعته، واحشرنا في زمرته، وأوردنا حوضه، واسقنا بكأسه، اللهم صل على محمد وآله، صلاة تبلغه بها أفضل ما يأمل من خيرك وفضلك وكرامتك، إنك ذو رحمة واسعة وفضل كريم، اللهم اجزه بما بلغ من رسالاتك، وأدى من آياتك، ونصح لعبادك، وجاهد في سبيلك، افضل ما جزيت أحدا من ملائكتك المقربين وأنبيائك المرسلين المصطفين، والسلام عليه وعلى آله الطيبين الطاهرين ورحمة الله وبركاته.

المصدر:  الصحيفة السجادية
    """,
]
