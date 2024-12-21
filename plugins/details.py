from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

def get_video_details(file_loc):
    title = None
    artist = None
    thumb = None
    duration = 0

    metadata = extractMetadata(createParser(file_loc))
    if metadata:
        if metadata.has("title"):
            title = metadata.get("title")
        if metadata.has("artist"):
            artist = metadata.get("artist")
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds

    return {
        "title": title,
        "artist": artist,
        "thumb": thumb,
        "duration": duration
    }

def get_audio_details(file_loc):
    title = None
    artist = None
    thumb = None
    duration = 0

    metadata = extractMetadata(createParser(file_loc))
    if metadata:
        if metadata.has("title"):
            title = metadata.get("title")
        if metadata.has("artist"):
            artist = metadata.get("artist")
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds

    return {
        'title': title,
        'artist': artist,
        'duration': duration,
        'thumb': thumb
    }
