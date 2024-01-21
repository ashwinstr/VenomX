# inline_help.py

from typing import Dict, List

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageEmpty, MessageNotModified
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InlineQuery,
                            InlineQueryResultArticle, InputTextMessageContent)

from venom import Collection, Config, MyMessage, SecureConfig, manager, venom
from venom.core.command_manager import plugin_parent
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
    """ help command """
    if Config.USER_MODE:
        await inline_help(message)
    else:
        await bot_help(message)


async def inline_help(message: MyMessage):
    """ inline help method """
    bot_u = (await venom.bot.get_me()).username
    results = await venom.get_inline_bot_results(bot_u, "")
    await venom.send_inline_bot_result(message.chat.id, query_id=results.query_id, result_id=results.results[0].id)


async def bot_help(message: MyMessage):
    """ bot help method """
    await message.edit("<b>Let's get started with the inline help...</b>",
                       reply_markup=start_button(),
                       parse_mode=ParseMode.HTML)

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
            message_text="<b>Let's get started with the inline help...</b>",
            disable_web_page_preview=True
        ),
        reply_markup=buttons_
    )
    results.append(article)
    if len(results) != 0:
        await iq.answer(results, cache_time=2)


################################################## callback ############################################################


@venom.bot.on_callback_query(filters.regex(r"ihelp_bot_mode"), group=1)
@VenomDecorators.callback_checker(owner=True)
async def inline_bot_mode(_, cq: CallbackQuery):
    """ Inline bot mode """
    # if isinstance(venom, VenomBot):
    #     return await cq.answer("Bot mode ihelp is disabled for now, please use it in user mode.", show_alert=True)
    if Config.USER_MODE:
        Config.USER_MODE = False
        text_ = "**Mode changed to BOT.**"
    else:
        Config.USER_MODE = True
        text_ = "**Mode changed to USER.**"
    if SecureConfig().STRING_SESSION:
        message = cq.message
        if message is not None:
            chat_ = cq.message.chat.id
            msg_ = cq.message.id
            await venom.bot.edit_message_text(chat_id=chat_, message_id=msg_, text=text_, reply_markup=start_button())
            # await cq.edit_message_text(text_)
        else:
            await cq.edit_message_text(text_, reply_markup=start_button())
    else:
        Config.USER_MODE = False
        await cq.answer("STRING_SESSION not valid/found...\nCan't change to USER mode.", show_alert=True)
    await Collection.TOGGLES.update_one(
        {"_id": "USER_MODE"},
        {"$set": {"switch": Config.USER_MODE}},
        upsert=True
    )


@venom.bot.on_callback_query(filters.regex(r"^ihelp_([A-Z_a-z]+)(\d{1,2})_(start|back|next|previous|[A-Z_a-z]+)_(\d{"
                                           r"1,2})"), group=6)
@VenomDecorators.callback_checker(owner=True)
async def ihelp_callback(_, cq: CallbackQuery):
    """ callback data for ihelp plugin """
    # if isinstance(venom, VenomBot):
    #     return await cq.answer("Bot mode ihelp is disabled for now, please use it in user mode.", show_alert=True)
    currently_in = cq.matches[0].group(1)
    last_index = int(cq.matches[0].group(2))
    btn_pressed = cq.matches[0].group(3)
    index = int(cq.matches[0].group(4))
    text_ = "testing"
    start_text = "**Let's get started with the inline help...**"
    general_text = "**Available folders are as below...**"
    folder_text = "**Currently in --{}-- folder...**"
    plugin_text = "**Right now in --{}-- plugin...**"
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
            parent_folder = plugin_parent(currently_in)
            text_ = folder_text.format(parent_folder)
            reply_markup = plugin_buttons(parent_folder, last_index)
        elif currently_in in manager.cmd_names():
            parent_plugin = manager.cmd_parent_plugin(currently_in)
            text_ = plugin_text.format(parent_plugin)
            parent_folder = plugin_parent(parent_plugin)
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
    if not reply_markup:
        await cq.answer("Something unexpected happened...\nReport in support group.", show_alert=True)
        text_ = start_text
        reply_markup = start_button()
    try:
        message = cq.message
        if message is None:
            await cq.edit_message_text(
                text=text_, disable_web_page_preview=True, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )
        else:
            chat_id = cq.message.chat.id
            message_id = cq.message.id
            await venom.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text_,
                dis_preview=True,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    except MessageNotModified:
        print("Not modified")
    except MessageEmpty:
        print("Empty")
    except TypeError:
        await cq.answer("Something unexpected happened...", show_alert=True)


