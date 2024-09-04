import secrets
from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastflyer.settings import BaseConfig as config

security = HTTPBasic()


def authorize(credentials: HTTPBasicCredentials = Depends(security)):
    """支持SwaggerUI开启BasicAuth鉴权
    """
    is_user_ok = secrets.compare_digest(credentials.username,
                                        config.env.get("flyer_auth_user"))
    is_pass_ok = secrets.compare_digest(credentials.password,
                                        config.env.get("flyer_auth_pass"))
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect user or password.",
                            headers={"WWW-Authenticate": "Basic"})
