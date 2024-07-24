def test_render_message_template():
    """Tests the render_message_template function.

    The message template should be filled with the kwargs values, and the datetime field should be properly formatted.
    """
    from dispatch.messaging.email.utils import render_message_template
    from datetime import datetime, UTC

    message_template = [
        {
            "title": "{{title}}",
            "text": "{{body}}",
            "datetime": "{{datetime | datetime}}",
        }
    ]
    kwargs = {
        "title": "Test Title",
        "body": "Test Body",
        "datetime": datetime.now(UTC).isoformat(),
    }

    rendered = render_message_template(message_template, **kwargs)

    assert rendered
    assert rendered[0].get("title") == kwargs.get("title")
    assert rendered[0].get("text") == kwargs.get("body")
    assert rendered[0].get("datetime")


def test_render_message_template__failed_filter():
    """Tests that render_message_template fails when the input does not adhere to the datetime filter rules."""
    from dispatch.messaging.email.utils import render_message_template

    message_template = [
        {
            "datetime": "{{datetime | datetime}}",
        }
    ]
    kwargs = {"datetime": "1234"}

    rendered = render_message_template(message_template, **kwargs)

    assert rendered
    assert not rendered[0].get("datetime")


def test_render_message_template__disable_code_execution():
    """Tests that render_message_template does not execute scripts in user input."""
    from dispatch.messaging.email.utils import render_message_template

    message_template = [
        {
            "title": "{{ title }}",
            "body": "{% for i in [].append(123) %}...{% endfor %}",
        }
    ]
    kwargs = {"title": "Test Title"}

    rendered = render_message_template(message_template, **kwargs)

    assert rendered
    assert rendered[0].get("title") == kwargs.get("title")
    assert rendered[0].get("body") == message_template[0].get("body")


def test_generate_welcome_message__default():
    """Tests the generate_welcome_message function."""
    from dispatch.messaging.strings import generate_welcome_message

    assert generate_welcome_message(None)


def test_generate_welcome_message__email_template(email_template):
    """Tests the generate_welcome_message function with an email template."""
    from dispatch.messaging.strings import generate_welcome_message

    welcome_message = generate_welcome_message(email_template)

    assert welcome_message
    assert welcome_message[0].get("title") == email_template.welcome_text
    assert welcome_message[0].get("text") == email_template.welcome_body
