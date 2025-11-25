import re

# List of dangerous terms that should block execution
DANGEROUS_TERMS = [
    "os.environ",
    "open(",
    "read(",
    "write(",
    "token",
    "api_key",
    "sys.modules",
    "eval(",
    "exec(",
    "subprocess",
    "shutil",
    "input("
]

def scan_code(code: str) -> bool:
    """
    Scans the provided code for dangerous terms.
    Returns True if safe, False if dangerous.
    """
    code_lower = code.lower()
    for term in DANGEROUS_TERMS:
        if term in code_lower:
            return False
    return True

def extract_code_block(text: str) -> str:
    """
    Extracts Python code from a markdown code block.
    """
    match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()
