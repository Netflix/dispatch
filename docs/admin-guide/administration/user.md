## User

Users represent users of the Dispatch UI and are different from individual contacts or incident participants. These user accounts are used to control access to the Dispatch UI only. We do not currently support the creation or removal of users via the Dispatch UI, except in the case of self-registration.

![](../../.gitbook/assets/admin-ui-incident-users.png)

**Role:** Dispatch uses role-based access control (RBAC) for its UI. Currently, this is only used to protect sensitive incidents whose visibilty is set to restricted. We do not currently have any controls surrounding Dispatch configuration and settings.

There are three roles defined by Dispatch:

- Admin: Allows full access to the Dispatch UI and all incidents, whether their visibility is open or restricted.
- Poweruser: Currently the same as Admin.
- User: Can access everything except restricted incidents unless they are a direct participant.
