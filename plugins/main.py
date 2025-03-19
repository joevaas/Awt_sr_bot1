import os
import asyncio 
import time
import tempfile
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ForceReply
import ffmpeg
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from concurrent.futures import ThreadPoolExecutor
from helper.utils import progress_for_pyrogram
from plugins.details import get_video_details
from plugins.screenshot import take_screenshot
from pyrogram.errors import MessageNotModified
from config import Config, Txt

# Dictionary to store stream selection
stream_selection = {}
# Dictionary to store user-specific data like mode and files
user_modes = {}
user_files = {}

executor = ThreadPoolExecutor(max_workers=4)


# /mode command to select operation mode
@Client.on_message(filters.command("mode") & filters.user(Config.ADMIN))
async def select_mode(client, message):
    user_id = message.from_user.id
    current_mode = user_modes.get(user_id, "Remove Audio")
    
    # Create buttons with the current mode indicated by ✅
    remove_audio_button = InlineKeyboardButton(
        f"Stream extractor {'✅' if current_mode == 'Remove Audio' else ''}", 
        callback_data="remove_audio"
    )
    trim_video_button = InlineKeyboardButton(
        f"Stream Remover {'✅' if current_mode == 'Trim Video' else ''}", 
        callback_data="trim_video"
    )
    merge_video_audio_button = InlineKeyboardButton(
        f"Video+Audio {'✅' if current_mode == 'Merge Video+Audio' else ''}", 
        callback_data="merge_video_audio"
    )
    Cancel = InlineKeyboardButton("❌ Close", callback_data="close")
    await message.reply(
        "Choose an operation mode to perform task👇☘️:",
        reply_markup=InlineKeyboardMarkup([[remove_audio_button, trim_video_button], [merge_video_audio_button], [Cancel]])
    )


