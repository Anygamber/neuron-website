"""Homepage language tags must be in the first HTML byte, not only after JS."""

from __future__ import annotations

import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import PROJECT_ROOT
from app.seo_html import inject_lang_meta, load_catalog, resolve_lang


class SeoHtmlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_catalog.cache_clear()

    def test_resolve_unknown_lang_falls_back_to_uzbek(self) -> None:
        self.assertEqual(resolve_lang(None), "uz")
        self.assertEqual(resolve_lang("DE"), "uz")
        self.assertEqual(resolve_lang("en"), "en")

    def test_russian_canonical_and_title_are_in_the_html(self) -> None:
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
        body, html_lang = inject_lang_meta(html, "ru")
        self.assertEqual(html_lang, "ru")
        self.assertRegex(body, r'<html\s+lang="ru"\s+data-lang="ru"')
        self.assertIn("<title>Нейрохирург Ташкент | NeurON — нейрохирургия и Центр боли</title>", body)
        self.assertIn('rel="canonical" href="https://neuronmedical.uz/?lang=ru"', body)
        self.assertIn('property="og:url" content="https://neuronmedical.uz/?lang=ru"', body)
        self.assertIn("лечение боли", body)
        self.assertNotIn("Pain Management (блокады", body)

    def test_english_ampersand_is_escaped(self) -> None:
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
        body, html_lang = inject_lang_meta(html, "en")
        self.assertEqual(html_lang, "en")
        self.assertRegex(body, r'<html\s+lang="en"\s+data-lang="en"')
        self.assertIn("Neurosurgery &amp; Pain Management", body)
        self.assertIn('rel="canonical" href="https://neuronmedical.uz/?lang=en"', body)

    def test_sitemap_has_no_fragment_urls(self) -> None:
        sitemap = (PROJECT_ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("#", sitemap)
        for lang in ("uz", "ru", "en"):
            self.assertIn(f"https://neuronmedical.uz/?lang={lang}", sitemap)
        self.assertEqual(sitemap.count('hreflang="x-default"'), 3)

    def test_clinic_figures_offer_webp(self) -> None:
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
        clinic = Path(PROJECT_ROOT / "images" / "clinic")
        for webp in clinic.glob("*.webp"):
            self.assertIn(f'srcset="images/clinic/{webp.name}"', html)
            self.assertTrue(webp.read_bytes().startswith(b"RIFF"))


class HomepageRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from app.factory import create_app

        cls.client = TestClient(create_app())

    def test_query_lang_is_visible_without_javascript(self) -> None:
        response = self.client.get("/?lang=ru")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-language"], "ru")
        self.assertIn("Нейрохирург Ташкент", response.text)
        self.assertIn('rel="canonical" href="https://neuronmedical.uz/?lang=ru"', response.text)

    def test_index_html_redirects_to_the_canonical_home(self) -> None:
        response = self.client.get("/index.html?lang=en", follow_redirects=False)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers["location"], "/?lang=en")

    def test_missing_path_is_a_real_404(self) -> None:
        response = self.client.get("/no-such-page")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Sahifa topilmadi", response.text)
        self.assertIn('content="noindex"', response.text)


if __name__ == "__main__":
    unittest.main()
