import pytest
from src.agents.generator import clean_unicode_for_latex, sanitize_data_recursive, escape_latex_special_chars

def test_clean_unicode():
    assert clean_unicode_for_latex("Développeur 1ᵉʳ") == "Développeur 1\\textsuperscript{e}r"
    assert clean_unicode_for_latex("Coût: 100€") == "Coût: 100\\euro{}"
    assert clean_unicode_for_latex("«hello»") == "\\guillemotleft{}hello\\guillemotright{}"

def test_escape_special_chars():
    assert escape_latex_special_chars("100% & more") == r"100\% \& more"
    assert escape_latex_special_chars("$50_000") == r"\$50\_000"
    assert escape_latex_special_chars("C# \\ C++") == r"C\# \textbackslash{} C++"
    
def test_sanitize_recursive():
    data = {
        "profile": {"name": "L'Oréal", "price": "10$"},
        "skills": ["C++", "C#", "100%"]
    }
    sanitized = sanitize_data_recursive(data)
    assert sanitized["profile"]["name"] == "L'Oréal" # Quote not escaped by default, maybe we should?
    assert sanitized["profile"]["price"] == r"10\$"
    assert sanitized["skills"][1] == r"C\#"
    assert sanitized["skills"][2] == r"100\%"
