from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "privacy-legal" / "skills" / "kr-pipa-dpa-review" / "SKILL.md"
README = ROOT / "privacy-legal" / "README.md"
SOURCE_CATALOG = ROOT / "references" / "korea" / "source-catalog.md"
MCP_GUIDE = ROOT / "docs" / "implementation" / "korean-law-mcp-setup.md"
PLAYBOOK = ROOT / "privacy-legal" / "references" / "korea-pipa-dpa-playbook.md"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "korean_law_mcp"
REVIEW_FIXTURE_DIR = ROOT / "tests" / "fixtures" / "kr_pipa_dpa_review"
SMOKE = ROOT / "scripts" / "korean_law_mcp_smoke.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_kr_pipa_dpa_skill_exists_with_source_and_review_gates():
    text = read(SKILL)

    required_phrases = [
        "name: kr-pipa-dpa-review",
        "개인정보 보호법",
        "PIPA",
        "korean-law-mcp",
        "verified_source",
        "model_inference",
        "requires_professional_review",
        "제26조",
        "제28조의8",
        "처리위탁",
        "제3자 제공",
        "국외 이전",
        "pass / conditional / fail",
        "required gaps",
        "recommended improvements",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_privacy_readme_exposes_kr_command():
    text = read(README)

    assert "/privacy-legal:kr-pipa-dpa-review" in text
    assert "Korea PIPA" in text


def test_korea_source_catalog_links_skill_to_mcp_setup():
    source_catalog = read(SOURCE_CATALOG)
    mcp_guide = read(MCP_GUIDE)

    assert "chrisryugj/korean-law-mcp" in source_catalog
    assert "korean-law-mcp" in mcp_guide
    assert "MCP" in mcp_guide


def test_korea_playbook_covers_pipa_dpa_review_matrix():
    text = read(PLAYBOOK)

    for phrase in [
        "처리위탁",
        "제3자 제공",
        "국외 이전",
        "AI vendor overlay",
        "제26조",
        "제28조의8",
        "required gaps",
    ]:
        assert phrase in text


def test_korean_law_mcp_fixtures_have_expected_source_schema():
    fixture_paths = sorted(FIXTURE_DIR.glob("*.json"))
    assert fixture_paths

    required_keys = {
        "source_family",
        "title",
        "identifier",
        "retrieval_status",
        "retrieved_at",
        "used_for",
        "source_status",
    }

    for fixture_path in fixture_paths:
        import json

        doc = json.loads(fixture_path.read_text(encoding="utf-8"))
        assert required_keys <= set(doc)
        assert doc["retrieval_status"] in {"retrieved", "not_found", "error"}
        assert doc["source_status"] in {
            "verified_source",
            "user_supplied_unverified",
            "model_inference",
        }


def test_live_smoke_script_is_api_key_gated_and_documents_user_entrypoint():
    smoke = read(SMOKE)
    guide = read(MCP_GUIDE)

    for phrase in [
        "LAW_OC",
        "KOREAN_LAW_API_KEY",
        "npx",
        "korean-law-mcp@latest",
        "search_law",
        "개인정보 보호법",
        "skip",
    ]:
        assert phrase in smoke

    assert '"-p",' in smoke
    assert '"korean-law",' in smoke
    assert '"korean-law-mcp@latest",' in smoke
    assert "python3 scripts/korean_law_mcp_smoke.py" in guide
    assert "export LAW_OC=" in guide


def test_live_smoke_script_fetches_pipa_core_articles_after_search():
    smoke = read(SMOKE)

    for article in ["제26조", "제28조의8", "제29조", "제34조"]:
        assert article in smoke

    assert "get_law_text" in smoke
    assert "PIPA_CORE_ARTICLES" in smoke
    assert "PIPA deep smoke ok" in smoke


def test_sample_dpa_review_fixture_defines_end_to_end_expected_shape():
    sample = read(REVIEW_FIXTURE_DIR / "sample_vendor_dpa.md")
    expected = read(REVIEW_FIXTURE_DIR / "expected_review_skeleton.md")

    for phrase in [
        "국외 이전",
        "AI training",
        "subprocessor",
        "breach notification",
    ]:
        assert phrase in sample

    for phrase in [
        "Verdict: conditional",
        "required gaps",
        "recommended improvements",
        "source status",
        "requires_professional_review",
        "제26조",
        "제28조의8",
    ]:
        assert phrase in expected