################################################## button functions ####################################################

def start_button() -> InlineKeyboardMarkup:
    mode_ = "USER" if Config.USER_MODE and SecureConfig().STRING_SESSION else "BOT"
    btn_ = [
        [
            InlineKeyboardButton(text="Start", callback_data="ihelp_start0_start_0")
        ],
        [
            InlineKeyboardButton(text=mode_, callback_data="ihelp_bot_mode")
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
    while index > 0 and index * 10 > len(folder_names):
        index -= 1
    i_start = index * 10
    i_end = index * 10 + 9
    if index == 0:
        start = True
    if i_end + 1 > len(folder_names):
        i_end = len(folder_names)
        end = True
    for one in folder_names[i_start:i_end]:
        if one == "help":
            continue
        one: str
        one_cap = one.capitalize()
        btn_ = InlineKeyboardButton(text=one_cap, callback_data=f"ihelp_folders{index}_{one}_0")
        btn_row.append(btn_)
        if i % 2 == 0:
            btns_.append(btn_row)
            btn_row = []
        i += 1
    btns_.append(btn_row)
    btns_.append(navigation_buttons("folders", start, end, index))
    return InlineKeyboardMarkup(btns_)


def plugin_buttons(folder: str, index: int) -> InlineKeyboardMarkup:
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
        i_end = len(plugin_names)
        end = True
    for one in plugin_names[i_start:i_end]:
        one_cap = one.capitalize()
        btn_ = InlineKeyboardButton(text=one_cap, callback_data=f"ihelp_{folder}{index}_{one}_0")
        btn_row.append(btn_)
        if i % 2 == 0:
            btns_.append(btn_row)
            btn_row = []
        i += 1
    btns_.append(btn_row)
    btns_.append(navigation_buttons(folder, start, end, index))
    return InlineKeyboardMarkup(btns_)


def cmd_buttons(folder: str, plugin: str, index: int) -> InlineKeyboardMarkup | bool:
    """ returns command buttons """
    try:
        cmd_dicts = help_structure[folder][plugin]
    except KeyError:
        print(folder, plugin, index, sep="\n")
        return False
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
        i_end = len(cmd_list)
        end = True
    for one in cmd_list[i_start:i_end]:
        one_cap = one.capitalize()
        btn_ = InlineKeyboardButton(text=one_cap, callback_data=f"ihelp_{plugin}{index}_{one}_0")
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
            
            f"__{my_cmd['usage'].capitalize() if 'usage' in my_cmd.keys() else 'No description...'}__\n\n"

            f"**Location:** `{manager.plugin_loc(plugin)}`\n"
            f"**GitHub link:** **[LINK]({gh_link})**"
        )
    else:
        out_ = "`Not documented.`"
    trigg = Config.CMD_TRIGGER
    return out_.format(tr=trigg)


def navigation_buttons(currently_at: str, start: bool, end: bool, index: int) -> List[InlineKeyboardButton]:
    buttons = []
    if not start:
        buttons.append(InlineKeyboardButton(text="<<", callback_data=f"ihelp_{currently_at}{index}_previous_{index-1}"))
    buttons.append(InlineKeyboardButton(text="Back", callback_data=f"ihelp_{currently_at}{index}_back_0"))
    if not end:
        buttons.append(InlineKeyboardButton(text=">>", callback_data=f"ihelp_{currently_at}{index}_next_{index+1}"))
    return buttons
