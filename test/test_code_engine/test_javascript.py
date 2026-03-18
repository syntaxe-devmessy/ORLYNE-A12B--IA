"""
Tests pour l'exécuteur JavaScript
"""

import pytest
from src.code_engine.javascript_executor import JavaScriptExecutor

class TestJavaScriptExecutor:
    
    @pytest.fixture
    def executor(self):
        return JavaScriptExecutor(use_docker=False)
    
    def test_hello_world(self, executor):
        code = 'console.log("Hello, World!");'
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "Hello, World!"
    
    def test_simple_math(self, executor):
        code = 'console.log(2 + 2);'
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "4"
    
    def test_variables(self, executor):
        code = '''
let x = 10;
let y = 20;
console.log(x + y);
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "30"
    
    def test_function(self, executor):
        code = '''
function add(a, b) {
    return a + b;
}
console.log(add(5, 7));
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "12"
    
    def test_arrow_function(self, executor):
        code = '''
const add = (a, b) => a + b;
console.log(add(5, 7));
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "12"
    
    def test_array_methods(self, executor):
        code = '''
const numbers = [1, 2, 3, 4, 5];
const squares = numbers.map(n => n * n);
console.log(squares);
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "[ 1, 4, 9, 16, 25 ]"
    
    def test_object(self, executor):
        code = '''
const obj = {a: 1, b: 2, c: 3};
console.log(obj.b);
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "2"
    
    def test_loop(self, executor):
        code = '''
let total = 0;
for (let i = 0; i < 5; i++) {
    total += i;
}
console.log(total);
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "10"