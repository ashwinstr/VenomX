# on_message.py

from pyrogram import Client as RClient, filters

class OnMessage(RClient):

    def on_message(self, filters: filters.Filter = None, group: int = 0):
        " custom on message decorator "