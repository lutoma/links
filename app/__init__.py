from pathlib import Path
from os import environ

from litestar import Litestar, MediaType, Request, Response
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import HTTPException
from litestar.template.config import TemplateConfig
from litestar_asyncpg import AsyncpgConfig, AsyncpgPlugin, PoolConfig
from litestar.static_files import create_static_files_router
from litestar.datastructures import CacheControlHeader

from .views import ViewsController
from .api import APIController


def plain_text_exception_handler(_: Request, exc: Exception) -> Response:
	return Response(
		media_type=MediaType.TEXT,
		content=getattr(exc, "detail", ""),
		status_code=getattr(exc, "status_code", 500),
	)


asyncpg = AsyncpgPlugin(config=AsyncpgConfig(
	pool_config=PoolConfig(dsn=environ["LINKS_DB"])))

static_router = create_static_files_router(
	path="/static",
	directories=["static"],
	cache_control=CacheControlHeader(public=True, max_age=3600),
)

app = Litestar(
	plugins=[asyncpg],
	route_handlers=[
		ViewsController,
		APIController,
		static_router,
	],
	exception_handlers={HTTPException: plain_text_exception_handler},
	template_config=TemplateConfig(
		directory=Path("templates"),
		engine=JinjaTemplateEngine,
	),
)
