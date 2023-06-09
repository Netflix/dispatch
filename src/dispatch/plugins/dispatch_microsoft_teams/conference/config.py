from pydantic import Field, SecretStr

from dispatch.config import BaseConfigurationModel


class MicrosoftTeamsConfiguration(BaseConfigurationModel):
    """MS teams configuration details."""

    authority: str = Field(
        title="MS team Authority URL",
        description="Following format https://login.microsoftonline.com/Enter_the_Tenant_Id_Here.",
    )
    client_id: str = Field(
        title="client id",
        description="It is the Application (client) ID for the application you registered.",
    )
    secret: SecretStr = Field(
        title="Azure Client Secret", description="This is the client secret created via Azure AD."
    )
    allow_auto_recording: bool = Field(
        False,
        title="Allow Auto Recording",
        description="Enable if you would like to record the meetings by default.",
    )
    user_id: str = Field(
        title="User id",
        description="It is the User ID for which the application will create meeting on behalf.",
    )
