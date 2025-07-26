from fastapi import FastAPI
from app.api.routes import (
    accounts,
    personas,
    campaigns,
    auth,
    neon_auth,
    companies,
    demo,
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Blossomer GTM API v2",
    description="""
    ## AI-Powered Go-to-Market Campaign Generator API
    
    This API provides both AI generation capabilities and comprehensive CRUD operations for managing B2B go-to-market campaigns.
    
    ### Authentication
    All CRUD endpoints require Stack Auth JWT authentication via the `Authorization: Bearer <token>` header.
    
    ### API Categories
    
    #### AI Generation Endpoints
    - **Company Analysis**: Generate company overviews and product analysis
    - **Account Generation**: Create target account profiles with firmographics
    - **Persona Generation**: Generate buyer personas with use cases and objections
    - **Campaign Generation**: Create personalized email campaigns and positioning
    
    #### CRUD Management Endpoints
    - **Companies**: Manage company records with analysis data
    - **Accounts**: Target account profiles with buying signals
    - **Personas**: Buyer personas with demographics and use cases
    - **Campaigns**: Email campaigns with segments and alternatives
    
    ### Row-Level Security
    All CRUD operations are user-scoped - users can only access their own data.
    
    ### Data Hierarchy
    ```
    User
    └── Company
        └── Account
            └── Persona
                └── Campaign
    ```
    
    ### Testing
    1. Start the server: `poetry run python -m uvicorn backend.app.api.main:app --reload`
    2. Import OpenAPI spec into Postman: `http://localhost:8000/openapi.json`
    3. Use interactive docs: `http://localhost:8000/docs`
    """,
    version="2.0.0",
    contact={
        "name": "Blossomer GTM API Support",
        "email": "support@blossomer.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.blossomer.com", "description": "Production server"},
    ],
)

# CORS middleware for frontend-backend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",  # Vite dev server (update to match your frontend port)
        "https://blossomer-gtm-app.onrender.com",  # Domain of production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API endpoints
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(accounts.router, prefix="/api", tags=["Accounts"])
app.include_router(personas.router, prefix="/api", tags=["Personas"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(neon_auth.router, prefix="/api/neon-auth", tags=["Neon Auth"])

# Register demo endpoints
app.include_router(demo.router, prefix="/demo", tags=["Demo"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
