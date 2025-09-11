from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.narrative.api import router as narrative_router

def create_app() -> FastAPI:
    app = FastAPI(title="StoryMaker Narrative", version="1.6.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok", "data": {"ok": True}}

    @app.get("/health/ready")
    def ready():
        from services.narrative.providers.groq_client import GroqError, get_config
        meta = {"checks": {}}
        try:
            cfg = get_config()
            meta["checks"]["groq_env"] = {"ok": True, "model": cfg.model}
            return {"status": "ok", "data": {"ready": True}, "meta": meta}
        except GroqError as e:
            meta["checks"]["groq_env"] = {"ok": False, "error": str(e)}
            return {"status": "error", "error": "groq_misconfig", "meta": meta}

    app.include_router(narrative_router)
    return app

app = create_app()
