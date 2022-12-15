# inline_help.py

import asyncio
import json
import os
from typing import Dict, List

from pyrogram import filters
from pyrogram.errors import MessageEmpty, MessageNotModified
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InlineQuery,
                            InlineQueryResultArticle, InputTextMessageContent)

from venom import Config, MyMessage, manager, venom
from venom.helpers import VenomDecorators, plugin_name

CHANNEL = venom.getCLogger(__name__)
HELP_ = Config.HELP[plugin_name(__name__)] = {'type': 'help', 'commands': []}
help_structure: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
folders = []
plugins = []


async def _init() -> None:
    global help_structure, plugins, folders
    help_ = Config.HELP
    plugins = help_.keys()
    folders = [help_[one]['type'] for one in plugins]
    folders = sorted([*set(folders)])
    for folder in folders:
        help_structure[folder] = {}
        for plugin in sorted(plugins):
            if help_[plugin]['type'] == folder:
                help_structure[folder][plugin] = help_[plugin]['commands']


########################################################################################################################

HELP_['commands'].append(
    {
        'command': 'ihelp',
        'flags': None,
        'usage': 'see inline help list',
        'syntax': '{tr}ihelp',
        'sudo': True
    }
)


@venom.trigger('ihelp')
async def i_help(_, message: MyMessage):
    """ inline help command """
    bot_u = (await venom.bot.get_me()).username
    results = await venom.get_inline_bot_results(bot_u, "helpME")
    await venom.send_inline_bot_result(message.chat.id, query_id=results.query_id, result_id=results.results[0].id)


############################################## inline command starter ##################################################


@venom.bot.on_inline_query(group=5)
@VenomDecorators.inline_checker(owner=True)
async def inline_helper(_, iq: InlineQuery):
    """ inline help for VenomX """
    results = []
    buttons_ = start_button()
    article = InlineQueryResultArticle(
        title="VenomX help...",
        input_message_content=InputTextMessageContent(
            message_text="<b>Let's get started with the inline help...</b>"
        ),
        reply_markup=buttons_
    )
    results.append(article)
    if len(results) != 0:
        await iq.answer(results, cache_time=2)


################################################## callback ############################################################


# @venom.bot.on_callback_query(filters.regex(r"ihelp_(start|back|next|previous)_(\d{1,2})"), group=4)
# async def ihelp_navigation(_, cq: CallbackQuery):
#     """ callback navigation """


@venom.bot.on_callback_query(filters.regex(r"^ihelp_([A-Za-z]+)(\d{1,2})_(start|back|next|previous|[A-Za-z]+)_(\d{1,2})"), group=6)
@VenomDecorators.callback_checker(owner=True)
async def ihelp_callback(_, cq: CallbackQuery):
    """ callback data for ihelp plugin """
    currently_in = cq.matches[0].group(1)
    last_index = int(cq.matches[0].group(2))
    btn_pressed = cq.matches[0].group(3)
    index = int(cq.matches[0].group(4)) or 0
    text_ = ""
    start_text = "<b>Let's get started with the inline help...</b>"
    general_text = "<b>Available folders are as below...</b>"
    folder_text = "<b>Currently in --{}-- folder...</b>"
    plugin_text = "<b>Right now in --{}-- plugin...</b>"
    reply_markup = start_button()
    if btn_pressed == "start":
        text_ = general_text
        reply_markup = folder_buttons(0)
    elif btn_pressed == "back":
        if currently_in == "folders":
            text_ = start_text
            reply_markup = start_button()
        elif currently_in in folders:
            text_ = general_text
            reply_markup = folder_buttons(last_index)
        elif currently_in in plugins:
            parent_folder = manager.plugin_parent(currently_in)
            text_ = folder_text.format(parent_folder)
            reply_markup = plugin_buttons(parent_folder, last_index)
        elif currently_in in manager.cmd_names():
            parent_plugin = manager.cmd_parent_plugin(currently_in)
            text_ = plugin_text.format(parent_plugin)
            parent_folder = manager.plugin_parent(parent_plugin)
            reply_markup = cmd_buttons(parent_folder, parent_plugin, last_index)
    elif btn_pressed in ["next", "previous"]:
        if currently_in == "folders":
            reply_markup = folder_buttons(index)
        elif currently_in in folders:
            reply_markup = plugin_buttons(currently_in, index)
        elif currently_in in plugins:
            reply_markup = cmd_buttons(currently_in, btn_pressed, index)
    else:
        if currently_in == "folders":
            text_ = folder_text.format(btn_pressed)
            reply_markup = plugin_buttons(btn_pressed, index)
        elif currently_in in folders:
            text_ = plugin_text.format(btn_pressed)
            reply_markup = cmd_buttons(currently_in, btn_pressed, index)
        elif currently_in in plugins:
            text_ = cmd_help(btn_pressed)
            reply_markup = InlineKeyboardMarkup([navigation_buttons(btn_pressed, True, True, 0)])
    try:
        await cq.edit_message_text(text_, disable_web_page_preview=True, reply_markup=reply_markup)
    except MessageNotModified:
        print("Not modified")
    except MessageEmpty:
        print("Empty")


################################################## button functions ####################################################

