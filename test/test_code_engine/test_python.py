"""
Tests pour l'exécuteur Python
"""

import pytest
from src.code_engine.python_executor import PythonExecutor

class TestPythonExecutor:
    
    @pytest.fixture
    def executor(self):
        return PythonExecutor(use_docker=False)
    
    def test_hello_world(self, executor):
        code = 'print("Hello, World!")'
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "Hello, World!"
    
    def test_simple_math(self, executor):
        code = 'print(2 + 2)'
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "4"
    
    def test_variables(self, executor):
        code = '''
x = 10
y = 20
print(x + y)
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "30"
    
    def test_function(self, executor):
        code = '''
def add(a, b):
    return a + b

print(add(5, 7))
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "12"
    
    def test_syntax_error(self, executor):
        code = 'print("Hello)'
        result = executor.execute(code)
        
        assert result["success"] is False
        assert "SyntaxError" in result["error"]
    
    def test_runtime_error(self, executor):
        code = 'print(1/0)'
        result = executor.execute(code)
        
        assert result["success"] is False
        assert "ZeroDivisionError" in result["error"]
    
    def test_multiple_statements(self, executor):
        code = '''
print("First")
print("Second")
print("Third")
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"] == "First\nSecond\nThird\n"
    
    def test_import(self, executor):
        code = '''
import math
print(math.pi)
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert "3.14" in result["output"]
    
    def test_list_comprehension(self, executor):
        code = '''
numbers = [1, 2, 3, 4, 5]
squares = [n**2 for n in numbers]
print(squares)
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "[1, 4, 9, 16, 25]"
    
    def test_dictionary(self, executor):
        code = '''
d = {"a": 1, "b": 2, "c": 3}
print(d["b"])
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "2"
    
    def test_loop(self, executor):
        code = '''
total = 0
for i in range(5):
    total += i
print(total)
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert result["output"].strip() == "10"