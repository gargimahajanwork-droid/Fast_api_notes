from fastapi import FastAPI 
from database import SessionLocal, engine, get_db

from schemas import UserCreate, NoteCreate, NoteResponse, UserLogin

from models import Base, User, Note

from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException

from auth import hash_password, verify_password , create_access_token, verify_token

app = FastAPI()

Base.metadata.create_all(bind = engine)

@app.post("/register")
def register_user(user : UserCreate , db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400,detail="Email already exists")

    new_user = User(name=user.name,email=user.email,password=hash_password(user.password))

    db.add(new_user)
    db.commit()

    return {"message": "User Registered Successfully"}

@app.post("/login")
def login_user(user:UserLogin, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user:
        raise HTTPException(status_code=400,detail="Invalid Credentials")

    if not verify_password(user.password,existing_user.password):
        raise HTTPException(status_code=400,detail="Invalid Credentials")

    access_token = create_access_token(data={"sub": existing_user.email})

    return {"access_token": access_token, "token_type": "bearer"}





@app.post("/notes")
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    email: str = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    new_note = Note(
        title=note.title,
        content=note.content,
        owner_id=user.id
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note

@app.get("/notes", response_model=list[NoteResponse])
def get_notes(db: Session = Depends(get_db)):

    notes = db.query(Note).all()

    return notes


@app.put("/notes/{id}")
def update_note(
    id: int,
    note: NoteCreate,
    db: Session = Depends(get_db),
    email: str = Depends(verify_token)
):

    # Get logged-in user
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Find the note
    db_note = db.query(Note).filter(Note.id == id).first()

    if db_note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    # Check ownership
    if db_note.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to update this note"
        )

    # Update note
    db_note.title = note.title
    db_note.content = note.content

    db.commit()
    db.refresh(db_note)

    return {
        "message": "Note updated successfully",
        "note": db_note
    }

@app.delete("/notes/{id}")
def delete_note(
    id: int,
    db: Session = Depends(get_db),
    email: str = Depends(verify_token)
):

    # Get logged-in user
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Find the note
    db_note = db.query(Note).filter(Note.id == id).first()

    if db_note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    # Check ownership
    if db_note.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to delete this note"
        )

    # Delete note
    db.delete(db_note)
    db.commit()

    return {
        "message": "Note deleted successfully"
    }