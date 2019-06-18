import os, sys
from discord import Embed
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

def setup_logger():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%H:%M:%S')
    handler = TimedRotatingFileHandler("logs/watchdog.log", when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger("watchdog")
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    logger.setLevel(logging.INFO)

async def log(message, bot, level="INFO", debug=""):
    channel = bot.get_channel(int(os.getenv('botlog')))
    st = datetime.datetime.now().strftime('%H:%M:%S')
    await channel.send("`[" + st + "]` **[" + level + "]** " + message)
    if debug == "":
        logDebug(message, level)
        return
    logDebug(debug, level)

def logDebug(message, level="INFO"):
    logger = logging.getLogger("watchdog")
    if level == "DEBUG":
        logger.debug(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "CRITICAL":
        logger.critical(message)
    else:
        logger.info(message)

async def logEmbed(color, description, bot, debug=""):
    channel = bot.get_channel(int(os.getenv('botlog')))
    await channel.send(embed=Embed(color=color, description=description, timestamp=datetime.datetime.now()))
    if debug == "":
        logDebug(description)
        return
    logDebug(debug)