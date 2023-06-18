# AllDebrid API plugin By Ryuk

import aiohttp

from venom import MyMessage, venom, Config

KEY = Config.DEBRID_TOKEN
WEB_HISTORY = Config.WEB_HISTORY
WEB_LINK = Config.WEB_LINK
WEB_TORRENT = Config.WEB_TORRENT
WEBDAV = Config.WEBDAV_URL


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
@venom.trigger('unrestrict')
async def debrid(message: MyMessage):
    if not ( link_ := message.filtered_input ):
        return await message.reply("Give a magnet or link to un-restrict.", quote=True)
    for i in link_.split():
        link = i
        if link.startswith("http"):
            if "-save" not in message.flags:
                endpoint = "/link/unlock"
                query = {"link": link}
                d_link = WEB_HISTORY
            else:
                endpoint = "/user/links/save"
                query = {"links[]": link}
                d_link = WEB_LINK
        else:
            endpoint = "/magnet/upload"
            query = {"magnets[]": link}
            d_link = WEB_TORRENT
        unrestrict = await get_json(endpoint=endpoint, query=query)
        if not isinstance(unrestrict, dict) or "error" in unrestrict:
            return await message.reply(unrestrict, quote=True)
        if "-save" in message.flags:
            await message.reply("Link Successfully Saved.", quote=True)
        else:
            if not link.startswith("http"):
                data = unrestrict["data"]["magnets"][0]
                name_ = data.get("name")
                id_ = data.get("id")
                size_ = round(int(data.get("size", 0)) / 1000000)
                ready_ = data.get("ready")
            else:
                data = unrestrict["data"]
                name_ = data.get("filename")
                id_ = data.get("id")
                size_ = round(int(data.get("filesize", 0)) / 1000000)
                ready_ = data.get("ready", "True")
                d_link = d_link + name_ if d_link else ""
            ret_str = f"""Name: **{name_}**\nID: `{id_}`\nSize: **{size_} mb**\nReady: __{ready_}__\nLink: {d_link.replace(" ","%20")}"""
            await message.reply(ret_str, quote=True)


# Get Status via id or Last 5 torrents
@venom.trigger('torrents')
async def torrents(message: MyMessage):
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
        status = data.get("status")
        ret_val = f"""
\n**Name**: __{data.get("filename")}__
Status: __{status}__
ID: ```{data.get("id")}```
Size: """
        if status == "Downloading":
            ret_val += f"""__{round(int(data.get("downloaded",0))/1000000)}__/"""
        ret_val += f"""__{round(int(data.get("size",0))/1000000)}__ mb"""
        if link := data.get("links"):
            ret_val += "\n__UptoBox__: \n[ " + "\n".join([ f"""<a href={z.get("link","")}>{z.get("filename","")}</a>""" for z in link]) + " ]"
        ret_val += f"\n\nSite: {WEB_TORRENT}" if WEB_TORRENT else ""
    else:
        ret_val = ""
        limit = 1
        if "-l" in message.flags:
            limit = int(message.filtered_input)
        for i in data[0:limit]:
            status = i.get("status")
            ret_val += f"""
\nName: __{i.get("filename")}__
Status: __{status}__
ID: ```{i.get("id")}```
Size: """
            if status == "Downloading":
                ret_val += f"""__{round(int(i.get("downloaded",0))/1000000)}__/"""
            ret_val += f"""__{round(int(i.get("size",0))/1000000)}__ mb"""
            if link := i.get("links"):
                ret_val += "\n__UptoBox__: \n[ " + "\n".join([ f"""<a href={z.get("link","")}>{z.get("filename","")}</a>""" for z in link]) + " ]"
        ret_val += f"\n\nSite: {WEB_TORRENT}\n\nWebDav : {WEBDAV}" if WEBDAV and WEB_TORRENT else ""
    await message.reply(ret_val, quote=True)


# Delete a Magnet
@venom.trigger('del_t')
async def delete_torrent(message: MyMessage):
    endpoint = "/magnet/delete"
    if not (id_ := message.filtered_input):
        return await message.reply("Enter an ID to delete")
    for i in id_.split():
        json = await get_json(endpoint=endpoint, query={ "id": i })
        await message.reply(str(json), quote=True)
