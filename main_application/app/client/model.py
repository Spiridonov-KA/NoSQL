from pydantic import BaseModel, EmailStr


class ClientSchema(BaseModel):
    id: str
    name: str
    email: EmailStr


class UpdateClientSchema(BaseModel):
    name: str
    email: EmailStr
