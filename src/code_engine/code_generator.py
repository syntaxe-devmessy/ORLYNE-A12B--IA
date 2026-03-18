"""
Générateur de code multi-langage
"""

from typing import Dict, Any, List, Optional
import random
import string

class CodeGenerator:
    """Génère du code dans différents langages"""
    
    def generate(self, description: str, language: str = "python", context: Dict = None) -> Dict[str, Any]:
        """
        Génère du code à partir d'une description
        
        Args:
            description: Description du code à générer
            language: Langage cible
            context: Contexte additionnel
            
        Returns:
            Code généré et métadonnées
        """
        generators = {
            "python": self._generate_python,
            "javascript": self._generate_javascript,
            "java": self._generate_java,
            "cpp": self._generate_cpp,
            "rust": self._generate_rust,
            "go": self._generate_go,
            "sql": self._generate_sql,
            "html": self._generate_html,
            "css": self._generate_css,
            "bash": self._generate_bash,
            "default": self._generate_generic
        }
        
        generator = generators.get(language, generators["default"])
        return generator(description, context or {})
    
    def _generate_python(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère du code Python"""
        
        templates = {
            "function": self._py_function_template,
            "class": self._py_class_template,
            "script": self._py_script_template,
            "api": self._py_api_template,
            "web": self._py_web_template
        }
        
        template_type = context.get("type", "script")
        template = templates.get(template_type, self._py_script_template)
        
        code = template(description, context)
        
        return {
            "code": code,
            "language": "python",
            "type": template_type,
            "description": description,
            "estimated_lines": len(code.split('\n'))
        }
    
    def _py_function_template(self, description: str, context: Dict) -> str:
        """Template de fonction Python"""
        func_name = context.get("name", self._generate_name("function"))
        params = context.get("params", ["param1", "param2"])
        return f'''def {func_name}({', '.join(params)}):
    """
    {description}
    
    Args:
        {chr(10).join([f'    {p}: Description of {p}' for p in params])}
    
    Returns:
        Description of return value
    """
    # TODO: Implement function
    pass
'''
    
    def _py_class_template(self, description: str, context: Dict) -> str:
        """Template de classe Python"""
        class_name = context.get("name", self._generate_name("Class"))
        return f'''class {class_name}:
    """
    {description}
    
    Attributes:
        TODO: Add attributes
    """
    
    def __init__(self):
        """Initialize the class"""
        # TODO: Initialize attributes
        pass
    
    def method1(self):
        """TODO: Add method description"""
        # TODO: Implement method
        pass
'''
    
    def _py_script_template(self, description: str, context: Dict) -> str:
        """Template de script Python"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
{description}
"""

import sys
import os


def main():
    """Main function"""
    # TODO: Implement main logic
    print("Hello from generated script!")
    
    # Add your code here
    # {description}
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _py_api_template(self, description: str, context: Dict) -> str:
        """Template d'API FastAPI"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
{description}
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Generated API", description="{description}")


class Item(BaseModel):
    """Item model"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {{"message": "Hello World", "description": "{description}"}}


@app.get("/items/{{item_id}}")
async def read_item(item_id: int):
    """Get item by ID"""
    # TODO: Implement item retrieval
    return {{"item_id": item_id}}


@app.post("/items/")
async def create_item(item: Item):
    """Create new item"""
    # TODO: Implement item creation
    return item


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _py_web_template(self, description: str, context: Dict) -> str:
        """Template d'application web Flask"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
{description}
"""

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', title="{description}")


@app.route('/api/data')
def get_data():
    """API endpoint"""
    return jsonify({{
        "message": "Hello from Flask!",
        "description": "{description}"
    }})


@app.route('/api/submit', methods=['POST'])
def submit():
    """Submit data"""
    data = request.json
    # TODO: Process data
    return jsonify({{"status": "success", "data": data}})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
    
    def _generate_javascript(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère du code JavaScript"""
        
        templates = {
            "function": self._js_function_template,
            "class": self._js_class_template,
            "node": self._js_node_template,
            "react": self._js_react_template
        }
        
        template_type = context.get("type", "function")
        template = templates.get(template_type, self._js_function_template)
        
        code = template(description, context)
        
        return {
            "code": code,
            "language": "javascript",
            "type": template_type,
            "description": description
        }
    
    def _js_function_template(self, description: str, context: Dict) -> str:
        """Template de fonction JavaScript"""
        func_name = context.get("name", self._generate_name("function"))
        params = context.get("params", ["param1", "param2"])
        return f'''/**
 * {description}
 * @param {{{', '.join(['any' for _ in params])}}} {', '.join(params)}
 * @returns {any}
 */
function {func_name}({', '.join(params)}) {{
    // TODO: Implement function
    console.log('{func_name} called');
    return null;
}}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {func_name};
}}
'''
    
    def _js_class_template(self, description: str, context: Dict) -> str:
        """Template de classe JavaScript"""
        class_name = context.get("name", self._generate_name("Class"))
        return f'''/**
 * {description}
 */
class {class_name} {{
    /**
     * Create a new instance
     * @param {object} config - Configuration object
     */
    constructor(config = {{}}) {{
        this.config = config;
        // TODO: Initialize properties
    }}
    
    /**
     * TODO: Add method description
     * @returns {any}
     */
    method1() {{
        // TODO: Implement method
        return null;
    }}
    
    /**
     * Static method
     * @returns {string}
     */
    static create() {{
        return new {class_name}();
    }}
}}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {class_name};
}}
'''
    
    def _js_node_template(self, description: str, context: Dict) -> str:
        """Template d'application Node.js"""
        return f'''#!/usr/bin/env node

/**
 * {description}
 */

const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

/**
 * Root endpoint
 */
app.get('/', (req, res) => {{
    res.json({{
        message: 'Hello from Node.js!',
        description: '{description}'
    }});
}});

/**
 * API endpoint
 */
app.get('/api/data', (req, res) => {{
    // TODO: Implement data retrieval
    res.json({{
        data: [],
        timestamp: new Date().toISOString()
    }});
}});

/**
 * Start server
 */
app.listen(port, () => {{
    console.log(`Server running on http://localhost:${{port}}`);
    console.log(`Description: {description}`);
}});
'''
    
    def _js_react_template(self, description: str, context: Dict) -> str:
        """Template de composant React"""
        component_name = context.get("name", self._generate_name("Component"))
        return f'''import React, {{ useState, useEffect }} from 'react';

/**
 * {description}
 * @param {object} props - Component props
 * @returns {JSX.Element}
 */
const {component_name} = (props) => {{
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {{
        // TODO: Fetch data or initialize
        const fetchData = async () => {{
            try {{
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 1000));
                setData({{ message: 'Hello from {component_name}!' }});
                setLoading(false);
            }} catch (error) {{
                console.error('Error:', error);
                setLoading(false);
            }}
        }};
        
        fetchData();
    }}, []);
    
    if (loading) {{
        return <div>Loading...</div>;
    }}
    
    return (
        <div className="{component_name.toLowerCase()}">
            <h2>{component_name}</h2>
            <p>{data?.message || 'No data'}</p>
            <p>Description: {description}</p>
            {/* TODO: Add more JSX */}
        </div>
    );
}};

export default {component_name};
'''
    
    def _generate_java(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère du code Java"""
        class_name = context.get("name", self._generate_name("Main"))
        
        code = f'''/**
 * {description}
 */
public class {class_name} {{
    
    /**
     * Main entry point
     * @param args Command line arguments
     */
    public static void main(String[] args) {{
        System.out.println("Hello from Java!");
        System.out.println("Description: {description}");
        
        // TODO: Implement main logic
        {class_name} instance = new {class_name}();
        instance.run();
    }}
    
    /**
     * Run the application
     */
    public void run() {{
        // TODO: Implement application logic
        System.out.println("Running {class_name}...");
    }}
    
    /**
     * Example method
     * @param input Input parameter
     * @return Processed result
     */
    public String process(String input) {{
        // TODO: Implement processing
        return "Processed: " + input;
    }}
}}
'''
        
        return {
            "code": code,
            "language": "java",
            "type": "class",
            "class_name": class_name,
            "description": description
        }
    
    def _generate_cpp(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère du code C++"""
        
        code = f'''/**
 * {description}
 */

#include <iostream>
#include <string>
#include <vector>

using namespace std;

class Application {{
private:
    string name;
    
public:
    /**
     * Constructor
     */
    Application() : name("GeneratedApp") {{
        // TODO: Initialize
    }}
    
    /**
     * Initialize the application
     */
    void initialize() {{
        cout << "Initializing application..." << endl;
        cout << "Description: {description}" << endl;
        // TODO: Add initialization code
    }}
    
    /**
     * Run the application
     */
    void run() {{
        cout << "Running application..." << endl;
        // TODO: Add main logic
    }}
    
    /**
     * Process data
     * @param data Input data
     * @return Processed result
     */
    string process(const string& data) {{
        // TODO: Implement processing
        return "Processed: " + data;
    }}
}};

/**
 * Main function
 */
int main() {{
    cout << "Starting C++ application" << endl;
    
    Application app;
    app.initialize();
    app.run();
    
    string result = app.process("test");
    cout << result << endl;
    
    return 0;
}}
'''
        
        return {
            "code": code,
            "language": "cpp",
            "type": "application",
            "description": description
        }
    
    def _generate_rust(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère du code Rust"""
        
        code = f'''/// {description}
struct Application {{
    name: String,
}}

impl Application {{
    /// Create a new application
    fn new() -> Self {{
        Self {{
            name: String::from("GeneratedApp"),
        }}
    }}
    
    /// Initialize the application
    fn initialize(&self) {{
        println!("Initializing application...");
        println!("Description: {description}");
    }}
    
    /// Run the application
    fn run(&self) {{
        println!("Running application...");
        // TODO: Add main logic
    }}
    
    /// Process data
    fn process(&self, data: &str) -> String {{
        format!("Processed: {{}}", data)
    }}
}}

/// Main function
fn main() {{
    println!("Starting Rust application");
    
    let app = Application::new();
    app.initialize();
    app.run();
    
    let result = app.process("test");
    println!("{{}}", result);
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_application() {{
        let app = Application::new();
        assert_eq!(app.process("test"), "Processed: test");
    }}
}}
'''
        
        return {
            "code": code,
            "language": "rust",
            "type": "application",
            "description": description
        }
    
    def _generate_go(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère du code Go"""
        
        code = f'''package main

import (
    "fmt"
    "log"
)

// App represents the main application
type App struct {{
    name string
}}

// NewApp creates a new application
func NewApp() *App {{
    return &App{{
        name: "GeneratedApp",
    }}
}}

// Initialize sets up the application
func (a *App) Initialize() {{
    fmt.Printf("Initializing application...\\n")
    fmt.Printf("Description: {description}\\n")
}}

// Run starts the application
func (a *App) Run() {{
    fmt.Printf("Running application...\\n")
    // TODO: Add main logic
}}

// Process handles data
func (a *App) Process(data string) string {{
    return fmt.Sprintf("Processed: %s", data)
}}

// Main function
func main() {{
    fmt.Println("Starting Go application")
    
    app := NewApp()
    app.Initialize()
    app.Run()
    
    result := app.Process("test")
    fmt.Println(result)
}}
'''
        
        return {
            "code": code,
            "language": "go",
            "type": "application",
            "description": description
        }
    
    def _generate_sql(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère des requêtes SQL"""
        
        table_name = context.get("table", "users")
        
        code = f'''-- {description}

-- Create table
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index
CREATE INDEX idx_{table_name}_username ON {table_name}(username);
CREATE INDEX idx_{table_name}_email ON {table_name}(email);

-- Insert sample data
INSERT INTO {table_name} (username, email, password_hash) VALUES
    ('john_doe', 'john@example.com', 'hash123'),
    ('jane_smith', 'jane@example.com', 'hash456');

-- Select queries
SELECT * FROM {table_name};
SELECT username, email FROM {table_name} WHERE id = 1;

-- Update query
UPDATE {table_name} 
SET updated_at = CURRENT_TIMESTAMP 
WHERE id = 1;

-- Delete query
DELETE FROM {table_name} WHERE id = 2;

-- Aggregation queries
SELECT COUNT(*) as user_count FROM {table_name};
SELECT DATE(created_at) as date, COUNT(*) as count 
FROM {table_name} 
GROUP BY DATE(created_at);

-- Join example (if another table exists)
/*
SELECT u.username, o.order_date
FROM {table_name} u
JOIN orders o ON u.id = o.user_id
WHERE u.id = 1;
*/
'''
        
        return {
            "code": code,
            "language": "sql",
            "type": "schema",
            "table": table_name,
            "description": description
        }
    
    def _generate_html(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère du code HTML"""
        
        title = context.get("title", "Generated Page")
        
        code = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>{title}</h1>
        <p>{description}</p>
    </header>
    
    <main>
        <section id="content">
            <h2>Main Content</h2>
            <p>This is the main content area.</p>
            <!-- TODO: Add more content -->
        </section>
        
        <aside>
            <h3>Sidebar</h3>
            <ul>
                <li><a href="#link1">Link 1</a></li>
                <li><a href="#link2">Link 2</a></li>
                <li><a href="#link3">Link 3</a></li>
            </ul>
        </aside>
    </main>
    
    <footer>
        <p>&copy; 2024 Generated Page. All rights reserved.</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>
'''
        
        return {
            "code": code,
            "language": "html",
            "type": "page",
            "title": title,
            "description": description
        }
    
    def _generate_css(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère du code CSS"""
        
        code = f'''/*
 * {description}
 */

/* Reset and base styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}}

/* Header styles */
header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    text-align: center;
}}

header h1 {{
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}}

/* Main content */
main {{
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
}}

/* Content section */
#content {{
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

#content h2 {{
    color: #667eea;
    margin-bottom: 1rem;
}}

