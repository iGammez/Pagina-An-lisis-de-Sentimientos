from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from textblob import TextBlob
from deep_translator import GoogleTranslator
from sqlalchemy.orm import Session
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
import numpy as np
import colorsys
from typing import Optional
import os

# Importamos los componentes de la base de datos
import models
from database import SessionLocal, engine

# Importar el generador avanzado de colores
from color_generator import AdvancedColorGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Creamos las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Emotion Color Palette API",
    description="Genera paletas de colores basadas en el análisis de sentimientos de texto",
    version="2.0.0"
)

# --- Configuración de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inicializar analizadores ---
vader_analyzer = SentimentIntensityAnalyzer()

# --- Pydantic Models ---
class TextInput(BaseModel):
    text: str
    method: str = "hybrid"
    language: Optional[str] = "auto"

    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('El texto no puede estar vacío')
        if len(v.strip()) < 2:
            raise ValueError('El texto debe tener al menos 2 caracteres')
        if len(v) > 1000:
            raise ValueError('El texto no puede exceder 1000 caracteres')
        return v.strip()

    @validator('method')
    def validate_method(cls, v):
        valid_methods = ['textblob', 'vader', 'hybrid', 'enhanced']
        if v not in valid_methods:
            raise ValueError(f'Método debe ser uno de: {", ".join(valid_methods)}')
        return v

class AnalysisResponse(BaseModel):
    colors: list[str]
    polarity: float
    sentiment: str
    confidence: float
    method_used: str
    translated_text: str
    original_text: str
    intensity: str
    emotion_details: dict

# --- Paletas de Colores de Referencia (para descripciones) ---
ENHANCED_PALETTES = {
    "very_positive": {"emotion": "Alegría intensa", "description": "Colores vibrantes y energéticos"},
    "positive": {"emotion": "Optimismo", "description": "Colores cálidos y esperanzadores"},
    "slightly_positive": {"emotion": "Satisfacción suave", "description": "Colores suaves y tranquilos"},
    "neutral": {"emotion": "Neutralidad", "description": "Colores equilibrados y serenos"},
    "slightly_negative": {"emotion": "Melancolía ligera", "description": "Tonos grises suaves"},
    "negative": {"emotion": "Tristeza", "description": "Colores oscuros y contemplativos"},
    "very_negative": {"emotion": "Dolor profundo", "description": "Colores intensamente oscuros"}
}

# --- Dependencia para la sesión de la base de datos ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Funciones de Lógica ---
def translate_text(text: str, target_lang: str = 'en') -> str:
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated if translated else text
    except Exception as e:
        logger.warning(f"Error en la traducción: {e}")
        return text

def analyze_with_textblob(text: str) -> tuple[float, float]:
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def analyze_with_vader(text: str) -> tuple[float, dict]:
    scores = vader_analyzer.polarity_scores(text)
    return scores['compound'], scores

def hybrid_analysis(text: str) -> tuple[float, float, dict]:
    tb_polarity, tb_subjectivity = analyze_with_textblob(text)
    vader_polarity, vader_scores = analyze_with_vader(text)
    combined_polarity = (vader_polarity * 0.6) + (tb_polarity * 0.4)
    agreement = 1 - abs(tb_polarity - vader_polarity) / 2
    confidence = max(0.3, agreement)
    analysis_details = {
        "textblob_polarity": round(tb_polarity, 3),
        "vader_compound": round(vader_polarity, 3),
        "agreement_score": round(agreement, 3)
    }
    return combined_polarity, confidence, analysis_details

