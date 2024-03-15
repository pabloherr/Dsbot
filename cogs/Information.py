from discord.ext import commands
from database import db_client

class Information(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"]
        

    @commands.command(description="Shows the effect of the passives")
    async def passive(self, ctx, passive = None):
        passives = {"Invulnerable": "Your pipo has a 33'%' of chance of taking no damage",
                    "Feel no pain": "Your pipo has a 50'%' of chance of reducing the damage by 1 for each damage incoming",
                    "Lethal Hits": "Your pipo's attacks have the chance of dealing 25'%' or 50'%' more damage",
                    "Fight First": "Your pipo have the chance to increase it's speed by 1, 2 or 3",
                    "Sustained Hits": "Your pipo has 25'%' of chance of making a second attack",
                    "Parry": "Your pipo has 20'%' of chance of reflecting 50'%' of incuming damage",
                    "Rapid Metabolism": "Your pipo has 25'%' of chance of increasing one of your stats by 1",
                    "Regeneration": "Your pipo has 66'%' of chance of healing 1 HP eche round",
                    "Void": "Your pipo have 50'%' of chance to desable the passive of the enemy for the next turn",
                    "Berserker": "Your pipo's attack increases by 25% when it is injured, and by 50% when it is below half HP",
                    "Healing Touch": "Your pipo has 25'%' of chance that instead of attacking, he heals an ally or himself for an amount equal to half his attack"
                    }
        if passive == None:
            for i in passives:
                await ctx.send(f"{i}: {passives[i]}")
        else:
            await ctx.send(f"{passive}: {passives[passive]}")
    
    
    @commands.command(description="Shows the effect of the out of combat objects")
    async def out_of_combat_objects(self, ctx, object = None):
        out_of_combat_objects = {"Potion": "Heals 3-5 HP",
                                "Super Potion": "Heals 6-10 HP",
                                "Hyper Potion": "Heals 11-20 HP",
                                "Max Potion": "Heals all the HP",
                                "Passive Reroll": "Rerolls the passive of a pipo",
                                "Passive Elixir":"Give a passive to a pipo that doesn't have one"
                                }
        if object == None:
            for i in out_of_combat_objects:
                await ctx.send(f"{i}: {out_of_combat_objects[i]}")
        else:
            await ctx.send(f"{object}: {out_of_combat_objects[object]}")
    
    
    @commands.command(description="Shows the effect of the in combat objects")
    async def in_combat_objects(self, ctx, object = None):
        in_combat_objects = {"Beer": "Your pipo has 20'%' of chance of healing 1 HP",
                            "Poison Dart": "The pipo you attack have a 60'%' of chance of not being able to heal itself",
                            "Tricked Coin": "You always attack first when your pipo's speed is equal to the enemy's speed",
                            "Training Sheet": "Increase the experience gained by 25'%'",
                            "Dancing Shoes": "When the hp of the pipo that is usign this item drops below 50'%' it changes places with another pipo of it's team",
                            "Dinamite Vest": "When the pipo that is using this item dies, the enemy that killed it receives damage equal to the pipo's attack",
                            "Mortar": "When the pipo that is using this item attacks, it has the same chance to attack the enemy's tank as the enemy's dps",
                            "Pipo's Sword": "Your pipo's attack increase by 1",
                            "Pipo's Shield": "Your pipo's defense increase by 1",
                            "Pipo's Boots": "Your pipo's speed increase by 1"
                            }
        if object == None:
            for i in in_combat_objects:
                await ctx.send(f"{i}: {in_combat_objects[i]}")
        else:
            await ctx.send(f"{object}: {in_combat_objects[object]}")
            
async def setup(client):
    await client.add_cog(Information(client))