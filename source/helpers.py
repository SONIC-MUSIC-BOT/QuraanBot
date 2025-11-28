from pyrogram import Client
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
)
from pyrogram.errors import FloodWait
from typing import Union
from json import load, dump
from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
import urllib3
import warnings
import json
import string
import random
import asyncio


def read(file_path: str) -> Union[dict, list]:
    with open(file_path, "r", encoding="utf-8") as file:
        return load(file)


def write(file_path: str, data: Union[dict, list]) -> None:
    with open(file_path, "w") as file:
        dump(data, file, indent=4, ensure_ascii=False)


hafs_db: dict = read("source/database/hafsData.json")
pages_db: dict = read("source/database/pages.json")


def search(text: str) -> list:
    results: list = []
    for item in hafs_db:
        if text in item["aya_text_emlaey"]:
            results.append(item)
    return results


async def send_results(
    client: Client,
    message: Message,
    search_id: str,
    results: list,
    start: int = 0,
    is_more_than_max: bool = False,
) -> None:
    if is_more_than_max:
        end: Union[int, None] = (start + 10) if start + 10 < len(results) else None
        if end:
            real_results = results[start:end]
        else:
            real_results = results[start:]
    else:
        real_results = results[start:]
    for result in real_results:
        caption: str = (
            f"( {result['aya_text'][:-2]} )\n\n"
            f"[{result['sura_name_ar']} : {result['aya_no']}]\n\n"
            f"- @{client.me.username}"
        )
        aya_markup: Markup = Markup(
            [[Button("- خيارات الآيه -", f"aya {result['id'] - 1}")]]
        )
        try:
            msg: Message = await message.reply(
                caption, reply_markup=aya_markup, reply_to_message_id=message.id
            )
        except FloodWait as e:
            duration: int = int(str(e).split("of ")[1].split(maxsplit=1)[0].strip())
            await asyncio.sleep(duration + 1)
            msg: Message = await message.reply(
                caption, reply_markup=aya_markup, reply_to_message_id=message.id
            )
    if is_more_than_max:
        aya_markup.inline_keyboard.append(
            [
                Button(
                    f"- المزيد ({len(results) - (start + 10)}) -",
                    f"more {start + 10} {search_id}",
                )
            ]
        )
        await msg.edit_reply_markup(reply_markup=aya_markup)


def get_page_img(page: int) -> str:
    if not isinstance(page, int) and not page.isnumeric():
        raise TypeError("Page argument must be type of int.")
    elif int(page) < 1 or int(page) > 604:
        raise ValueError("Page argument must be from 1 to 604.")
    return f"https://quran.ksu.edu.sa/png_big/{page}.png"


def suppress_warnings() -> None:
    warnings.filterwarnings(
        "ignore",
        message="Unverified HTTPS request is being made",
        category=urllib3.exceptions.InsecureRequestWarning,
    )


def get_ar_muyassar_tafsir(sura: int, start_aya: int = 1, end_aya: int = 1) -> dict:
    if any(
        [
            not isinstance(sura, int) and not sura.isnumeric(),
            not isinstance(start_aya, int) and not start_aya.isnumeric(),
            not isinstance(end_aya, int) and not end_aya.isnumeric(),
        ]
    ):
        raise TypeError("All arguments must be type of int.")
    elif int(sura) < 1 or int(sura) > 114:
        raise ValueError("Sura argument must be from 1 to 114.")
    url: str = "https://quran.ksu.edu.sa/interface.php"
    params: dict = {
        "ui": "mobile",
        "do": "tarjama",
        "tafsir": "ar_muyassar",
        "b_sura": sura,
        "b_aya": start_aya,
        "e_sura": int(sura) + 1,
        "e_aya": end_aya,
    }
    headers: dict = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }
    suppress_warnings()
    response: requests.Response = requests.get(
        url, params=params, headers=headers, verify=False
    )
    data: dict = {"ok": True}
    if response.status_code != 200:
        data = {"ok": False, "status_code": response.status_code}
    else:
        try:
            data.update(response.json())
        except json.JSONDecodeError:
            data = {
                "ok": False,
                "response": response.text,
                "status_code": response.status_code,
            }
    return data


