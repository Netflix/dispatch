from dispatch.enums import DispatchEnum


class GroupType(DispatchEnum):
    tactical = "tactical"
    notifications = "notifications"


class GroupAction(DispatchEnum):
    add_member = "add_member"
    remove_member = "remove_member"
