from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from textblob import TextBlob
from deep_translator import GoogleTranslator
from sqlalchemy.orm import Session

# Importamos los componentes de la base de datos
import models
from database import SessionLocal, engine

# Creamos las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Configuración de CORS ---
origins = ["http://localhost", "http://127.0.0.1", "null"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model ---
class TextInput(BaseModel):
    text: str

# --- Paletas de Colores ---
PALETTES = {
    "positive": ["#FFD700", "#FF6347", "#ADFF2F", "#00BFFF", "#FF69B4"],
    "neutral":  ["#B0C4DE", "#778899", "#A9A9A9", "#DCDCDC", "#F5F5F5"],
    "negative": ["#191970", "#4B0082", "#2F4F4F", "#800000", "#556B2F"]
}

# --- Dependencia para la sesión de la base de datos ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoint de Análisis ---
@app.post("/analyze")
def analyze_text(request: TextInput, db: Session = Depends(get_db)):
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(request.text)
    except Exception as e:
        print(f"Error en la traducción: {e}")
        translated_text = request.text
    
    blob = TextBlob(translated_text)
    polarity = blob.sentiment.polarity

    if polarity > 0.2:
        selected_palette = PALETTES["positive"]
    elif polarity < -0.2:
        selected_palette = PALETTES["negative"]
    else:
        selected_palette = PALETTES["neutral"]
    
    # Guardamos el resultado en la base de datos
    db_palette = models.Palette(
        input_text=request.text,
        translated_text=translated_text,
        polarity=f"{polarity:.2f}",
        colors=",".join(selected_palette)
    )
    db.add(db_palette)
    db.commit()
    db.refresh(db_palette)

    return {"colors": selected_palette}

# --- Endpoint para obtener la galería de paletas ---
@app.get("/gallery")
def get_gallery(db: Session = Depends(get_db)):
    palettes = db.query(models.Palette).order_by(models.Palette.created_at.desc()).all()
    return palettes