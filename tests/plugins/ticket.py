from dispatch.plugins.bases import TicketPlugin


class TestTicketPlugin(TicketPlugin):
    title = "Test Ticket"
    slug = "test-ticket"

    def create(self, ticket_id, **kwargs):
        return

    def update(self, ticket_id, **kwargs):
        return
