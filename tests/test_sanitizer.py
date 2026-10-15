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
    JWT_REGEX,
    BEARER_REGEX,
    API_KEY_REGEX,
    PRIVATE_IP_REGEX,
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


def test_phone_sanitization_end_to_end():
    """Verify end-to-end detection and masking of phone numbers in realistic copy."""
    text = "Fale conosco pelo telefone +55 11 98765-4321 ou suporte comercial (21) 98765-4321."
    findings = inspect_sensitive_data(text)
    phone_findings = [f for f in findings if f["type"] == "phone"]
    assert len(phone_findings) == 2

    sanitized, audit_log = sanitize_text(text)
    assert "+55 11 98765-4321" not in sanitized
    assert "(21) 98765-4321" not in sanitized
    assert "[TELEFONE PROTEGIDO]" in sanitized


def test_jwt_and_bearer_sanitization():
    """Verify JWT and Authorization Bearer header detection and sanitization."""
    raw_jwt = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    text_jwt = f"Use o token de acesso: {raw_jwt} para autenticar."
    findings = inspect_sensitive_data(text_jwt)
    assert any(f["type"] == "jwt" for f in findings)

    sanitized_jwt, _ = sanitize_text(text_jwt)
    assert raw_jwt not in sanitized_jwt
    assert "[JWT PROTEGIDO]" in sanitized_jwt

    text_bearer = "Authorization: Bearer my_super_secret_access_token_123456789"
    findings_bearer = inspect_sensitive_data(text_bearer)
    assert any(f["type"] == "bearer_token" for f in findings_bearer)

    sanitized_bearer, _ = sanitize_text(text_bearer)
    assert "my_super_secret_access_token_123456789" not in sanitized_bearer
    assert "[BEARER PROTEGIDO]" in sanitized_bearer


def test_private_ip_and_api_key_sanitization():
    """Verify private IPv4 ranges (RFC 1918 + loopback) and API keys are redacted."""
    text = (
        "Conecte o serviço em 192.168.1.50 e teste no cluster 10.0.0.1 ou loopback 127.0.0.1. "
        "Não exponha em 8.8.8.8. Chave: sk_live_1234567890abcdef123456."
    )
    findings = inspect_sensitive_data(text)
    types = [f["type"] for f in findings]
    assert "private_ip" in types
    assert "api_key" in types

    sanitized, _ = sanitize_text(text)
    assert "192.168.1.50" not in sanitized
    assert "10.0.0.1" not in sanitized
    assert "127.0.0.1" not in sanitized
    assert "[IP PRIVADO PROTEGIDO]" in sanitized
    assert "sk_live_1234567890abcdef123456" not in sanitized
    assert "[CHAVE PROTEGIDA]" in sanitized
    # Public IP must remain intact
    assert "8.8.8.8" in sanitized


def test_year_ranges_and_uuids_not_masked_as_phones():
    """Verify year ranges, UUIDs, and large integers are NOT falsely flagged as phone numbers."""
    text = (
        "No período de 2023-2024 e 1999-2000, o investimento foi de 10000000 reais. "
        "Identificador de rastreio: 12345678-1234-1234-1234-123456789abc."
    )
    findings = inspect_sensitive_data(text)
    phone_findings = [f for f in findings if f["type"] == "phone"]
    assert len(phone_findings) == 0

    sanitized, audit = sanitize_text(text)
    assert "2023-2024" in sanitized
    assert "1999-2000" in sanitized
    assert "10000000" in sanitized
    assert "12345678-1234-1234-1234-123456789abc" in sanitized
    assert "[TELEFONE PROTEGIDO]" not in sanitized


def test_modern_ai_api_keys_and_version_strings():
    """Verify OpenAI sk-proj, Anthropic sk-ant, Google AIza keys, and IP version strings."""
    text = (
        "OpenAI: sk-proj-1234567890abcdef1234567890\n"
        "Anthropic: sk-ant-api03-1234567890abcdef1234567890\n"
        "Google: AIzaSyD-1234567890abcdef123456789012345\n"
        "Software version: 192.168.1.1.2 should not be masked as private IP"
    )
    findings = inspect_sensitive_data(text)
    api_key_findings = [f for f in findings if f["type"] == "api_key"]
    assert len(api_key_findings) == 3

    # 192.168.1.1.2 is a 5-octet version number, not an IPv4
    ip_findings = [f for f in findings if f["type"] == "private_ip"]
    assert len(ip_findings) == 0

    sanitized, _ = sanitize_text(text)
    assert "sk-proj-" not in sanitized
    assert "sk-ant-" not in sanitized
    assert "AIzaSy" not in sanitized
    assert sanitized.count("[CHAVE PROTEGIDA]") == 3
    assert "192.168.1.1.2" in sanitized


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