@Client.on_callback_query()
async def combined_callback_handler(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # Handling mode selection
    if data in ["remove_audio", "trim_video", "merge_video_audio"]:
        if data == "remove_audio":
            user_modes[user_id] = "Remove Audio"
        elif data == "trim_video":
            user_modes[user_id] = "Trim Video"
        elif data == "merge_video_audio":
            user_modes[user_id] = "Merge Video+Audio"
        
        # Update buttons based on selected mode
        remove_audio_button = InlineKeyboardButton(
            f"Stream extractor {'✅' if user_modes[user_id] == 'Remove Audio' else ''}", 
            callback_data="remove_audio"
        )
        trim_video_button = InlineKeyboardButton(
            f"Stream Remover {'✅' if user_modes[user_id] == 'Trim Video' else ''}", 
            callback_data="trim_video"
        )
        merge_video_audio_button = InlineKeyboardButton(
            f"Video+Audio {'✅' if user_modes[user_id] == 'Merge Video+Audio' else ''}", 
            callback_data="merge_video_audio"
        )
        Cancel = InlineKeyboardButton("❌ Close", callback_data="close")
        
        new_markup = InlineKeyboardMarkup([[remove_audio_button, trim_video_button], [merge_video_audio_button], [Cancel]])
        await callback_query.message.edit_reply_markup(reply_markup=new_markup)
        await callback_query.answer("Mode selected ✅.")

    elif data == "start_data":
        await callback_query.answer()
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚔️Update Channel", url="https://t.me/Anime_Warrior_Tamil"),
                InlineKeyboardButton("🛡️Support Group", url="https://t.me/+NITVxLchQhYzNGZl")
            ],
            [
                InlineKeyboardButton("📢Help", callback_data="help"),
                InlineKeyboardButton("⚡About", callback_data="about")
            ],
            [
                InlineKeyboardButton("❌Close", callback_data="close")
            ]
        ])

        await callback_query.message.edit_text(
            text=Txt.START_TXT.format(callback_query.from_user.mention),
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    
    elif data == "help":
        await callback_query.answer()
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😈 Owner", url="https://t.me/Devilo7")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close"),
                InlineKeyboardButton("⏪ Back", callback_data="start_data")
            ]
        ])
        
        await callback_query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=keyboard
        )
    
    elif data == "about":
        await callback_query.answer()
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😈 Owner", url="https://t.me/Devilo7")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close"),
                InlineKeyboardButton("⏪ Back", callback_data="start_data")
            ]
        ])  

        await callback_query.message.edit_text(
            text=Txt.ABOUT_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=keyboard
        )
        return

    elif data == "about":
        await callback_query.answer()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("😈 ᴏᴡɴᴇʀ", url="https://t.me/Devilo7")],
            [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close"),
             InlineKeyboardButton("⏪ Bᴀᴄᴋ", callback_data="start")]
        ])  

        await callback_query.message.edit_text(
            text=Txt.ABOUT_TXT.format(client.mention),
            disable_web_page_preview=True,
        )
        return

    elif data == "close":
        try:
            await callback_query.message.delete()
            await callback_query.message.reply_to_message.delete()
            await callback_query.message.continue_propagation()
        except:
            await callback_query.message.delete()
            await callback_query.message.continue_propagation()


    # Handling stream selection toggle
    elif data.startswith("toggle_"):
        index = int(data.split("_")[1])
        if user_id not in stream_selection:
            stream_selection[user_id] = [False] * 5  # Adjust length as needed
        stream_selection[user_id][index] = not stream_selection[user_id][index]
        await update_buttons(callback_query)

    elif data.startswith('audio'):
        await callback_query.answer()
        try:
            _, mapping, keyword = data.split('_')
            audio_data = DATA[keyword][int(mapping)]
            await extract_audio(client, callback_query.message, audio_data)
        except KeyError:
            await callback_query.message.edit_text("**Details Not Found**")

    elif data.startswith('subtitle'):
        await callback_query.answer()
        try:
            _, mapping, keyword = data.split('_')
            subtitle_data = DATA[keyword][int(mapping)]
            await extract_subtitle(client, callback_query.message, subtitle_data)
        except KeyError:
            await callback_query.message.edit_text("**Details Not Found**")

    elif data.startswith('cancel'):
        try:
            query_type, mapping, keyword = data.split('_')
            data = DATA[keyword][int(mapping)] 
            await clean_up(data['location'])  
            await callback_query.message.edit_text("**Cancelled...**")
            await callback_query.answer(
                "Cancelled...",
                show_alert=True
            ) 
        except:
            await callback_query.answer() 
            await callback_query.message.edit_text("**Details Not Found**")

    # Handling reverse selection
    elif data == "reverse_selection":
        if user_id in stream_selection:
            stream_selection[user_id] = [not selected for selected in stream_selection[user_id]]
            await update_buttons(callback_query)
        else:
            await callback_query.answer("No streams to reverse.")

    # Handling cancellation
    elif data == "cancel":
        await callback_query.message.edit_text("Stream selection canceled.")
        if "file_path" in stream_selection:
            os.remove(stream_selection["file_path"])
        if user_id in stream_selection:
            del stream_selection[user_id]

    # Handling completion
    elif data == "done":
        await callback_query.message.edit_text("⏳ Processing your video...")
        await process_video(client, callback_query.message, user_id)

async def update_buttons(callback_query):
    # Function to update buttons based on stream selection (customize this based on your needs)
    await callback_query.answer("Buttons updated.")

