from disnake import ButtonStyle, MessageInteraction, ui

import core.views as views
import core.selectmenus as selectmenu
from core.embeds import error


class PresetButton(ui.Button):
    import main

    def __init__(
        self,
        bot: main.MyBot,
        emoji: str,
        len_embeds: int = 0,
    ):
        super().__init__(
            emoji=emoji,
            style=ButtonStyle.gray,
            disabled=str(emoji) == "◀️" or (str(emoji) == "▶️" and len_embeds == 1),
        )
        self.bot = bot

    async def callback(self, inter: MessageInteraction) -> None:
        await inter.response.defer(ephemeral=True)

        view: views.SelectPreset = self.view
        if inter.author.id != view.author_id:
            return await inter.send(embed=error("You cannot interact with this button."))
        
        if str(self.emoji) == "▶️":
            view.current_embed += 1
            if view.current_embed + 1 == len(view.embeds):
                self.disabled = True
            for child in view.children:
                if isinstance(child, selectmenu.SelectionMenu):
                    continue
                if str(child.emoji) == "◀️":
                    child.disabled = False
        elif str(self.emoji) == "◀️":
            view.current_embed = view.current_embed - 1
            if view.current_embed == 0:
                self.disabled = True
            for child in view.children:
                if isinstance(child, selectmenu.SelectionMenu):
                    continue
                if str(child.emoji) == "▶️":
                    child.disabled = False

        for child in view.children:
            if isinstance(child, selectmenu.SelectionMenu):
                view.remove_item(child)
        view.add_item(selectmenu.SelectionMenu(view.options[view.current_embed]))

        await inter.edit_original_message(
            view=view, embed=view.embeds[view.current_embed]
        )