/* Sidebar */
aside {{
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

aside h3 {{
    color: #764ba2;
    margin-bottom: 1rem;
}}

aside ul {{
    list-style: none;
}}

aside li {{
    margin-bottom: 0.5rem;
}}

aside a {{
    color: #667eea;
    text-decoration: none;
    transition: color 0.3s;
}}

aside a:hover {{
    color: #764ba2;
}}

/* Footer */
footer {{
    text-align: center;
    padding: 2rem;
    background: #333;
    color: white;
    margin-top: 2rem;
}}

/* Responsive design */
@media (max-width: 768px) {{
    main {{
        grid-template-columns: 1fr;
    }}
    
    header h1 {{
        font-size: 2rem;
    }}
}}

/* TODO: Add more styles as needed */
'''
        
        return {
            "code": code,
            "language": "css",
            "type": "styles",
            "description": description
        }
    
    def _generate_bash(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génère un script Bash"""
        
        code = f'''#!/bin/bash

# {description}

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
LOG_FILE="${{SCRIPT_DIR}}/script.log"

# Helper functions
log() {{
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}}

info() {{
    log "${GREEN}[INFO]${NC} $1"
}}

warn() {{
    log "${YELLOW}[WARN]${NC} $1"
}}

error() {{
    log "${RED}[ERROR]${NC} $1"
}}

# Check dependencies
check_dependencies() {{
    local deps=("$@")
    local missing=()
    
    for dep in "${{deps[@]}}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ "${{#missing[@]}}" -gt 0 ]; then
        error "Missing dependencies: ${{missing[*]}}"
        exit 1
    fi
}}

# Main function
main() {{
    info "Starting script: $SCRIPT_NAME"
    info "Description: {description}"
    
    # Check required dependencies
    # check_dependencies "curl" "jq"
    
    # TODO: Add main script logic here
    info "Processing..."
    
    # Example: Process arguments
    while getopts "hvf:" opt; do
        case $opt in
            h)
                show_help
                exit 0
                ;;
            v)
                echo "Version 1.0.0"
                exit 0
                ;;
            f)
                file="$OPTARG"
                info "Processing file: $file"
                ;;
            \\?)
                error "Invalid option: -$OPTARG"
                show_help
                exit 1
                ;;
        esac
    done
    
    info "Script completed successfully"
}}

# Help function
show_help() {{
    cat << EOF
Usage: $SCRIPT_NAME [options]

Options:
    -h              Show this help message
    -v              Show version
    -f <file>       Process specified file

Description: {description}
EOF
}}

# Run main function
main "$@"
'''
        
        return {
            "code": code,
            "language": "bash",
            "type": "script",
            "description": description
        }
    
    def _generate_generic(self, description: str, context: Dict) -> Dict[str, Any]:
        """Génération générique"""
        return {
            "code": f"// {description}\n// TODO: Generate code for language: {context.get('language', 'unknown')}",
            "language": context.get("language", "unknown"),
            "type": "generic",
            "description": description,
            "warning": "Generic generation - language may not be fully supported"
        }
    
    def _generate_name(self, prefix: str) -> str:
        """Génère un nom aléatoire"""
        return f"{prefix}_{''.join(random.choices(string.ascii_lowercase, k=8))}"