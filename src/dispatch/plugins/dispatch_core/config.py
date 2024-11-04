import logging

from pydantic import Field
from starlette.config import Config

from dispatch.config import BaseConfigurationModel

log = logging.getLogger(__name__)

config = Config(".env")


class DispatchTicketConfiguration(BaseConfigurationModel):
    """Dispatch ticket configuration"""

    use_incident_name: bool = Field(
        True,
        title="Use Incident Name",
        description="Use the incident name as the ticket title.",
    )
