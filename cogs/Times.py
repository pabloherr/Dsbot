import datetime
import random
from discord.ext import commands, tasks
from database import db_client
from tools import random_pipo

class Times(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mongo_client = db_client
        self.db = self.mongo_client["discord"] 
        self.daily_pipo_shop.start()
        self.daily_obj_shop.start()
        self.mega_pipo.start()
        self.all_pipos_restore.start()
        self.wild_restore.start()
    
    def cog_unload(self):     
        self.daily_pipo_shop.cancel()
        self.daily_obj_shop.cancel()
        self.mega_pipo.cancel()
        self.all_pipos_restore.cancel()
        self.wild_restore.cancel()
    
    # Restock the shop every 24 hours
    @tasks.loop(hours=1)
    async def daily_pipo_shop(self):
        if not self.db["time"].find_one({"id": "shop"}):
            self.db["time"].insert_one({"id": "shop", "time": datetime.datetime.now()})
        if self.db["time"].find_one({"id": "shop"})["time"] < datetime.datetime.now():
            self.db["time"].update_one({"id": "shop"}, {"$set": {"time": datetime.datetime.now() + datetime.timedelta(hours=24)}})
            self.db["pipo_shop"].delete_many({})
            for i in range(6):
                pipo = await random_pipo()
                self.db["pipo_shop"].insert_one(pipo)
    
    
    # Restock the item shop every 3 hour
    @tasks.loop(minutes=10)
    async def daily_obj_shop(self):
        if not self.db["time"].find_one({"id": "obj_shop"}):
            self.db["time"].insert_one({"id": "obj_shop", "time": datetime.datetime.now()})
        if self.db["time"].find_one({"id": "obj_shop"})["time"] < datetime.datetime.now():
            self.db["time"].update_one({"id": "obj_shop"}, {"$set": {"time": datetime.datetime.now() + datetime.timedelta(hours=3)}})
            self.db["obj_shop"].delete_many({})
            items = ["potions", "super_potions", "hyper_potions", "max_potions", "passive_reroll", "passive_elixir"]
            numbers = [random.randint(1, 50) for _ in range(len(items)-1)]
            while sum(numbers) > 50:
                numbers = [random.randint(1, 50) for _ in range(len(items)-1)]
            numbers.append(50 - sum(numbers))
            for i in range(len(items)):
                if items[i] == "potions":
                    price = 5
                elif items[i] == "super_potions":
                    price = 10
                elif items[i] == "hyper_potions":
                    price = 15
                elif items[i] == "max_potions":
                    price = 30
                elif items[i] == "passive_elixir":
                    price = 60
                elif items[i] == "passive_reroll":
                    price = 100
                self.db["obj_shop"].insert_one({"name": items[i], "stock": numbers[i], "price": price})
    
    # Delete the wild pipos every 10 minutes
    @tasks.loop(minutes=1)
    async def wild_restore(self):
        if not self.db["time"].find_one({"id": "wild_restore"}):
            self.db["time"].insert_one({"id": "wild_restore", "time": datetime.datetime.now()})
        if self.db["time"].find_one({"id": "wild_restore"})["time"] < datetime.datetime.now():
            self.db["time"].update_one({"id": "wild_restore"}, {"$set": {"time": datetime.datetime.now() + datetime.timedelta(minutes=10)}})
            self.db["wild_pipos"].delete_many({})
    
    # Restore all pipos every 10 minutes
    @tasks.loop(minutes=10)
    async def all_pipos_restore(self):
        if not self.db["time"].find_one({"id": "all_pipos_restore"}):
            self.db["time"].insert_one({"id": "all_pipos_restore", "time": datetime.datetime.now()})
        if self.db["time"].find_one({"id": "all_pipos_restore"})["time"] < datetime.datetime.now():
            self.db["time"].update_one({"id": "all_pipos_restore"}, {"$set": {"time": datetime.datetime.now() + datetime.timedelta(hours=1)}})
            user = self.db["users"].find()
            for u in user:
                for pipo in u["pipos"]:
                    pipo["hp"] = pipo["max_hp"]
                    self.db["users"].update_one({"id": u["id"]}, {"$set": {"pipos": u["pipos"]}})
    
    # Weekly wild mega pipo
    @tasks.loop(hours=1)
    async def mega_pipo(self):
        if not self.db["time"].find_one({"id": "mega_pipo"}):
            self.db["time"].insert_one({"id": "mega_pipo", "time": datetime.datetime.now()})
        if self.db["time"].find_one({"id": "mega_pipo"})["time"] < datetime.datetime.now():
            self.db["time"].update_one({"id": "mega_pipo"}, {"$set": {"time": datetime.datetime.now() + datetime.timedelta(hours=168)}})
            if  self.collection2.count_documents({}) > 0:
                self.collection2.delete_many({})
            mega_zone = ["megaforest", "megadesert", "megamountain"] 
            for zone in mega_zone:
                pipo = await wild(zone)
                self.collection2.insert_one(pipo)
                self.collection2.update_one({"name": pipo["name"]}, {"$set": {"name": f"Mega {pipo['name']}"}})
    


async def setup(client):
    await client.add_cog(Times(client))

