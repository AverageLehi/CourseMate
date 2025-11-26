import pytest
from formatting_utils import (
    toggle_bold,
    toggle_italic,
    toggle_underline,
    toggle_strikethrough,
    toggle_bullets,
    parse_inline_markers,
    inline_markers_to_spans,
    toggle_span,
)


def test_toggle_bold_wrap_unwrap():
    t = "Hello world"
    new, s, e = toggle_bold(t, 6, 11)  # 'world'
    assert new == "Hello **world**"
    # unwrap
    new2, s2, e2 = toggle_bold(new, s, e)
    assert new2 == t


def test_toggle_italic_wrap_selection():
    t = "abc"
    # select 'b' (offsets 1..2)
    new, s, e = toggle_italic(t, 1, 2)
    assert new == "a*b*c"


def test_toggle_underline_and_strike():
    t = "Note this"
    n1, s1, e1 = toggle_underline(t, 5, 9)
    assert "<u>this</u>" in n1
    n2, s2, e2 = toggle_strikethrough(t, 5, 9)
    assert "~~this~~" in n2


def test_toggle_bullets_add_remove():
    t = "Line1\nLine2\nLine3"
    new, s, e = toggle_bullets(t, 0, len(t))
    assert new.split('\n')[0].startswith('• ')
    # remove bullets
    removed, s2, e2 = toggle_bullets(new, 0, len(new))
    assert removed.split('\n')[0] == 'Line1'


def test_toggle_bullets_on_empty_lines():
    t = "Line1\n\nLine3"
    new, s, e = toggle_bullets(t, 0, len(t))
    # middle empty line should receive a bullet marker
    assert new.split('\n')[1].startswith('• ')
    # removing bullets should restore empty line
    removed, s2, e2 = toggle_bullets(new, 0, len(new))
    assert removed.split('\n')[1] == ''


def test_parse_inline_markers_finds_markers():
    t = "Start **bold** middle *italic* <u>under</u> end ~~strike~~"
    markers = parse_inline_markers(t)
    tags = {m[0] for m in markers}
    assert {'bold', 'italic', 'underline', 'strike'} <= tags


def test_inline_markers_to_spans_and_migration():
    t = "Hello **World** and *italic* and <u>under</u> and ~~strike~~"
    plain, spans = inline_markers_to_spans(t)
    assert 'World' in plain and 'italic' in plain
    tags = {s['tag'] for s in spans}
    assert {'bold', 'italic', 'underline', 'strike'} <= tags


def test_toggle_span_add_remove():
    spans = []
    spans = toggle_span(spans, 'bold', 5, 10)
    assert any(s['tag'] == 'bold' for s in spans)
    spans = toggle_span(spans, 'bold', 5, 10)
    assert not any(s['tag'] == 'bold' for s in spans)
