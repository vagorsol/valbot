import discord
from discord.ext import commands
import requests
import os
from bs4 import BeautifulSoup
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", description="Just a server helper bot!", intents = intents)

class MyClient(discord.Client):
    
    async def on_ready():
        print("Starting up!")

    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None: 
            to_send = f'Welcome {member.mention} to {guild.name}!\n'
            + 'Please read the rules first at <#1011466566572969984>'
            + 'and then assign yourself roles at {#1011108293076324353} and introduce yourself at <#1011794135633629294>!\n'
            + 'Enjoy your time here!'
            await guild.system_channel.send(to_send)

    async def on_raw_reaction_add(self, payload):
        ''' Handles specific actions for when, in certain channels, a particular emoji reaction occurs
            Params: payload (the emoji that was reacted with)
        '''
        pronouns_msgID = 1011109559982628885

        guild = client.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)

        # pin messages
        if payload.emoji.name == "📌":
            channel = client.get_channel(payload.channel_id)

            message = await channel.fetch_message(payload.message_id)
            reaction = discord.utils.get(message.reactions, emoji = payload.emoji.name)
            
            # sees how many pin reactions are there and if they are a certain number, pin the message
            # (to change reaction requirement but for now since i'm testing there's only me)
            if reaction and reaction.count >= 1:
                await message.pin()

        # assign pronoun roles
        if str(payload.emoji) == "🌠" and payload.message_id == pronouns_msgID:
            added = discord.utils.get(guild.roles, name="they/them")
            if added not in user.roles:
                await user.add_roles(added)

        if str(payload.emoji) == "✨" and payload.message_id == pronouns_msgID:
            added = discord.utils.get(guild.roles, name="she/her")
            if added not in user.roles:
                await user.add_roles(added)
            
        if str(payload.emoji) == "⭐" and payload.message_id == pronouns_msgID:
            added = discord.utils.get(guild.roles, name="he/him")
            if added not in user.roles:
                await user.add_roles(added)
        
        if str(payload.emoji) == "🌃" and payload.message_id == pronouns_msgID:
            added = discord.utils.get(guild.roles, name="ask my pronouns")
            if added not in user.roles:
                await user.add_roles(added)

    async def on_raw_reaction_remove(self, payload):
        '''Handles specific actions for when particular emojis are removed
            Params: payload (the emoji that was reacted with)
        '''
        pronouns_msgID = 1011109559982628885

        guild = client.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)

        # pin messages
        if payload.emoji.name == "📌":
            channel = client.get_channel(payload.channel_id)

            message = await channel.fetch_message(payload.message_id)
            reaction = discord.utils.get(message.reactions, emoji = payload.emoji.name)
            
            # sees how many pin reactions are there and if they are under certain number, unpin the message
            if reaction and reaction.count < 1:
                await message.unpin()

        # unassign pronoun roles
        if str(payload.emoji) == "🌠" and payload.message_id == pronouns_msgID:
            added = discord.utils.get(guild.roles, name="they/them")
            if added in user.roles:
                await user.remove_roles(added)

        if str(payload.emoji) == "✨" and payload.message_id == pronouns_msgID:
            added = discord.utils.get(guild.roles, name="she/her")
            if added in user.roles:
                await user.remove_roles(added)
            
        if str(payload.emoji) == "⭐" and payload.message_id == pronouns_msgID:
            added = discord.utils.get(guild.roles, name="he/him")
            if added in user.roles:
                await user.remove_roles(added)
        
        if str(payload.emoji) == "🌃" and payload.message_id == pronouns_msgID:
            added = discord.utils.get(guild.roles, name="ask my pronouns")
            if added in user.roles:
                await user.remove_roles(added)

    async def on_message(self, message):

        if message.author == self.user:
            return

        message = message.content.lower()

        # if a link from AO3 is sent
        if("https://archiveofourown.org/works/") in message:
            print("Attempting to read AO3 link now!")
            
            # get the url
            linkPos = message.find("https://archiveofourown.org/works/")
            newLine = message[linkPos:len(message.content)]

            # checking to see if any additional text is placed after the link
            # if so, trim it
            if " " in newLine:
                endPos = newLine.find(" ") + linkPos
            else:
                endPos = len(message.content)
            
            print(endPos)
            url = message.content[linkPos:endPos]
            print(url)

            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # handles finding and processing tags
            def archiveTags(tag_name):
                l = soup.find("dd",{"class":tag_name})
                ret = ""
                count = 0 # this makes the nice commans happen

                # get all the tags
                for i in l.findAll("a"):
                    if count > 0:
                        ret = ret + (", " + (i.text))
                    else:
                        ret = ret + (i.text)
                    count += 1

                return ret

            # reads the information that are classes 
            # (I am assuming, potes your code readability sucks ass (affectionate))
            def archiveBoth(start, category_name):
                l = soup.find(start, {"class": category_name})
                return(l.text)

            # reads modules
            def archiveMod(start, module_name):
                l = soup.find(start, {"class": module_name})
                ret = l.find("blockquote",{"class": "userstuff"})
                return(ret.text)
            
            # http_response 200 = OK
            print(resp.status_code)

            # Reads the link and pulls summary information from it
            try:
                author = "By " + archiveBoth("h3","byline heading")
                author = ' '.join(author.splitlines())

                embed=discord.Embed(title=archiveBoth("h2","title heading"), url=url, description=(author), color=0xff2424)
                embed.set_thumbnail( url="https://archiveofourown.org/images/ao3_logos/logo.png")
                embed.set_author(name=("Archive Of Our Own"), icon_url="https://archiveofourown.org/images/ao3_logos/logo.png")
                embed.add_field(name="Rating:", value=(archiveTags("rating tags")), inline=True)
                embed.add_field(name="Warning:", value=(archiveTags("warning tags")), inline=True)

                try: 
                    embed.add_field(name="Categories:", value=(archiveTags("category tags")), inline=True)
                except:
                    x = "y"

                embed.add_field(name="Fandoms:", value=(archiveTags("fandom tags")), inline=False)

                try: 
                    embed.add_field(name="Relationships:", value=(archiveTags("relationship tags")), inline=False)
                except:
                    x = "y"
                
                embed.add_field(name="Characters:", value=(archiveTags("character tags")), inline=False)
                embed.add_field(name="Additional tags:", value=(archiveTags("freeform tags")), inline=False)

                try:
                    embed.add_field(name="Summary:", value=(archiveMod("div","summary module")), inline=False)
                except:
                    x = "y"
                
                try: 
                    embed.add_field(name="Series:", value=(archiveTags("series")), inline=False)
                except:
                    x = "y"
                    
                embed.set_footer(text="Words: " + archiveBoth("dd","words") + " | Chapters: "+ archiveBoth("dd","chapters")+ " | Published: "+ archiveBoth("dd","published"))

                await message.channel.sent(embed = embed)
            except:
                # if the link is unreadable, throw an error message
                await message.channel.send("Something went wrong in transit! Please verify that the link you sent is valid!")

keep_alive()
client = MyClient(intents = intents)
token = os.environ.get("bot token")
client.run(token)