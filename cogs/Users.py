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
    
    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello!')
        
    @commands.command()
    async def join(self, ctx):
        if self.collection.find_one({"id": ctx.author.id}) is not None:
            await ctx.send('Usuario ya existe!')
            return
        user = User( id = ctx.author.id)
        self.collection.insert_one(user.dict())
        await ctx.send('Usuario creado!')


    @commands.command()
    async def setinfo(self, ctx, *, info):
        self.collection.update_one({"_id": ctx.author.id}, {"$set": {"info": info}}, upsert=True)
        await ctx.send('Información establecida! por' + ctx.author.mention)

    @commands.command()
    async def getinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_info = self.collection.find_one({"_id": member.id})
        if user_info is not None:
            await ctx.send(self.user_info.get(member.id, 'No se encontró información para este usuario'))
        else:
            await ctx.send('No se encontró información para este usuario')


async def setup(client):
    await client.add_cog(Users(client))