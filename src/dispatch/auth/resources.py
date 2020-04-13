from fastapi_permissions import Allow, Deny, Authenticated, Everyone


class StaticAclResource:
    __acl__ = [(Allow, Everyone, "view"), (Allow, "role:user", "share")]


class DynamicAclResource:
    def __acl__(self):
        return [
            (Allow, "role:user", "share"),
            (Allow, "role:admin", "share"),
            (Allow, f"user:{self.owner}", "edit"),
        ]


# in contrast to pyramid, resources might be access conroll list themselves
# this can save some typing:

AclResourceAsList = [(Allow, Everyone, "view"), (Deny, "role:troll", "edit")]
