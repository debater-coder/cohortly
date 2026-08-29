import markdown
import nh3

MARKDOWN_HELP_TEXT = """Format your text using <a href="https://www.markdownguide.org/cheat-sheet/">Markdown Syntax</a> to easily add bolding, italics, lists, and links."""

ALLOWED_TAGS = {
    "img",
    "p",
    "br",
    "strong",
    "em",
    "a",
    "ul",
    "ol",
    "li",
    "code",
    "pre",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h4",
    "h6",
    "table",
    "tbody",
    "tfoot",
    "td",
    "th",
    "thead",
    "tr",
}
ALLOWED_ATTRS = {"a": {"href", "title"}, "img": {"src", "alt"}}


def safe_markdownify(content):
    html = markdown.markdown(content, extensions=["fenced_code"])
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer nofollow",
    )
