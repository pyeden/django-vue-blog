"""Markdown rendering helpers: HTML + TOC with a bleach allowlist."""
import re

import bleach
import markdown

ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr", "blockquote",
    "strong", "b", "em", "i", "del", "s", "sup", "sub",
    "ul", "ol", "li",
    "a", "img",
    "pre", "code", "span", "div",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td",
]
ALLOWED_ATTRIBUTES = {
    "*": ["class", "id"],
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "th": ["align", "colspan", "rowspan"],
    "td": ["align", "colspan", "rowspan"],
    "code": ["class"],
    "pre": ["class"],
    "span": ["class"],
    "div": ["class"],
}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

MD_EXTENSIONS = ["fenced_code", "codehilite", "toc", "tables"]
MD_EXTENSION_CONFIGS = {
    "codehilite": {"css_class": "codehilite", "guess_lang": False, "linenums": False},
    "toc": {"permalink": False, "toc_depth": "1-6"},
}


def render_markdown(text: str) -> str:
    """Render markdown to sanitized HTML."""
    if not text:
        return ""
    html = markdown.markdown(
        text, extensions=MD_EXTENSIONS, extension_configs=MD_EXTENSION_CONFIGS
    )
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def extract_toc(text: str) -> list[dict]:
    """Return a flat [{level, text, anchor}] TOC in document order."""
    if not text:
        return []
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS, extension_configs=MD_EXTENSION_CONFIGS
    )
    md.convert(text)
    toc: list[dict] = []

    def walk(tokens):
        for token in tokens:
            toc.append(
                {
                    "level": token.get("level", 1),
                    "text": token.get("name", ""),
                    "anchor": token.get("id", ""),
                }
            )
            walk(token.get("children", []))

    walk(getattr(md, "toc_tokens", []))
    return toc


def make_excerpt(text: str, length: int = 120) -> str:
    """Build a short plain-text excerpt from markdown source."""
    if not text:
        return ""
    # Drop fenced code blocks entirely.
    plain = re.sub(r"```.*?```", " ", text, flags=re.S)
    plain = re.sub(r"`([^`]*)`", r"\1", plain)
    plain = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", plain)
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", plain)
    plain = re.sub(r"^#{1,6}\s*", "", plain, flags=re.M)
    plain = re.sub(r"^\s*>\s?", "", plain, flags=re.M)
    plain = re.sub(r"[*_~#>-]+", " ", plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    if len(plain) <= length:
        return plain
    return plain[:length].rstrip() + "…"
