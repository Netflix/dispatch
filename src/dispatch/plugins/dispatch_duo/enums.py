from dispatch.enums import DispatchEnum


class PushResponseResult(DispatchEnum):
    allow = "allow"
    deny = "deny"
    fraud = "fraud"
    failed = "push_failed"
    timeout = "timeout"
    user_not_found = "user_not_found"
