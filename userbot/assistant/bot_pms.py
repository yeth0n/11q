import re
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union

from telethon import Button, events
from telethon.errors import UserIsBlockedError
from telethon.events import CallbackQuery, StopPropagation
from telethon.utils import get_display_name
from userbot import BOTLOG, BOTLOG_CHATID, jmthon

from ..Config import Config
from ..core.inlinebot import *

from userbot import Config, jmthon

from ..core import check_owner, pool
from ..core.logger import logging
from ..core.session import tgbot
from ..helpers import reply_id
from ..helpers.utils import _format
from ..sql_helper.bot_blacklists import check_is_black_list
from ..sql_helper.bot_pms_sql import (
    add_user_to_db,
    get_user_id,
    get_user_logging,
    get_user_reply,
)
from ..sql_helper.bot_starters import add_starter_to_db, get_starter_details
from ..sql_helper.globals import delgvar, gvarstatus
#from . import BOTLOG, BOTLOG_CHATID
from userbot.assistant.botmanagers import ban_user_from_bot

LOGS = logging.getLogger(__name__)

plugin_category = "bot"
botusername = Config.TG_BOT_USERNAME


class FloodConfig:
    BANNED_USERS = set()
    USERS = defaultdict(list)
    MESSAGES = 3
    SECONDS = 6
    ALERT = defaultdict(dict)
    AUTOBAN = 10


async def check_bot_started_users(user, event):
    if user.id == Config.OWNER_ID:
        return
    check = get_starter_details(user.id)
    if check is None:
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        notification = f"👤 {_format.mentionuser(user.first_name , user.id)} has started me.\
                \n**الايدي: **`{user.id}`\
                \n**الاسم: **{get_display_name(user)}"
    else:
        start_date = check.date
        notification = f"👤 {_format.mentionuser(user.first_name , user.id)} has restarted me.\
                \n**الايدي: **`{user.id}`\
                \n**الاسم: **{get_display_name(user)}"
    try:
        add_starter_to_db(user.id, get_display_name(user), start_date, user.username)
    except Exception as e:
        LOGS.error(str(e))
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, notification)


@jmthon.bot_cmd(
    pattern=f"^/start({botusername})?([\s]+)?$",
    incoming=True,
    func=lambda e: e.is_private,
)
async def bot_start(event):
    chat = await event.get_chat()
    user = await jmthon.get_me()
    if check_is_black_list(chat.id):
        return
    reply_to = await reply_id(event)
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{user.first_name}](tg://user?id={user.id})"
    first = chat.first_name
    last = chat.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{chat.username}" if chat.username else mention
    userid = chat.id
    my_first = user.first_name
    my_last = user.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{user.username}" if user.username else my_mention
    if chat.id != Config.OWNER_ID:
        customstrmsg = gvarstatus("START_TEXT") or None
        if customstrmsg is not None:
            start_msg = customstrmsg.format(
                mention=mention,
                first=first,
                last=last,
                fullname=fullname,
                username=username,
                userid=userid,
                my_first=my_first,
                my_last=my_last,
                my_fullname=my_fullname,
                my_username=my_username,
                my_mention=my_mention,
            )
        else:
            start_msg = f"اهلا ! 👤{mention},\
                        \nانا هو البوت المساعد الخاص بـ {my_mention}.\
                        \nيمكنك التواصل مع مالك الحسابمن هنا.\
                        \n\nتم صنع بواسطه سوري [جمثون](https://t.me/jmthon)"
        buttons = [
            (
                Button.url("Repo", "https://github.com/JMTHON-AR/jmthon"),
                Button.url(
                    "Deploy",
                    "https://dashboard.heroku.com/new?button-url=https%3A%2F%2Fgithub.com%2FJMTHON-AR%2Fjmthon&template=https%3A%2F%2Fgithub.com%2FJMTHON-AR%2Fjmthon",
                ),
            )
        ]
    else:
        start_msg = "اهلا بك مطور البوت\
            \nكيف يمكنني مساعدتك؟"
        buttons = [
                [
                    Button.url("• السورس •", "https://t.me/jmthon"),
                    Button.inline("• لوحة التحكم •", data="gibcmd"),
                ],
                [
                    Button.inline("• دخول عبر تيرمكس •", data="jm_hhack"),
                ],
            ]
    try:
        await event.client.send_message(
            chat.id,
            start_msg,
            link_preview=False,
            buttons=buttons,
            reply_to=reply_to,
        )
    except Exception as e:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**خطأ**\nهنالك خطأ اثناء محاولة مستخدم بتشغيل بوتك.\\\x1f                \n`{e}`",
            )

    else:
        await check_bot_started_users(chat, event)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"gibcmd")))
