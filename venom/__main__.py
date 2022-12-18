# main.py

from venom import venom
from pyrogram.errors import AuthKeyDuplicated
import sys

if __name__ == "__main__":
  try:
    venom.run()
  except AuthKeyDuplicated:
    print("String has expired, Make new")
    sys.exit()