def write_in_png(
    text: str,
    img_path: str,
    width: int = 1200,
    height: int = 800,
    font_size: int = 48,
    font_path: str = "source/uthmanic_hafs_v20.ttf",
    text_color=(255, 255, 255),
    textwrap_width: int = 95,
    background_color: tuple = (0, 0, 0),
    direction: str = "rtl",
) -> str:
    image: Image.Image = Image.new("RGB", (width, height), background_color)
    text: str = textwrap.fill(text, width=textwrap_width)
    font: ImageFont.FreeTypeFont = ImageFont.truetype(font_path, font_size)
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)
    text_bbox: tuple = draw.textbbox((0, 0), text, font=font)
    text_width: int = text_bbox[2] - text_bbox[0]
    text_height: int = text_bbox[3] - text_bbox[1]
    text_position: tuple = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(text_position, text, fill=text_color, font=font, direction=direction)
    image.save(img_path)
    return img_path


def generate_random_string(length: int) -> str:
    letters: list = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(length))


def aya_markup(aya: dict) -> Markup:
    aya_index: int = aya["id"] - 1
    return Markup(
        [
            [
                Button(
                    "￩",
                    f"next {(aya_index + 1) if aya_index < (len(hafs_db) - 1) else 0} {aya['sura_name_en']}",
                ),
                Button("￫", f"pre {aya_index - 1} {aya['sura_name_en']}"),
            ],
            [Button("- التفسير الميسر للآيه -", f"muyassar {aya_index}")],
            [
                Button("- كتابة الآيه في صوره -", f"img {aya_index}"),
                Button("- عرض الآيه في المصحف -", f"mushaf aya send {aya_index}"),
            ],
            [Button("- معملومات الآيه -", f"info {aya_index}")],
        ]
    )


def page_markup(page: int) -> Markup:
    return Markup(
        [
            [
                Button(
                    "￩", f"mushaf page edit {(page + 1) if (page + 1) < 605 else 1}"
                ),
                Button(
                    "￫", f"mushaf page edit {(page - 1) if (page - 1) > 0 else 604}"
                ),
            ],
            [Button("- إرسال الصفحه مكتوبه -", f"written {page}")],
            [Button("- ❌️ -", "del")],
        ]
    )


def khatma_page_markup(page: int, user_id: int):
    markup = [
        [
            Button(
                "￩",
                f"khatma page edit {(page + 1) if (page + 1) < 605 else 1} {user_id}",
            ),
            Button(
                "￫",
                f"khatma page edit {(page - 1) if (page - 1) > 0 else 604} {user_id}",
            ),
        ],
        [Button("- غلق الصفحه -", f"del {user_id}")],
    ]
    if page >= 604:
        markup.insert(1, [Button("- 🤍 انهاء التخمة 🤍 -", f"end_khatma {user_id}")])
    return Markup(markup)


