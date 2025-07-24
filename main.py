from app.main import app

if __name__ == "__main__":
    import os
    import uvicorn

    # Odczytaj port z zmiennej środowiskowej
    APP_PORT = int(os.getenv("APP_CONTAINER_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)
