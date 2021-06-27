from pathlib import Path

from starlette.applications import Starlette
from starlette.responses import Response, RedirectResponse
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

current_dir = Path(__file__).parent
app = Starlette()
app.mount("/static", StaticFiles(directory=str(current_dir / "static")), name="static")


@app.route("/")
async def index(request: Request):
    return Response("Hello, World!")


@app.route("/favicon.ico")
async def favicon(request: Request):
    return RedirectResponse(url="/static/favicon.ico")
