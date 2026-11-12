"""Unit tests for the parts of scraper.py that do not need a browser."""
import csv

import scraper


class FakeAnchor:
    def __init__(self, href):
        self._href = href

    def get_attribute(self, name):
        return self._href if name == "href" else None


class FakeDriver:
    def __init__(self, anchors):
        self._anchors = anchors

    def find_elements(self, by, sel):
        return self._anchors


def test_read_prompts_skips_blank_rows(tmp_path):
    p = tmp_path / "prompts.csv"
    with open(p, "w", newline="") as f:
        csv.writer(f).writerows([["What is GEO?"], [], ["  "], ["Best AI agencies"]])
    assert scraper.read_prompts(str(p)) == ["What is GEO?", "Best AI agencies"]


def test_read_prompts_defaults_without_file():
    assert scraper.read_prompts(None) == scraper.DEFAULT_PROMPTS


def test_clean_url_strips_trailing_punctuation_and_fragment():
    assert scraper.clean_url("https://example.com/a).") == "https://example.com/a"
    assert scraper.clean_url("https://example.com/a#x") == "https://example.com/a"


def test_extract_citations_merges_links_and_text_and_drops_internal():
    site = scraper.SITES["chatgpt"]
    driver = FakeDriver([FakeAnchor("https://chatgpt.com/c/123"), FakeAnchor("https://one.com/x?utm=1")])
    text = "See https://two.org/page) and https://one.com/x?utm=1 for more."
    assert scraper.extract_citations(driver, site, text) == [
        "https://one.com/x?utm=1",
        "https://two.org/page",
    ]


def test_result_row_has_error_column():
    r = scraper.Result(idx=1, prompt="q", error="boom")
    assert r.to_row()["error"] == "boom"
    assert r.to_row()["citations"] == ""
