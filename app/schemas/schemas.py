import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str
    address: str
    date_of_birth: datetime.date
    gender: str 
    country: str
    role: str

class UserIn(BaseModel):
    email: str
    full_name: str
    phone: str
    address: str
    date_of_birth: datetime.date
    gender: str
    country: str

class UserAdminIn(BaseModel):
    email: str
    full_name: str
    phone: str
    address: str
    date_of_birth: datetime.date
    gender: str  # Adjust length based on your needs
    country: str  # Optional
    role: str

class UserOut(BaseModel):
    id: str
    email: str


class requestdetails(BaseModel):
    email: str
    password: str
        
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    role: str

class changepassword(BaseModel):
    email:str
    old_password:str
    new_password:str
    confirm_new_password: str

class TokenCreate(BaseModel):
    uid:str
    access_token:str
    refresh_token:str
    status:bool
    created_date:datetime.datetime