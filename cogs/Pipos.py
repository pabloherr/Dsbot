import discord
from discord.ext import commands
from pydantic import BaseModel
from models.pipo import Pipo
import random

pipos_list= []
class Pipos(commands.Cog):
    def __init__(self, client):
        self.client = client



    @commands.command()
    async def create_random_pipo(self,ctx) -> Pipo:
        rarity = random.choice(["common", "uncommon", "rare"])
        if rarity == "common":
            stats = [1, 1, 2, 3]
        elif rarity == "uncommon":
            stats = [1, 1, 2, 4]
        else:
            stats = [2, 2, 3, 4]
        random.shuffle(stats)
        pipo_name = "Pipo_" + str(random.randint(1, 100))

        await ctx.send( Pipo(rarity=rarity, name=pipo_name,
                    hp=5+stats[0], attack=stats[1], 
                    defense=stats[2], speed=stats[3]))

#async def get_pipo(pipo_name: str) -> Pipo:
#    for pipo in pipos_list:
#        if pipo.name == pipo_name:
#            return pipo
#    return None
#
#async def get_pipos() -> list[Pipo]:
#    return pipos_list


async def setup(client):
    await client.add_cog(Pipos(client))