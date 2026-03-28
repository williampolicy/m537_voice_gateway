"""
M537 Voice Gateway - Mobile & PWA Tests
Tests for mobile optimization and PWA features
"""
import pytest
import os
import json


class TestMobileCSS:
    """Tests for mobile-responsive CSS"""

    @pytest.fixture
    def css_content(self):
        css_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend', 'css', 'styles.css'
        )
        with open(css_path, 'r') as f:
            return f.read()

    def test_has_mobile_breakpoints(self, css_content):
        """Test CSS has mobile breakpoints"""
        assert '@media (max-width: 768px)' in css_content
        assert '@media (max-width: 480px)' in css_content
        assert '@media (max-width: 360px)' in css_content

    def test_has_touch_friendly_styles(self, css_content):
        """Test CSS has touch-friendly enhancements"""
        assert '@media (hover: none)' in css_content
        assert 'pointer: coarse' in css_content

    def test_has_safe_area_insets(self, css_content):
        """Test CSS supports notched devices"""
        assert 'env(safe-area-inset' in css_content

    def test_has_dark_mode(self, css_content):
        """Test CSS has dark mode support"""
        assert '@media (prefers-color-scheme: dark)' in css_content

    def test_has_reduced_motion(self, css_content):
        """Test CSS respects reduced motion preference"""
        assert '@media (prefers-reduced-motion: reduce)' in css_content

    def test_has_high_contrast(self, css_content):
        """Test CSS has high contrast mode"""
        assert '@media (prefers-contrast: high)' in css_content

    def test_has_landscape_orientation(self, css_content):
        """Test CSS handles landscape orientation"""
        assert 'orientation: landscape' in css_content

    def test_has_pwa_standalone_styles(self, css_content):
        """Test CSS has PWA standalone mode styles"""
        assert '@media (display-mode: standalone)' in css_content

    def test_has_print_styles(self, css_content):
        """Test CSS has print styles"""
        assert '@media print' in css_content

    def test_has_rtl_support(self, css_content):
        """Test CSS has RTL language support"""
        assert '[dir="rtl"]' in css_content


class TestPWAManifest:
    """Tests for PWA manifest"""

    @pytest.fixture
    def manifest(self):
        manifest_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend', 'manifest.json'
        )
        with open(manifest_path, 'r') as f:
            return json.load(f)

    def test_manifest_has_name(self, manifest):
        """Test manifest has name"""
        assert 'name' in manifest
        assert len(manifest['name']) > 0

    def test_manifest_has_short_name(self, manifest):
        """Test manifest has short name"""
        assert 'short_name' in manifest
        assert len(manifest['short_name']) <= 12

    def test_manifest_has_icons(self, manifest):
        """Test manifest has icons"""
        assert 'icons' in manifest
        assert len(manifest['icons']) > 0

    def test_manifest_has_required_icon_sizes(self, manifest):
        """Test manifest has required icon sizes"""
        sizes = [icon['sizes'] for icon in manifest['icons']]
        assert '192x192' in sizes
        assert '512x512' in sizes

    def test_manifest_has_start_url(self, manifest):
        """Test manifest has start URL"""
        assert 'start_url' in manifest

    def test_manifest_has_display_mode(self, manifest):
        """Test manifest has display mode"""
        assert 'display' in manifest
        assert manifest['display'] in ['standalone', 'fullscreen', 'minimal-ui', 'browser']

    def test_manifest_has_theme_color(self, manifest):
        """Test manifest has theme color"""
        assert 'theme_color' in manifest

    def test_manifest_has_background_color(self, manifest):
        """Test manifest has background color"""
        assert 'background_color' in manifest

    def test_manifest_has_orientation(self, manifest):
        """Test manifest has orientation"""
        assert 'orientation' in manifest


class TestServiceWorker:
    """Tests for service worker"""

    @pytest.fixture
    def sw_content(self):
        sw_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend', 'sw.js'
        )
        with open(sw_path, 'r') as f:
            return f.read()

    def test_sw_has_cache_name(self, sw_content):
        """Test service worker has cache name"""
        assert 'CACHE_NAME' in sw_content or 'cacheName' in sw_content.lower()

    def test_sw_handles_install(self, sw_content):
        """Test service worker handles install event"""
        assert "'install'" in sw_content

    def test_sw_handles_activate(self, sw_content):
        """Test service worker handles activate event"""
        assert "'activate'" in sw_content

    def test_sw_handles_fetch(self, sw_content):
        """Test service worker handles fetch event"""
        assert "'fetch'" in sw_content

    def test_sw_has_offline_support(self, sw_content):
        """Test service worker has offline support"""
        # Should cache or have fallback
        assert 'cache' in sw_content.lower()


class TestAccessibility:
    """Tests for accessibility features"""

    @pytest.fixture
    def html_content(self):
        html_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend', 'index.html'
        )
        with open(html_path, 'r') as f:
            return f.read()

    def test_html_has_lang_attribute(self, html_content):
        """Test HTML has lang attribute"""
        assert 'lang="' in html_content

    def test_html_has_skip_link(self, html_content):
        """Test HTML has skip link for keyboard navigation"""
        assert 'skip-link' in html_content

    def test_html_has_aria_labels(self, html_content):
        """Test HTML has ARIA labels"""
        assert 'aria-label' in html_content

    def test_html_has_aria_live_regions(self, html_content):
        """Test HTML has ARIA live regions"""
        assert 'aria-live' in html_content

    def test_html_has_role_attributes(self, html_content):
        """Test HTML has role attributes"""
        assert 'role="' in html_content

    def test_html_has_offline_indicator(self, html_content):
        """Test HTML has offline indicator"""
        assert 'offline' in html_content.lower()


class TestToastNotifications:
    """Tests for toast notification system"""

    @pytest.fixture
    def toast_content(self):
        toast_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend', 'js', 'toast.js'
        )
        with open(toast_path, 'r') as f:
            return f.read()

    def test_toast_has_show_method(self, toast_content):
        """Test toast has show method"""
        assert 'show(' in toast_content

    def test_toast_has_success_method(self, toast_content):
        """Test toast has success method"""
        assert 'success(' in toast_content

    def test_toast_has_error_method(self, toast_content):
        """Test toast has error method"""
        assert 'error(' in toast_content

    def test_toast_has_remove_method(self, toast_content):
        """Test toast has remove method"""
        assert 'remove(' in toast_content

    def test_toast_is_globally_available(self, toast_content):
        """Test toast is globally available"""
        assert 'window.toast' in toast_content


# Run tests with: pytest tests/test_mobile_pwa.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
