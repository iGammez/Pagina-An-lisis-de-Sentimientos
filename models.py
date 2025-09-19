from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

# Define la tabla 'palettes' que guardará la información
class Palette(Base):
    __tablename__ = "palettes"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(String, index=True)
    translated_text = Column(String)
    polarity = Column(String)
    colors = Column(String) # Guardaremos los colores como un string separado por comas
    created_at = Column(DateTime(timezone=True), server_default=func.now())