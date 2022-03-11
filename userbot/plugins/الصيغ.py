# by @mrconfused (@sandy1709)
import asyncio
import base64
import io
import logging
import os
import time
from datetime import datetime
from io import BytesIO
from shutil import copyfile

import fitz
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pymediainfo import MediaInfo
from telethon import types
from telethon.errors import PhotoInvalidDimensionsError
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.tl.functions.messages import SendMediaRequest
from telethon.utils import get_attributes

from userbot import jmthon

from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import media_type, progress, thumb_from_audio
from ..helpers.functions import (
    convert_toimage,
    convert_tosticker,
    invert_frames,
    l_frames,
    r_frames,
    spin_frames,
    ud_frames,
    vid_to_gif,
)
from ..helpers.utils import _jmthontools, _jmthonutils, _format, parse_pre, reply_id
from . import make_gif

plugin_category = "misc"


if not os.path.isdir("./temp"):
    os.makedirs("./temp")


LOGS = logging.getLogger(__name__)
PATH = os.path.join("./temp", "temp_vid.mp4")

thumb_loc = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")



@jmthon.ar_cmd(
    pattern="تحويل لدائري ?((-)?s)?$",
    command=("تحويل لدائري", plugin_category),
    info={
        "header": "To make circular video note/sticker.",
        "description": "crcular video note supports atmost 60 sec so give appropariate video.",
        "usage": "{tr}circle <reply to video/sticker/image>",
    },
)
async def video_jmthonfile(event):  # sourcery no-metrics
    "To make circular video note."
    reply = await event.get_reply_message()
    args = event.pattern_match.group(1)
    jmthonid = await reply_id(event)
    if not reply or not reply.media:
        return await edit_delete(event, "**- عذرا عليك الرد على ملصق او صورة او فيديو عادي لتحويله**")
    mediatype = media_type(reply)
    if mediatype == "Round Video":
        return await edit_delete(
            event,
            "هل انت غبي ام غبي  ؟ لقد قمت بالرد على فيديو دائري لتحويله لفيديو دائري!؟ ",
        )
    if mediatype not in ["Photo", "Audio", "Voice", "Gif", "Sticker", "Video"]:
        return await edit_delete(event, "عذرا عليك الرد على ملصق او صورة او متحركه او فيديو عادي لتحويله**")
    flag = True
    jmthonevent = await edit_or_reply(event, "-**جارِ التحويل الى فيديو دائري انتظر قليلا**")
    jmthonfile = await reply.download_media(file="./temp/")
    if mediatype in ["Gif", "Video", "Sticker"]:
        if not jmthonfile.endswith((".webp")):
            if jmthonfile.endswith((".tgs")):
                hmm = await make_gif(jmthonevent, jmthonfile)
                os.rename(hmm, "./temp/circle.mp4")
                jmthonfile = "./temp/circle.mp4"
            media_info = MediaInfo.parse(jmthonfile)
            aspect_ratio = 1
            for track in media_info.tracks:
                if track.track_type == "Video":
                    aspect_ratio = track.display_aspect_ratio
                    height = track.height
                    width = track.width
            if aspect_ratio != 1:
                crop_by = min(height, width)
                await _jmthonutils.runcmd(
                    f'ffmpeg -i {jmthonfile} -vf "crop={crop_by}:{crop_by}" {PATH}'
                )
            else:
                copyfile(jmthonfile, PATH)
            if str(jmthonfile) != str(PATH):
                os.remove(jmthonfile)
            try:
                jmthonthumb = await reply.download_media(thumb=-1)
            except Exception as e:
                LOGS.error(f"circle - {e}")
    elif mediatype in ["Voice", "Audio"]:
        jmthonthumb = None
        try:
            jmthonthumb = await reply.download_media(thumb=-1)
        except Exception:
            jmthonthumb = os.path.join("./temp", "thumb.jpg")
            await thumb_from_audio(jmthonfile, jmthonthumb)
        if jmthonthumb is not None and not os.path.exists(jmthonthumb):
            jmthonthumb = os.path.join("./temp", "thumb.jpg")
            copyfile(thumb_loc, jmthonthumb)
        if (
            jmthonthumb is not None
            and not os.path.exists(jmthonthumb)
            and os.path.exists(thumb_loc)
        ):
            flag = False
            jmthonthumb = os.path.join("./temp", "thumb.jpg")
            copyfile(thumb_loc, jmthonthumb)
        if jmthonthumb is not None and os.path.exists(jmthonthumb):
            await _jmthonutils.runcmd(
                f"""ffmpeg -loop 1 -i {jmthonthumb} -i {jmthonfile} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -vf \"scale=\'iw-mod (iw,2)\':\'ih-mod(ih,2)\',format=yuv420p\" -shortest -movflags +faststart {PATH}"""
            )
            os.remove(jmthonfile)
        else:
            os.remove(jmthonfile)
            return await edit_delete(
                jmthonevent, "**- لم يتم العثور على غلاف من الاغنيه لتحويله الى فيديو دائري**", 5
            )
    if mediatype in [
        "Voice",
        "Audio",
        "Gif",
        "Video",
        "Sticker",
    ] and not jmthonfile.endswith((".webp")):
        if os.path.exists(PATH):
            c_time = time.time()
            attributes, mime_type = get_attributes(PATH)
            ul = io.open(PATH, "rb")
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, jmthonevent, c_time, "Uploading....")
                ),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type="video/mp4",
                attributes=[
                    types.DocumentAttributeVideo(
                        duration=0,
                        w=1,
                        h=1,
                        round_message=True,
                        supports_streaming=True,
                    )
                ],
                force_file=False,
                thumb=await event.client.upload_file(jmthonthumb) if jmthonthumb else None,
            )
            sandy = await event.client.send_file(
                event.chat_id,
                media,
                reply_to=jmthonid,
                video_note=True,
                supports_streaming=True,
            )

            if not args:
                await _jmthonutils.unsavegif(event, sandy)
            os.remove(PATH)
            if flag:
                os.remove(jmthonthumb)
        await jmthonevent.delete()
        return
    data = reply.photo or reply.media.document
    img = io.BytesIO()
    await event.client.download_file(data, img)
    im = Image.open(img)
    w, h = im.size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(im, (0, 0))
    m = min(w, h)
    img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((10, 10, w - 10, h - 10), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    img = ImageOps.fit(img, (w, h))
    img.putalpha(mask)
    im = io.BytesIO()
    im.name = "jmthon.webp"
    img.save(im)
    im.seek(0)
    await event.client.send_file(event.chat_id, im, reply_to=jmthonid)
    await jmthonevent.delete()


@jmthon.ar_cmd(
    pattern="تحويل صورة$",
    command=("تحويل صورة", plugin_category),
    info={
        "header": "Reply this command to a sticker to get image.",
        "description": "This also converts every media to image. that is if video then extracts image from that video.if audio then extracts thumb.",
        "usage": "{tr}stoi",
    },
)
async def _(event):
    "Sticker to image Conversion."
    reply_to_id = await reply_id(event)
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(
            event, "- عليك الرد على ملصق/فيديو لتحويلها الى ملصق"
        )
    output = await _jmthontools.media_to_pic(event, reply)
    if output[1] is None:
        return await edit_delete(
            output[0], "- هل هذا ملصق  ؟  عليك الرد على الملصق فقط"
        )
    meme_file = convert_toimage(output[1])
    await event.client.send_file(
        event.chat_id, meme_file, reply_to=reply_to_id, force_document=False
    )
    await output[0].delete()


@jmthon.ar_cmd(
    pattern="تحويل ملصق$",
    command=("تحويل ملصق", plugin_category),
    info={
        "header": "Reply this command to image to get sticker.",
        "description": "This also converts every media to sticker. that is if video then extracts image from that video. if audio then extracts thumb.",
        "usage": "{tr}itos",
    },
)
async def _(event):
    "Image to Sticker Conversion."
    reply_to_id = await reply_id(event)
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(
            event, "- عليك الرد على الصورة لتحويلها الى ملصق"
        )
    output = await _jmthontools.media_to_pic(event, reply)
    if output[1] is None:
        return await edit_delete(
            output[0], "- هل هذه صورة  ؟  عليك الرد على الصور فقط"
        )
    meme_file = convert_tosticker(output[1])
    await event.client.send_file(
        event.chat_id, meme_file, reply_to=reply_to_id, force_document=False
    )
    await output[0].delete()


@jmthon.ar_cmd(
    pattern="لملف ([\s\S]*)",
    command=("لملف", plugin_category),
    info={
        "header": "Text to file.",
        "description": "Reply this command to a text message to convert it into file with given name.",
        "usage": "{tr}ttf <file name>",
    },
)
async def get(event):
    "text to file conversion"
    name = event.text[5:]
    if name is None:
        await edit_or_reply(event, "يجب عليك الرد على بعض النص بـ `.كتابة <اسم الملف>`")
        return
    m = await event.get_reply_message()
    if m.text:
        with open(name, "w") as f:
            f.write(m.message)
        await event.delete()
        await event.client.send_file(event.chat_id, name, force_document=True)
        os.remove(name)
    else:
        await edit_or_reply(event, "يجب عليك الرد على بعض النص بـ `.كتابة <اسم الملف>`")


@jmthon.ar_cmd(
    pattern="قراءة$",
    command=("قراءة", plugin_category))
async def get(event):
    "File to text message conversion."
    reply = await event.get_reply_message()
    mediatype = media_type(reply)
    if mediatype != "Document":
        return await edit_delete(
            event, "**- عذرا عليك الرد على الملفات فقط"
        )
    file_loc = await reply.download_media()
    file_content = ""
    try:
        with open(file_loc) as f:
            file_content = f.read().rstrip("\n")
    except UnicodeDecodeError:
        pass
    except Exception as e:
        LOGS.info(e)
    if file_content == "":
        try:
            with fitz.open(file_loc) as doc:
                for page in doc:
                    file_content += page.getText()
        except Exception as e:
            if os.path.exists(file_loc):
                os.remove(file_loc)
            return await edit_delete(event, f"**خطأ**\n__{e}__")
    await edit_or_reply(
        event,
        file_content,
        parse_mode=parse_pre,
        aslink=True,
        noformat=True,
        linktext="**يسمح التلجرام فقط بـ 4096 حرفًا في رسالة واحدة. لكن الملف يحتوي على أكثر من ذلك بكثير. لذلك لصقها على موقع معين \nالرابط :**",
    )
    if os.path.exists(file_loc):
        os.remove(file_loc)

@jmthon.ar_cmd(
    pattern="تحويل (mp3|voice)",
    command=("تحويل", plugin_category),
    info={
        "header": "Converts the required media file to voice or mp3 file.",
        "usage": [
            "{tr}nfc mp3",
            "{tr}nfc voice",
        ],
    },
)
async def _(event):
    "Converts the required media file to voice or mp3 file."
    if not event.reply_to_msg_id:
        await edit_or_reply(event, "**⌯︙يـجب الـرد على اي مـلف اولا ⚠️**")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await edit_or_reply(event, "**⌯︙يـجب الـرد على اي مـلف اولا ⚠️**")
        return
    input_str = event.pattern_match.group(1)
    event = await edit_or_reply(event, "⌯︙يتـم التـحويل انتـظر قليـلا ⏱")
    try:
        start = datetime.now()
        c_time = time.time()
        downloaded_file_name = await event.client.download_media(
            reply_message,
            Config.TMP_DOWNLOAD_DIRECTORY,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, event, c_time, "trying to download")
            ),
        )
    except Exception as e:
        await event.edit(str(e))
    else:
        end = datetime.now()
        ms = (end - start).seconds
        await event.edit(
            "⌯︙التحـميل الى `{}` في {} من الثواني ⏱".format(downloaded_file_name, ms)
        )
        new_required_file_name = ""
        new_required_file_caption = ""
        command_to_run = []
        voice_note = False
        supports_streaming = False
        if input_str == "voice":
            new_required_file_caption = "voice_" + str(round(time.time())) + ".opus"
            new_required_file_name = (
                Config.TMP_DOWNLOAD_DIRECTORY + "/" + new_required_file_caption
            )
            command_to_run = [
                "ffmpeg",
                "-i",
                downloaded_file_name,
                "-map",
                "0:a",
                "-codec:a",
                "libopus",
                "-b:a",
                "100k",
                "-vbr",
                "on",
                new_required_file_name,
            ]
            voice_note = True
            supports_streaming = True
        elif input_str == "mp3":
            new_required_file_caption = "mp3_" + str(round(time.time())) + ".mp3"
            new_required_file_name = (
                Config.TMP_DOWNLOAD_DIRECTORY + "/" + new_required_file_caption
            )
            command_to_run = [
                "ffmpeg",
                "-i",
                downloaded_file_name,
                "-vn",
                new_required_file_name,
            ]
            voice_note = False
            supports_streaming = True
        else:
            await event.edit("⌯︙غـير مدعوم ❕")
            os.remove(downloaded_file_name)
            return
        process = await asyncio.create_subprocess_exec(
            *command_to_run,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
        os.remove(downloaded_file_name)
        if os.path.exists(new_required_file_name):
            force_document = False
            await event.client.send_file(
                entity=event.chat_id,
                file=new_required_file_name,
                allow_cache=False,
                silent=True,
                force_document=force_document,
                voice_note=voice_note,
                supports_streaming=supports_streaming,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, event, c_time, "trying to upload")
                ),
            )
            os.remove(new_required_file_name)
            await event.delete()