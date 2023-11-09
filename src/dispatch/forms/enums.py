from dispatch.enums import DispatchEnum


class FormStatus(DispatchEnum):
    new = "New"
    draft = "Draft"
    complete = "Complete"


class FormAttorneyStatus(DispatchEnum):
    not_reviewed = "Not reviewed"
    reviewed_no_action = "Reviewed: no action required"
    reviewed_action_required = "Reviewed: follow up required"
