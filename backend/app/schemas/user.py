from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # replaces class Config

    id: str
    email: EmailStr
    role: str    

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"