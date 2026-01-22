from pydantic import BaseModel


## Request 
class GoogleLoginRequest(BaseModel):
    id_token: str



## Response
class GoogleLoginResponse(BaseModel):
    success: bool
    status_code: int
    status: str

class GoogleTokenResponse(BaseModel):
    success: bool
    status_code: int 
    url: str


class UserLoginResponse(BaseModel):
    success: bool
    status_code: int 
    key: str

class UserResponseError(BaseModel):
    success: bool
    status_code: int
    error_msg: str 

#######################

