"""Unit tests for OmniPress MCP core modules."""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.sanitizer import sanitize_text, inspect_sensitive_data
from src.adapters.markdown_adapter import MarkdownArchiveAdapter, slugify


def test_sanitizer_detection():
    sample_text = (
        "No processo 0001234-56.2023.8.26.0100 o perito analisou o CNPJ 12.345.678/0001-90 "
        "e o autor com CPF 123.456.789-00 enviou email para perito@tribunal.jus.br."
    )
    findings = inspect_sensitive_data(sample_text)
    assert len(findings) == 4, f"Expected 4 sensitive items, got {len(findings)}"

    sanitized, _ = sanitize_text(sample_text)
    assert "0001234-56.2023.8.26.0100" not in sanitized
    assert "12.345.678/0001-90" not in sanitized
    assert "123.456.789-00" not in sanitized
    assert "perito@tribunal.jus.br" not in sanitized
    assert "[PROCESSO ANÔNIMO]" in sanitized
    print("✓ Sanitizer test passed successfully.")


def test_slugify():
    assert slugify("Reforma Tributária e Software: O que Muda?") == "reforma-tributaria-e-software-o-que-muda"
    assert slugify("Test 123! & Special Chars") == "test-123-special-chars"
    print("✓ Slugify test passed successfully.")


def test_markdown_adapter(tmp_path: Path):
    adapter = MarkdownArchiveAdapter(base_dir=str(tmp_path))
    res = adapter.save_article(
        title="Auditando Bancos de Dados em Perícia Judicial",
        content_markdown="Aqui está o conteúdo técnico da perícia...",
        category="pericia-judicial",
        tags=["pericia", "sql", "forense"],
    )

    assert res["success"] is True
    saved_file = Path(res["filepath"])
    assert saved_file.exists()

    content = saved_file.read_text(encoding="utf-8")
    assert 'title: "Auditando Bancos de Dados em Perícia Judicial"' in content
    assert "category: \"pericia-judicial\"" in content
    assert "- pericia" in content

    recent = adapter.list_recent(limit=5)
    assert len(recent) == 1
    assert recent[0]["name"] == res["filename"]
    print("✓ Markdown adapter test passed successfully.")


def test_mcp_server():
    from src.server import (
        MCP_TOOL_ANNOTATIONS,
        omnipress_publish_article,
        omnipress_queue_post,
        omnipress_inspect_content,
        omnipress_list_articles,
        omnipress_list_recent,
    )

    required_tools = [
        "omnipress_publish_article",
        "omnipress_queue_post",
        "omnipress_inspect_content",
        "omnipress_list_articles",
        "omnipress_list_recent",
    ]

    for tool_name in required_tools:
        assert tool_name in MCP_TOOL_ANNOTATIONS, f"Missing annotation for {tool_name}"
        annot = MCP_TOOL_ANNOTATIONS[tool_name]
        for key in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
            assert isinstance(annot.get(key), bool), f"{key} in {tool_name} must be a boolean"

    # Verify structured docstrings
    for func in (omnipress_publish_article, omnipress_queue_post, omnipress_inspect_content, omnipress_list_articles):
        doc = func.__doc__ or ""
        assert "Use when:" in doc, f"{func.__name__} docstring missing 'Use when:'"
        assert "Do NOT use when:" in doc, f"{func.__name__} docstring missing 'Do NOT use when:'"
        assert "Returns:" in doc, f"{func.__name__} docstring missing 'Returns:'"

    # Verify alias parity
    canonical_res = omnipress_list_articles(limit=5)
    alias_res = omnipress_list_recent(limit=5)
    assert canonical_res == alias_res, "omnipress_list_articles and omnipress_list_recent must yield identical output"
    print("✓ MCP server annotations, docstrings, and alias parity passed successfully.")


if __name__ == "__main__":
    test_sanitizer_detection()
    test_slugify()
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_markdown_adapter(Path(tmpdir))
    test_mcp_server()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
