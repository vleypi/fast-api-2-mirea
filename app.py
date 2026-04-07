from fastapi import FastAPI
from routers import users, products, auth, headers

app = FastAPI(title="Контрольная 2")

app.include_router(users.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(headers.router)
