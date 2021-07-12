# test_my_application.py
def test_example_is_working(server, page):
    page.goto("http://127.0.0.1:9999/api/v1/docs")
    assert page.inner_text("h1") == "Example Domain"
    page.click("text=More information")
