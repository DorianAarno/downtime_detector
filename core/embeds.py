import disnake


def error(description):
    return disnake.Embed(
        description=":x: " + description,
        color=disnake.Color.from_rgb(255, 0, 0),
    )


def success(description):
    return disnake.Embed(
        description="✅ " + description,
        color=disnake.Color.green(),
    )


def warning(description):
    return disnake.Embed(
        description=":warning: " + description,
        color=disnake.Color.yellow(),
    )
