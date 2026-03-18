"""
Mémoire conversationnelle d'Orlyne
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

class ConversationMemory:
    """Gère la mémoire des conversations"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path("data/conversations/memory.db")
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        
        # Mémoire à court terme (conversation en cours)
        self.short_term = []
        self.current_conversation_id = None
    
    def _init_database(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                summary TEXT,
                topics TEXT
            )
        ''')
        
        # Table des messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                tokens INTEGER,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # Table des entités importantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                type TEXT,
                context TEXT,
                last_seen TIMESTAMP,
                importance REAL DEFAULT 1.0
            )
        ''')
        
        # Table des préférences utilisateur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_conversation(self, user_id: str = "default") -> str:
        """Débute une nouvelle conversation"""
        conversation_id = hashlib.md5(
            f"{user_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (id, user_id, start_time, message_count)
            VALUES (?, ?, ?, 0)
        ''', (conversation_id, user_id, datetime.now()))
        
        conn.commit()
        conn.close()
        
        self.current_conversation_id = conversation_id
        self.short_term = []
        
        return conversation_id
    
    def add_message(self, role: str, content: str, tokens: int = 0, metadata: Dict = None):
        """Ajoute un message à la conversation"""
        if not self.current_conversation_id:
            self.start_conversation()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ajout du message
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content, timestamp, tokens, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            self.current_conversation_id,
            role,
            content,
            datetime.now(),
            tokens,
            json.dumps(metadata) if metadata else None
        ))
        
        # Mise à jour du compteur
        cursor.execute('''
            UPDATE conversations 
            SET message_count = message_count + 1
            WHERE id = ?
        ''', (self.current_conversation_id,))
        
        conn.commit()
        conn.close()
        
        # Mémoire court terme
        self.short_term.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extraction d'entités
        self._extract_entities(content)
    
    def end_conversation(self, summary: str = None):
        """Termine la conversation en cours"""
        if not self.current_conversation_id:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations 
            SET end_time = ?, summary = ?
            WHERE id = ?
        ''', (datetime.now(), summary, self.current_conversation_id))
        
        conn.commit()
        conn.close()
        
        self.current_conversation_id = None
        self.short_term = []
    
    def get_conversation_history(self, conversation_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Récupère l'historique d'une conversation"""
        if not conversation_id:
            conversation_id = self.current_conversation_id
        
        if not conversation_id:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp, tokens, metadata
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (conversation_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "tokens": row[3],
                "metadata": json.loads(row[4]) if row[4] else None
            })
        
        conn.close()
        
        return messages
    
    def get_recent_context(self, limit: int = 10) -> List[Dict]:
        """Récupère le contexte récent (court terme)"""
        return self.short_term[-limit:]
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche dans les conversations passées"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Recherche simple par mot-clé
        cursor.execute('''
            SELECT role, content, timestamp, conversation_id
            FROM messages
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "conversation_id": row[3]
            })
        
        conn.close()
        return results
    
    def _extract_entities(self, text: str):
        """Extrait des entités importantes du texte"""
        # Mots-clés à surveiller
        important_keywords = [
            "projet", "application", "site", "api", "base de données",
            "python", "javascript", "java", "bug", "erreur"
        ]
        
        for keyword in important_keywords:
            if keyword.lower() in text.lower():
                self._update_entity(keyword, "topic")
    
    def _update_entity(self, name: str, entity_type: str, importance: float = 1.0):
        """Met à jour une entité dans la base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO entities (name, type, last_seen, importance)
            VALUES (?, ?, ?, ?)
        ''', (name, entity_type, datetime.now(), importance))
        
        conn.commit()
        conn.close()
    
    def get_important_entities(self, limit: int = 20) -> List[Dict]:
        """Récupère les entités les plus importantes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, type, last_seen, importance
            FROM entities
            ORDER BY importance DESC, last_seen DESC
            LIMIT ?
        ''', (limit,))
        
        entities = []
        for row in cursor.fetchall():
            entities.append({
                "name": row[0],
                "type": row[1],
                "last_seen": row[2],
                "importance": row[3]
            })
        
        conn.close()
        return entities
    
    def set_user_preference(self, user_id: str, preferences: Dict):
        """Enregistre les préférences d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, preferences, last_updated)
            VALUES (?, ?, ?)
        ''', (user_id, json.dumps(preferences), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_user_preference(self, user_id: str) -> Dict:
        """Récupère les préférences d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT preferences FROM user_preferences
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return {}
    
    def clear_old_conversations(self, days: int = 30):
        """Nettoie les conversations de plus de X jours"""
        cutoff = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM messages
            WHERE conversation_id IN (
                SELECT id FROM conversations
                WHERE start_time < ?
            )
        ''', (cutoff,))
        
        cursor.execute('''
            DELETE FROM conversations
            WHERE start_time < ?
        ''', (cutoff,))
        
        conn.commit()
        conn.close()