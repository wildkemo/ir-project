from typing import Any, Dict, Optional
from pydantic import BaseModel


class ProjectExplainRequest(BaseModel):
    repo: Dict[str, Any]
    profile: Optional[Dict[str, Any]] = None
    query: Optional[str] = None
