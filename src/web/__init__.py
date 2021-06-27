from starlette.applications import Starlette
from starlette.responses import Response
from starlette.requests import Request

app = Starlette()


@app.route("/")
async def index(request: Request):
    return Response("Hello, World!")
