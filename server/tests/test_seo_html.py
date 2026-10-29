"""Homepage language tags must be in the first HTML byte, not only after JS."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from app.config import PROJECT_ROOT
from app.seo_html import inject_lang_meta, load_catalog, load_schema, resolve_lang


class SeoHtmlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_catalog.cache_clear()
        load_schema.cache_clear()

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

    def test_schema_matches_visible_language_and_nap(self) -> None:
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("+998 (71) 200-00-20", html)
        self.assertEqual(html.count("Ташкент, Юнусабад, Отчопар-2, 3-й проезд Чинабад, дом 2"), 2)
        self.assertIn("+998 71 200 00 20", html)

        ru_body, _lang = inject_lang_meta(html, "ru")
        ru = _json_ld(ru_body)
        clinic = _clinic(ru)
        self.assertIn("MedicalClinic", clinic["@type"])
        self.assertNotIn("Hospital", clinic["@type"])
        self.assertEqual(clinic["name"], "NeurON Medical Centre")
        self.assertEqual(clinic["telephone"], "+998 71 200 00 20")
        self.assertEqual(
            clinic["address"]["streetAddress"],
            "Юнусабад, Отчопар-2, 3-й проезд Чинабад, дом 2",
        )
        self.assertEqual(clinic["address"]["addressLocality"], "Ташкент")
        self.assertEqual(
            clinic["sameAs"],
            [
                "https://t.me/neuronmedical_center",
                "https://www.instagram.com/neuron.medical.uz/",
                "https://www.facebook.com/profile.php?id=61595203029647",
            ],
        )
        hours = clinic["openingHoursSpecification"][0]
        self.assertEqual(hours["opens"], "08:00")
        self.assertEqual(hours["closes"], "20:00")
        self.assertIn("https://schema.org/Monday", hours["dayOfWeek"])
        self.assertIn("https://schema.org/Saturday", hours["dayOfWeek"])
        self.assertNotIn("https://schema.org/Sunday", hours["dayOfWeek"])

        faq = next(node for node in ru["@graph"] if node["@type"] == "FAQPage")
        self.assertEqual(faq["inLanguage"], "ru")
        self.assertEqual(len(faq["mainEntity"]), 4)
        self.assertEqual(
            faq["mainEntity"][0]["name"],
            "Кто такой нейрохирург и когда обращаться в Ташкенте?",
        )
        self.assertIn(faq["mainEntity"][2]["acceptedAnswer"]["text"], ru_body)
        self.assertIn("импульсную радиочастотную терапию", ru_body)

        physicians = [node for node in ru["@graph"] if node["@type"] == "Physician"]
        self.assertEqual(len(physicians), 39)
        self.assertEqual(ru_body.count('id="doctor-burnashev"'), 1)
        self.assertIn('data-i18n="doctors.more"', ru_body)
        added = next(node for node in physicians if node["@id"].endswith("#doctor-abdurahmanov"))
        self.assertEqual(added["name"], "Абдурахманов Отабек Мухамматсолиевич")
        self.assertEqual(added["medicalSpecialty"], "Гематолог-трансфузиолог")
        self.assertEqual(added["worksFor"], {"@id": "https://neuronmedical.uz/#organization"})
        self.assertIn(">Абдурахманов Отабек Мухамматсолиевич<", ru_body)
        burnashev = next(node for node in physicians if node["@id"].endswith("#doctor-burnashev"))
        self.assertEqual(burnashev["name"], "Бурнашев Марсель Ильдарович")
        self.assertEqual(burnashev["medicalSpecialty"], "Врач высшей категории · Нейрохирург")
        self.assertEqual(burnashev["worksFor"], {"@id": "https://neuronmedical.uz/#organization"})
        self.assertEqual(
            burnashev["image"],
            "https://neuronmedical.uz/images/doctors/placeholder.jpg",
        )
        self.assertEqual(
            burnashev["url"],
            "https://neuronmedical.uz/?lang=ru#doctor-burnashev",
        )
        self.assertIn(">Бурнашев Марсель Ильдарович<", ru_body)

        en_body, _lang = inject_lang_meta(html, "en")
        en = _json_ld(en_body)
        en_faq = next(node for node in en["@graph"] if node["@type"] == "FAQPage")
        self.assertEqual(en_faq["inLanguage"], "en")
        self.assertEqual(en_faq["mainEntity"][0]["name"], "What does a neurosurgeon treat in Tashkent?")
        self.assertIn(">What does a neurosurgeon treat in Tashkent?<", en_body)
        en_doc = next(
            node for node in en["@graph"] if node["@type"] == "Physician" and node["@id"].endswith("burnashev")
        )
        self.assertEqual(en_doc["name"], "Marsel Ildarovich Burnashev")
        self.assertIn(">Marsel Ildarovich Burnashev<", en_body)
        en_added = next(
            node for node in en["@graph"] if node["@type"] == "Physician" and node["@id"].endswith("abdurahmanov")
        )
        self.assertEqual(en_added["name"], "Otabek Muhammatsolievich Abdurahmanov")
        self.assertIn(">Otabek Muhammatsolievich Abdurahmanov<", en_body)
        self.assertEqual(len([node for node in en["@graph"] if node["@type"] == "Physician"]), 39)
        self.assertNotIn("Кто такой нейрохирург и когда обращаться в Ташкенте?", en_body)

        uz_body, _lang = inject_lang_meta(html, "uz")
        uz = _json_ld(uz_body)
        uz_faq = next(node for node in uz["@graph"] if node["@type"] == "FAQPage")
        self.assertEqual(uz_faq["mainEntity"][0]["name"], "Neyroxirurg kim va Toshkentda qachon murojaat qilish kerak?")
        self.assertIn(">Neyroxirurg kim va Toshkentda qachon murojaat qilish kerak?<", uz_body)
        self.assertIn(">Abdurahmanov Otabek Muhammatsolievich<", uz_body)
        self.assertEqual(len([node for node in uz["@graph"] if node["@type"] == "Physician"]), 39)

    def test_geo_pin_and_breadcrumbs_follow_the_language(self) -> None:
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            'name="google-site-verification" content="Shz3pfUKHM2TyL6iZdIZepvHQAAe4klejX5C31PNIyQ"',
            html,
        )
        self.assertIn('name="geo.region" content="UZ-TK"', html)
        self.assertIn('name="geo.position" content="41.3549516;69.3108567"', html)
        self.assertIn('name="ICBM" content="41.3549516, 69.3108567"', html)
        self.assertNotIn("UZ-TO", html)
        self.assertIn("Тошкент, Юнусобод тумани", html)
        for href in (
            "https://go.2gis.com/ZarM1",
            "https://maps.app.goo.gl/KBZqrHesEsAqRX5F9",
            "https://yandex.uz/maps/-/CXeOi6mH",
        ):
            self.assertIn(f'href="{href}"', html)
            self.assertRegex(html, rf'href="{re.escape(href)}"[^>]*rel="noopener noreferrer"')

        ru_body, _lang = inject_lang_meta(html, "ru")
        self.assertEqual(
            ru_body.count(
                'name="google-site-verification" content="Shz3pfUKHM2TyL6iZdIZepvHQAAe4klejX5C31PNIyQ"'
            ),
            1,
        )
        ru = _json_ld(ru_body)
        clinic = _clinic(ru)
        self.assertEqual(clinic["geo"]["latitude"], 41.3549516)
        self.assertEqual(clinic["geo"]["longitude"], 69.3108567)
        self.assertIn("https://maps.app.goo.gl/KBZqrHesEsAqRX5F9", clinic["hasMap"])
        ru_crumb = next(node for node in ru["@graph"] if node["@type"] == "BreadcrumbList")
        self.assertEqual(
            [item["name"] for item in ru_crumb["itemListElement"]],
            ["Главная", "Русская версия"],
        )
        self.assertEqual(ru_crumb["itemListElement"][1]["item"], "https://neuronmedical.uz/?lang=ru")

        en_body, _lang = inject_lang_meta(html, "en")
        en_crumb = next(node for node in _json_ld(en_body)["@graph"] if node["@type"] == "BreadcrumbList")
        self.assertEqual(
            [item["name"] for item in en_crumb["itemListElement"]],
            ["Home", "English version"],
        )
        self.assertIn('name="geo.region" content="UZ-TK"', en_body)

        uz_body, _lang = inject_lang_meta(html, "uz")
        uz_crumb = next(node for node in _json_ld(uz_body)["@graph"] if node["@type"] == "BreadcrumbList")
        self.assertEqual([item["name"] for item in uz_crumb["itemListElement"]], ["Bosh sahifa"])
        self.assertEqual(uz_crumb["itemListElement"][0]["item"], "https://neuronmedical.uz/?lang=uz")

        missing = (PROJECT_ROOT / "404.html").read_text(encoding="utf-8")
        self.assertIn('"@type": "BreadcrumbList"', missing)
        self.assertIn("Sahifa topilmadi", missing)
        self.assertIn('name="geo.region" content="UZ-TK"', missing)

    def test_clinic_figures_offer_webp(self) -> None:
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
        clinic = Path(PROJECT_ROOT / "images" / "clinic")
        for webp in clinic.glob("*.webp"):
            self.assertIn(f'srcset="images/clinic/{webp.name}"', html)
            self.assertTrue(webp.read_bytes().startswith(b"RIFF"))


def _json_ld(html: str) -> dict:
    match = re.search(
        r'<script\s+type="application/ld\+json"\s+id="neuron-schema-org">(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        raise AssertionError("JSON-LD block is missing")
    return json.loads(match.group(1))


def _clinic(graph: dict) -> dict:
    for node in graph["@graph"]:
        types = node.get("@type")
        if isinstance(types, str):
            types = [types]
        if types and "MedicalClinic" in types:
            return node
    raise AssertionError("MedicalClinic is missing")


class HomepageRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from fastapi.testclient import TestClient

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
