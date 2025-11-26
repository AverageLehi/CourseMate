import pytest

from tags_utils import _normalize_token, sanitize_tags_from_text, extract_hashtags_from_text


def test_normalize_token_basic():
    assert _normalize_token('Cornell Notes') == 'cornell-notes'
    assert _normalize_token('#Main Idea & Details') == 'main-idea-details'


def test_sanitize_tags_from_text():
    inp = ' , #Cornell Notes, cornell-notes, #cornell NOTES  ,'
    out = sanitize_tags_from_text(inp)
    assert out == ['#cornell-notes']


def test_sanitize_handles_empty_and_duplicates():
    assert sanitize_tags_from_text('') == []
    assert sanitize_tags_from_text('  , , #a, #A, a') == ['#a']


def test_extract_hashtags_from_text():
    txt = "This is a #note about #Math and #science. Repeated #math should dedupe."
    assert extract_hashtags_from_text(txt) == ['#note', '#math', '#science']


def test_extract_hashtags_edgecases():
    assert extract_hashtags_from_text('no tags here') == []
    # underscores / hyphens are normalized by _normalize_token which strips non-alphanumeric characters
    assert extract_hashtags_from_text('#Main-Idea #main_idea') == ['#mainidea']
