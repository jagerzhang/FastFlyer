from os import getenv
from secrets import compare_digest
from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def authorize(credentials: HTTPBasicCredentials = Depends(security)):
    """支持SwaggerUI开启BasicAuth鉴权"""
    is_user_ok = compare_digest(credentials.username, getenv("flyer_auth_user"))
    is_pass_ok = compare_digest(credentials.password, getenv("flyer_auth_pass"))
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password.",
            headers={"WWW-Authenticate": "Basic"},
        )
