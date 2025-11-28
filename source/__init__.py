from pyrogram import Client
from source.helpers import hafs_db, pages_db
import config
import pyromod

app: Client = Client(
    "QuraanBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="source/plugins"),
)
