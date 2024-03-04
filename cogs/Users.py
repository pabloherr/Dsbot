import discord
from discord.ext import commands

class Users(commands.Cog):
    def __init__(self, client):
        self.client = client
    


    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello!')

    @commands.command()
    async def setinfo(self, ctx, *, info):
        discord_id = str(ctx.message.author.id)

        # Verificar si el usuario ya tiene información almacenada
        user = self.users.find_one({'discord_id': discord_id})
        if user is not None:
            # Actualizar la información del usuario
            self.users.update_one({'discord_id': discord_id}, {'$set': {'info': info}})
        else:
            # Almacenar la información del usuario
            self.users.insert_one({'discord_id': discord_id, 'info': info})

        await ctx.send('Tu información ha sido almacenada con éxito!')

    @commands.command()
    async def getinfo(self, ctx):
        discord_id = str(ctx.message.author.id)

        # Obtener la información del usuario
        user = self.users.find_one({'discord_id': discord_id})

        if user is not None:
            await ctx.send(f'Tu información es: {user["info"]}')
        else:
            await ctx.send('No tienes ninguna información almacenada.')

#def setup(client):  
#    client.add_cog(Users(client))
async def setup(client):
    await client.add_cog(Users(client))