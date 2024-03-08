import discord
from discord.ext import commands
from database import db_client
from models.user import User


class Users(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"] 
        self.collection = self.db["users"] 
    
    # Command to create a new user
    @commands.command()
    async def join(self, ctx):
        if self.collection.find_one({"id": ctx.author.id}) is not None:
            await ctx.send('User already exists!')
            return
        user = User(id = ctx.author.id, name = ctx.author.name)
        self.collection.insert_one(user.dict())
        user = self.collection.find_one({"id": ctx.author.id})
        await ctx.send(f'Welcome {user["name"]}!')
        await ctx.send('Use !shop to buy a pipo')
    
        #Command to show the leaderboards
    @commands.command()
    async def leaderboard(self, ctx):
        leaderboard = self.db["leaderboard"].find().sort("points", -1)
        for user in leaderboard:
            await ctx.send(f"1 | {user['name']} - {user['points']} points")
    
    # Command to show the user's profile
    @commands.command()
    async def profile(self, ctx):
        user = self.collection.find_one({"id": ctx.author.id})
        if user is None:
            await ctx.send('User does not exist!')
            return
        if user['defender'] is None:
            defender = "None"
        else:
            defender = user['defender']['name']
        await ctx.send(f"User: {user["name"]}\n Gold: {user['gold']} \nDefender: {defender} \nPipos: {len(user['pipos'])}")
    
    # Command to show the user's pipos
    @commands.command()
    async def pipos(self, ctx):
        lvl = {1:0, 2:10, 3:40, 4:80, 5:160, 6:320, 7:640, 8:1280, 9:2560, 10:5120}
        user = self.collection.find_one({"id": ctx.author.id})
        if user is None:
            await ctx.send('User does not exist!')
            return
        if len(user['pipos']) == 0:
            await ctx.send('No pipos!')
            return
        for pipo in user['pipos']:
            exp = lvl[pipo['lvl']+1]
            await ctx.send(f"{pipo['name']} ({pipo['rarity']}) | Lvl:{pipo['lvl']} exp: {pipo['exp']}/{exp} \n{pipo['hp']} HP \n{pipo['attack']} ATK \n{pipo['defense']} DEF \n{pipo['speed']} SPD \nPassive: {pipo['passive']}")

    # Command to see other user's profile
    @commands.command()
    async def other_profile(self, ctx):
        user = self.collection.find_one({"id": ctx.message.mentions[0].id})
        if user is None:
            await ctx.send('User does not exist!')
            return
        if user['defender'] is None:
            defender = "None"
        else:
            defender = user['defender']['name']
        await ctx.send(f"User: {ctx.message.mentions[0].name}\nGold: {user['gold']} \nDefender: {defender} \nPipos: {len(user['pipos'])}")

    # Command to see other user's pipos
    @commands.command()
    async def other_pipos(self, ctx):
        user = self.collection.find_one({"id": ctx.message.mentions[0].id})
        if user is None:
            await ctx.send('User does not exist!')
            return
        if len(user['pipos']) == 0:
            await ctx.send('No pipos!')
            return
        for pipo in user['pipos']:
            await ctx.send(f"Lvl:1 / {pipo['name']} / {pipo['rarity']} \n{pipo['hp']} HP \n{pipo['attack']} ATK \n{pipo['defense']} DEF \n{pipo['speed']} SPD \n Passive: {pipo['passive']}")

    # Command to set a pipo as the user's defender
    @commands.command()
    async def set_defender(self, ctx, pipo_name: str):
        user = self.collection.find_one({"id": ctx.author.id})
        pipo = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        if pipo is None:
            await ctx.send("Pipo not found")
            return
        user["defender"] = pipo
        self.collection.update_one({"id": ctx.author.id}, {"$set": user})
        await ctx.send(f"{pipo_name} set as defender")

async def setup(client):
    await client.add_cog(Users(client))