# logger.py

import os
import logging
from logging.handlers import RotatingFileHandler


if not os.path.isdir("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s - %(levelname)s] - %(name)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            "logs/venom.log", maxBytes=(20480), backupCount=10
        ),
        logging.StreamHandler()
    ]
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.parser.html").setLevel(logging.ERROR)
logging.getLogger("pyrogram.session.session").setLevel(logging.ERROR)