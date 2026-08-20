import markdown
import nh3

ALLOWED_TAGS = {
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
}
ALLOWED_ATTRS = {"a": {"href", "title"}}


def safe_markdownify(content):
    html = markdown.markdown(content, extensions=["fenced_code"])
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer nofollow",
    )
