from ninja import NinjaAPI

from system.client_api import router as client_router

# Initialize the API used for client communication. This API requires no authentication,
# the same way the xmlrpc-communication requires no authentication, because the
# functions (endpoints) themselves verify that they are being called by a registered computer.
# We overwrite docs_url because we do not want Django Ninja to generate a docs page for this API.
api = NinjaAPI(urls_namespace="client-api", docs_url="")

api.add_router("/", client_router)
