import uvicorn
from src.web.app import app

if __name__ == "__main__":
    connect_kwargs = {
        "use_colors": False,
        "host": "localhost",
    }
    config = uvicorn.Config(app, **connect_kwargs)
    server = uvicorn.Server(config)

    server.run()
