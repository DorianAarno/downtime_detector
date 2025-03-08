from disnake import ButtonStyle, ui
from core.buttons import PresetButton
from core.selectmenus import SelectionMenu

class ConfirmationView(ui.View):
    def __init__(self, authorid):
        super().__init__(timeout=120.0)
        self.value = None
        self.authorid = authorid

    @ui.button(emoji="✖️", style=ButtonStyle.red)
    async def first_button(self, button, inter):
        if inter.user.id != self.authorid:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        self.value = False
        for button in self.children:
            button.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()

    @ui.button(emoji="✔️", style=ButtonStyle.green)
    async def second_button(self, button, inter):
        if inter.user.id != self.authorid:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        self.value = True
        for button in self.children:
            button.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()

class SelectPreset(ui.View):
    import main

    def __init__(self, bot: main.MyBot, author_id: int, embeds, options):
        super().__init__(timeout=None)
        self.bot = bot
        self.value = None
        self.author_id = author_id
        self.options = options
        self.embeds = embeds
        self.current_embed = 0
        self.add_item(PresetButton(bot, "◀️"))
        self.add_item(PresetButton(bot, "▶️", len(embeds) == 1))
        self.add_item(SelectionMenu(options[self.current_embed]))

