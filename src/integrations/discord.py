"""
Bot Discord pour Orlyne
"""

import discord
from discord.ext import commands
import logging
from typing import Optional, Dict, Any
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class DiscordBot:
    """Bot Discord pour Orlyne"""
    
    def __init__(self, token: str, orlyne_url: str = "http://localhost:8000"):
        self.token = token
        self.orlyne_url = orlyne_url
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        self.setup_commands()
    
    def setup_commands(self):
        """Configure les commandes du bot"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'Bot Discord connecté en tant que {self.bot.user}')
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name="!help pour les commandes"
                )
            )
        
        @self.bot.command(name='ask', help='Pose une question à Orlyne')
        async def ask(ctx, *, question):
            async with ctx.typing():
                response = await self.query_orlyne(question)
                # Discord a une limite de 2000 caractères
                if len(response) > 1900:
                    response = response[:1900] + "..."
                await ctx.reply(f"**Orlyne:** {response}")
        
        @self.bot.command(name='code', help='Exécute du code')
        async def code(ctx, language, *, code_block):
            # Extraction du code du bloc Discord
            if code_block.startswith('```'):
                code_block = code_block.strip('`')
                if '\n' in code_block:
                    lines = code_block.split('\n')
                    if lines[0] in ['python', 'js', 'java', 'cpp']:
                        language = lines[0]
                        code_block = '\n'.join(lines[1:])
            
            async with ctx.typing():
                result = await self.execute_code(code_block, language)
                
                embed = discord.Embed(
                    title=f"Exécution {language}",
                    color=0x00ff00 if result['success'] else 0xff0000
                )
                
                if result.get('output'):
                    embed.add_field(
                        name="Sortie",
                        value=f"```\n{result['output'][:1000]}```",
                        inline=False
                    )
                
                if result.get('error'):
                    embed.add_field(
                        name="Erreur",
                        value=f"```\n{result['error'][:1000]}```",
                        inline=False
                    )
                
                await ctx.reply(embed=embed)
        
        @self.bot.command(name='explain', help='Explique un concept')
        async def explain(ctx, *, concept):
            async with ctx.typing():
                response = await self.query_orlyne(f"Explique moi {concept} simplement")
                await ctx.reply(f"**Orlyne:** {response[:1900]}")
        
        @self.bot.command(name='joke', help='Raconte une blague')
        async def joke(ctx):
            async with ctx.typing():
                response = await self.query_orlyne("Raconte une blague de dev")
                await ctx.reply(f"**Orlyne:** {response}")
        
        @self.bot.command(name='helpme', help='Aide détaillée')
        async def helpme(ctx):
            embed = discord.Embed(
                title="Commandes Orlyne",
                description="Voici les commandes disponibles",
                color=0x6366f1
            )
            
            embed.add_field(
                name="!ask <question>",
                value="Pose une question à Orlyne",
                inline=False
            )
            embed.add_field(
                name="!code <langage> ```code```",
                value="Exécute du code",
                inline=False
            )
            embed.add_field(
                name="!explain <concept>",
                value="Explique un concept",
                inline=False
            )
            embed.add_field(
                name="!joke",
                value="Raconte une blague",
                inline=False
            )
            embed.add_field(
                name="!translate <lang> ```code```",
                value="Traduit du code",
                inline=False
            )
            
            await ctx.reply(embed=embed)
        
        @self.bot.command(name='translate')
        async def translate(ctx, target_lang, *, code_block):
            # Extraction du code
            if code_block.startswith('```'):
                code_block = code_block.strip('`')
                if '\n' in code_block:
                    lines = code_block.split('\n')
                    source_lang = lines[0]
                    code = '\n'.join(lines[1:])
                else:
                    source_lang = 'python'
                    code = code_block
            else:
                source_lang = 'python'
                code = code_block
            
            async with ctx.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.orlyne_url}/api/code/translate",
                        json={
                            "code": code,
                            "from_language": source_lang,
                            "to_language": target_lang
                        }
                    ) as resp:
                        result = await resp.json()
                        
                        if result.get('success'):
                            embed = discord.Embed(
                                title=f"Traduction {source_lang} → {target_lang}",
                                color=0x6366f1
                            )
                            embed.add_field(
                                name="Résultat",
                                value=f"```{target_lang}\n{result['translated_code'][:1500]}```",
                                inline=False
                            )
                            await ctx.reply(embed=embed)
                        else:
                            await ctx.reply(f"❌ {result.get('error', 'Erreur inconnue')}")
    
    async def query_orlyne(self, prompt: str) -> str:
        """Interroge Orlyne via l'API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.orlyne_url}/api/chat",
                    json={"prompt": prompt}
                ) as resp:
                    data = await resp.json()
                    return data.get('response', "Désolée, je n'ai pas pu répondre 😅")
        except Exception as e:
            logger.error(f"Erreur requête Orlyne: {e}")
            return "Désolée, je rencontre des problèmes de connexion 😓"
    
    async def execute_code(self, code: str, language: str) -> Dict[str, Any]:
        """Exécute du code via l'API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.orlyne_url}/api/code/execute",
                    json={
                        "code": code,
                        "language": language
                    }
                ) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"Erreur exécution code: {e}")
            return {"success": False, "error": str(e)}
    
    def run(self):
        """Démarre le bot"""
        self.bot.run(self.token)