async def users(event):
    await event.delete()
    rorza = "**▾∮ قائـمه اوامر المطور **\n* تستخدم في ↫ `{Config.TG_BOT_USERNAME} ` فقط! `\n**⍣ⵧⵧⵧⵧⵧᴊᴍᴛʜᴏɴⵧⵧⵧⵧⵧ⍣**\n\n*الامر  ( اذاعة  ) \n- لعمل اذاعة لمستخدمي البوت ◛ ↶\n**⋆ قم بالرد ع الرسالة لاذاعتها للمستخدمين ↸**\n\n*الامر ( معلومات ) \n- لمعرفة الملصقات المرسلة ↶\n**⋆ بالرد ع المستخدم لجلب معلوماتة **\n\n*الامر ( حظر + سبب )\n- لحظر مستخدم من البوت \n**⋆ بالرد ع المستخدم مع سبب مثل **\n**حظر @RR9R7 قمت بازعاجي**\n\n* الامر ( الغاء حظر ) \n لالغاء حظر المستخدم من البوت √\n**⋆ الامر والمعرف والسبب (اختياري) مثل **\n**الغاء حظر @RR9R7 + السبب اختياري**\n\n**⋆ الامر ( المحظورين )\n- لمعرفة المحظورين من البوت  **\n\n**⋆ امر ( المستخدمين ) \n- لمعرفة مستخدمين بوتك  **\n\n**⋆ الاوامر ( التكرار + تفعيل / تعطيل ) \n- تشغيل وايقاف التكرار (في البوت) ↶**\n* عند التشغيل يحظر المزعجين تلقائيًا ⊝\n\n\n**⍣ⵧⵧⵧⵧⵧᴊᴍᴛʜᴏɴⵧⵧⵧⵧⵧ⍣**\n𝙅𝙈𝙏𝙃𝙊𝙉 𝙐𝙎𝙀𝙍𝘽𝙊𝙏 🧸♥"
    await tgbot.send_message(event.chat_id, rorza)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"jm_hhack")))
async def users(event):
    await event.delete()
    rorza = "الان ارسل  /rz"
    await tgbot.send_message(event.chat_id, rorza)

@jmthon.bot_cmd(incoming=True, func=lambda e: e.is_private)
async def bot_pms(event):  # sourcery no-metrics
    chat = await event.get_chat()
    if check_is_black_list(chat.id):
        return
    if chat.id != Config.OWNER_ID:
        msg = await event.forward_to(Config.OWNER_ID)
        try:
            add_user_to_db(msg.id, get_display_name(chat), chat.id, event.id, 0, 0)
        except Exception as e:
            LOGS.error(str(e))
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"**خطـأ**\nاثناء التعرف على معلومات الرسالة في قاعده البيانات\n`{str(e)}`",
                )
    else:
        if event.text.startswith("/"):
            return
        reply_to = await reply_id(event)
        if reply_to is None:
            return
        users = get_user_id(reply_to)
        if users is None:
            return
        for usr in users:
            user_id = int(usr.chat_id)
            reply_msg = usr.reply_id
            user_name = usr.first_name
            break
        if user_id is not None:
            try:
                if event.media:
                    msg = await event.client.send_file(
                        user_id, event.media, caption=event.text, reply_to=reply_msg
                    )
                else:
                    msg = await event.client.send_message(
                        user_id, event.text, reply_to=reply_msg, link_preview=False
                    )
            except UserIsBlockedError:
                return await event.reply("تم حظر البوت من قبل المستخدم")
            except Exception as e:
                return await event.reply(f"**Error:**\n`{e}`")
            try:
                add_user_to_db(
                    reply_to, user_name, user_id, reply_msg, event.id, msg.id
                )
            except Exception as e:
                LOGS.error(str(e))
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**خطـأ**\nاثناء التعرف على معلومات الرسالة في قاعده البيانات\n`{e}`",
                    )