def get_enhanced_sentiment(polarity: float, confidence: float = 1.0) -> tuple[str, str, dict]:
    intensity_factor = abs(polarity) * confidence
    if polarity > 0.6: sentiment_key = "very_positive"
    elif polarity > 0.3: sentiment_key = "positive"
    elif polarity > 0.05: sentiment_key = "slightly_positive"
    elif polarity < -0.6: sentiment_key = "very_negative"
    elif polarity < -0.3: sentiment_key = "negative"
    elif polarity < -0.05: sentiment_key = "slightly_negative"
    else: sentiment_key = "neutral"
    
    if intensity_factor > 0.7: intensity = "muy alta"
    elif intensity_factor > 0.4: intensity = "alta"
    elif intensity_factor > 0.2: intensity = "media"
    else: intensity = "baja"
    
    sentiment_label = sentiment_key.replace("_", " ")
    return sentiment_label, intensity, ENHANCED_PALETTES[sentiment_key]

def generate_advanced_colors(sentiment_key: str, confidence: float) -> dict:
    """Genera paleta usando el generador avanzado"""
    return AdvancedColorGenerator.generate_advanced_palette(sentiment_key, confidence)

# Función de respaldo (la original) en caso de error
def generate_dynamic_palette(polarity: float, confidence: float) -> list[str]:
    base_hue = np.interp(polarity, [-1, 1], [0, 120]) / 360.0
    base_saturation = np.interp(confidence, [0, 1], [0.45, 0.95])
    base_lightness = np.interp(abs(polarity), [0, 1], [0.9, 0.5])

    palette_hsl = [
        (base_hue, base_saturation, min(0.95, base_lightness + 0.15)),
        ((base_hue - 30/360.0) % 1.0, base_saturation, base_lightness),
        (base_hue, base_saturation, base_lightness),
        ((base_hue + 30/360.0) % 1.0, base_saturation, base_lightness),
        (base_hue, base_saturation, max(0.2, base_lightness - 0.15))
    ]

    palette_hex = []
    for h, s, l in palette_hsl:
        rgb = colorsys.hls_to_rgb(h, l, s)
        hex_color = f"#{''.join(f'{int(c * 255):02x}' for c in rgb)}"
        palette_hex.append(hex_color)
    return palette_hex

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "Emotion Color Palette API is running!", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "api": "running", "features": ["advanced_colors", "sentiment_analysis"]}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_text(request: TextInput, db: Session = Depends(get_db)):
    try:
        original_text = request.text
        translated_text = translate_text(original_text)
        
        if request.method == "textblob":
            polarity, subjectivity = analyze_with_textblob(translated_text)
            confidence = 1 - subjectivity
            analysis_details = {"subjectivity": round(subjectivity, 3)}
        elif request.method == "vader":
            polarity, vader_scores = analyze_with_vader(translated_text)
            confidence = abs(polarity)
            analysis_details = {"vader_scores": vader_scores}
        else: # hybrid o enhanced
            polarity, confidence, analysis_details = hybrid_analysis(translated_text)
        
        sentiment_label, intensity, palette_info = get_enhanced_sentiment(polarity, confidence)
        
        # Usar el generador avanzado de colores
        try:
            palette_data = generate_advanced_colors(sentiment_label, confidence)
            dynamic_colors = palette_data["colors"]
            
            # Información enriquecida de la emoción
            emotion_details = {
                "emotion": palette_data.get("emotion", palette_info["emotion"]),
                "description": palette_data.get("description", "Paleta generada dinámicamente"),
                "temperature": palette_data.get("temperature", "neutral"),
                "harmony": palette_data.get("harmony", "balanced"),
                "mood": palette_data.get("mood", "neutral"),
                "energy": palette_data.get("energy", "medium"),
                "color_meanings": palette_data.get("color_meanings", []),
                "analysis": analysis_details
            }
        except Exception as color_error:
            logger.warning(f"Error en generador avanzado, usando respaldo: {color_error}")
            # Usar generador de respaldo
            dynamic_colors = generate_dynamic_palette(polarity, confidence)
            emotion_details = {
                "emotion": palette_info["emotion"],
                "description": "Paleta generada con algoritmo de respaldo",
                "temperature": "neutral",
                "harmony": "basic",
                "mood": "neutral",
                "energy": "medium",
                "color_meanings": [],
                "analysis": analysis_details
            }
        
        response_data = {
            "colors": dynamic_colors,
            "polarity": round(polarity, 3),
            "sentiment": sentiment_label,
            "confidence": round(confidence, 3),
            "method_used": request.method,
            "translated_text": translated_text,
            "original_text": original_text,
            "intensity": intensity,
            "emotion_details": emotion_details
        }
        
        # Guardar en base de datos
        try:
            db_palette = models.Palette(
                input_text=original_text,
                translated_text=translated_text,
                polarity=f"{polarity:.3f}",
                colors=",".join(dynamic_colors),
                analysis_method=request.method,
                confidence_score=confidence,
                sentiment_label=sentiment_label,
                intensity=intensity,
                emotion_type=emotion_details.get("emotion", palette_info["emotion"])
            )
            db.add(db_palette)
            db.commit()
            db.refresh(db_palette)
            logger.info(f"Paleta guardada exitosamente para texto: '{original_text[:30]}...'")
        except Exception as db_error:
            logger.warning(f"Error al guardar en BD: {db_error}")
            # Continuar sin fallar
        
        return AnalysisResponse(**response_data)
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/gallery")
def get_gallery(limit: int = 50, db: Session = Depends(get_db)):
    try:
        limit = min(limit, 100)
        palettes = db.query(models.Palette).order_by(models.Palette.created_at.desc()).limit(limit).all()
        return {"total": len(palettes), "palettes": palettes}
    except Exception as e:
        logger.error(f"Error en galería: {e}")
        return {"total": 0, "palettes": []}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Endpoint para obtener estadísticas de uso"""
    try:
        total_palettes = db.query(models.Palette).count()
        
        # Contar por métodos de análisis
        methods_count = {}
        methods = db.query(models.Palette.analysis_method).distinct().all()
        for method in methods:
            if method[0]:
                count = db.query(models.Palette).filter(models.Palette.analysis_method == method[0]).count()
                methods_count[method[0]] = count
        
        # Contar por tipos de emoción
        emotions_count = {}
        emotions = db.query(models.Palette.emotion_type).distinct().all()
        for emotion in emotions:
            if emotion[0]:
                count = db.query(models.Palette).filter(models.Palette.emotion_type == emotion[0]).count()
                emotions_count[emotion[0]] = count
        
        return {
            "total_palettes": total_palettes,
            "methods_usage": methods_count,
            "emotions_distribution": emotions_count,
            "api_version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Error en estadísticas: {e}")
        return {
            "total_palettes": 0,
            "methods_usage": {},
            "emotions_distribution": {},
            "error": "No se pudieron obtener las estadísticas"
        }
# ==========================================
# ENDPOINTS DE ELIMINACIÓN (CRUD COMPLETO)
# ==========================================

@app.delete("/palettes/{palette_id}")
def delete_palette(palette_id: int, db: Session = Depends(get_db)):
    """
    Eliminar una paleta específica por ID
    """
    try:
        palette = db.query(models.Palette).filter(models.Palette.id == palette_id).first()
        
        if not palette:
            raise HTTPException(status_code=404, detail="Paleta no encontrada")
        
        db.delete(palette)
        db.commit()
        
        logger.info(f"Paleta {palette_id} eliminada exitosamente")
        return {"message": "Paleta eliminada exitosamente", "id": palette_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar paleta {palette_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar paleta")

@app.delete("/palettes/clear-all")
def clear_all_palettes(db: Session = Depends(get_db)):
    """
    Eliminar TODAS las paletas (usar con precaución)
    """
    try:
        count = db.query(models.Palette).count()
        db.query(models.Palette).delete()
        db.commit()
        
        logger.warning(f"Todas las paletas eliminadas: {count} registros")
        return {"message": f"{count} paletas eliminadas", "count": count}
        
    except Exception as e:
        logger.error(f"Error al limpiar paletas: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al limpiar base de datos")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)