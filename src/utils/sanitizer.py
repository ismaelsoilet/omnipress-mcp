"""Privacy and de-identification sanitizer for legal, tax, and technical publishing."""

import re
from typing import Tuple, List, Dict

# CNJ Lawsuit Number format (e.g., 0001234-56.2023.8.26.0100)
CNJ_REGEX = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")

# Brazilian Tax IDs (CPF and CNPJ)
CPF_REGEX = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CNPJ_REGEX = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")

# General Sensitive Data (Email and international phone numbers)
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_REGEX = re.compile(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})[-\s]?\d{4}\b")


def inspect_sensitive_data(text: str) -> List[Dict[str, str]]:
    """
    Scans content for identifying information that may breach legal privacy,
    judicial secrecy (segredo de justiça), or LGPD/GDPR regulations.
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

    return findings


def sanitize_text(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Masks identifying information with generic anonymized tokens.
    Returns the sanitized string and a log of replaced items.
    """
    findings = inspect_sensitive_data(text)
    sanitized = text

    sanitized = CNJ_REGEX.sub("[PROCESSO ANÔNIMO]", sanitized)
    sanitized = CPF_REGEX.sub("[CPF PROTEGIDO]", sanitized)
    sanitized = CNPJ_REGEX.sub("[CNPJ PROTEGIDO]", sanitized)
    sanitized = EMAIL_REGEX.sub("[EMAIL PROTEGIDO]", sanitized)

    return sanitized, findings