# Handle incoming video or document files
@Client.on_message(filters.video | filters.document & filters.incoming & filters.user(Config.ADMIN))
async def handle_video(client, message: Message):
    user_id = message.from_user.id
    current_mode = user_modes.get(user_id, "Remove Audio")
    
    # Process based on current mode
    if current_mode == "Remove Audio":
        await stream_remove(client, message)
    elif current_mode == "Trim Video":
        await stream_remove(client, message)
    elif current_mode == "Merge Video+Audio":
        # Download video and store path in user_files
        msg = await message.reply("📥Downloading your video...")
        try:
            video_file = await message.download(
                progress=progress_for_pyrogram,
                progress_args=("📥Downloading your Video...", msg, time.time())
            )
        except Exception as e:
            print(e)
            return await ms.edit(f"An error occurred while downloading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)

        user_files[user_id] = {"video": video_file, "message": message}

        await msg.edit_text("Now send an audio File 🎵 to merge .")
        await asyncio.sleep(20)
        await msg.delete()

# Handle incoming audio files
@Client.on_message(filters.audio | filters.voice)
async def handle_audio(client, message: Message):
    user_id = message.from_user.id
    
    if "video" in user_files.get(user_id, {}):
        msg = await message.reply("📥Downloading Your audio File...")
        audio_file = await message.download(progress=progress_for_pyrogram, progress_args=("📥Downloading your audio file...", msg, time.time()))
        await msg.edit_text("Audio Downloaded Successfully ✅")
        await asyncio.sleep(1)
        await msg.delete()
        user_files[user_id]["audio"] = audio_file
        
        # Prompt user for the new name
        l = await message.reply("Please enter a new file name Without (extinction) :", reply_markup=ForceReply())
        await asyncio.sleep(20)
        await l.delete()
    else:
        await msg.edit_text("Please upload a video first, then send the audio to merge.")

# Handle the reply with the new name for the merged file
@Client.on_message(filters.reply & filters.text)
async def handle_name_reply(client, message: Message):
    user_id = message.from_user.id
    await asyncio.sleep(1)
    await message.delete()
    if user_id in user_files and "video" in user_files[user_id] and "audio" in user_files[user_id]:
        new_name = message.text
        await merge_video_audio(client, user_files[user_id]["message"], new_name)
    else:
        await message.reply("Please upload both video and audio files before setting a name.")

# Function to merge video and audio
async def merge_video_audio(client, message, new_name):
    user_id = message.from_user.id
    video_path = user_files[user_id]["video"]
    audio_path = user_files[user_id]["audio"]
    output_path = f"{new_name}.mkv"
    
    try:
        command = [
            'ffmpeg', '-y',              # Overwrite without asking
    '-i', video_path,            # Input video
    '-i', audio_path,            # Input audio
    '-c:v', 'copy',              # Copy video without re-encoding
    '-c:a', 'copy',              # Use audio from the new audio file
    '-c:s', 'copy',              # Copy subtitle stream(s) without re-encoding
    '-map', '0:v',               # Map video from the first input (video file)
    '-map', '1:a',               # Map audio from the second input (audio file)
    '-map', '2:s?',              # Map subtitles from the video file (if available)
    output_path  # Output file
        ]
        
        # Execute the FFmpeg command
        msg = await message.reply("Merging Video and Audio...")
        process = await asyncio.create_subprocess_exec(*command)
        await process.communicate()
        details = get_video_details(output_path)
        duration = details.get('duration', 0)
        title = details.get('title', 'Untitled')
        artist = details.get('artist', 'Unknown Artist')
        
        
        user_mention = f"[{message.from_user.first_name}](tg://user?id={user_id})"
        caption = (
            f"File Name: {new_name}.\n"
            f"Uploaded by: {user_mention}\n"
            f"Title: {title}\n"
            f"Artist: {artist}\n"
            f"Duration: {round(float(duration) / 60, 2)} minutes."
        )
        base_name = os.path.basename(output_path)
        loop = asyncio.get_running_loop()
        # Take a screenshot at the 5-second mark (adjust the timestamp as needed)
        thumbnail_path = tempfile.mktemp(suffix=f"_{base_name}_thumb.jpg")
        thumbnail = await loop.run_in_executor(executor, take_screenshot, output_path, 5, thumbnail_path)

        # Check if the thumbnail was successfully created
        if not os.path.exists(thumbnail_path):
            thumbnail_path = None


        uploader = await msg.edit_text("💫 Ready to upload merged video...")
        await client.send_document(
            chat_id=message.chat.id,
            caption=caption,
            document=output_path,
            thumb=thumbnail_path,
            progress=progress_for_pyrogram,
            progress_args=("📤Uploading Your Video file...", uploader, time.time())

        )
        
        await uploader.delete()
    except Exception as e:
        await msg.edit(f"Error: {e}")
    finally:
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(output_path)


###################################     Stream Remover      ##########################################

async def stream_remove(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name  
    # Send a message indicating download status
    status_message = await message.reply("📥 Downloading video file...")

    file_path = await message.download(progress=progress_for_pyrogram, progress_args=("📥 Downloading video file...", status_message, time.time()))
    # Update the status message to indicate download completion
    duration = extract_video_duration(file_path)

    await status_message.edit_text("Analyzing the streams from your file 🎆...")

    # Retrieve streams info from the video using ffmpeg
    streams = ffmpeg.probe(file_path)["streams"]

    # Create inline buttons for each stream
    buttons = []
    for index, stream in enumerate(streams):
        lang = stream.get("tags", {}).get("language")
        if lang is None or not lang.isalpha():  # Validate the language code
            lang = "unknown"  # Default to 'unknown' if invalid

        codec_type = stream["codec_type"]
        button_text = f"{index + 1} {lang} {'🎵' if codec_type == 'audio' else '📜'}"
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"toggle_{index}")])

    buttons.append([InlineKeyboardButton("Reverse Selection", callback_data="reverse_selection")])
    buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel"), InlineKeyboardButton("Done", callback_data="done")])

    # Send the buttons to the user
    await status_message.edit_text(
        "Now Select The Streams You Want To Add From Media.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    # Store initial state
    stream_selection[message.chat.id] = [False] * len(streams)
    stream_selection["file_path"] = file_path
    stream_selection["duration"] = duration
    stream_selection["filename"] = filename
    stream_selection["status_message"] = status_message


async def update_buttons(callback_query):
    user_id = callback_query.message.chat.id
    message = callback_query.message
    streams = ffmpeg.probe(stream_selection["file_path"])["streams"]
    buttons = []

    for index, selected in enumerate(stream_selection[user_id]):
        lang = streams[index].get("tags", {}).get("language")
        if lang is None or not lang.isalpha():  # Validate the language code
            lang = "unknown"  # Default to 'unknown' if invalid

        codec_type = streams[index]["codec_type"]
        status = "✅" if selected else ""
        button_text = f"{index + 1} {lang} {'🎵' if codec_type == 'audio' else '📜'} {status}"
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"toggle_{index}")])

    buttons.append([InlineKeyboardButton("Reverse Selection", callback_data="reverse_selection")])
    buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel"), InlineKeyboardButton("Done", callback_data="done")])

    await message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

