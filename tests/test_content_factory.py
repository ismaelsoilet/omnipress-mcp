"""
Test suite for OmniPress Content Factory (v0.5.0).
Validates all 12 specialized subagents, the 4 declarative recipes,
the handoff JSON schemas, and master skill metadata.
"""

import json
from pathlib import Path
import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".agents" / "agents"
RECIPES_DIR = REPO_ROOT / ".agents" / "recipes"
SCHEMAS_DIR = REPO_ROOT / ".agents" / "schemas"
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"


def test_content_factory_schemas_validity():
    """Ensure all handoff JSON schemas are valid JSON Schema Draft-07 documents."""
    schema_files = [
        "recipe.schema.json",
        "roteiro.schema.json",
        "production_log.schema.json",
        "audit_report.schema.json",
    ]
    for schema_file in schema_files:
        path = SCHEMAS_DIR / schema_file
        assert path.exists(), f"Schema {schema_file} must exist"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        jsonschema.Draft7Validator.check_schema(data)


def test_content_factory_recipes_conformance():
    """Ensure all declarative execution recipes conform to recipe.schema.json."""
    recipe_schema_path = SCHEMAS_DIR / "recipe.schema.json"
    with open(recipe_schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validator = jsonschema.Draft7Validator(schema)
    expected_recipes = ["express.json", "standard.json", "full_production.json", "remix.json"]

    for recipe_name in expected_recipes:
        recipe_path = RECIPES_DIR / recipe_name
        assert recipe_path.exists(), f"Recipe {recipe_name} must exist"
        with open(recipe_path, "r", encoding="utf-8") as f:
            recipe_data = json.load(f)
        errors = list(validator.iter_errors(recipe_data))
        assert len(errors) == 0, f"Recipe {recipe_name} validation failed: {errors}"


def test_content_factory_all_twelve_agents_present():
    """Ensure all 12 specialized agent definition files exist with complete YAML frontmatter."""
    expected_agents = [
        "01_researcher_scriptwriter.md",
        "02_image_curator.md",
        "03_audio_engineer.md",
        "04_language_reviewer.md",
        "05_timing_checker.md",
        "06_visual_verifier.md",
        "07_vfx_remotion.md",
        "08_sfx_designer.md",
        "09_soundtrack_director.md",
        "10_narration_director.md",
        "11_adversarial_auditor.md",
        "12_director_orchestrator.md",
    ]

    for agent_file in expected_agents:
        path = AGENTS_DIR / agent_file
        assert path.exists(), f"Agent file {agent_file} must exist"
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---"), f"{agent_file} must have YAML frontmatter"
        assert "## Papel" in content, f"{agent_file} must document ## Papel"
        assert "## Entradas" in content, f"{agent_file} must document ## Entradas"
        assert "## Saídas" in content, f"{agent_file} must document ## Saídas"
        assert "## Comportamento Obrigatório" in content, f"{agent_file} must document ## Comportamento Obrigatório"
        assert "## Critérios de Sucesso" in content, f"{agent_file} must document ## Critérios de Sucesso"


def test_content_factory_master_skill_present():
    """Ensure the master content-factory skill exists and contains operational directives."""
    skill_path = SKILLS_DIR / "content-factory" / "SKILL.md"
    assert skill_path.exists(), "Master skill content-factory/SKILL.md must exist"
    content = skill_path.read_text(encoding="utf-8")
    assert "name: content-factory" in content
    assert "AG12" in content
    assert "Express" in content
    assert "Full Production" in content