@jmthon.bot_cmd(edited=True)
async def bot_pms_edit(event):  # sourcery no-metrics
    chat = await event.get_chat()
    if check_is_black_list(chat.id):
        return
    if chat.id != Config.OWNER_ID:
        users = get_user_reply(event.id)
        if users is None:
            return
        if reply_msg := next(
            (user.message_id for user in users if user.chat_id == str(chat.id)),
            None,
        ):
            await event.client.send_message(
                Config.OWNER_ID,
                f"⬆️ **هذه الرسالة تم تعديلها من قبل المستخدم** {_format.mentionuser(get_display_name(chat) , chat.id)} كـ :",
                reply_to=reply_msg,
            )
            msg = await event.forward_to(Config.OWNER_ID)
            try:
                add_user_to_db(msg.id, get_display_name(chat), chat.id, event.id, 0, 0)
            except Exception as e:
                LOGS.error(str(e))
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**خطـأ**\nاثناء التعرف على معلومات الرسالة في قاعده البيانات\n`{e}`",
                    )

    else:
        reply_to = await reply_id(event)
        if reply_to is not None:
            users = get_user_id(reply_to)
            result_id = 0
            if users is None:
                return
            for usr in users:
                if event.id == usr.logger_id:
                    user_id = int(usr.chat_id)
                    reply_msg = usr.reply_id
                    result_id = usr.result_id
                    break
            if result_id != 0:
                try:
                    await event.client.edit_message(
                        user_id, result_id, event.text, file=event.media
                    )
                except Exception as e:
                    LOGS.error(str(e))


@tgbot.on(events.MessageDeleted)
async def handler(event):
    for msg_id in event.deleted_ids:
        users_1 = get_user_reply(msg_id)
        users_2 = get_user_logging(msg_id)
        if users_2 is not None:
            result_id = 0
            for usr in users_2:
                if msg_id == usr.logger_id:
                    user_id = int(usr.chat_id)
                    result_id = usr.result_id
                    break
            if result_id != 0:
                try:
                    await event.client.delete_messages(user_id, result_id)
                except Exception as e:
                    LOGS.error(str(e))
        if users_1 is not None:
            reply_msg = next(
                (
                    user.message_id
                    for user in users_1
                    if user.chat_id != Config.OWNER_ID
                ),
                None,
            )
            try:
                if reply_msg:
                    users = get_user_id(reply_msg)
                    for usr in users:
                        user_id = int(usr.chat_id)
                        user_name = usr.first_name
                        break
                    if check_is_black_list(user_id):
                        return
                    await event.client.send_message(
                        Config.OWNER_ID,
                        f"⬆️ **هذه الرسالة تم حذفها من قبل المستخدم** {_format.mentionuser(user_name , user_id)}.",
                        reply_to=reply_msg,
                    )
            except Exception as e:
                LOGS.error(str(e))


