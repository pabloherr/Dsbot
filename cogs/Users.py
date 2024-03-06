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
            await ctx.send('Usuario ya existe!')
            return
        user = User( id = ctx.author.id)
        self.collection.insert_one(user.dict())
        await ctx.send('Usuario creado!')
    
    # Command to show the user's profile
    @commands.command()
    async def profile(self, ctx):
        user = self.collection.find_one({"id": ctx.author.id})
        if user is None:
            await ctx.send('Usuario no existe!')
            return
        await ctx.send(f"Usuario: {ctx.author.name}\nCash: {user['cash']}\nPipos: {len(user['pipos'])}")
    
    # Command to show the user's pipos
    @commands.command()
    async def pipos(self, ctx):
        user = self.collection.find_one({"id": ctx.author.id})
        if user is None:
            await ctx.send('Usuario no existe!')
            return
        if len(user['pipos']) == 0:
            await ctx.send('No tienes pipos!')
            return
        for pipo in user['pipos']:
            await ctx.send(f"{pipo['name']} {pipo['rarity']} \n{pipo['hp']} HP \n{pipo['attack']} ATK \n{pipo['defense']} DEF \n{pipo['speed']} SPD")


async def setup(client):
    await client.add_cog(Users(client))