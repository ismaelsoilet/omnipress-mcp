"""Dedicated unit tests for OmniPress privacy and de-identification sanitizer (src/utils/sanitizer.py)."""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.sanitizer import (
    inspect_sensitive_data,
    sanitize_text,
    CNJ_REGEX,
    CPF_REGEX,
    CNPJ_REGEX,
    EMAIL_REGEX,
    PHONE_REGEX,
)


def test_cnj_lawsuit_detection_and_masking():
    """Verify CNJ format (0000000-00.0000.0.00.0000) detection and anonymization."""
    text = "Processo judicial n. 0001234-56.2023.8.26.0100 em trâmite na 1a Vara Cível."
    findings = inspect_sensitive_data(text)

    assert len(findings) == 1
    assert findings[0]["type"] == "lawsuit_number"
    assert findings[0]["match"] == "0001234-56.2023.8.26.0100"

    sanitized, _ = sanitize_text(text)
    assert "0001234-56.2023.8.26.0100" not in sanitized
    assert "[PROCESSO ANÔNIMO]" in sanitized
    assert "em trâmite na 1a Vara Cível." in sanitized


def test_cpf_and_cnpj_tax_id_sanitization():
    """Verify Brazilian CPF and CNPJ detection and replacement with protected placeholders."""
    text = (
        "O autor portador do CPF 123.456.789-00 ajuizou ação contra a empresa "
        "inscrita no CNPJ 12.345.678/0001-90."
    )
    findings = inspect_sensitive_data(text)
    types = [f["type"] for f in findings]
    assert "cpf" in types
    assert "cnpj" in types

    sanitized, _ = sanitize_text(text)
    assert "123.456.789-00" not in sanitized
    assert "12.345.678/0001-90" not in sanitized
    assert "[CPF PROTEGIDO]" in sanitized
    assert "[CNPJ PROTEGIDO]" in sanitized


def test_email_sanitization():
    """Verify standard, uppercase, and tagged email addresses are masked."""
    text = (
        "Enviar manifestação para perito.forense@tribunal.jus.br ou "
        "ADMIN_CONTROL@CORP.COM.BR com cópia para contato+auditoria@empresa.org."
    )
    findings = inspect_sensitive_data(text)
    assert len(findings) == 3
    for f in findings:
        assert f["type"] == "email"

    sanitized, _ = sanitize_text(text)
    assert "perito.forense@tribunal.jus.br" not in sanitized
    assert "ADMIN_CONTROL@CORP.COM.BR" not in sanitized
    assert "contato+auditoria@empresa.org" not in sanitized
    assert "[EMAIL PROTEGIDO]" in sanitized


def test_phone_regex_patterns():
    """Verify PHONE_REGEX matches common Brazilian mobile and landline patterns."""
    phone_samples = [
        "+55 11 98765-4321",
        "(21) 98765-4321",
        "11 98765-4321",
        "(31) 3214-5678",
    ]
    for sample in phone_samples:
        match = PHONE_REGEX.search(sample)
        assert match is not None, f"Phone regex failed to match '{sample}'"


def test_clean_content_immutability():
    """Verify text without sensitive information remains completely unmodified."""
    clean_article = (
        "# Arquitetura Limpa e microsserviços em Go\n\n"
        "Neste artigo exploramos as vantagens de separação de camadas, "
        "injeção de dependência e desacoplamento de storage e adaptadores."
    )
    findings = inspect_sensitive_data(clean_article)
    assert len(findings) == 0

    sanitized, audit_log = sanitize_text(clean_article)
    assert sanitized == clean_article
    assert len(audit_log) == 0


def test_edge_cases_and_punctuation():
    """Verify sanitizer handles empty strings, adjacent punctuation, and multiple occurrences."""
    # Empty string
    sanitized_empty, findings_empty = sanitize_text("")
    assert sanitized_empty == ""
    assert len(findings_empty) == 0

    # Adjacent punctuation (commas, parentheses, brackets)
    punct_text = (
        "(Proc. 0001234-56.2023.8.26.0100), réu (CPF: 123.456.789-00), "
        "empresa: [CNPJ: 12.345.678/0001-90], email: <contato@jus.gov.br>."
    )
    sanitized_punct, findings_punct = sanitize_text(punct_text)
    assert len(findings_punct) == 4
    assert "[PROCESSO ANÔNIMO]" in sanitized_punct
    assert "[CPF PROTEGIDO]" in sanitized_punct
    assert "[CNPJ PROTEGIDO]" in sanitized_punct
    assert "[EMAIL PROTEGIDO]" in sanitized_punct
    assert "0001234-56.2023.8.26.0100" not in sanitized_punct


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
