# AllDebrid API plugin By Ryuk

import os

import aiohttp
from venom import venom, Config, MyMessage
from venom.helpers.venom_tools import plugin_name, post_tg

HELP = Config.HELP[plugin_name(__name__)] = {"type": "fun", "commands": []}
HELP["commands"].extend(
    [
        {
            "command": "unrestrict",
            "flags": {"-save": "to save link in servers"},
            "about": "Unrestrict Links or Magnets on Alldebrid",
            "syntax": "{tr}unrestrict [www.example.com] or [magnet]",
        },
        {
            "command": "torrents",
            "about": "Get singla magnet info or last magnet info using id",
            "flags": {"-s": "-s {id} for status", "-l": "limited number of results you want, defaults to 1"},
            "syntax": "\n{tr}torrents\n{tr}torrents -s 12345\n{tr}torrents -l 10",
        },
        {   "command": "del_t",
            "about": "Delete the previously unrestricted Torrent",
            "syntax": "{tr}del_t 123456\n{tr}del_t 123456 78806"
        },
    ]
)


# Your Alldbrid App token
KEY = os.environ.get("DEBRID_TOKEN")

TEMPLATE = """
<b>Name</b>: <i>{name}</i>
Status: <i>{status}</i>
ID: {id}
Size: {size}
{uptobox}"""


# Get response from api and return json or the error
async def get_json(endpoint: str, query: dict):
    if not KEY:
        return "API key not found."
    api = "https://api.alldebrid.com/v4" + endpoint
    params = {"agent": "bot", "apikey": KEY, **query}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=api, params=params) as ses:
            try:
                json = await ses.json()
                return json
            except Exception as e:
                return str(e)


# Unlock Links or magnets
@venom.trigger("unrestrict")
async def debrid(_, message: MyMessage):
    if not (link_ := message.filtered_input):
        return await message.reply("Give a magnet or link to unrestrict.", quote=True)
    for i in link_.split():
        link = i
        if link.startswith("http"):
            if "-save" not in message.flags:
                endpoint = "/link/unlock"
                query = {"link": link}
            else:
                endpoint = "/user/links/save"
                query = {"links[]": link}
        else:
            endpoint = "/magnet/upload"
            query = {"magnets[]": link}
        unrestrict = await get_json(endpoint=endpoint, query=query)
        if not isinstance(unrestrict, dict) or "error" in unrestrict:
            return await message.reply(unrestrict, quote=True)
        if "-save" in message.flags:
            await message.reply("Link Successfully Saved.", quote=True)
        else:
            if not link.startswith("http"):
                data = unrestrict["data"]["magnets"][0]
            else:
                data = unrestrict["data"]
            name_ = data.get("filename", data.get("name", ""))
            id_ = data.get("id")
            size_ = round(int(data.get("size", data.get("filesize", 0))) / 1000000)
            ready_ = data.get("ready", "True")
            ret_str = f"""Name: **{name_}**\nID: `{id_}`\nSize: **{size_} mb**\nReady: __{ready_}__"""
            await message.reply(ret_str, quote=True)


# Get Status via id or Last 5 torrents
@venom.trigger("torrents")
async def torrents(_, message: MyMessage):
    endpoint = "/magnet/status"
    query = {}

    if "-s" in message.flags and "-l" in message.flags:
        return await message.reply("can't use two flags at once", quote=True)

    if "-s" in message.flags:
        if not (input_ := message.filtered_input):
            return await message.reply("ID required with -s flag", quote=True)

        query = {"id": input_}

    json = await get_json(endpoint=endpoint, query=query)
    if not isinstance(json, dict) or "error" in json:
        return await message.reply(json, quote=True)

    data = json["data"]["magnets"]
    if not isinstance(data, list):
        data = [data]

    ret_str_list = []
    limit = 1
    if "-l" in message.flags:
        limit = int(message.filtered_input)

    for i in data[0:limit]:
        status = i.get("status")
        name = i.get("filename")
        id = i.get("id")
        downloaded = ""
        uptobox = ""
        if status == "Downloading":
            downloaded = f"""<i>{round(int(i.get("downloaded",0))/1000000)}</i>/"""
        size = f"""{downloaded}<i>{round(int(i.get("size",0))/1000000)}</i> mb"""
        if link := i.get("links"):
            uptobox = "<i>UptoBox</i>: \n[ " + "\n".join([f"""<a href={z.get("link","")}>{z.get("filename","")}</a>""" for z in link]) + " ]"
        ret_str_list.append(ret_val := TEMPLATE.format(name=name, status=status, id=id, size=size, uptobox=uptobox))

    ret_str = "<br>".join(ret_str_list)
    if len(ret_str) < 4096:
        await message.reply(ret_str, quote=True)
    else:
        await message.reply(post_tg("Magnets", ret_str.replace("\n", "<br>")), disable_web_page_preview=True, quote=True)


# Delete a Magnet
@venom.trigger("del_t")
async def delete_torrent(_, message: MyMessage):
    endpoint = "/magnet/delete"
    if not (id := message.filtered_input):
        return await message.reply("Enter an ID to delete")
    for i in id.split():
        json = await get_json(endpoint=endpoint, query={"id": i})
        await message.reply(str(json), quote=True)
