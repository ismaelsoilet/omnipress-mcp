# Privacy & De-Identification Shield 🛡️

Publishing technical, legal, financial, or operational case studies carries significant privacy and legal risks. OmniPress includes an automated **Privacy & Secrets Sanitizer** designed to protect your sensitive data before anything is submitted externally.

---

## 1. What Gets Scanned

The sanitizer automatically scans all content submitted to `omnipress_publish_article` and `omnipress_queue_post`:

| Category | Regex Pattern | Replacement Token |
| :--- | :--- | :--- |
| **CNJ Lawsuit Numbers** | `\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}` | `[PROCESSO ANÔNIMO]` |
| **CPF (Brazilian Tax ID)** | `\d{3}\.\d{3}\.\d{3}-\d{2}` | `[CPF PROTEGIDO]` |
| **CNPJ (Corporate ID)** | `\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}` | `[CNPJ PROTEGIDO]` |
| **Email Addresses** | Standard RFC 5322 regex | `[EMAIL PROTEGIDO]` |

---

## 2. Using the Standalone Inspector Tool

You can ask the agent to inspect text at any time without triggering a publication or queue action:

```text
OmniPress: Inspect this paragraph for any sensitive judicial or identifying data:
"No processo 0001234-56.2023.8.26.0100 o perito analisou a empresa sob CNPJ 12.345.678/0001-90."
```

The agent will invoke `omnipress_inspect_content(text)` and report:

```text
⚠️ Found 2 sensitive item(s):
  - [LAWSUIT_NUMBER]: 0001234-56.2023.8.26.0100
  - [CNPJ]: 12.345.678/0001-90
```

---

## 3. Disabling Sanitization (When Intended)

If you are intentionally publishing public case citations or your own public contact information, you can pass `sanitize: false` in the tool call. By default, sanitization is **always enabled** (`sanitize: true`).
