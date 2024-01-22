""" thumbnails.py """

from venom import venom, MyMessage


@venom.trigger('sthumb')
async def save_thumbnail(_, message: MyMessage):
    """ save thumbnails """
    await message.edit("Processing...")