def start_button() -> InlineKeyboardMarkup:
    btn_ = [
        [
            InlineKeyboardButton(text="Start", callback_data="ihelp_start0_start_0")
        ]
    ]
    return InlineKeyboardMarkup(btn_)


def folder_buttons(index: int) -> InlineKeyboardMarkup:
    """ returns folder buttons """
    folder_names = sorted([*set(folders)])
    btn_row = []
    btns_ = []
    start = False
    end = False
    i = 1
    i_start = index * 10
    i_end = index * 10 + 9
    if index == 0:
        start = True
    if i_end + 1 > len(folder_names):
        i_end = len(folder_names) - 1
        end = True
    for one in folder_names[i_start:i_end]:
        if one == "help":
            continue
        btn_ = InlineKeyboardButton(text=one, callback_data=f"ihelp_folders{index}_{one}_0")
        btn_row.append(btn_)
        if i % 2 == 0:
            btns_.append(btn_row)
            btn_row = []
        i += 1
    btns_.append(btn_row)
    btns_.append(navigation_buttons("folders", start, end, index))
    return InlineKeyboardMarkup(btns_)


def plugin_buttons(folder: str, index: int) -> InlineKeyboardMarkup | None:
    """ returns plugin buttons """
    plugin_names = sorted(help_structure[folder].keys())
    btn_row = []
    btns_ = []
    start = False
    end = False
    i = 1
    i_start = index * 10
    i_end = index * 10 + 9
    if index == 0:
        start = True
    if i_end + 1 > len(plugin_names):
        i_end = len(plugin_names) - 1
        end = True
    for one in plugin_names:
        btn_ = InlineKeyboardButton(text=one, callback_data=f"ihelp_{folder}{index}_{one}_0")
        btn_row.append(btn_)
        if i % 2 == 0:
            btns_.append(btn_row)
            btn_row = []
        i += 1
    btns_.append(btn_row)
    btns_.append(navigation_buttons(folder, start, end, index))
    return InlineKeyboardMarkup(btns_)


def cmd_buttons(folder: str, plugin: str, index: int) -> InlineKeyboardMarkup:
    """ returns command buttons """
    cmd_dicts = help_structure[folder][plugin]
    cmd_list = [one['command'] for one in cmd_dicts]
    cmd_list = sorted(cmd_list)
    btn_row = []
    btns_ = []
    start = False
    end = False
    i = 1
    i_start = index * 10
    i_end = index * 10 + 9
    if index == 0:
        start = True
    if i_end + 1 > len(cmd_list):
        i_end = len(cmd_list) - 1
        end = True
    for one in cmd_list:
        btn_ = InlineKeyboardButton(text=one, callback_data=f"ihelp_{plugin}{index}_{one}_0")
        btn_row.append(btn_)
        if i % 2 == 0:
            btns_.append(btn_row)
            btn_row = []
        i += 1
    btns_.append(btn_row)
    btns_.append(navigation_buttons(plugin, start, end, index))
    return InlineKeyboardMarkup(btns_)


def cmd_help(cmd_name: str) -> str:
    out_ = f"--Details on command **{cmd_name}**--:\n\n"
    dot_ = Config.BULLET_DOT
    plugin = manager.cmd_parent_plugin(cmd_name)
    help_ = Config.HELP[plugin]['commands'] if plugin in Config.HELP.keys() else None
    if help_ is not None:
        my_cmd = None
        for one in help_:
            if one['command'] == cmd_name:
                my_cmd = one
                break
    else:
        my_cmd = None
    if my_cmd:
        gh_link = manager.gh_link(cmd_name)
        sytx = my_cmd['syntax'] if 'syntax' in my_cmd.keys() else 'Not documented.'
        flags_ = my_cmd['flags'] if 'flags' in my_cmd.keys() and my_cmd['flags'] is not None else None
        _flags = "None\n"
        if flags_:
            _flags = "\n"
            for k, v in flags_.items():
                _flags += f"    `{str(k)}` : __{str(v)}__\n"
        out_ += (
            f"{dot_} **Name:** `{cmd_name}`\n"
            f"{dot_} **Flags:** {_flags}"
            f"{dot_} **Syntax:** `{sytx}`\n"
            f"{dot_} **Sudo access:** {my_cmd['sudo'] if 'sudo' in my_cmd.keys() else '`Not documented.`'}\n\n"

            f"**Location:** `{manager.plugin_loc(plugin)}`\n"
            f"**GitHub link:** **[LINK]({gh_link})**"
        )
    else:
        out_ = "`Not documented.`"
    trigg = Config.CMD_TRIGGER
    return out_.replace("{tr}", trigg)


def navigation_buttons(currently_at: str, start: bool, end: bool, index: int) -> List[InlineKeyboardButton]:
    buttons = []
    if not start:
        buttons.append(InlineKeyboardButton(text="<<", callback_data=f"ihelp_{currently_at}{index}_previous_{index-1}"))
    buttons.append(InlineKeyboardButton(text="Back", callback_data=f"ihelp_{currently_at}{index}_back_0"))
    if not end:
        buttons.append(InlineKeyboardButton(text=">>", callback_data=f"ihelp_{currently_at}{index}_next_{index+1}"))
    return buttons
