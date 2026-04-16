from pydantic import ConfigDict, BaseModel
from uuid import UUID


class ChatParticipantOut(BaseModel):
    user_id: UUID
    role: str

    model_config = ConfigDict(from_attributes=True)
