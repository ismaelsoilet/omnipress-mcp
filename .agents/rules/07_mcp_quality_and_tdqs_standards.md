# Rule 07: MCP Server Quality and TDQS Standards (Glama A+ & MCP 2026 Protocol)

> **Context**: OmniPress exposes multi-channel publishing tools via the Model Context Protocol (MCP) in dual runtimes: Node.js (`src/server.js`) and Python (`src/server.py`). All tools registered in this repository must adhere to the Glama Tool Definition Quality Score (TDQS) **Grade A+ (5.0/5.0)** and the 2026 MCP specification.

---

## 1. Mandatory Tool Annotations (MCP 2026 Spec)

Every tool exposed in `tools/list` must declare explicit boolean behavior hints within an `annotations` object:

```json
{
  "readOnlyHint": false,
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false
}
```

### Protocol Semantics:
- **`readOnlyHint`** (`boolean`): Set to `true` ONLY if the tool performs reads without any persistent side effects, file creations, or external dispatches (e.g. `omnipress_inspect_content`, `omnipress_list_articles`). Set to `false` for mutating tools (`omnipress_publish_article`, `omnipress_queue_post`).
- **`destructiveHint`** (`boolean`): Set to `true` if the tool destroys, drops, or permanently deletes data. For OmniPress tools, this is `false`.
- **`idempotentHint`** (`boolean`): Set to `true` if repeated executions with identical inputs produce the identical result without duplicate side effects.
- **`openWorldHint`** (`boolean`): Set to `true` if the tool interacts with third-party networks, external APIs (Buffer, Reddit, Webhooks), or public services. Set to `false` for purely local operations.

---

## 2. Canonical `verb_noun` Naming & Backward Compatibility

All tool names must strictly conform to the `verb_noun` standard:

| Canonical Name (`verb_noun`) | Action Type | Legacy Alias (Backward Compatible) |
| :--- | :--- | :--- |
| `omnipress_publish_article` | Mutation / Disk & Event | — |
| `omnipress_queue_post` | Mutation / Social Distribution | — |
| `omnipress_inspect_content` | Read-Only / Privacy Scan | — |
| `omnipress_list_articles` | Read-Only / File Metadata | `omnipress_list_recent` |

### Backward Compatibility Contract:
- `tools/list` returns canonical names to achieve 100% TDQS scoring.
- `tools/call` MUST continue to accept legacy aliases (`omnipress_list_recent`) in both Node.js and Python dispatchers, routing them to the same underlying implementation.

---

## 3. Human-Readable Titles (`title`)

Every tool definition must specify a concise, human-friendly `title` attribute:
- `omnipress_publish_article` -> `"Publish and Archive Article"`
- `omnipress_queue_post` -> `"Queue Social Post or Thread"`
- `omnipress_inspect_content` -> `"Inspect Content for PII and Legal IDs"`
- `omnipress_list_articles` -> `"List Archived Articles"`

---

## 4. Structured Descriptions with Markdown Sections

Descriptions must be self-contained and structured with three mandatory markdown sections:

1. **`Use when:`**: Bullet points detailing specific agent trigger conditions.
2. **`Do NOT use when:`**: Negative guidance directing the model to alternative tools.
3. **`Returns:`**: Clear specification of returned data shapes, confirmations, or warnings.

---

## 5. Input Schema Hardening

- All string parameters must define appropriate constraints (`minLength`, `maxLength`).
- Numerical limits must specify `minimum`, `maximum`, and `default`.
- Categorical options must use explicit `enum` arrays.
