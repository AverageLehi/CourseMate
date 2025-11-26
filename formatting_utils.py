import re
from typing import Tuple, List, Dict

# Markup conventions used by CourseMate formatting:
# - Bold:          **text**
# - Italic:        *text*
# - Underline:     <u>text</u>
# - Strikethrough: ~~text~~
# - Bullet:        line(s) starting with '• ' (toggle bullet adds/removes this marker per line)


class ContentModel:
    """Store text with markup markers visible (just like bullets work).
    
    The markers ARE part of the text content. Visual formatting makes them look good.
    """
    
    def __init__(self, markup_text: str = ""):
        """Initialize with markup text."""
        self.markup_content = markup_text
    
    def get_text(self) -> str:
        """Get text with markers (what's shown in UI and saved to file)."""
        return self.markup_content
    
    def set_text(self, text: str):
        """Update text content."""
        self.markup_content = text
    
    def get_formatting_spans(self) -> List[Dict]:
        """Get formatting spans for applying visual tags."""
        _, spans = inline_markers_to_spans(self.markup_content)
        return spans


def _wrap_selection(text: str, start: int, end: int, left: str, right: str = None) -> Tuple[str, int, int]:
    """Wrap the substring [start:end] with left and right markers and return updated text
    and new selection (start,end) which will encompass the inserted markers and original text.
    If right is None, use left for both sides.
    """
    if right is None:
        right = left
    if start >= end:
        # No selection: insert left+right and place cursor between
        new_text = text[:start] + left + right + text[end:]
        new_start = start + len(left)
        new_end = new_start
        return new_text, new_start, new_end

    new_text = text[:start] + left + text[start:end] + right + text[end:]
    new_start = start
    new_end = end + len(left) + len(right)
    return new_text, new_start, new_end


def _unwrap_selection(text: str, start: int, end: int, left: str, right: str = None) -> Tuple[str, int, int]:
    """If selection has left..right around it, remove them. Return updated text and new selection range.
    If right is None, use left for both sides.
    If markers not present, return original inputs unchanged.
    """
    if right is None:
        right = left
    # ensure segmentation is safe
    if start < len(left) and end + len(right) > len(text):
        return text, start, end
    # Check boundaries for left and right markers
    pre = text[:start]
    mid = text[start:end]
    post = text[end:]

    # If selection already contains markers (i.e. the markers surround the selection) remove them
    left_len = len(left)
    right_len = len(right)
    if start + left_len <= len(text) and end - right_len >= 0:
        if text[start:start+left_len] == left and text[end-right_len:end] == right:
            # Extract inner content between markers
            inner = text[start+left_len:end-right_len]
            new_text = text[:start] + inner + text[end:]
            new_start = start
            new_end = new_start + len(inner)
            return new_text, new_start, new_end
    return text, start, end


def toggle_bold(text: str, start: int, end: int) -> Tuple[str, int, int]:
    return _toggle_inline(text, start, end, '**', '**')


def toggle_italic(text: str, start: int, end: int) -> Tuple[str, int, int]:
    return _toggle_inline(text, start, end, '*', '*')


def toggle_underline(text: str, start: int, end: int) -> Tuple[str, int, int]:
    return _toggle_inline(text, start, end, '<u>', '</u>')


def toggle_strikethrough(text: str, start: int, end: int) -> Tuple[str, int, int]:
    return _toggle_inline(text, start, end, '~~', '~~')


def _toggle_inline(text: str, start: int, end: int, left: str, right: str = None) -> Tuple[str, int, int]:
    # First try to unwrap if already wrapped
    new_text, ns, ne = _unwrap_selection(text, start, end, left, right)
    if (new_text, ns, ne) != (text, start, end):
        return new_text, ns, ne
    # Otherwise wrap
    return _wrap_selection(text, start, end, left, right)


def toggle_bullets(text: str, start: int, end: int) -> Tuple[str, int, int]:
    """Toggle bullets ('- ') on lines overlapping [start:end]. Returns updated text and new selection indices.
    Behavior: if all selected lines start with '- ' then remove the prefix; otherwise, add '- ' to each selected line.
    """
    if start > end:
        start, end = end, start
    # Convert to line indices
    # Find start of first line
    s_line_start = text.rfind('\n', 0, start)
    s_line_start = s_line_start + 1 if s_line_start != -1 else 0
    # Find end of last line
    e_line_end = text.find('\n', end)
    e_line_end = e_line_end if e_line_end != -1 else len(text)

    block = text[s_line_start:e_line_end]
    lines = block.split('\n')
    marker = '• '
    # consider previous dash bullets for compatibility
    all_bulleted = all((line.startswith(marker) or line.startswith('- ')) for line in lines if line.strip() != '')

    if all_bulleted:
        # remove existing bullet markers ('• ' or '- ') from each non-empty line
        def strip_marker(line):
            if line.startswith(marker):
                return line[len(marker):]
            if line.startswith('- '):
                return line[2:]
            return line
        new_lines = [strip_marker(line) for line in lines]
    else:
        # add bullet marker to all lines (including empty lines -> '• ')
        new_lines = [marker + line for line in lines]

    new_block = '\n'.join(new_lines)

    new_text = text[:s_line_start] + new_block + text[e_line_end:]

    # Compute new start/end offsets
    # If we added bullets, start increases by len(marker) for the first line; end increases by len(marker) * number_of_lines
    if all_bulleted:
        # Removing bullets shortens length by 2 * count
        delta = 0
        for line in lines:
            if line.startswith(marker):
                delta += len(marker)
            elif line.startswith('- '):
                delta += 2
        new_start = max(s_line_start, start - (len(marker) if start > s_line_start else 0))
        new_end = end - delta
    else:
        delta = sum((len(marker)) for _ in lines)
        new_start = start + (len(marker) if start >= s_line_start else 0)
        new_end = end + delta

    return new_text, new_start, new_end


