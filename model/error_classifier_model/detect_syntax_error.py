import re


def detect_syntax_error(text):
    """Detect syntax errors from extracted text."""
    syntax_error_match = re.search(r"(SyntaxError:.*|IndentationError:.*|unexpected EOF while parsing)", text)
    if syntax_error_match:
        return f"Syntax Error detected: {syntax_error_match.group()}"
    else:
        return "No Syntax Error detected."


if __name__ == "__main__":
    sample_text = "File 'test.py', line 2\n    print(Hello World)\n              ^\nSyntaxError: invalid syntax"
    result = detect_syntax_error(sample_text)
    print(result)
