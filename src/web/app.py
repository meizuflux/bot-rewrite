from starlette.applications import Starlette
from starlette.responses import Response, RedirectResponse
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from web import ipc

templates = Jinja2Templates(directory="web/templates")
client = ipc.Client()


async def start():
    await client.initiate()


async def stop():
    await client.close()


async def index(request: Request) -> Response:
    return templates.TemplateResponse("index.html", context={"request": request, "name": "who knows?"})


async def favicon(request: Request):
    return RedirectResponse(url="/static/favicon.ico")


async def test(r):
    e = await client.request("test", text="test")
    return Response(e)


routes = [
    Route("/", endpoint=index),
    Route("/favicon.ico", endpoint=favicon),
    Route("/stats", endpoint=test),
    Mount("/static", StaticFiles(directory="web/static")),
]

app = Starlette(debug=True, routes=routes, on_startup=[start], on_shutdown=[stop])
