"""
Extension VS Code pour Orlyne
"""

import json
import logging
import socket
import threading
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class VSCodeIntegration:
    """Intégration avec VS Code via extension"""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.server = None
        self.connected = False
        self.clients = []
        
    def start_server(self):
        """Démarre le serveur pour l'extension VS Code"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server.bind(('localhost', self.port))
            self.server.listen(5)
            self.connected = True
            
            thread = threading.Thread(target=self._accept_connections)
            thread.daemon = True
            thread.start()
            
            logger.info(f"Serveur VS Code démarré sur le port {self.port}")
        except Exception as e:
            logger.error(f"Erreur démarrage serveur VS Code: {e}")
    
    def _accept_connections(self):
        """Accepte les connexions des extensions"""
        while self.connected:
            try:
                client, address = self.server.accept()
                self.clients.append(client)
                logger.info(f"Nouvelle connexion VS Code: {address}")
                
                thread = threading.Thread(target=self._handle_client, args=(client,))
                thread.daemon = True
                thread.start()
            except:
                break
    
    def _handle_client(self, client):
        """Gère un client connecté"""
        while True:
            try:
                data = client.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                self._process_message(message, client)
            except:
                break
        
        if client in self.clients:
            self.clients.remove(client)
        client.close()
    
    def _process_message(self, message: Dict, client):
        """Traite un message de l'extension"""
        command = message.get('command')
        
        if command == 'ping':
            self._send_response(client, {'status': 'pong'})
        
        elif command == 'get_code':
            self._send_response(client, {
                'status': 'ok',
                'code': message.get('code', '')
            })
        
        elif command == 'execute':
            self._send_response(client, {
                'status': 'ok',
                'message': 'Code reçu pour exécution'
            })
    
    def _send_response(self, client, data: Dict):
        """Envoie une réponse au client"""
        try:
            client.send(json.dumps(data).encode('utf-8'))
        except Exception as e:
            logger.error(f"Erreur envoi réponse: {e}")
    
    def send_to_vscode(self, command: str, data: Dict = None):
        """Envoie une commande à VS Code"""
        message = {
            'command': command,
            'data': data or {}
        }
        
        for client in self.clients[:]:
            try:
                client.send(json.dumps(message).encode('utf-8'))
            except:
                if client in self.clients:
                    self.clients.remove(client)
    
    def generate_extension(self, output_path: Path):
        """Génère l'extension VS Code"""
        extension_files = {
            "package.json": self._generate_package_json(),
            "extension.js": self._generate_extension_js(),
            ".vscodeignore": self._generate_vscodeignore()
        }
        
        for filename, content in extension_files.items():
            file_path = output_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        
        logger.info(f"Extension VS Code générée dans {output_path}")
    
    def _generate_package_json(self) -> str:
        return json.dumps({
            "name": "orlyne-ai",
            "displayName": "Orlyne AI Assistant",
            "description": "Assistant IA sans limites pour VS Code",
            "version": "1.0.0",
            "engines": {
                "vscode": "^1.85.0"
            },
            "categories": [
                "Programming Languages",
                "Snippets",
                "Other"
            ],
            "activationEvents": [
                "onLanguage"
            ],
            "main": "./extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "orlyne.explain",
                        "title": "Orlyne: Expliquer le code"
                    },
                    {
                        "command": "orlyne.improve",
                        "title": "Orlyne: Améliorer le code"
                    },
                    {
                        "command": "orlyne.debug",
                        "title": "Orlyne: Déboguer"
                    },
                    {
                        "command": "orlyne.chat",
                        "title": "Orlyne: Ouvrir le chat"
                    }
                ],
                "keybindings": [
                    {
                        "command": "orlyne.explain",
                        "key": "ctrl+shift+e",
                        "mac": "cmd+shift+e"
                    }
                ],
                "menus": {
                    "editor/context": [
                        {
                            "command": "orlyne.explain",
                            "group": "orlyne"
                        },
                        {
                            "command": "orlyne.improve",
                            "group": "orlyne"
                        }
                    ]
                }
            },
            "scripts": {
                "vscode:prepublish": "npm run compile",
                "compile": "echo done"
            },
            "devDependencies": {
                "@types/vscode": "^1.85.0"
            }
        }, indent=2)
    
    def _generate_extension_js(self) -> str:
        return '''
const vscode = require('vscode');
const WebSocket = require('ws');

let ws = null;

function activate(context) {
    console.log('Extension Orlyne activée');
    
    // Connexion WebSocket à Orlyne
    connectToOrlyne();
    
    // Commande Expliquer
    let explainCommand = vscode.commands.registerCommand('orlyne.explain', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('Ouvre un fichier d\'abord !');
            return;
        }
        
        const selection = editor.selection;
        const text = editor.document.getText(selection);
        
        if (!text) {
            vscode.window.showInformationMessage('Sélectionne du code à expliquer');
            return;
        }
        
        sendToOrlyne('explain', {
            code: text,
            language: editor.document.languageId
        });
    });
    
    // Commande Améliorer
    let improveCommand = vscode.commands.registerCommand('orlyne.improve', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;
        
        const text = editor.document.getText();
        sendToOrlyne('improve', {
            code: text,
            language: editor.document.languageId
        });
    });
    
    // Commande Debug
    let debugCommand = vscode.commands.registerCommand('orlyne.debug', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;
        
        const text = editor.document.getText();
        sendToOrlyne('debug', {
            code: text,
            language: editor.document.languageId
        });
    });
    
    // Commande Chat
    let chatCommand = vscode.commands.registerCommand('orlyne.chat', function () {
        const panel = vscode.window.createWebviewPanel(
            'orlyneChat',
            'Orlyne Chat',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true
            }
        );
        
        panel.webview.html = getWebviewContent();
    });
    
    context.subscriptions.push(explainCommand);
    context.subscriptions.push(improveCommand);
    context.subscriptions.push(debugCommand);
    context.subscriptions.push(chatCommand);
}

function connectToOrlyne() {
    ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.on('open', () => {
        vscode.window.showInformationMessage('Connecté à Orlyne !');
    });
    
    ws.on('message', (data) => {
        const response = JSON.parse(data);
        handleOrlyneResponse(response);
    });
    
    ws.on('close', () => {
        setTimeout(connectToOrlyne, 3000);
    });
}

function sendToOrlyne(command, data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            command: command,
            data: data
        }));
    } else {
        vscode.window.showErrorMessage('Pas connecté à Orlyne');
    }
}

function handleOrlyneResponse(response) {
    if (response.command === 'explain') {
        vscode.window.showInformationMessage('Explication reçue !');
        // Afficher dans un panel
        const panel = vscode.window.createWebviewPanel(
            'orlyneResponse',
            'Orlyne Response',
            vscode.ViewColumn.Beside,
            {}
        );
        panel.webview.html = `<pre>${response.data}</pre>`;
    }
}

function getWebviewContent() {
    return `<!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial; padding: 20px; background: #1e1e1e; color: #fff; }
            #chat { height: 400px; overflow-y: auto; border: 1px solid #333; padding: 10px; }
            #input { width: 100%; padding: 10px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div id="chat"></div>
        <input id="input" placeholder="Message à Orlyne...">
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws');
            const chat = document.getElementById('chat');
            const input = document.getElementById('input');
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                chat.innerHTML += '<div><b>Orlyne:</b> ' + data.response + '</div>';
                chat.scrollTop = chat.scrollHeight;
            };
            
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const msg = input.value;
                    chat.innerHTML += '<div><b>Vous:</b> ' + msg + '</div>';
                    ws.send(JSON.stringify({prompt: msg}));
                    input.value = '';
                }
            });
        </script>
    </body>
    </html>`;
}

function deactivate() {
    if (ws) {
        ws.close();
    }
}

module.exports = {
    activate,
    deactivate
};
'''
    
    def _generate_vscodeignore(self) -> str:
        return '''
node_modules
.vscode-test
.gitignore
vsc-extension-quickstart.md
**/*.ts
**/*.map
'''