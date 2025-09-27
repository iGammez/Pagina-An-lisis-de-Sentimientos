from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from database import Base

class Palette(Base):
    __tablename__ = "palettes"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(String, index=True)
    translated_text = Column(String, nullable=True)
    polarity = Column(String)
    colors = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # --- NUEVAS COLUMNAS ---
    analysis_method = Column(String, default="hybrid")
    confidence_score = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)
    intensity = Column(String, nullable=True)
    emotion_type = Column(String, nullable=True)