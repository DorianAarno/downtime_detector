from disnake import *
from disnake.ext.commands import *
from Paginator import CreatePaginator

from core.embeds import error, success, warning
from core.views import ConfirmationView, SelectPreset

class Monitor(Cog):
    import main
    def __init__(self, bot: main.MyBot):
        self.bot = bot
    
    async def cog_slash_command_check(self, inter: ApplicationCommandInteraction):
        if inter.author.guild_permissions.administrator:
            return True
        
        await inter.send(embed=error(f'You need **administrator** permission to use this command.'))
        return False

    @slash_command()
    async def monitor(self, inter: ApplicationCommandInteraction, ):
        pass

    @monitor.sub_command()
    async def add(self, inter: ApplicationCommandInteraction, bot: Member, reminder_type: str = Param(choices={'TextChannel': '2', 'DMs': '1'}), textchannel: TextChannel | NewsChannel = Param(channel_types=[ChannelType.text, ChannelType.news], description="Fill this if you select reminder_type as textchannel", default=None)):
        """
        Add a bot in the monitored list
        """
        if not bot.bot:
            return await inter.send(embed=error("You can only monitor a bot."))
        reminder_type = int(reminder_type)
        if reminder_type == 0 and textchannel == None:
            return await inter.send(embed=error("You need to specify textchannel for this type of reminder."))
            
        data = await self.bot.fetchrow("SELECT guild_id FROM monitored_bots WHERE bot_user_id = %s AND guild_id = %s", bot.id, inter.guild.id)
        if data:
            conf_view = ConfirmationView(inter.author.id)
            await inter.send(embed=warning(f"{bot.mention} is already being monitored, would you like to update it's configuration?"), view=conf_view)
            await conf_view.wait()
            if conf_view.value:
                await self.bot.execute("DELETE FROM monitored_bots WHERE guild_id = %s AND bot_user_id = %s", inter.guild.id, bot.id)
            else:
                return await inter.edit_original_message("Process was cancelled.")
        await self.bot.execute(
            "INSERT INTO monitored_bots(guild_id, bot_user_id, alert_type, alert_entity_id, current_status) VALUES(%s,%s,%s,%s,%s)",
            inter.guild.id,
            bot.id,
            int(reminder_type),
            inter.author.id if reminder_type == 1 else textchannel.id,
            0 if bot.status.name == 'offline' else 1
        )
        await inter.send(embed=success(f"{bot.mention} added to monitored list successfully!"))

    @monitor.sub_command()
    async def remove(self, inter: ApplicationCommandInteraction):
        """
        Remove a bot from monitored list
        """
        data = await self.bot.fetch("SELECT bot_user_id, alert_type, alert_entity_id, added_at FROM monitored_bots WHERE guild_id = %s", inter.guild.id)
        
        embeds = [
            Embed(
                title=":tv: Monitored List",
                description="",
                color=self.bot.brand_color,
            )
        ]
        embeds[-1].set_footer(text="Developed by aarno.dev", icon_url="https://upload.wikimedia.org/wikipedia/commons/c/cc/Circle-icons-dev.svg")
        options = [[]]
        
        for i, entry in enumerate(data):
            bot_user_id, alert_type, alert_entity_id, added_at = entry
            content = f"{i+1}. <@{bot_user_id}> \n> Reminder Type: {'Text Channel' if alert_type == 0 else 'DMs'} \n> Reminder Target: {f'<#{alert_entity_id}>' if alert_type == 0 else f'<@{alert_entity_id}>'} \n"
            
            if (len(embeds[-1].description) + len(content)) >= 4000 or (i%20 if i != 0 else False):
                embeds.append(
                    Embed(
                        description="",
                        color=self.bot.brand_color
                    )
                )
                options.append([])
            
            embeds[-1].description += content
            bot_user = inter.guild.get_member(bot_user_id)
            if bot_user:
                bot_name = bot_user.name
            else:
                bot_name = str(bot_user_id)
            options[-1].append(
                SelectOption(label=f"{i+1}. {bot_name}", value=bot_user_id)
            )
        
        await inter.send(embed=embeds[0], view=SelectPreset(self.bot, inter.author.id, embeds, options))
        
    @monitor.sub_command()
    async def view(self, inter: ApplicationCommandInteraction):
        """
        View all active bots in the monitored list
        """
        data = await self.bot.fetch("SELECT bot_user_id, alert_type, alert_entity_id, added_at FROM monitored_bots WHERE guild_id = %s", inter.guild.id)
        
        embeds = [
            Embed(
                title=":tv: Monitored List",
                description="",
                color=self.bot.brand_color,
            )
        ]
        embeds[-1].set_footer(text="Developed by aarno.dev", icon_url="https://upload.wikimedia.org/wikipedia/commons/c/cc/Circle-icons-dev.svg")
        
        for i, entry in enumerate(data):
            bot_user_id, alert_type, alert_entity_id, added_at = entry
            content = f"{i+1}. <@{bot_user_id}> \n> Reminder Type: {'Text Channel' if alert_type == 0 else 'DMs'} \n> Reminder Target: {f'<#{alert_entity_id}>' if alert_type == 0 else f'<@{alert_entity_id}>'} \n"
            
            if (len(embeds[-1].description) + len(content)) >= 4000 or (i%20 if i != 0 else False):
                embeds.append(
                    Embed(
                        description="",
                        color=self.bot.brand_color
                    )
                )
            
            embeds[-1].description += content

        await inter.send(embed=embeds[0], view=CreatePaginator(embeds, inter.author.id))


def setup(bot):
    bot.add_cog(Monitor(bot))