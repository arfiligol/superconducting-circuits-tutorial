from dataclasses import dataclass
from typing import Literal

AuditOutcome = Literal["accepted", "rejected", "completed", "failed"]


@dataclass(frozen=True)
class AuditRecord:
    audit_id: str
    occurred_at: str
    actor_user_id: str
    session_id: str
    workspace_id: str
    action_kind: str
    resource_kind: str
    resource_id: str
    outcome: AuditOutcome
    payload: dict[str, object]