@jmthon.bot_cmd(pattern="^معلومات$", from_users=Config.OWNER_ID)
async def bot_start(event):
    reply_to = await reply_id(event)
    if not reply_to:
        return await event.reply("**▾∮قم بالرد ع رسالة المستخدم لجلب المعلومات!**")
    info_msg = await event.client.send_message(
        event.chat_id,
        "**▾∮ سأجلب المعلومات من قاعدة بياناتي ✓",
        reply_to=reply_to,
    )
    users = get_user_id(reply_to)
    if users is None:
        return await info_msg.edit("حدث خطأ!\n**لم اعثر على المستخدم في بياناتي ✘**")
    for usr in users:
        user_id = int(usr.chat_id)
        user_name = usr.first_name
        break
    if user_id is None:
        return await info_msg.edit("حدث خطأ!\n**لم اعثر على المستخدم في بياناتي ✘**")
    uinfo = f"**▾∮الاسم ⪼ **`{user_name}`\n**▾∮الايدي ⪼ **`{user_id}`\n**▾∮الرابط ⪼** 「{_format.mentionuser(user_name , user_id)}」\n\n**⍣ⵧⵧⵧⵧⵧᴊᴍᴛʜᴏɴⵧⵧⵧⵧⵧ⍣**\n[𝙅𝙈𝙏𝙃𝙊𝙉 𝙐𝙎𝙀𝙍𝘽𝙊𝙏 🧸♥](https://t.me/JMTHON)"
    await info_msg.edit(uinfo)


async def send_flood_alert(user_) -> None:
    # sourcery no-metrics
    buttons = [
        (
            Button.inline("حظر المستخدم ⛔️❗️", data=f"bot_pm_ban_{user_.id}"),
            Button.inline(
                "ايقاف تحذير التكرار ﹥[off] ⚠️",
                data="toggle_bot-antiflood_off",
            ),
        )
    ]
    found = False
    if FloodConfig.ALERT and (user_.id in FloodConfig.ALERT.keys()):
        found = True
        try:
            FloodConfig.ALERT[user_.id]["count"] += 1
        except KeyError:
            found = False
            FloodConfig.ALERT[user_.id]["count"] = 1
        except Exception as e:
            if BOTLOG:
                await jmthon.tgbot.send_message(
                    BOTLOG_CHATID,
                    f"**Error:**\nWhile updating flood count\n`{e}`",
                )

        flood_count = FloodConfig.ALERT[user_.id]["count"]
    else:
        flood_count = FloodConfig.ALERT[user_.id]["count"] = 1

    flood_msg = (
        r"تحذير التكرار ⚠️"
        "\n\n"
        f"**▾∮  المستخدم ⪼** 「{_format.mentionuser(get_display_name(user_), user_.id)}」\n**▾∮الايدي ⪼ **`{user_.id}`\n\n**▾ المستخدم قام بتكرار الرسائل! العدد ↫** `({flood_count})`\n`*عند الاهمال سيتم حظره تلقائي ❗️`\n**للاجراء السريع في الاسفل ↶** \n**⍣ⵧⵧⵧⵧⵧᴊᴍᴛʜᴏɴⵧⵧⵧⵧⵧ⍣**\n[𝙅𝙈𝙏𝙃𝙊𝙉 𝙐𝙎𝙀𝙍𝘽𝙊𝙏 🧸♥](https://t.me/JMTHON)"
    )

    if found:
        if flood_count >= FloodConfig.AUTOBAN:
            if user_.id in Config.SUDO_USERS:
                sudo_spam = (
                    f"**المالك الثانوي** {_format.mentionuser(user_.first_name , user_.id)}:\n  الايدي: {user_.id}\n\n"
                    "يقوم بعمل تكرار في بوتك  ! تأكظ من الاوامر و احذفه من قائمه النالك الثانوي."
                )
                if BOTLOG:
                    await jmthon.tgbot.send_message(BOTLOG_CHATID, sudo_spam)
            else:
                await ban_user_from_bot(
                    user_,
                    f"▾∮ حظر تلقائي لتكرارك {FloodConfig.AUTOBAN} رسائل!",
                )
                FloodConfig.USERS[user_.id].clear()
                FloodConfig.ALERT[user_.id].clear()
                FloodConfig.BANNED_USERS.remove(user_.id)
            return
        fa_id = FloodConfig.ALERT[user_.id].get("fa_id")
        if not fa_id:
            return
        try:
            msg_ = await jmthon.tgbot.get_messages(BOTLOG_CHATID, fa_id)
            if msg_.text != flood_msg:
                await msg_.edit(flood_msg, buttons=buttons)
        except Exception as fa_id_err:
            LOGS.debug(fa_id_err)
            return
    else:
        if BOTLOG:
            fa_msg = await jmthon.tgbot.send_message(
                BOTLOG_CHATID,
                flood_msg,
                buttons=buttons,
            )
        try:
            chat = await jmthon.tgbot.get_entity(BOTLOG_CHATID)
            await jmthon.tgbot.send_message(
                Config.OWNER_ID,
                f"⚠️  **[▾∮ يوجد تكرار!\nإضغط ع الرسالة لمعرفتهُ واجراء اللازم!](https://t.me/c/{chat.id}/{fa_msg.id})**",
            )
        except UserIsBlockedError:
            if BOTLOG:
                await jmthon.tgbot.send_message(BOTLOG_CHATID, "**Unblock your bot !**")
    if FloodConfig.ALERT[user_.id].get("fa_id") is None and fa_msg:
        FloodConfig.ALERT[user_.id]["fa_id"] = fa_msg.id


