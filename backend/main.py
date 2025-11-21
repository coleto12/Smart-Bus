from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from backend.database.database import engine, Base
from backend.routers import (
    usuarios, conductores, buses, rutas, quejas,
    auth, paradas, incidentes, ubicaciones
)
import os


app = FastAPI()


# ----------- INIT DATABASE -----------
@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")


# ----------- CORS -----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------- STATIC & FRONTEND ROUTES -----------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_DIR = os.path.join(BASE_DIR, "backend", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend")

print(f"📁 BASE_DIR: {BASE_DIR}")
print(f"📁 STATIC_DIR: {STATIC_DIR} exists? {os.path.exists(STATIC_DIR)}")
print(f"📁 FRONTEND_DIR: {TEMPLATES_DIR} exists? {os.path.exists(TEMPLATES_DIR)}")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ----------- ROUTERS -----------
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(conductores.router)
app.include_router(buses.router)
app.include_router(rutas.router)
app.include_router(quejas.router)
app.include_router(paradas.router)
app.include_router(incidentes.router)
app.include_router(ubicaciones.router)


# ----------- FRONTEND PAGES -----------

@app.get("/")
def root():
    return RedirectResponse(url="/auth")


@app.get("/auth")
def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/dashboard/pasajero")
def dashboard_pasajero(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard/conductor")
def dashboard_conductor(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard/admin")
def dashboard_admin(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/admin/buses")
def admin_buses(request: Request):
    return templates.TemplateResponse("admin_buses.html", {"request": request})


@app.get("/admin/conductores")
def admin_conductores(request: Request):
    return templates.TemplateResponse("admin_conductores.html", {"request": request})


@app.get("/admin/quejas")
def admin_quejas(request: Request):
    return templates.TemplateResponse("admin_quejas.html", {"request": request})


@app.get("/admin/zonas")
def admin_zonas(request: Request):
    return templates.TemplateResponse("admin_zonas.html", {"request": request})


@app.get("/admin/usuarios")
def admin_usuarios(request: Request):
    return templates.TemplateResponse("admin_usuarios.html", {"request": request})


@app.get("/admin/rutas")
def admin_rutas(request: Request):
    return templates.TemplateResponse("admin_rutas.html", {"request": request})


@app.get("/pasajero/quejas")
def pasajero_quejas_page(request: Request):
    return templates.TemplateResponse("pasajero_quejas.html", {"request": request})


@app.get("/pasajero/buses-activos")
def pasajero_buses_activos(request: Request):
    return templates.TemplateResponse("pasajero_buses_activos.html", {"request": request})


@app.get("/admin/paradas")
def admin_paradas(request: Request):
    return templates.TemplateResponse("admin_paradas.html", {"request": request})


@app.get("/pasajero/rutas")
def pasajero_rutas(request: Request):
    return templates.TemplateResponse("pasajero_rutas.html", {"request": request})


@app.get("/conductor/incidente")
def conductor_incidente(request: Request):
    return templates.TemplateResponse("conductor_incidente.html", {"request": request})


@app.get("/pasajero/incidentes")
def pasajero_incidentes(request: Request):
    return templates.TemplateResponse("pasajero_incidentes.html", {"request": request})


@app.get("/conductor/estado")
def conductor_estado(request: Request):
    return templates.TemplateResponse("conductor_estado.html", {"request": request})


@app.get("/conductor/ubicacion")
def conductor_ubicacion(request: Request):
    return templates.TemplateResponse("conductor_ubicacion.html", {"request": request})


@app.get("/pasajero/ubicacion")
def pasajero_ubicacion(request: Request):
    return templates.TemplateResponse("pasajero_ubicacion.html", {"request": request})


# ----------- RENDER PORT BINDING -----------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
