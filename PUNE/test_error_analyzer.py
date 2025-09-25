from analyze_error import AIModelInterface

def test_error_analyzer():
    analyzer = AIModelInterface()
    
    # Test SyntaxError
    print("Testing SyntaxError:")
    result = analyzer.analyze_error(test_text="""SyntaxError: invalid syntax (test.py, line 5)
    File "test.py", line 5
        print("Hello world'
                     ^
    SyntaxError: invalid syntax""")
    print(result)
    
    # Test ModuleNotFoundError
    print("\nTesting ModuleNotFoundError:")
    result = analyzer.analyze_error(test_text="""ModuleNotFoundError: No module named 'numpy'
    File "script.py", line 3, in <module>
        import numpy as np""")
    print(result)
    
    # Test NameError
    print("\nTesting NameError:")
    result = analyzer.analyze_error(test_text="""NameError: name 'x' is not defined
    File "app.py", line 10, in <module>
        print(x)""")
    print(result)

if __name__ == "__main__":
    test_error_analyzer()
