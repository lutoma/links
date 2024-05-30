from litestar import get
from litestar.response import Template
from litestar.exceptions import NotFoundException
from asyncpg import Connection


#@get("/", cache=120)
@get("/")
async def index(db_connection: Connection) -> Template:
	lists = await db_connection.fetch("SELECT slug, name, description FROM lists WHERE parent_id IS NULL")
	return Template(template_name="index.html", context={"lists": lists})


#@get("/{slug:str}", cache=120)
@get("/{slug:path}")
async def get_list(slug: str, db_connection: Connection) -> Template:
	meta = await db_connection.fetchrow("SELECT id, name, description, updated_at FROM lists WHERE slug=$1", slug[1:])
	if not meta:
		raise NotFoundException

	links = await db_connection.fetch("SELECT title, url, domain FROM links WHERE list_id=$1", meta['id'])
	lists = await db_connection.fetch("SELECT slug, name, description FROM lists WHERE parent_id=$1", meta['id'])

	slug_parts = slug.split('/')
	breadcrumbs = []
	for i in range(1, len(slug_parts)):
		print(i)
		breadcrumbs.append(['/'.join(slug_parts[1:i+1]), slug_parts[i]])

	return Template(template_name="list.html", context={
		"list": meta,
		"links": links,
		"lists": lists,
		"breadcrumbs": breadcrumbs,
	})