suras_keyboard1: Markup = Markup(
    [
        [
            Button("الفَاتِحة (Al-Fātiḥah)", "mushaf page send 1"),
            Button("البَقَرَة (Al-Baqarah)", "mushaf page send 2"),
            Button("آل عِمران (Āl-‘Imrān)", "mushaf page send 50"),
        ],
        [
            Button("النِّسَاء (An-Nisā’)", "mushaf page send 77"),
            Button("المَائدة (Al-Mā’idah)", "mushaf page send 106"),
            Button("الأنعَام (Al-An‘ām)", "mushaf page send 128"),
        ],
        [
            Button("الأعرَاف (Al-A‘rāf)", "mushaf page send 151"),
            Button("الأنفَال (Al-Anfāl)", "mushaf page send 177"),
            Button("التوبَة (At-Taubah)", "mushaf page send 187"),
        ],
        [
            Button("يُونس (Yūnus)", "mushaf page send 208"),
            Button("هُود (Hūd)", "mushaf page send 221"),
            Button("يُوسُف (Yūsuf)", "mushaf page send 235"),
        ],
        [
            Button("الرَّعد (Ar-Ra‘d)", "mushaf page send 249"),
            Button("إبراهِيم (Ibrāhīm)", "mushaf page send 255"),
            Button("الحِجر (Al-Ḥijr)", "mushaf page send 262"),
        ],
        [
            Button("النَّحل (An-Naḥl)", "mushaf page send 267"),
            Button("الإسرَاء (Al-Isrā’)", "mushaf page send 282"),
            Button("الكَهف (Al-Kahf)", "mushaf page send 293"),
        ],
        [
            Button("مَريَم (Maryam)", "mushaf page send 305"),
            Button("طه (Ṭā-Hā)", "mushaf page send 312"),
            Button("الأنبيَاء (Al-Anbiyā’)", "mushaf page send 322"),
        ],
        [
            Button("الحج (Al-Ḥajj)", "mushaf page send 332"),
            Button("المؤمنُون (Al-Mu’minūn)", "mushaf page send 342"),
            Button("النور (An-Nūr)", "mushaf page send 350"),
        ],
        [
            Button("الفُرقَان (Al-Furqān)", "mushaf page send 359"),
            Button("الشعراء (Ash-Shu‘arā’)", "mushaf page send 367"),
            Button("النَّمل (An-Naml)", "mushaf page send 377"),
        ],
        [
            Button("القَصَص (Al-Qaṣaṣ)", "mushaf page send 385"),
            Button("العَنكبُوت (Al-‘Ankabūt)", "mushaf page send 396"),
            Button("الرُّوم (Ar-Rūm)", "mushaf page send 404"),
        ],
        [
            Button("لُقمَان (Luqmān)", "mushaf page send 411"),
            Button("السَّجدة (As-Sajdah)", "mushaf page send 415"),
            Button("الأحزَاب (Al-Aḥzāb)", "mushaf page send 418"),
        ],
        [
            Button("سَبإ (Saba’)", "mushaf page send 428"),
            Button("فَاطِر (Fāṭir)", "mushaf page send 434"),
            Button("يسٓ (Yā-Sīn)", "mushaf page send 440"),
        ],
        [
            Button("الصَّافَات (Aṣ-Ṣāffāt)", "mushaf page send 446"),
            Button("صٓ (Ṣād)", "mushaf page send 453"),
            Button("الزُّمَر (Az-Zumar)", "mushaf page send 458"),
        ],
        [
            Button("غَافِر (Ghāfir)", "mushaf page send 467"),
            Button("فُصِّلَت (Fuṣṣilat)", "mushaf page send 477"),
            Button("الشُّوري (Ash-Shūra)", "mushaf page send 483"),
        ],
        [
            Button("الزُّخرُف (Az-Zukhruf)", "mushaf page send 489"),
            Button("الدُّخان (Ad-Dukhān)", "mushaf page send 496"),
            Button("الجاثِية (Al-Jāthiyah)", "mushaf page send 499"),
        ],
        [
            Button("الأحقَاف (Al-Aḥqāf)", "mushaf page send 502"),
            Button("مُحمد (Muḥammad)", "mushaf page send 507"),
            Button("الفَتح (Al-Fatḥ)", "mushaf page send 511"),
        ],
        [
            Button("الحُجُرَات (Al-Ḥujurāt)", "mushaf page send 515"),
            Button("قٓ (Qāf)", "mushaf page send 518"),
            Button("الذَّاريَات (Adh-Dhāriyāt)", "mushaf page send 520"),
        ],
        [
            Button("الطُّور (Aṭ-Ṭūr)", "mushaf page send 523"),
            Button("النَّجم (An-Najm)", "mushaf page send 526"),
            Button("القَمَر (Al-Qamar)", "mushaf page send 528"),
        ],
        [
            Button("الرَّحمٰن (Ar-Raḥmān)", "mushaf page send 531"),
            Button("الوَاقِعة (Al-Wāqi‘ah)", "mushaf page send 534"),
            Button("الحدِيد (Al-Ḥadīd)", "mushaf page send 537"),
        ],
        [Button("- ↓ -", "suras 2")],
        [Button("- الرئيسيه -", "home")],
    ]
)

