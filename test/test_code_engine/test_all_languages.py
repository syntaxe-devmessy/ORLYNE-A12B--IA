"""
Tests pour tous les exécuteurs de code
"""

import pytest
from src.code_engine import (
    PythonExecutor,
    JavaScriptExecutor,
    JavaExecutor,
    CPPExecutor,
    RustExecutor,
    GoExecutor,
    RubyExecutor,
    PHPExecutor
)

class TestAllExecutors:
    
    @pytest.mark.parametrize("executor_class,language,code,expected", [
        (PythonExecutor, "python", 'print("Hello")', "Hello"),
        (JavaScriptExecutor, "javascript", 'console.log("Hello");', "Hello"),
        (RubyExecutor, "ruby", 'puts "Hello"', "Hello"),
        (PHPExecutor, "php", '<?php echo "Hello"; ?>', "Hello"),
    ])
    def test_hello_world(self, executor_class, language, code, expected):
        executor = executor_class(use_docker=False)
        result = executor.execute(code)
        
        assert result["success"] is True
        assert expected in result["output"]
    
    @pytest.mark.parametrize("executor_class,language,code,expected", [
        (PythonExecutor, "python", 'print(2 + 2)', "4"),
        (JavaScriptExecutor, "javascript", 'console.log(2 + 2);', "4"),
        (RubyExecutor, "ruby", 'puts 2 + 2', "4"),
        (PHPExecutor, "php", '<?php echo 2 + 2; ?>', "4"),
    ])
    def test_math(self, executor_class, language, code, expected):
        executor = executor_class(use_docker=False)
        result = executor.execute(code)
        
        assert result["success"] is True
        assert expected in result["output"]
    
    def test_python_complex(self):
        executor = PythonExecutor(use_docker=False)
        code = '''
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        print(a, end=' ')
        a, b = b, a + b

fibonacci(10)
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert "0 1 1 2 3 5 8 13 21 34" in result["output"]
    
    def test_java_basic(self):
        executor = JavaExecutor(use_docker=False)
        code = '''
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert "Hello from Java!" in result["output"]
    
    def test_cpp_basic(self):
        executor = CPPExecutor(use_docker=False)
        code = '''
#include <iostream>
using namespace std;
int main() {
    cout << "Hello from C++!" << endl;
    return 0;
}
'''
        result = executor.execute(code)
        
        assert result["success"] is True
        assert "Hello from C++!" in result["output"]