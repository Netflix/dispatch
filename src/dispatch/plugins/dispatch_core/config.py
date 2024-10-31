import logging
from dispatch.config import BaseConfigurationModel

from starlette.config import Config
from pydantic import Field

log = logging.getLogger(__name__)


config = Config(".env")


class DispatchTicketConfiguration(BaseConfigurationModel):
    """Dispatch ticket configuration"""

    use_incident_name: bool = Field(
        True,
        title="Use Incident Name",
        description="Use the incident name as the ticket title.",
    )
