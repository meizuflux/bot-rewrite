from starlette.applications import Starlette
from starlette.responses import Response, RedirectResponse
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

templates = Jinja2Templates(directory="src/web/templates")

async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        context = {
            "request": request,
            "name": "who knows?"
        }
    )

async def favicon(request: Request):
    return RedirectResponse(url="/static/favicon.ico")

routes = [
    Route("/", endpoint=index),
    Route("/favicon.ico", endpoint=favicon),

    Mount("/static", StaticFiles(directory="src/web/static"))
]

app = Starlette(debug=True, routes=routes)
