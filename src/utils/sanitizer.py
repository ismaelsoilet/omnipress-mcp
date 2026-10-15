"""Privacy and de-identification sanitizer for legal, tax, and technical publishing."""

import re
from typing import Tuple, List, Dict

# CNJ Lawsuit Number format (e.g., 0001234-56.2023.8.26.0100)
CNJ_REGEX = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")

# Brazilian Tax IDs (CPF and CNPJ)
CPF_REGEX = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CNPJ_REGEX = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")

# General Sensitive Data (Email and phone numbers)
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")

# Brazilian landline & mobile phone numbers
# With DDD: (11) 98765-4321, 11 98765-4321, +55 11 98765-4321, (31) 3214-5678, etc.
# Standalone without DDD: 9-digit mobile (e.g. 98765-4321, 987654321)
_DDD = r"(?:\+?55\s*)?(?:\([1-9]{2}\)\s*|[1-9]{2}\s*)"
_NUM_WITH_DDD = r"(?:9\s?\d{4}[-\s]?\d{4}|[2-5]\d{3}[-\s]?\d{4})"
_NUM_STANDALONE = r"(?:9\d{4}[-\s]?\d{4})"
PHONE_REGEX = re.compile(
    rf"(?<![0-9a-zA-Z\-])(?:{_DDD}{_NUM_WITH_DDD}|{_NUM_STANDALONE})(?![0-9a-zA-Z\-])"
)

# Technical Credentials & Secrets
JWT_REGEX = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")
BEARER_REGEX = re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.=:~+/]{16,}\b", re.IGNORECASE)
API_KEY_REGEX = re.compile(
    r"\b(?:sk[-_](?:proj|ant|live|test)[-_][A-Za-z0-9_\-]{16,}|(?:sk|pk|ghp|gho|ghu|ghs|ghr|xoxb|xoxp|live|test)_[A-Za-z0-9_]{16,}|AIza[0-9A-Za-z\-_]{35})\b"
)

# Private IPv4 addresses (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8)
_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
PRIVATE_IP_REGEX = re.compile(
    rf"(?<!\d\.)(?<!\d)(?:10(?:\.{_OCTET}){{3}}|172\.(?:1[6-9]|2\d|3[01])(?:\.{_OCTET}){{2}}|192\.168(?:\.{_OCTET}){{2}}|127(?:\.{_OCTET}){{3}})(?!\.\d|\d)"
)


def inspect_sensitive_data(text: str) -> List[Dict[str, str]]:
    """
    Scans content for identifying information that may breach legal privacy,
    judicial secrecy (segredo de justiça), LGPD/GDPR regulations, or technical credential safety.
    """
    findings = []

    for match in CNJ_REGEX.finditer(text):
        findings.append({"type": "lawsuit_number", "match": match.group()})

    for match in CPF_REGEX.finditer(text):
        findings.append({"type": "cpf", "match": match.group()})

    for match in CNPJ_REGEX.finditer(text):
        findings.append({"type": "cnpj", "match": match.group()})

    for match in EMAIL_REGEX.finditer(text):
        findings.append({"type": "email", "match": match.group()})

    for match in BEARER_REGEX.finditer(text):
        findings.append({"type": "bearer_token", "match": match.group()})

    for match in JWT_REGEX.finditer(text):
        if not any(match.group() in f["match"] for f in findings if f["type"] == "bearer_token"):
            findings.append({"type": "jwt", "match": match.group()})

    for match in API_KEY_REGEX.finditer(text):
        findings.append({"type": "api_key", "match": match.group()})

    for match in PRIVATE_IP_REGEX.finditer(text):
        findings.append({"type": "private_ip", "match": match.group()})

    for match in PHONE_REGEX.finditer(text):
        findings.append({"type": "phone", "match": match.group().strip()})

    return findings


def sanitize_text(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Masks identifying information with generic anonymized tokens.
    Returns the sanitized string and a log of replaced items.
    """
    findings = inspect_sensitive_data(text)
    sanitized = text

    # Credentials & secrets sanitized first
    sanitized = BEARER_REGEX.sub("[BEARER PROTEGIDO]", sanitized)
    sanitized = JWT_REGEX.sub("[JWT PROTEGIDO]", sanitized)
    sanitized = API_KEY_REGEX.sub("[CHAVE PROTEGIDA]", sanitized)
    sanitized = PRIVATE_IP_REGEX.sub("[IP PRIVADO PROTEGIDO]", sanitized)

    # Legal & identifying data
    sanitized = CNJ_REGEX.sub("[PROCESSO ANÔNIMO]", sanitized)
    sanitized = CPF_REGEX.sub("[CPF PROTEGIDO]", sanitized)
    sanitized = CNPJ_REGEX.sub("[CNPJ PROTEGIDO]", sanitized)
    sanitized = EMAIL_REGEX.sub("[EMAIL PROTEGIDO]", sanitized)
    sanitized = PHONE_REGEX.sub("[TELEFONE PROTEGIDO]", sanitized)

    return sanitized, findings
