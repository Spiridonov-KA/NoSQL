from pydantic import BaseModel, EmailStr


class ClientSchema(BaseModel):
    id: str
    name: str
    email: EmailStr


class UpdateClientSchema(BaseModel):  # class contains changeable fields for ClientSchema
    name: str
    email: EmailStr
