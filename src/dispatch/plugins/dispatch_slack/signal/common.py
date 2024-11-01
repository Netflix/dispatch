from blockkit import Context, Divider, MarkdownText, Modal, Section
from slack_bolt import Ack


def ack_mfa_required_submission_event(
    ack: Ack, mfa_enabled: bool, challenge_url: str | None = None
) -> None:
    """Handles the add engagement submission event acknowledgement."""

    if mfa_enabled:
        mfa_text = (
            "🔐 To complete this action, you need to verify your identity through Multi-Factor Authentication (MFA).\n\n"
            f"Please <{challenge_url}|click here> to open the MFA verification page."
        )
    else:
        mfa_text = "✅ No additional verification required. You can proceed with the confirmation."

    blocks = [
        Section(text=mfa_text),
        Divider(),
        Context(
            elements=[
                MarkdownText(
                    text="💡 This step protects against unauthorized confirmation if your account is compromised."
                )
            ]
        ),
    ]

    modal = Modal(
        title="Confirm Your Identity",
        close="Cancel",
        blocks=blocks,
    ).build()

    ack(response_action="update", view=modal)
