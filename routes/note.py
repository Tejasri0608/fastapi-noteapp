from fastapi import FastAPI, Request, APIRouter, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from models.note import Note
from config.db import conn
from schemas.note import noteEntity, notesEntity
from fastapi.templating import Jinja2Templates
from bson import ObjectId

note = APIRouter()

templates = Jinja2Templates(directory="templates")

# Route to fetch and display notes
@note.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    try:
        docs = conn.notes.notes.find({})
        newDocs = []
        for doc in docs:
            newDocs.append({
                "id": str(doc["_id"]),  # Ensure ObjectId is converted to a string
                "title": doc["title"],
                "desc": doc["desc"],
                "important": doc["important"]
            })
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "newDocs": newDocs}
        )
    except Exception as e:
        print(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail="Error fetching notes")

# Route to add a new note
@note.post("/")
async def create_item(
    title: str = Form(...),
    desc: str = Form(...),
    important: str = Form(None)
):
    try:
        # Create the note dictionary
        note_data = {
            "title": title,
            "desc": desc,
            "important": True if important == "on" else False
        }

        # Insert into the database
        result = conn.notes.notes.insert_one(note_data)

        # Confirm insertion
        if result.inserted_id:
            return JSONResponse(
                status_code=201,
                content={"success": True, "message": "Note added successfully!"}
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Failed to add note."}
            )
    except Exception as e:
        print(f"Error adding note: {e}")
        raise HTTPException(status_code=500, detail="Error adding note")

# Route to delete a note
@note.delete("/{note_id}")
async def delete_item(note_id: str):
    try:
        # Attempt to delete the note
        result = conn.notes.notes.delete_one({"_id": ObjectId(note_id)})

        # Check if a document was deleted
        if result.deleted_count == 1:
            return JSONResponse(
                status_code=200,
                content={"success": True, "message": "Note deleted successfully!"}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "Note not found."}
            )
    except Exception as e:
        print(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail="Error deleting note")
