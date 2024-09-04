from fastapi import APIRouter as FastAPIRouter
# from fastapi.routing import APIRoute
from .middleware import MiddleWare


class APIRouter(FastAPIRouter):

    def __init__(self, *args, **kwargs):
        super().__init__(route_class=MiddleWare, *args, **kwargs)
