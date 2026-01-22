from pydantic import BaseModel


## Request 
class LLMRequest(BaseModel):
    prompt: str 
    session_id: str


## Response
class LLMResponse(BaseModel):
    success: bool
    text: str
    status_code: int

class LLMResponseError(BaseModel):
    success: bool
    status_code: int
    error_msg: str 

#######################

