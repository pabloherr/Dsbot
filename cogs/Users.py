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
        

async def setup(client):
    await client.add_cog(Users(client))