async def process_video(client, message, user_id):
    selected_streams = stream_selection[user_id]
    file_path = stream_selection["file_path"]
    duration = stream_selection["duration"]
    filename = stream_selection["filename"]
    status_message = stream_selection["status_message"]
    output_file = "output_" + os.path.basename(file_path)
    user_mention = f"[{message.from_user.first_name}](tg://user?id={user_id})"
    
    caption = f"Here is your Stream Removed  file 🗃️🫡 \n File Name : {filename}\n Uploaded by: {user_mention}"
    

    # Create a list of "-map" arguments
    map_args = []
    for index, keep in enumerate(selected_streams):
        if not keep:
            map_args.extend(["-map", f"-0:{index}"])

    # Run FFmpeg command
    process = await asyncio.create_subprocess_exec(
    "ffmpeg",
    "-i", file_path,            # Input file
    "-map", "0",                # Map all streams (video, audio, etc.)
    "-map", "1:s?",             # Map subtitle streams if they exist
    "-c", "copy",               # Copy streams without re-encoding
    *map_args,                  # Additional arguments
    "-bufsize", "10M",          # Buffer size
    output_file                 # Output file
)

    await process.communicate()

    thumbnail_path = "thumbnail.jpg"
    # Take a screenshot at the halfway point
    base_name = os.path.basename(output_file)
    loop = asyncio.get_running_loop()
    # Take a screenshot at the 5-second mark (adjust the timestamp as needed)
    thumbnail_path = tempfile.mktemp(suffix=f"_{base_name}_thumb.jpg")
    thumbnail = await loop.run_in_executor(executor, take_screenshot, output_file, 5, thumbnail_path)

    # Ensure the thumbnail exists
    if not os.path.exists(thumbnail_path):
        thumbnail_path = None

    # Update status to indicate upload
    await status_message.edit_text("📤 Uploading the processed video...")

    # Upload the processed video with the thumbnail and progress
    await client.send_document(
        chat_id=message.chat.id,
        document=output_file,
        caption=caption,
        thumb=thumbnail_path,
        progress=progress_for_pyrogram,
        progress_args=("📤 Uploading your video file...", status_message, time.time())
    )
    

# Ensure cleanup after upload
    os.remove(file_path)
    os.remove(output_file)
    if thumbnail_path:
        os.remove(thumbnail_path)

    del stream_selection[user_id]

    # Update the status to indicate completion
    await status_message.edit_text("✅ Processing and upload complete!")

def extract_video_duration(file_path):
    """Extracts the duration of the video."""
    metadata = extractMetadata(createParser(file_path))
    duration = 0
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    return duration
