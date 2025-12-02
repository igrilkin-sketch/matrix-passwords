# эффективный гейбан. слит by @zovcorporation

import time
import typing
from asyncio import sleep as asleep

from telethon.tl.types import Channel, Chat, Message, User
from .. import loader, utils

# zovban
BANNED_RIGHTS = {
    "view_messages": False,
    "send_messages": False,
    "send_media": False,
    "send_stickers": False,
    "send_gifs": False,
    "send_games": False,
    "send_inline": False,
    "send_polls": False,
    "change_info": False,
    "invite_users": False,
}

# @zovcorporation наш тгк
UNBAN_RIGHTS = {k: True for k in BANNED_RIGHTS}

def get_full_name(user: typing.Union[User, Channel]) -> str:
    return utils.escape_html(
        user.title if isinstance(user, Channel)
        else f"{user.first_name} " + (user.last_name or "")
    ).strip()

@loader.tds
class GlobalRestrict(loader.Module):
    """гейбан"""

    strings = {
        "name": "gayban",
        "no_reason": "jirban",
        "args": "<b>инвалид аргументы</b>",
        "glbanning": ' <b>запускаю глобальный бан <a href="{}">{}</a>...</b>',
        "glban": '<b><a href="{}">{}</a></b>\n<i>{}</i>\n\n<b>забанено в {} чатах</b>',
    }

    def __init__(self):
        self._gban_cache = {}

    async def args_parser(self, message: Message) -> tuple:
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if reply and not args:
            user = await self._client.get_entity(reply.sender_id)
            reason = "гей бан"
        else:
            try:
                user = await self._client.get_entity(args.split()[0])
            except:
                await utils.answer(message, self.strings("args"))
                return None
            reason = " ".join(args.split()[1:]).strip() or "jirban"

        return user, utils.escape_html(reason)

    async def dikindishen(self, chat_id: int, user):
        """цикл"""
        try:
            for _ in range(3):
                await self._client.edit_permissions(chat_id, user, **BANNED_RIGHTS)
                await asleep(0.4)
                await self._client.edit_permissions(chat_id, user, **UNBAN_RIGHTS)
                await asleep(0.4)
                await self._client.edit_permissions(chat_id, user, **BANNED_RIGHTS)
                await asleep(0.4)

            await self._client.kick_participant(chat_id, user)
            await asleep(0.5)
            await self._client.edit_permissions(chat_id, user, **UNBAN_RIGHTS)
            await asleep(0.5)
            await self._client.edit_permissions(chat_id, user, **BANNED_RIGHTS)
        except:
            pass

    async def pashalko(self, chat_id: int, user):
        try:
            for _ in range(6):
                await self._client.edit_permissions(chat_id, user, **BANNED_RIGHTS)
                await asleep(0.5)
        except:
            pass

    @loader.command(
        ru_doc="<реплай | @юзер> - говнобан по чатам каналам",
    )
    async def glban(self, message: Message):
        parsed = await self.args_parser(message)
        if not parsed:
            return

        user, reason = parsed

        msg = await utils.answer(
            message,
            self.strings("glbanning").format(utils.get_entity_url(user), get_full_name(user))
        )

        if not self._gban_cache or self._gban_cache.get("exp", 0) < time.time():
            self._gban_cache = {
                "exp": time.time() + 600,
                "chats": [
                    chat.entity async for chat in self._client.iter_dialogs()
                    if isinstance(chat.entity, (Chat, Channel))
                    and getattr(chat.entity, "admin_rights", None)
                    and getattr(chat.entity.admin_rights, "ban_users", False)
                ]
            }

        success = 0
        for chat in self._gban_cache["chats"]:
            try:
                await asleep(0.1)
                if isinstance(chat, Chat):
                    await self.dikindishen(chat.id, user)
                else:
                    await self.pashalko(chat.id, user)
                success += 1
            except:
                continue

        await utils.answer(
            msg,
            self.strings("glban").format(
                utils.get_entity_url(user),
                get_full_name(user),
                reason,
                success
            )
        )
