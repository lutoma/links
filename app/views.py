from litestar import Controller, get
from litestar.response import Template
from litestar.exceptions import NotFoundException
from asyncpg import Connection


class ViewsController(Controller):
	path = "/"

	@get(cache=300)
	async def index(self, db_connection: Connection) -> Template:
		lists = await db_connection.fetch("""
			SELECT slug, name, description
			FROM lists
			WHERE parent_id IS NULL
			ORDER BY name
		""")
		return Template(template_name="index.html", context={"lists": lists})


	@get("{slug:path}", cache=300)
	async def get_list(self, slug: str, db_connection: Connection) -> Template:
		meta = await db_connection.fetchrow("""
			SELECT id, name, description, updated_at
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

		lists = await db_connection.fetch("""
			SELECT slug, name, description
			FROM lists
			WHERE parent_id=$1
			ORDER BY name
		""", meta['id'])

		slug_parts = slug.split('/')
		breadcrumbs = []
		for i in range(1, len(slug_parts)):
			breadcrumbs.append(['/'.join(slug_parts[1:i+1]), slug_parts[i]])

		return Template(template_name="list.html", context={
			"meta": meta,
			"links": links,
			"lists": lists,
			"breadcrumbs": breadcrumbs,
		})
