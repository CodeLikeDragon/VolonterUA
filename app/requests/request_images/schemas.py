from uuid import UUID
from pydantic import ConfigDict, BaseModel


class RequestImageCreate(BaseModel):
    request_id: UUID


class RequestImageOut(BaseModel):
    id: UUID
    request_id: UUID
    public_id: str
    image_url: str

    model_config = ConfigDict(from_attributes=True)
