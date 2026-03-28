"""
M537 Voice Gateway - Internationalization Tests
Tests for multi-language support
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.i18n import TranslationService, translator, t, detect_language


class TestTranslationService:
    """Test TranslationService functionality"""

    def test_translate_chinese_default(self):
        """Chinese should be the default language"""
        result = translator.translate(
            "count_projects.success",
            total=100, p0=10, p1=20, p2=30, p3=40
        )
        assert "当前共有 100 个项目" in result
        assert "P0 项目 10 个" in result

    def test_translate_english(self):
        """English translation should work"""
        result = translator.translate(
            "count_projects.success",
            language="en-US",
            total=100, p0=10, p1=20, p2=30, p3=40
        )
        assert "100 projects" in result
        assert "P0: 10" in result

    def test_translate_japanese(self):
        """Japanese translation should work"""
        result = translator.translate(
            "count_projects.success",
            language="ja-JP",
            total=100, p0=10, p1=20, p2=30, p3=40
        )
        assert "100 件のプロジェクト" in result
        assert "P0: 10件" in result

    def test_translate_fallback_to_default(self):
        """Unknown language should fallback to default"""
        result = translator.translate(
            "count_projects.success",
            language="fr-FR",  # Not supported
            total=100, p0=10, p1=20, p2=30, p3=40
        )
        # Should fallback to Chinese
        assert "当前共有" in result

    def test_translate_unknown_key(self):
        """Unknown key should return the key itself"""
        result = translator.translate("unknown.key")
        assert result == "unknown.key"

    def test_translate_with_missing_params(self):
        """Missing parameters should not cause errors"""
        # Template expects more params, but we only provide some
        result = translator.translate(
            "count_projects.success",
            total=100
        )
        # Should not crash - will have unformatted placeholders
        # The template is returned with {placeholders} intact
        assert "{total}" in result or "100" in result


class TestLanguageDetection:
    """Test Accept-Language header parsing"""

    def test_detect_exact_match(self):
        """Exact language match should work"""
        ts = TranslationService()
        lang = ts.get_language_from_header("en-US")
        assert lang == "en-US"

    def test_detect_with_quality(self):
        """Languages with quality values should be sorted"""
        ts = TranslationService()
        # Prefer Chinese even though it has lower quality
        lang = ts.get_language_from_header("en-US;q=0.5,zh-CN;q=0.9")
        assert lang == "zh-CN"

    def test_detect_language_family(self):
        """Language family should match"""
        ts = TranslationService()
        # 'en' should match 'en-US'
        lang = ts.get_language_from_header("en")
        assert lang == "en-US"

    def test_detect_complex_header(self):
        """Complex Accept-Language header should work"""
        ts = TranslationService()
        lang = ts.get_language_from_header("zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7")
        assert lang == "zh-CN"

    def test_detect_empty_header(self):
        """Empty header should return default"""
        ts = TranslationService()
        lang = ts.get_language_from_header("")
        assert lang == "zh-CN"

    def test_detect_unsupported_language(self):
        """Unsupported language should return default"""
        ts = TranslationService()
        lang = ts.get_language_from_header("fr-FR,de-DE")
        assert lang == "zh-CN"


class TestShorthandFunctions:
    """Test shorthand translation functions"""

    def test_t_function(self):
        """t() shorthand should work"""
        result = t("count_projects.empty")
        assert "当前没有" in result

    def test_t_with_language(self):
        """t() with language parameter should work"""
        result = t("count_projects.empty", language="en-US")
        assert "No projects" in result

    def test_t_with_params(self):
        """t() with format parameters should work"""
        result = t(
            "recent_errors.success",
            hours=24,
            count=5,
            errors="Error1, Error2"
        )
        assert "24" in result
        assert "5" in result

    def test_detect_language_from_headers(self):
        """detect_language() should work with dict headers"""
        lang = detect_language({"accept-language": "ja-JP,ja;q=0.9"})
        assert lang == "ja-JP"


class TestTranslationCoverage:
    """Test that all major translations exist"""

    @pytest.fixture
    def ts(self):
        return TranslationService()

    def test_all_languages_have_count_projects(self, ts):
        """All languages should have count_projects translations"""
        for lang in ts.SUPPORTED_LANGUAGES:
            result = ts.translate(
                "count_projects.success",
                language=lang,
                total=100, p0=10, p1=20, p2=30, p3=40
            )
            assert len(result) > 0
            assert "100" in result

    def test_all_languages_have_system_status(self, ts):
        """All languages should have system_status translations"""
        for lang in ts.SUPPORTED_LANGUAGES:
            result = ts.translate(
                "system_status.success",
                language=lang,
                cpu=50, memory=60, disk=70, warning=""
            )
            assert len(result) > 0
            assert "50" in result

    def test_all_languages_have_error_messages(self, ts):
        """All languages should have error message translations"""
        for lang in ts.SUPPORTED_LANGUAGES:
            result = ts.translate(
                "error.intent_not_recognized",
                language=lang
            )
            assert len(result) > 0


class TestIntegration:
    """Integration tests with actual API"""

    @pytest.fixture
    def client(self):
        from main import app
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_api_with_english_header(self, client):
        """API should respect Accept-Language header"""
        # Note: This test verifies the header is received,
        # but response language depends on implementation
        response = client.get(
            "/health",
            headers={"Accept-Language": "en-US"}
        )
        assert response.status_code == 200

    def test_api_with_japanese_header(self, client):
        """API should handle Japanese Accept-Language"""
        response = client.get(
            "/health",
            headers={"Accept-Language": "ja-JP"}
        )
        assert response.status_code == 200


# Run tests with: pytest tests/test_i18n.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
