# test_my_application.py
def test_example_is_working(server, page):
    page.goto("http://localhost:8000")
    assert page.inner_text("h1") == "Example Domain"
    page.click("text=More information")
