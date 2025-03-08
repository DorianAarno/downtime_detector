from disnake import Member, Status
from disnake.ext.commands import slash_command, Cog

from disnake.ext import tasks

class Events(Cog):
    import main
    def __init__(self, bot: main.MyBot):
        self.bot = bot
        self.status_verifier.start()

    async def get_entity(self, alert_type, alert_entity_id):
        if alert_type == 1:
            entity = self.bot.get_user(alert_entity_id)
            if not entity:
                try:
                    entity = await self.bot.fetch_user(alert_entity_id)
                except:
                    return
        if alert_type == 0:
            entity = self.bot.get_channel(alert_entity_id)
            if not entity:
                try:
                    entity = await self.bot.fetch_channel(alert_entity_id)
                except:
                    return
        
        return entity

    @Cog.listener()
    async def on_presence_update(self, before: Member, after: Member):
        if before.status != after.status and before.bot:  # Only trigger on status changes
            if after.status == Status.offline:
                data = await self.bot.fetchrow("SELECT alert_type, alert_entity_id FROM monitored_bots WHERE guild_id = %s AND bot_user_id = %s AND current_status = %s", before.guild.id, before.id, 1)
                if not data:
                    return
                alert_type, alert_entity_id = data
                entity = await self.get_entity(alert_type, alert_entity_id)
                if not entity:
                    return
                
                await entity.send(
                    content=f":red_circle: {after.mention} has gone offline!"
                )
                await self.bot.execute("UPDATE monitored_bots SET current_status = %s WHERE guild_id = %s AND bot_user_id = %s", 0, before.guild.id, before.id)
            if after.status != Status.offline:
                data = await self.bot.fetchrow("SELECT alert_type, alert_entity_id FROM monitored_bots WHERE guild_id = %s AND bot_user_id = %s AND current_status = %s", before.guild.id, before.id, 0)
                if not data:
                    return
                alert_type, alert_entity_id = data
                entity = await self.get_entity(alert_type, alert_entity_id)
                if not entity:
                    return
                
                await entity.send(
                    content=f":green_circle: {after.mention} is now online!"
                )
                await self.bot.execute("UPDATE monitored_bots SET current_status = %s WHERE guild_id = %s AND bot_user_id = %s", 0, before.guild.id, before.id)

    @tasks.loop(minutes=10)
    async def status_verifier(self):
        await self.bot.wait_until_ready()
        data = await self.bot.fetch("SELECT guild_id, bot_user_id, current_status FROM monitored_bots")
        for entry in data:
            guild_id, bot_user_id, current_status = entry
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            member = guild.get_member(bot_user_id)
            if member:
                new_status = 0 if member.status.name == 'offline' else 1
                if new_status != current_status:
                    await self.bot.execute("UPDATE monitored_bots SET current_status = %s WHERE guild_id = %s AND bot_user_id = %s", new_status, guild_id, bot_user_id)
def setup(bot):
    bot.add_cog(Events(bot))