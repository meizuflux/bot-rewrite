from starlette.applications import Starlette
from starlette.responses import Response, RedirectResponse
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from web import ipc

templates = Jinja2Templates(directory="web/templates")
client = ipc.Client()

bot_name = "Walrus"


async def start():
    await client.initiate()


async def stop():
    await client.close()


async def index(request: Request) -> Response:
    stats = await client.request("stats")
    return templates.TemplateResponse(
        "index.jinja", context={"request": request, "name": bot_name, "stats": stats}
    )


async def not_found(request, exc):
    return templates.TemplateResponse("404.jinja", context={"request": request})


async def stats(request):
    return templates.TemplateResponse("stats.jinja", context={"request": request, "name": bot_name})


routes = [
    Route("/", endpoint=index),
    Route("/stats", endpoint=stats),
    Mount("/static", StaticFiles(directory="web/static")),
]

exceptions = {404: not_found}

app = Starlette(
    debug=False, routes=routes, exception_handlers=exceptions, on_startup=[start], on_shutdown=[stop]
)
