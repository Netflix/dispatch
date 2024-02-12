# Representation of document in the Google Docs API.
# See https://developers.google.com/docs/api/samples/output-json.


def test_find_links():
    """Tests the find_links function returns the expected urls."""
    from dispatch.plugins.dispatch_google.docs.plugin import find_links
    from dispatch.plugins.dispatch_test.document import TestDocumentResource

    links = list(find_links(TestDocumentResource().get("body").get("content"), "link"))
    # We have one link in the document.
    assert len(links) == 1
    # The url field is nested 8 levels deep.
    assert len(links[0]) == 8
    assert links[0][0]["url"] == "https://www.netflix.com"


def test_no_find_links():
    """Tests the find_links function returns an empty list when the document does not contain urls."""
    from dispatch.plugins.dispatch_google.docs.plugin import find_links
    from dispatch.plugins.dispatch_test.document import TestDocumentResource

    links = list(
        find_links(
            TestDocumentResource({"body": {"content": {"something": "not something"}}}),
            "link",
        )
    )

    assert not links


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
    from dispatch.plugins.dispatch_test.document import TestDocumentResource

    has_link = False
    for url, item in iter_links(TestDocumentResource().get("body").get("content")):
        assert url == "https://www.netflix.com"
        assert item.get("endIndex") == 40
        assert item.get("startIndex") == 0
        assert "textRun" in item
        assert item.get("textRun").get("content") == "Incident Conversation Commands Reference"
        has_link = True

    assert has_link


def test_no_iter_links():
    """Tests the iter_links function returns an empty list when the document does not contain urls.

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
    from dispatch.plugins.dispatch_test.document import TestDocumentResource

    links = list(
        iter_links(
            TestDocumentResource({"body": {"content": {"something": "not something"}}})
            .get("body")
            .get("content")
        )
    )

    assert not links


def test_replace_text():
    """Tests the replace_text function."""
    from dispatch.plugins.dispatch_google.docs.plugin import replace_text
    from dispatch.plugins.dispatch_test.document import TestResource

    replace_text(client=TestResource(), document_id="1234", replacements={"old": "new"})


def test_replace_weblinks():
    """Tests the replace_weblinks function."""
    from dispatch.plugins.dispatch_google.docs.plugin import replace_weblinks
    from dispatch.plugins.dispatch_test.document import TestResource

    replace_weblinks(client=TestResource(), document_id="1234", replacements={"old": "new"})
