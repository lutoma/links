from litestar import Controller, get
from litestar.exceptions import NotFoundException
from asyncpg import Connection

from pydantic import BaseModel


class LinkSchema(BaseModel):
	title: str
	url: str
	domain: str
	description: str | None


class ListSchema(BaseModel):
	slug: str
	name: str
	description: str | None


class CurrentListSchema(ListSchema):
	children: list[ListSchema]
	links: list[LinkSchema]


class APIController(Controller):
	path = "/api"

	@get(cache=300)
	async def index(self, db_connection: Connection) -> CurrentListSchema:
		lists = await db_connection.fetch("""
			SELECT slug, name, description
			FROM lists
			WHERE parent_id IS NULL
			ORDER BY name
		""")
		lists = [ListSchema(**row) for row in lists]
		return CurrentListSchema(slug='', name='root', description=None, children=lists, links=[])

	@get("{slug:path}", cache=300)
	async def get_list(self, slug: str, db_connection: Connection) -> CurrentListSchema:
		meta = await db_connection.fetchrow("""
			SELECT id, slug, name, description
			FROM lists
			WHERE slug=$1
		""", slug[1:])
		if not meta:
			raise NotFoundException

		links = await db_connection.fetch("""
			SELECT title, url, domain, description
			FROM links
			WHERE list_id=$1
			ORDER BY created_at
		""", meta['id'])
		links = [LinkSchema(**row) for row in links]

		lists = await db_connection.fetch("""
			SELECT slug, name, description
			FROM lists
			WHERE parent_id=$1
			ORDER BY name
		""", meta['id'])
		lists = [ListSchema(**row) for row in lists]

		return CurrentListSchema(children=lists, links=links, **meta)
