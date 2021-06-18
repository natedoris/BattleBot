from discord import embeds

# Fancy canned messages
def error(message):
    error = embeds.Embed()
    error.colour = 0xe74c3c
    #error.set_thumbnail(url=".\\embeddable\\images\\error.png")
    error.add_field(name="Error", value=message, inline=False)
    return error


def warning(message):
    warning = embeds.Embed()
    warning.colour = 0xffff00
    # error.thumbnail = ".\\images\\thumbnails\\error.png"
    warning.add_field(name="Warning", value=message, inline=False)

    return warning


def base(message):
    e = embeds.Embed()
    e.colour = 0x2ecc71
    # error.thumbnail = ".\\images\\thumbnails\\error.png"
    e.add_field(name="BattleBot", value=message, inline=False)
    return e

