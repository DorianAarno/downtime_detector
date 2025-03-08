from disnake import MessageInteraction, ui

from core.embeds import error

class SelectionMenu(ui.StringSelect):
    def __init__(self, options):
        super().__init__(max_values=1, min_values=1, options=options)

    async def callback(self, inter: MessageInteraction) -> None:
        if inter.author.id != self.view.author_id:
            return await inter.send(embed=error("You cannot interact with this button."))
        await inter.response.defer()
        await inter.delete_original_message()
        self.view.value = self.values[0]
        self.view.stop()
        