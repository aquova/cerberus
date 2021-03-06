import discord
from config import CENSOR_LIST, CENSOR_WATCH, CENSOR_CHAN, SYS_LOG, VALID_INPUT_CHANS, WATCHLIST_CHAN
from re import search, IGNORECASE

async def listCensor(message, _):
    delete_items = '\n'.join(CENSOR_LIST)
    watch_items = '\n'.join(CENSOR_WATCH)
    mes = f"Here are the things we censor. I hope you know regex.\n\nItems we delete:\n```{delete_items}```\nItems we watch:\n```{watch_items}```"

    await message.channel.send(mes)

async def check_censor(message):
    # If you're posting in an admin channel, you can swear all you like
    if message.channel.id in VALID_INPUT_CHANS:
        return False

    for item in CENSOR_LIST:
        if bool(search(item, message.content, IGNORECASE)):
            await censor_message(message)
            return True

    for item in CENSOR_WATCH:
        if bool(search(item, message.content, IGNORECASE)):
            await watch_message(message)
            return False

    return False

async def censor_message(message):
    # If censor violation found:
    # - Delete message
    # - Post a message removal message ourselves (since bots are normally ignored)
    # - Point the admins to the fact that we deleted a message
    # - DM the user telling them that we deleted their message

    await message.delete()

    censor_mes = f":face_with_symbols_over_mouth: **{str(message.author)}** (ID: {message.author.id}) had a message removed by the censor in <#{message.channel.id}>: `{message.content}`"
    syslog_chan = discord.utils.get(message.guild.channels, id=SYS_LOG)
    log_message = await syslog_chan.send(censor_mes)

    mod_mes = f"Uh oh, looks like <@{message.author.id}> tripped the censor.\n{log_message.jump_url}"
    chan = discord.utils.get(message.guild.channels, id=CENSOR_CHAN)
    await chan.send(mod_mes)

    # Create a DM channel between Bouncer if it doesn't exist
    dm_chan = message.author.dm_channel
    if dm_chan == None:
        dm_chan = await message.author.create_dm()

    await dm_chan.send(f"Hi there! This is an automated courtesy message informing you that your post was deleted for containing a censored word: `{message.content}`. This is not a warning. The staff team will examine the context and situation of the censor trip and you will be contacted later only if any disciplinary action is taken.")

async def watch_message(message):
    # These are words whose usage we don't want to delete, but we should post to the watch channel
    watch_chan = discord.utils.get(message.guild.channels, id=WATCHLIST_CHAN)
    censor_mes = f"I've flagged a message from **{str(message.author)}** (ID: {message.author.id}) in <#{message.channel.id}>: `{message.content}`\n{message.jump_url}"

    await watch_chan.send(censor_mes)
