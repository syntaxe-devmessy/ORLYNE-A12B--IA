"""
Bot Telegram pour Orlyne
"""

import logging
from typing import Optional, Dict, Any
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

logger = logging.getLogger(__name__)

class TelegramBot:
    """Bot Telegram pour Orlyne"""
    
    def __init__(self, token: str, orlyne_url: str = "http://localhost:8000"):
        self.token = token
        self.orlyne_url = orlyne_url
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configure les handlers du bot"""
        
        # Commandes
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("code", self.code_command))
        self.application.add_handler(CommandHandler("joke", self.joke_command))
        
        # Messages texte
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callbacks pour les boutons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /start"""
        keyboard = [
            [
                InlineKeyboardButton("💬 Chat", callback_data='chat'),
                InlineKeyboardButton("💻 Code", callback_data='code')
            ],
            [
                InlineKeyboardButton("😄 Blague", callback_data='joke'),
                InlineKeyboardButton("❓ Help", callback_data='help')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🌟 **Bienvenue sur Orlyne !**\n\n"
            "Je suis ton assistante IA sans limites.\n"
            "Amicale comme ChatGPT, codeuse comme Claude, et sans censure !\n\n"
            "Utilise les boutons ci-dessous ou envoie-moi directement un message.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /help"""
        help_text = """
📚 **Commandes disponibles**

/start - Démarrer le bot
/help - Afficher cette aide
/code <lang> - Exécuter du code
/joke - Raconter une blague

💡 **Utilisation**
- Pose-moi des questions normalement
- Envoie du code pour l'exécuter
- Demande des explications
- Traduction de code

🔓 **Sans censure**
Je peux t'aider avec TOUT type de code !
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def code_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /code"""
        # Récupère le code après la commande
        if context.args:
            language = context.args[0] if context.args else 'python'
            code = ' '.join(context.args[1:]) if len(context.args) > 1 else ''
            
            if code:
                await self.execute_code(update, code, language)
                return
        
        # Sinon, demande le code
        await update.message.reply_text(
            "Envoie-moi ton code à exécuter au format :\n"
            "`/code python`\n```python\nton code ici\n```",
            parse_mode='Markdown'
        )
    
    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /joke"""
        await update.message.reply_text("😂 Je cherche une bonne blague...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.orlyne_url}/api/chat",
                json={"prompt": "Raconte une blague de développeur"}
            ) as resp:
                data = await resp.json()
                await update.message.reply_text(f"**Orlyne:** {data.get('response', '😅')}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les messages texte"""
        user_message = update.message.text
        
        # Indicateur de frappe
        await update.message.chat.send_action(action="typing")
        
        # Détection si c'est du code
        if '```' in user_message:
            # Extraction du code
            parts = user_message.split('```')
            if len(parts) >= 3:
                code_block = parts[1]
                if '\n' in code_block:
                    lines = code_block.split('\n')
                    language = lines[0] if lines else 'python'
                    code = '\n'.join(lines[1:]) if len(lines) > 1 else ''
                else:
                    language = 'python'
                    code = code_block
                
                await self.execute_code(update, code, language)
                return
        
        # Sinon, chat normal
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.orlyne_url}/api/chat",
                json={"prompt": user_message}
            ) as resp:
                data = await resp.json()
                
                response = data.get('response', "Désolée, je n'ai pas pu répondre 😅")
                
                # Détection de code dans la réponse
                if '```' in response:
                    # Envoyer en plusieurs messages
                    parts = response.split('```')
                    for i, part in enumerate(parts):
                        if i % 2 == 0:  # Texte normal
                            if part.strip():
                                await update.message.reply_text(part)
                        else:  # Code
                            await update.message.reply_text(f"```\n{part}\n```")
                else:
                    await update.message.reply_text(f"**Orlyne:** {response}")
    
    async def execute_code(self, update: Update, code: str, language: str):
        """Exécute du code"""
        await update.message.reply_text(f"⚙️ Exécution du code {language}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.orlyne_url}/api/code/execute",
                json={
                    "code": code,
                    "language": language
                }
            ) as resp:
                result = await resp.json()
                
                if result['success']:
                    output = result.get('output', '')
                    if output:
                        await update.message.reply_text(
                            f"✅ **Résultat:**\n```\n{output[:1000]}\n```",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text("✅ Code exécuté avec succès !")
                else:
                    error = result.get('error', 'Erreur inconnue')
                    await update.message.reply_text(
                        f"❌ **Erreur:**\n```\n{error[:500]}\n```",
                        parse_mode='Markdown'
                    )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les callbacks des boutons"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'chat':
            await query.edit_message_text(
                "Pose-moi une question ! Je suis là pour t'aider."
            )
        elif query.data == 'code':
            await query.edit_message_text(
                "Envoie-moi du code avec ```python\ncode ici```"
            )
        elif query.data == 'joke':
            await self.joke_command(update, context)
        elif query.data == 'help':
            await self.help_command(update, context)
    
    def run(self):
        """Démarre le bot"""
        logger.info("Démarrage du bot Telegram...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)