# Lightweight parser for inline markup -> used by UI to apply visual formatting
def parse_inline_markers(text: str):
    """Return a list of markers found in text as tuples (tag, start_idx, end_idx) where start/end
    are absolute character offsets. Tags: 'bold','italic','underline','strike'
    This is a simple approach — it intentionally doesn't support nesting resolution beyond simple matching.
    """
    markers = []
    # Bold: **text**
    for m in re.finditer(r"\*\*(.+?)\*\*", text, flags=re.DOTALL):
        markers.append(('bold', m.start(), m.end()))
    # Italic: *text* (avoid matching ** which is bold)
    for m in re.finditer(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)(?<!\*)\*(?!\*)", text, flags=re.DOTALL):
        markers.append(('italic', m.start(), m.end()))
    # Underline: <u>text</u>
    for m in re.finditer(r"<u>(.+?)</u>", text, flags=re.DOTALL):
        markers.append(('underline', m.start(), m.end()))
    # Strikethrough: ~~text~~
    for m in re.finditer(r"~~(.+?)~~", text, flags=re.DOTALL):
        markers.append(('strike', m.start(), m.end()))

    return markers


def inline_markers_to_spans(text: str):
    """Parse inline markers and return two things:
    - plain text with markers removed (the visible content)
    - a list of span dicts:{"tag": 'bold'|'italic'|'underline'|'strike', "start":int, "end":int}

    This is used for migration from inline-markup storage to background span storage.
    """
    spans = []
    # We'll progressively replace markers with their inner text and map offsets.
    # Approach: iterate through matched markers from left-to-right and build plain_text while tracking offsets.
    # Patterns and corresponding tags
    patterns = [
        (r"\*\*(.+?)\*\*", 'bold'),
        (r"~~(.+?)~~", 'strike'),
        (r"<u>(.+?)</u>", 'underline'),
        (r"(?<!\*)\*(?!\*)(.+?)(?<!\*)(?<!\*)\*(?!\*)", 'italic'),
    ]

    # We'll do repeated scans; for simplicity use a generic method: find matches, replace marker tokens with inner text,
    # and record spans using their absolute offsets in the resulting plain text.
    plain = text
    offset_delta = 0
    # To avoid overlapping detection issues, handle tags in a single-pass by scanning for any of the marker sets
    # create combined regex with groups
    combined = re.compile(r"\*\*(.+?)\*\*|~~(.+?)~~|<u>(.+?)</u>|(?<!\*)\*(?!\*)(.+?)(?<!\*)(?<!\*)\*(?!\*)", flags=re.DOTALL)

    out = []
    last_end = 0
    plain_builder = []
    for m in combined.finditer(text):
        # Append text between last_end and m.start()
        plain_builder.append(text[last_end:m.start()])
        inner = m.group(1) or m.group(2) or m.group(3) or m.group(4) or ''
        tag = None
        if m.group(1):
            tag = 'bold'
        elif m.group(2):
            tag = 'strike'
        elif m.group(3):
            tag = 'underline'
        elif m.group(4):
            tag = 'italic'

        start_offset = sum(len(p) for p in plain_builder)
        plain_builder.append(inner)
        end_offset = start_offset + len(inner)
        if tag and inner:
            spans.append({'tag': tag, 'start': start_offset, 'end': end_offset})
        last_end = m.end()

    # Append remaining tail
    plain_builder.append(text[last_end:])
    plain_text = ''.join(plain_builder)
    return plain_text, spans


def compact_spans(spans):
    """Return spans normalized (merged if necessary) and sorted by start."""
    # naive: sort and merge same-tag overlapping spans
    out = []
    spans_sorted = sorted(spans, key=lambda s: (s['tag'], s['start']))
    for s in spans_sorted:
        if not out:
            out.append(s.copy())
            continue
        last = out[-1]
        if last['tag'] == s['tag'] and s['start'] <= last['end']:
            # merge
            last['end'] = max(last['end'], s['end'])
        else:
            out.append(s.copy())
    return out


def add_span(spans, tag, start, end):
    """Add a formatting span and return updated spans (merged/sorted)."""
    spans.append({'tag': tag, 'start': start, 'end': end})
    return compact_spans(spans)


def remove_span(spans, tag, start, end):
    """Remove the tag spans that intersect [start,end]. For simplicity fully remove spans that have overlap.
    Returns new spans list.
    """
    out = []
    for s in spans:
        if s['tag'] != tag:
            out.append(s)
            continue
        # if overlap, skip (i.e., remove). If s fully contains region we could split; to keep it simple, remove whole s if overlap.
        if s['end'] <= start or s['start'] >= end:
            out.append(s)
        else:
            # removed
            continue
    return out


def toggle_span(spans, tag, start, end):
    # if any existing spans overlap -> remove them; else add
    overlaps = [s for s in spans if s['tag'] == tag and not (s['end'] <= start or s['start'] >= end)]
    if overlaps:
        return remove_span(spans, tag, start, end)
    return add_span(spans, tag, start, end)
