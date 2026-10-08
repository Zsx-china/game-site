from seoscout.core.web import html_to_text, robots_allows


def test_html_to_text_omits_non_visible_content():
    html = "<html><head><style>body { color: red }</style></head><body><h1>Guide</h1><p>Useful text.</p><script>ignored()</script></body></html>"

    assert html_to_text(html) == "Guide\nUseful text."


def test_robots_rules_are_checked_per_url_and_agent():
    robots = """User-agent: seoscout
Disallow: /private/

User-agent: *
Disallow: /blocked/
"""

    assert not robots_allows(robots, "seoscout/0.1", "https://example.com/private/post")
    assert robots_allows(robots, "seoscout/0.1", "https://example.com/blocked/post")