@jmthon.tgbot.on(CallbackQuery(data=re.compile(b"bot_pm_ban_([0-9]+)")))
@check_owner
async def bot_pm_ban_cb(c_q: CallbackQuery):
    user_id = int(c_q.pattern_match.group(1))
    try:
        user = await jmthon.get_entity(user_id)
    except Exception as e:
        await c_q.answer(f"Error:\n{str(e)}")
    else:
        await c_q.answer(f"جاري حظر المستخدم ↫ `{user_id}`", alert=False)
        await ban_user_from_bot(user, "لا يسمح بتكرار الرسائل!")
        await c_q.edit(
            f"▾∮ تم حظر المستخدم بسبب التكرار❗️ ↶**\n**▾∮الاسم ⪼ **`{user_name}`\n**▾∮الايدي ⪼ **`{user_id}`\n**▾∮الرابط ⪼** 「{_format.mentionuser(user_name , user_id)}**⍣ⵧⵧⵧⵧⵧᴊᴍᴛʜᴏɴⵧⵧⵧⵧⵧ⍣**\n[𝙅𝙈𝙏𝙃𝙊𝙉 𝙐𝙎𝙀𝙍𝘽𝙊𝙏 🧸♥](https://t.me/JMTHON)"
        )


def time_now() -> Union[float, int]:
    return datetime.timestamp(datetime.now())


@pool.run_in_thread
def is_flood(uid: int) -> Optional[bool]:
    """Checks if a user is flooding"""
    FloodConfig.USERS[uid].append(time_now())
    if (
        len(
            list(
                filter(
                    lambda x: time_now() - int(x) < FloodConfig.SECONDS,
                    FloodConfig.USERS[uid],
                )
            )
        )
        > FloodConfig.MESSAGES
    ):
        FloodConfig.USERS[uid] = list(
            filter(
                lambda x: time_now() - int(x) < FloodConfig.SECONDS,
                FloodConfig.USERS[uid],
            )
        )
        return True


@jmthon.tgbot.on(CallbackQuery(data=re.compile(b"toggle_bot-antiflood_off$")))
@check_owner
async def settings_toggle(c_q: CallbackQuery):
    if gvarstatus("bot_antif") is None:
        return await c_q.answer(f" تحذير التكرار فعلا غير مفعل ❓", alert=False)
    delgvar("bot_antif")
    await c_q.answer(f" تم ايقاف تحذير التكرار ❗️", alert=False)
    await c_q.edit("**▾∮ تحذير التكرار غير مفعل الان  ✅**")


@jmthon.bot_cmd(incoming=True, func=lambda e: e.is_private)
@jmthon.bot_cmd(edited=True, func=lambda e: e.is_private)
async def antif_on_msg(event):
    if gvarstatus("bot_antif") is None:
        return
    chat = await event.get_chat()
    if chat.id == Config.OWNER_ID:
        return
    user_id = chat.id
    if check_is_black_list(user_id):
        raise StopPropagation
    if await is_flood(user_id):
        await send_flood_alert(chat)
        FloodConfig.BANNED_USERS.add(user_id)
        raise StopPropagation
    if user_id in FloodConfig.BANNED_USERS:
        FloodConfig.BANNED_USERS.remove(user_id)
