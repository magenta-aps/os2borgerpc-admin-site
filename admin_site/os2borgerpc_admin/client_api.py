from ninja import NinjaAPI

from system.client_api  import router as client_router

api = NinjaAPI(urls_namespace="client-api", docs_url="")
# api = NinjaAPI(urls_namespace="client-api")

api.add_router("/", client_router)
