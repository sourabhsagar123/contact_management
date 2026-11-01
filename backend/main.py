"""
FastAPI Backend Application Entry Point
======================================
Serves REST API endpoints for contacts and mounts the interactive frontend web UI.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from sample_data import seed_sample_data_if_empty
from contact_service import contact_service
from models import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    RelationshipCreate,
    ConnectionPathQuery
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database, seed sample data if empty, and populate ADSA memory structures
    init_db()
    seed_sample_data_if_empty()
    contact_service.initialize()
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title="ADSA Contact Management System",
    description="A complete Contact Management System demonstrating Trie, AVL Tree, Hash Table, Max-Heap, and Graph algorithms.",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Core Contact Endpoints ====================

@app.get("/api/contacts", summary="Get all contacts with filtering & ADSA sorting")
def get_contacts(
    category: str = Query("All", description="Category filter (All, Work, College, Friends, Family, Emergency)"),
    sort_by: str = Query("alphabetical", description="Sorting criterion: 'alphabetical' (AVL Tree), 'frequent' (Max-Heap), 'created_at'"),
    reverse: bool = Query(False, description="Reverse sort order"),
    search: str = Query(None, description="Search keyword for name/phone/email")
):
    return contact_service.get_contacts(category=category, sort_by=sort_by, reverse=reverse, search=search)


@app.get("/api/contacts/{contact_id}", summary="Get single contact by ID (Hash Table O(1))")
def get_contact(contact_id: int):
    contact = contact_service.get_contact_by_id(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact.to_dict()


@app.post("/api/contacts", status_code=status.HTTP_201_CREATED, summary="Create new contact")
def create_contact(payload: ContactCreate):
    try:
        new_contact = contact_service.create_contact(payload.model_dump())
        return new_contact.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/contacts/{contact_id}", summary="Update existing contact")
def update_contact(contact_id: int, payload: ContactUpdate):
    try:
        updated = contact_service.update_contact(contact_id, payload.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Contact not found")
        return updated.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/contacts/{contact_id}", summary="Delete contact")
def delete_contact(contact_id: int):
    success = contact_service.delete_contact(contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": f"Contact #{contact_id} successfully deleted from database and ADSA structures"}


@app.post("/api/contacts/{contact_id}/call", summary="Increment call/interaction count (Max-Heap update)")
def record_call(contact_id: int):
    updated = contact_service.record_interaction(contact_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {
        "message": "Call interaction recorded",
        "new_call_count": updated.call_count,
        "contact": updated.to_dict()
    }


# ==================== ADSA Algorithmic Endpoints ====================

@app.get("/api/autocomplete", summary="Trie-based prefix search (O(L + M))")
def autocomplete(q: str = Query(..., min_length=1, description="Prefix to autocomplete")):
    return contact_service.autocomplete(prefix=q, max_results=10)


@app.get("/api/fuzzy", summary="Fuzzy typo-tolerant search (Levenshtein Distance)")
def fuzzy_search_api(
    q: str = Query(..., min_length=1, description="Search term with possible typos"),
    max_distance: int = Query(2, ge=1, le=5, description="Maximum edit distance threshold")
):
    return contact_service.fuzzy_search_contacts(query=q, max_distance=max_distance)


@app.get("/api/frequent", summary="Top frequent contacts (Max-Heap O(K log N))")
def get_frequent(limit: int = Query(5, ge=1, le=50)):
    return contact_service.get_frequent_contacts(limit=limit)


@app.get("/api/graph", summary="Full relationship network data for Graph visualization")
def get_graph():
    return contact_service.get_graph_network()


@app.post("/api/relationships", summary="Add relationship edge in Graph")
def add_relationship(payload: RelationshipCreate):
    try:
        contact_service.add_relationship(payload.from_id, payload.to_id, payload.relationship)
        return {"message": "Relationship created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/relationships/path", summary="BFS shortest path between two contacts (Degrees of Separation)")
def find_connection_path(
    from_id: int = Query(..., description="Starting contact ID"),
    to_id: int = Query(..., description="Target contact ID")
):
    path = contact_service.find_connection_path(from_id, to_id)
    if path is None:
        return {"connected": False, "degrees": -1, "path": []}
    return {
        "connected": True,
        "degrees": len(path) - 1,
        "path": path
    }


@app.get("/api/avl/structure", summary="Hierarchical AVL tree structure for visualization")
def get_avl_structure():
    tree = contact_service.get_avl_tree_structure()
    return {
        "tree": tree,
        "height": contact_service.avl.get_tree_height(),
        "total_nodes": contact_service.avl.total_nodes,
        "rotations": contact_service.avl.rotations
    }


@app.get("/api/adsa/benchmark", summary="Side-by-side performance benchmark (Trie vs Linear Scan vs Hash Table)")
def get_benchmark(q: str = Query("a", description="Query string to benchmark")):
    return contact_service.get_adsa_benchmark(query=q)


@app.get("/api/adsa/stats", summary="Comprehensive ADSA memory and complexity metrics")
def get_adsa_stats():
    return contact_service.get_adsa_stats()


@app.post("/api/reset-sample-data", summary="Reset and re-seed sample contacts for testing/demo")
def reset_sample_data():
    from database import get_db_connection
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM contact_relationships")
    c.execute("DELETE FROM contacts")
    conn.commit()
    conn.close()

    from sample_data import seed_sample_data_if_empty
    seed_sample_data_if_empty()
    contact_service.initialize()
    return {"message": "Sample dataset re-seeded successfully", "total_contacts": len(contact_service.id_hash_table.values())}



# ==================== Frontend Static Serving ====================

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "ADSA Contact Management System Backend Active. Frontend files pending."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
