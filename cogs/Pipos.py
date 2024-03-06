import discord
import random
from discord.ext import commands
from pydantic import BaseModel
from database import db_client
from models.pipo import Pipo

class Pipos(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"] 

    # Rename the pipos
    @commands.command()
    async def rename(self, ctx, pipo_name, new_name):
        user = self.db["users"].find_one({"id": ctx.author.id})
        pipo = next((pipo for pipo in user["pipos"] if pipo["name"] == pipo_name), None)
        if pipo is None:
            await ctx.send("Pipo not found")
            return
        pipo["name"] = new_name
        self.db["users"].update_one({"id": ctx.author.id}, {"$set": user})
        await ctx.send(f"{pipo_name} renamed to {new_name}")
        
        
async def setup(client):
    await client.add_cog(Pipos(client))