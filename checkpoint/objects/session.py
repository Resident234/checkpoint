from typing import *

import httpx
from checkpoint.helpers.utils import get_httpx_client
from checkpoint.helpers import auth
from checkpoint.objects.base import CheckPointCreds, SmartObj


# class Session(SmartObj):
#     def __init__(self, client: httpx.AsyncClient = None) -> None:
#         self.creds: CheckPointCreds = None
#         self.client: httpx.AsyncClient = client or get_httpx_client()

#     @staticmethod
#     async def new(client: httpx.AsyncClient = None, authentify=False) -> "Session":
#         cls = Session(client=client)

#         if authentify:
#             cls.creds = await auth.load_and_auth(client)
#         return cls