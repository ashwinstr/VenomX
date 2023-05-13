# raw functions

import random
from typing import Union, List

from pyrogram.raw.base import ForumTopic, Updates
from pyrogram.raw.base.messages import ForumTopics
from pyrogram.raw.functions.channels import GetForumTopics, CreateForumTopic, EditForumTopic
from pyrogram.raw.types import InputChannel

from ..core import client as _client


async def get_topics(client: Union['_client.Venom', '_client.VenomBot'], channel: int) -> List[ForumTopic]:
    """ get topics of conversation """
    chat_ = await client.resolve_peer(channel)
    channel_ = InputChannel(channel_id=chat_.channel_id, access_hash=chat_.access_hash)
    get_topics_ = GetForumTopics(channel=channel_, offset_date=0, offset_topic=0, offset_id=0, limit=5)
    topics: ForumTopics = await client.invoke(get_topics_)
    topics.order_by_create_date = True
    return topics.topics


async def create_topic(client: Union['_client.Venom', '_client.VenomBot'], channel: int, title: str) -> Updates:
    """ create topic in group """
    chat_ = await client.resolve_peer(channel)
    channel_ = InputChannel(channel_id=chat_.channel_id, access_hash=chat_.access_hash)
    create_topic_ = CreateForumTopic(channel=channel_, title=title, random_id=random.randint(10000000, 99999999))
    updates: Updates = await client.invoke(create_topic_)
    return updates


async def lock_topic(client: Union['_client.Venom', '_client.VenomBot'], channel: int, id: int):
    """ lock specified topic in group """
    chat_ = await client.resolve_peer(channel)
    input_channel = InputChannel(channel_id=chat_.channel_id, access_hash=chat_.access_hash)
    manage_topic_ = EditForumTopic(channel=input_channel, topic_id=id, closed=True)
    await client.invoke(manage_topic_)
