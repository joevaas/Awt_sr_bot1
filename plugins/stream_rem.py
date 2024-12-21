
import time
import json
import time
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from helper.utils import progress_for_pyrogram
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import shlex
import asyncio
from typing import Tuple
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
DATA = {}

async def execute(cmnd: str) -> Tuple[str, str, int, int]:
    cmnds = shlex.split(cmnd)
    process = await asyncio.create_subprocess_exec(
        *cmnds,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)

async def clean_up(input1, input2=None):
    try:
        os.remove(input1)
    except:
        pass
    try:
        os.remove(input2)
    except:
        pass        

async def download_file(client, message):
    msg = await message.reply_text("Downloading your file 📥...")
    c_time = time.time()

    try:
        download_location = await message.download(
            progress=progress_for_pyrogram,
            progress_args=(
                "**Downloading your file 📥...**",
                msg,
                c_time
            )
        )
    except Exception as e:
        print(e)
        return await msg.edit(f"An error occurred while downloading.")
    
    try:
        await msg.edit_text("Finding the streams 🔍....")
        output = await execute(f"ffprobe -hide_banner -show_streams -print_format json '{download_location}'")
    
        if not output:
            await clean_up(download_location)
            await msg.edit_text("Some Error Occurred while Fetching Details...")
            return

        details = json.loads(output[0])
        buttons = []
        DATA[f"{message.chat.id}-{message.id}"] = {}
        for stream in details["streams"]:
            mapping = stream["index"]
            stream_name = stream["codec_name"]
            stream_type = stream["codec_type"]
            if stream_type in ("audio", "subtitle"):
                pass
            else:
                continue
            try: 
                lang = stream["tags"]["language"]
            except:
                lang = mapping
        
            DATA[f"{message.chat.id}-{message.id}"][int(mapping)] = {
                "map": mapping,
                "name": stream_name,
                "type": stream_type,
                "lang": lang,
                "location": download_location
            }
            buttons.append([
                InlineKeyboardButton(
                    f"{stream_type.upper()} - {str(lang).upper()}", f"{stream_type}_{mapping}_{message.chat.id}-{message.id}"
                )
            ])

        buttons.append([
            InlineKeyboardButton("CANCEL", f"cancel_{mapping}_{message.chat.id}-{message.id}")
        ])    

        await msg.edit_text(
            "**Select the Stream to be Extracted👇...**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        print(e)
        await msg.edit(f"An error occurred during processing.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)
    finally:
        # Call extract_audio function only when needed and when data is available
        await extract_audio(client, message, DATA[f"{message.chat.id}-{message.id}"])

async def extract_audio(client, message, data):
    await message.edit_text("Extracting Stream from file...")

    dwld_loc = data['location']
    out_loc = f"{data['location']}.mp3"

    # Use copy codec if extracting without re-encoding
    codec_option = "-c copy" if data['name'] == "mp3" else ""

    # Run FFmpeg command with optimized parameters
    command = f"ffmpeg -hide_banner -loglevel error -i '{dwld_loc}' -map 0:{data['map']} {codec_option} '{out_loc}' -y"
    
    # Execute FFmpeg asynchronously
    out, err, rcode, pid = await execute(command)
    
    if rcode != 0:
        await message.edit_text("**Error Occurred. See Logs for more info.**")
        print(err)
        await clean_up(dwld_loc, out_loc)
        return

    await clean_up(dwld_loc)
    await upload_audio(client, message, out_loc)


async def extract_subtitle(client, message, data):
    await message.edit_text("Extracting Stream from file")

    dwld_loc = data['location']
    out_loc = data['location'] + ".srt"   

    out, err, rcode, pid = await execute(f"ffmpeg -i '{dwld_loc}' -map 0:{data['map']} '{out_loc}' -y")
    if rcode != 0:
        await message.edit_text("**Error Occured. See Logs for more info.**")
        print(err)
        await clean_up(dwld_loc, out_loc)
        return

    await clean_up(dwld_loc)  
    await upload_subtitle(client, message, out_loc)



async def upload_audio(client, message, file_loc):
    msg = await message.edit_text("Uploading Extracted audio 📤...")

    title = None
    artist = None
    thumb = None
    duration = 0

    metadata = extractMetadata(createParser(file_loc))
    if metadata and metadata.has("title"):
        title = metadata.get("title")
    if metadata and metadata.has("artist"):
        artist = metadata.get("artist")
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds

    file_size_bytes = os.path.getsize(file_loc)
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to MB
    c_time = time.time()
    user_mention = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"  # Corrected line
    caption = (
        f"Uploaded by: {user_mention}\n"
        f"Size: {round(file_size_mb, 2)} MB"
    )

    try:
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file_loc,
            thumb=thumb,
            title=title,
            performer=artist,
            caption=caption,
            duration=duration,
            progress=progress_for_pyrogram,
            progress_args=(
                "**Uploading Extracted audio 📤...**",
                msg,
                c_time
            )
        )
        await client.send_audio(
            chat_id=Config.DUMP_CHANNEL_ID,
            caption=caption,
            audio=file_loc,
            thumb=thumb,
            duration=duration
        )
    except Exception as e:
        print(e)     
        await msg.edit_text("**Some Error Occurred. See Logs for More Info.**")   
        return

    await msg.delete()
    await clean_up(file_loc)    


async def upload_subtitle(client, message, file_loc):

    msg = await message.edit_text("Uploading Extracted subtitle 📤...")

    c_time = time.time() 

    try:
        await client.send_document(
            chat_id=message.chat.id,
            document=file_loc,
            caption="**Awt_bots**",
            progress=progress_for_pyrogram,
            progress_args=(
                "**Uploading Extracted subtitle 📤...**",
                msg,
                c_time
            )
        )
        await client.send_document(
            chat_id=Config.DUMP_CHANNEL_ID,
            caption=caption,
            document=file_loc,
        )
    except Exception as e:
        print(e)     
        await msg.edit_text("**Some Error Occurred. See Logs for More Info.**")   
        return

    await msg.delete()
    await clean_up(file_loc)        
    
