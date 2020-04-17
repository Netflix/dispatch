from dispatch.plugins.bases import TicketPlugin


class TestTicketPlugin(TicketPlugin):
    title = "Dispatch Test Plugin - Ticket"
    slug = "test-ticket"

    def create(self, ticket_id, **kwargs):
        return

    def update(self, ticket_id, **kwargs):
        return
