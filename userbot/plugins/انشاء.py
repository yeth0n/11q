from telethon.tl import functions

from .. import jmthon
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..utils.tools import create_supergroup

plugin_category = "tools"


@jmthon.ar_cmd(
    pattern="صنع (مجموعة خارقة|مجموعة عادية|قناة) ([\s\S]*)",
    command=("create", plugin_category),
    info={
        "header": "To create a private group/channel with userbot.",
        "description": "Use this cmd to create super group , normal group or channel.",
        "flags": {
            "b": "to create a private super group",
            "g": "To create a private basic group.",
            "c": "to create a private channel",
        },
        "usage": "{tr}create (b|g|c) <name of group/channel>",
        "examples": "{tr}create b catuserbot",
    },
)
async def _(event):
    "To create a private group/channel with userbot"
    type_of_group = event.pattern_match.group(1)
    group_name = event.pattern_match.group(2)
    if type_of_group == "c":
        descript = "- هذه مجموعه للتجربه فقط "
    else:
        descript = "- هذه مجموعه للتجربه فقط "
    if type_of_group == "مجموعة عادية":
        try:
            result = await event.client(
                functions.messages.CreateChatRequest(
                    users=[Config.TG_BOT_USERNAME],
                    # Not enough users (to create a chat, for example)
                    # Telegram, no longer allows creating a chat with ourselves
                    title=group_name,
                )
            )
            created_chat_id = result.chats[0].id
            result = await event.client(
                functions.messages.ExportChatInviteRequest(
                    peer=created_chat_id,
                )
            )
            await edit_or_reply(
                event, f"المجموعة `{group_name}` تم صنعها بنجاح\nالرابط: {result.link}", 
            )
        except Exception as e:
            await edit_delete(event, f"**خـطأ:**\n{str(e)}")
    elif type_of_group == "قناة":
        try:
            r = await event.client(
                functions.channels.CreateChannelRequest(
                    title=group_name,
                    about=descript,
                    megagroup=False,
                )
            )
            created_chat_id = r.chats[0].id
            result = await event.client(
                functions.messages.ExportChatInviteRequest(
                    peer=created_chat_id,
                )
            )
            await edit_or_reply(
                event,
                f"القناة `{group_name}` تم صنعها بنجاح\nالرابط: {result.link}", 
            )
        except Exception as e:
            await edit_delete(event, f"**Error:**\n{e}")
    elif type_of_group == "مجموعة خارقة":
        answer = await create_supergroup(
            group_name, event.client, Config.TG_BOT_USERNAME, descript
        )
        if answer[0] != "error":
            await edit_or_reply(
                event,
                f"المجموعة الصغيره `{group_name}`` تم صنعها بنجاح\nالرابط: {answer[0].link}",
            )
        else:
            await edit_delete(event, f"**خـطأ:**\n{answer[1]}")
    else:
        await edit_delete(event, "أرسل  .الاوامر للتعلم على كيفيه استخدام الامر")
