import discord
from discord.ext import commands
import asyncio
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract
import aiohttp        
import aiofiles
import os.path
import os

from sharedFunctions import printLeaderboard, createLeaderboardEmbed

db = TinyDB('json/db.json') #Database file: stores points of every user.
cfg = TinyDB("json/config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('json/server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
post = TinyDB('json/comments.json') #Comment leaderboard.
priv = TinyDB('json/blacklist.json') #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.
best = TinyDB('json/bestname.json') #name and type of notif
dm = TinyDB('json/deletables.json') #Message deletion for Leaderboards.

for c in cfg:
    bottoken = c['bottoken']
    botname = c['botname']
    support = c['support']
    botver = c['botver']
    prefix = c['prefix']

class Help(commands.Cog):
    """
    How to get support, find out about the bot's commands and more.
    """
    def __init__(self, client):
        self.client = client
        client.remove_command('help')


    @commands.command(pass_context=True)
    @commands.has_permissions(add_reactions=True,embed_links=True)
    async def help(self,ctx,*cog):
        """Gets all cogs and commands of mine."""
        if not cog:
            """Cog listing.  What more?"""
            halp=discord.Embed(title=botname + "'s Commands",
                               description="Use `!help *category*` to find out more about each command!\n_(Don't know where to start? Use ?setup to get everything going!)_\nIf you're in need of assistance, [join our support server](https://discord.gg/RAwfrty)!")
            cogs_desc = ''
            for x in self.client.cogs:
                if (x != "Reaction") and (x != "Management"):
                    cogs_desc += ('💠 _{}_ {}'.format(x,self.client.cogs[x].__doc__)+'\n')
            halp.add_field(name='Categories',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
            cmds_desc = ''
            for y in self.client.walk_commands():
                if not y.cog_name and not y.hidden:
                    cmds_desc += ('{} - {}'.format(y.name,y.help)+'\n')
            await ctx.message.add_reaction(emoji='✉')
            await ctx.message.author.send('',embed=halp)
        else:
            """Helps me remind you if you pass too many args."""
            if len(cog) > 1:
                halp = discord.Embed(title='Error!',description='That is too many a category!',color=discord.Color.red())
                await ctx.message.author.send('',embed=halp)
            else:
                splice = cog[0]
                cog = splice[0].upper() + splice[1:].lower()
                #printing commands of cog
                """Command listing within a cog."""
                found = False
                #finding Cog
                for x in self.client.cogs:
                    #for y in cog:
                    if x == cog: 
                        #making title
                        halp=discord.Embed(title=cog+' - Commands',description=self.client.cogs[cog].__doc__, color=discord.Color.green())
                        print(type(halp))
                        for c in self.client.get_cog(cog).get_commands():
                            if not c.hidden: #if cog not hidden
                                halp.add_field(name=c.name,value=c.help,inline=False)
                        found = True
                if not found:
                    """Reminds you if that cog doesn't exist."""
                    halp = discord.Embed(title='Error!',description='Is "'+cog[0]+'" a valid category?',color=discord.Color.red())
                else:
                    await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('',embed=halp)
                print(type(halp))
        
def setup(client):
    client.add_cog(Help(client))