suras_keyboard2: Markup = Markup(
    [
        [Button("↑", "suras 1")],
        [
            Button("المُجَادلة (Al-Mujādilah)", "mushaf page send 542"),
            Button("الحَشر (Al-Ḥashr)", "mushaf page send 545"),
            Button("المُمتَحنَة (Al-Mumtaḥanah)", "mushaf page send 549"),
        ],
        [
            Button("الصَّف (Aṣ-Ṣaff)", "mushaf page send 551"),
            Button("الجُمعَة (Al-Jumu‘ah)", "mushaf page send 553"),
            Button("المُنَافِقُونَ (Al-Munāfiqūn)", "mushaf page send 554"),
        ],
        [
            Button("التغَابُن (At-Taghābun)", "mushaf page send 556"),
            Button("الطَّلَاق (Aṭ-Ṭalāq)", "mushaf page send 558"),
            Button("التَّحرِيم (At-Taḥrīm)", "mushaf page send 560"),
        ],
        [
            Button("المُلك (Al-Mulk)", "mushaf page send 562"),
            Button("القَلَم (Al-Qalam)", "mushaf page send 564"),
            Button("الحَاقة (Al-Ḥāqqah)", "mushaf page send 566"),
        ],
        [
            Button("المَعَارج (Al-Ma‘ārij)", "mushaf page send 568"),
            Button("نُوح (Nūḥ)", "mushaf page send 570"),
            Button("الجِن (Al-Jinn)", "mushaf page send 572"),
        ],
        [
            Button("المُزمل (Al-Muzzammil)", "mushaf page send 574"),
            Button("المُدثر (Al-Muddaththir)", "mushaf page send 575"),
            Button("القِيَامة (Al-Qiyāmah)", "mushaf page send 577"),
        ],
        [
            Button("الإنسَان (Al-Insān)", "mushaf page send 578"),
            Button("المُرسَلات (Al-Mursalāt)", "mushaf page send 580"),
            Button("النَّبَإ (An-Naba’)", "mushaf page send 582"),
        ],
        [
            Button("النَّازعَات (An-Nāzi‘āt)", "mushaf page send 583"),
            Button("عَبَسَ (‘Abasa)", "mushaf page send 585"),
            Button("التَّكوير (At-Takwīr)", "mushaf page send 586"),
        ],
        [
            Button("الانفِطَار (Al-Infiṭār)", "mushaf page send 587"),
            Button("المُطَففين (Al-Muṭaffifīn)", "mushaf page send 587"),
            Button("الانشِقَاق (Al-Inshiqāq)", "mushaf page send 589"),
        ],
        [
            Button("البُرُوج (Al-Burūj)", "mushaf page send 590"),
            Button("الطَّارق (Aṭ-Ṭāriq)", "mushaf page send 591"),
            Button("الأعلى (Al-A‘lā)", "mushaf page send 591"),
        ],
        [
            Button("الغَاشِية (Al-Ghāshiyah)", "mushaf page send 592"),
            Button("الفَجر (Al-Fajr)", "mushaf page send 593"),
            Button("البَلَد (Al-Balad)", "mushaf page send 594"),
        ],
        [
            Button("الشَّمس (Ash-Shams)", "mushaf page send 595"),
            Button("اللَّيل (Al-Lail)", "mushaf page send 595"),
            Button("الضُّحى (Aḍ-Ḍuḥā)", "mushaf page send 596"),
        ],
        [
            Button("الشَّرح (Ash-Sharḥ)", "mushaf page send 596"),
            Button("التِّين (At-Tīn)", "mushaf page send 597"),
            Button("العَلَق (Al-‘Alaq)", "mushaf page send 597"),
        ],
        [
            Button("القَدر (Al-Qadr)", "mushaf page send 598"),
            Button("البَينَة (Al-Bayyinah)", "mushaf page send 598"),
            Button("الزَّلزَلة (Az-Zalzalah)", "mushaf page send 599"),
        ],
        [
            Button("العَاديَات (Al-‘Ādiyāt)", "mushaf page send 599"),
            Button("القَارعَة (Al-Qāri‘ah)", "mushaf page send 600"),
            Button("التَّكاثُر (At-Takāthur)", "mushaf page send 600"),
        ],
        [
            Button("العَصر (Al-‘Aṣr)", "mushaf page send 601"),
            Button("الهُمَزة (Al-Humazah)", "mushaf page send 601"),
            Button("الفِيل (Al-Fīl)", "mushaf page send 601"),
        ],
        [
            Button("قُرَيش (Quraish)", "mushaf page send 602"),
            Button("المَاعُون (Al-Mā‘ūn)", "mushaf page send 602"),
            Button("الكَوثر (Al-Kauthar)", "mushaf page send 602"),
        ],
        [
            Button("الكافِرون (Al-Kāfirūn)", "mushaf page send 603"),
            Button("النَّصر (An-Naṣr)", "mushaf page send 603"),
            Button("المَسَد (Al-Masad)", "mushaf page send 603"),
        ],
        [
            Button("الإخلَاص (Al-Ikhlāṣ)", "mushaf page send 604"),
            Button("الفَلَق (Al-Falaq)", "mushaf page send 604"),
            Button("النَّاس (An-Nās)", "mushaf page send 604"),
        ],
    ]
)
