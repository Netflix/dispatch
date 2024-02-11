# Representation of document in the Google Docs API.
# See https://developers.google.com/docs/api/samples/output-json.
_DOCUMENT = {
    "body": {
        "content": [
            {
                "startIndex": 0,
                "endIndex": 40,
                "paragraph": {
                    "elements": [
                        {
                            "endIndex": 40,
                            "startIndex": 0,
                            "textRun": {
                                "content": "Incident Conversation Commands Reference",
                                "textStyle": {
                                    "link": {"url": "https://www.netflix.com"},
                                },
                            },
                        }
                    ],
                },
            },
        ]
    }
}


def test_find_links():
    """Tests the find_links function returns the expected urls."""
    from dispatch.plugins.dispatch_google.docs.plugin import find_links

    links = list(find_links(_DOCUMENT.get("body").get("content"), "link"))
    # We have one link in the document.
    assert len(links) == 1
    # The url field is nested 8 levels deep.
    assert len(links[0]) == 8
    assert links[0][0]["url"] == "https://www.netflix.com"


def test_iter_links():
    """Tests the iter_links function returns the expected urls and elements.

    The expected value is a tuple with the url "https://www.netflix.com" and the element
    {
        "endIndex": 40,
        "startIndex": 0,
        "textRun": {
            "content": "Incident Conversation Commands Reference",
            "textStyle": {"link": {"url": "https://www.netflix.com"}},
        },
    }
    """
    from dispatch.plugins.dispatch_google.docs.plugin import iter_links

    has_link = False
    for url, item in iter_links(_DOCUMENT.get("body").get("content")):
        assert url == "https://www.netflix.com"
        assert item.get("endIndex") == 40
        assert item.get("startIndex") == 0
        assert "textRun" in item
        assert item.get("textRun").get("content") == "Incident Conversation Commands Reference"
        has_link = True

    assert has_link
