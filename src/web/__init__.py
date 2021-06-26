from starlette.applications import Starlette
from starlette.responses import Response

app = Starlette()

@app.route("/")
async def index(request):
    return Response("Hello, World!")

