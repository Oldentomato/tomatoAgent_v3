
def user_session(ssession_id: str) -> str:
    return f"user:session:{ssession_id}"

def email_otp(email: str) -> str:
    return f"otp:email:{email}"

def rate_limit(ip: str) -> str:
    return f"rate:ip:{ip}"
