from starlette.applications import Starlette
from starlette.responses import Response
from starlette.requests import Request

app = Starlette()

@app.route("/")
async def index(request: Request):
    return Response("Hello, World!")

@app.route("/numbers", methods=["GET"])
async def numbers(request: Request):
    print(request.query_params)
    return Response()