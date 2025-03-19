import os, time

class Config(object):
    # Audio-_edit_bot client Config 
    API_ID = os.getenv("API_ID", "21740783")
    API_HASH = os.getenv("API_HASH", "a5dc7fec8302615f5b441ec5e238cd46")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8192707394:AAF7Qw97L5HqLzXEoiDST3t-Rk1yEUHZXZE")
    
    # Database config
    DB_NAME = os.environ.get("DB_NAME", "boyrokey00")     
    DB_URL  = os.environ.get("DB_URL", "mongodb+srv://boyrokey00:rajan123@cluster0.4fhuu.mongodb.net/")
    
    # Other configs
    BOT_UPTIME  = time.time()
    DUMP_CHANNEL_ID = int(os.environ.get("DUMP_CHANNEL_ID", "0"))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    START_PIC   = os.environ.get("START_PIC", "https://telegra.ph/file/feb6dd0a1cb8576943c0f.jpg")
    
    # Web response configuration     
    WEBHOOK = bool(os.environ.get("WEBHOOK", "True"))
    
    ADMIN   = [6693549185]  # Closed the square bracket here
    
class Txt(object):
    
    START_TXT = """Hello {} Friend I am An Advanced Triple Usage bot. I have special features like "stream extract" and "Video merger."
    
</a>"\n Bot Is Made By @Anime_Warrior_Tamil"</b>"""
    
    ABOUT_TXT = f"""<b>😈 My Name :</b> <a href='https://t.me/Gjjbsrijjb_bot'>Triple Usage Bot ⚡</a>
<b>📝 Language :</b> <a href='https://python.org'>Python 3</a>
<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram 2.0</a>
<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a>
<b>📢 Channel :</b> <a href='https://t.me/Anime_Warrior_Tamil'>AWT BOTS</a>
<b>🛡️ :</b> <a href='https://t.me/+NITVxLchQhYzNGZl'>AWT Developer</a>
    
<b>😈 Bot Made By :</b> @AWT_Bot_Developer"""


    MEN = """ for {}"""
    HELP_TXT = """
<b><u>Video Editor Bot Commands</u></b>
  
<b>•»</b> /start Use this command to check if the bot is alive ✅.
<b>•»</b> /mode Use this Command to Change the Operation 👍

✏️ <b><u>How To Use the Bot</u></b>

<b>•»</b> Simple select the mode then Send a File 🗃️.          

ℹ️ Any other help, contact: <a href=https://t.me/AWT_bots_developer>Bot Developer</a>
"""

    # ⚠️ Don't Remove Our Credits @ILLGELA_DEVELOPER🙏🥲
    DEV_TXT = """hiiiiiiiiiii"""
    
    PROGRESS_BAR = """\n
<b>📁 Size</b> : {1} | {2}
<b>⏳️ Done</b> : {0}%
<b>🚀 Speed</b> : {3}/s
<b>⏰️ ETA</b> : {4} """
