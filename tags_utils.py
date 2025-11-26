import re


def _normalize_token(text: str) -> str:
    """Return a normalized token for a tag (no '#', lowercase, hyphen-joined).

    Examples:
      'Cornell Notes' -> 'cornell-notes'
      '#Main Idea & Details' -> 'main-idea-details'
    """
    if not text:
        return ""
    # Remove any non-alphanumeric characters except spaces, lowercase
    cleaned = re.sub(r'[^0-9a-zA-Z ]+', '', str(text)).strip().lower()
    if not cleaned:
        return ""
    parts = [p for p in cleaned.split() if p]
    return '-'.join(parts)


def sanitize_tags_from_text(text: str) -> list:
    """Turn a comma separated tags string into a sanitized list of tags.

    Returns canonical form including leading '#', no duplicates, order preserved.
    """
    if not text:
        return []
    pieces = [p.strip() for p in text.split(',')]
    out = []
    seen = set()
    for p in pieces:
        if not p:
            continue
        # Remove leading '#' for normalization
        bare = p.lstrip('#').strip()
        token = _normalize_token(bare)
        if not token:
            continue
        if token in seen:
            continue
        seen.add(token)
        out.append('#' + token)
    return out


def extract_hashtags_from_text(text: str) -> list:
    """Extract hashtag tokens from arbitrary text and return a sanitized list.

    Finds tokens that look like '#token' (alphanumeric, underscore or hyphen)
    and returns them in canonical sanitized form (leading '#', hyphen-joined, lowercase).
    Order is preserved and duplicates removed.
    """
    if not text:
        return []
    # Find candidate hashtags: '#' followed by letters/numbers/underscore/hyphen
    raw_tags = re.findall(r"#([0-9A-Za-z_-]+)", text)
    out = []
    seen = set()
    for raw in raw_tags:
        token = _normalize_token(raw)
        if not token:
            continue
        if token in seen:
            continue
        seen.add(token)
        out.append('#' + token)
    return out
