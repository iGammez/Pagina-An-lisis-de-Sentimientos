#!/usr/bin/env python3
"""
Pruebas Unitarias - Análisis Emocional a Color
Ejecutar: pytest test_unit.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from models import Base, Palette
from database import DATABASE_URL
import json

# Cliente de prueba
client = TestClient(app)

# Base de datos de prueba en memoria
TEST_DATABASE_URL = "sqlite:///./test_palettes.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def setup_database():
    """Crear BD de prueba antes de cada test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ==========================================
# PRUEBAS UNITARIAS - CRUD COMPLETO
# ==========================================

class TestCRUDOperations:
    """Pruebas de operaciones CRUD (Create, Read, Update, Delete)"""
    
    def test_create_palette(self, setup_database):
        """Prueba: AGREGAR paleta a la base de datos"""
        response = client.post(
            "/analyze",
            json={"text": "Me siento muy feliz", "method": "hybrid"}
        )
        
        assert response.status_code == 200, "Error al crear paleta"
        data = response.json()
        assert "colors" in data, "Respuesta no contiene colores"
        assert len(data["colors"]) == 5, "Debe generar 5 colores"
        assert data["polarity"] > 0, "Texto positivo debe tener polaridad positiva"
        print("AGREGAR: Paleta creada exitosamente")
    
    def test_read_all_palettes(self, setup_database):
        """Prueba: VISUALIZAR todas las paletas"""
        # Crear paletas de prueba
        client.post("/analyze", json={"text": "Feliz", "method": "hybrid"})
        client.post("/analyze", json={"text": "Triste", "method": "hybrid"})
        
        # Leer galería
        response = client.get("/gallery")
        
        assert response.status_code == 200, "Error al leer galería"
        data = response.json()
        assert "palettes" in data, "Respuesta no contiene paletas"
        assert data["total"] == 2, f"Esperaba 2 paletas, encontré {data['total']}"
        print(f"VISUALIZAR: {data['total']} paletas leídas correctamente")
    
    def test_delete_palette(self, setup_database):
        """Prueba: ELIMINAR paleta específica"""
        # Crear paleta
        create_response = client.post("/analyze", json={"text": "Test", "method": "hybrid"})
        
        # Obtener ID de la paleta creada
        gallery_response = client.get("/gallery")
        palette_id = gallery_response.json()["palettes"][0]["id"]
        
        # Eliminar paleta
        delete_response = client.delete(f"/palettes/{palette_id}")
        
        assert delete_response.status_code == 200, "Error al eliminar paleta"
        assert delete_response.json()["id"] == palette_id, "ID no coincide"
        
        # Verificar que se eliminó
        verify_response = client.get("/gallery")
        assert verify_response.json()["total"] == 0, "Paleta no se eliminó"
        print(f"ELIMINAR: Paleta {palette_id} eliminada correctamente")
    
    def test_delete_nonexistent_palette(self, setup_database):
        """Prueba: ELIMINAR paleta que no existe (debe fallar)"""
        response = client.delete("/palettes/99999")
        
        assert response.status_code == 404, "Debe retornar 404 para paleta inexistente"
        print("ELIMINAR: Error 404 correctamente manejado")

# ==========================================
# PRUEBAS UNITARIAS - VALIDACIONES
# ==========================================

class TestInputValidation:
    """Pruebas de validación de entrada"""
    
    def test_empty_text(self, setup_database):
        """Prueba: Texto vacío debe ser rechazado"""
        response = client.post("/analyze", json={"text": "", "method": "hybrid"})
        
        assert response.status_code == 422 or response.status_code == 400, "Debe rechazar texto vacío"
        print("VALIDACIÓN: Texto vacío rechazado correctamente")
    
    def test_text_too_short(self, setup_database):
        """Prueba: Texto muy corto debe ser rechazado"""
        response = client.post("/analyze", json={"text": "a", "method": "hybrid"})
        
        assert response.status_code == 422 or response.status_code == 400, "Debe rechazar texto muy corto"
        print("VALIDACIÓN: Texto corto rechazado correctamente")
    
    def test_text_too_long(self, setup_database):
        """Prueba: Texto muy largo debe ser rechazado"""
        long_text = "a" * 1001
        response = client.post("/analyze", json={"text": long_text, "method": "hybrid"})
        
        assert response.status_code == 422 or response.status_code == 400, "Debe rechazar texto muy largo"
        print("VALIDACIÓN: Texto largo rechazado correctamente")
    
    def test_invalid_method(self, setup_database):
        """Prueba: Método inválido debe ser rechazado"""
        response = client.post("/analyze", json={"text": "test", "method": "invalid_method"})
        
        assert response.status_code == 422 or response.status_code == 400, "Debe rechazar método inválido"
        print("VALIDACIÓN: Método inválido rechazado correctamente")

# ==========================================
# PRUEBAS UNITARIAS - ANÁLISIS DE SENTIMIENTOS
# ==========================================

class TestSentimentAnalysis:
    """Pruebas del análisis de sentimientos"""
    
    def test_positive_sentiment(self, setup_database):
        """Prueba: Texto positivo debe generar polaridad positiva"""
        response = client.post("/analyze", json={
            "text": "Me siento increíblemente feliz y emocionado",
            "method": "hybrid"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["polarity"] > 0.3, f"Polaridad muy baja para texto positivo: {data['polarity']}"
        assert "positive" in data["sentiment"].lower(), "Sentimiento debe ser positivo"
        print(f"ANÁLISIS: Sentimiento positivo detectado (polaridad: {data['polarity']})")
    
    def test_negative_sentiment(self, setup_database):
        """Prueba: Texto negativo debe generar polaridad negativa"""
        response = client.post("/analyze", json={
            "text": "Me siento muy triste y deprimido",
            "method": "hybrid"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["polarity"] < -0.1, f"Polaridad muy alta para texto negativo: {data['polarity']}"
        assert "negative" in data["sentiment"].lower() or "trist" in data["sentiment"].lower(), "Sentimiento debe ser negativo"
        print(f"ANÁLISIS: Sentimiento negativo detectado (polaridad: {data['polarity']})")
    
    def test_neutral_sentiment(self, setup_database):
        """Prueba: Texto neutral debe generar polaridad cercana a cero"""
        response = client.post("/analyze", json={
            "text": "El clima está normal hoy",
            "method": "hybrid"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert -0.2 <= data["polarity"] <= 0.2, f"Polaridad fuera de rango neutral: {data['polarity']}"
        print(f"ANÁLISIS: Sentimiento neutral detectado (polaridad: {data['polarity']})")
    
    def test_confidence_score(self, setup_database):
        """Prueba: Confianza debe estar entre 0 y 1"""
        response = client.post("/analyze", json={"text": "Estoy feliz", "method": "hybrid"})
        
        assert response.status_code == 200
        data = response.json()
        assert 0 <= data["confidence"] <= 1, f" Confianza fuera de rango: {data['confidence']}"
        print(f"ANÁLISIS: Confianza válida ({data['confidence']})")

# ==========================================
# PRUEBAS UNITARIAS - GENERACIÓN DE COLORES
# ==========================================

class TestColorGeneration:
    """Pruebas de generación de paletas de colores"""
    
    def test_color_format(self, setup_database):
        """Prueba: Colores deben estar en formato hexadecimal válido"""
        response = client.post("/analyze", json={"text": "Alegre", "method": "hybrid"})
        
        assert response.status_code == 200
        data = response.json()
        
        for color in data["colors"]:
            assert color.startswith("#"), f"Color debe comenzar con #: {color}"
            assert len(color) == 7, f"Color debe tener 7 caracteres: {color}"
            # Verificar que sea hexadecimal válido
            try:
                int(color[1:], 16)
            except ValueError:
                pytest.fail(f"Color no es hexadecimal válido: {color}")
        
        print(f"COLORES: Formato válido para {len(data['colors'])} colores")
    
    def test_color_count(self, setup_database):
        """Prueba: Debe generar exactamente 5 colores"""
        response = client.post("/analyze", json={"text": "Test", "method": "hybrid"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["colors"]) == 5, f"Esperaba 5 colores, recibió {len(data['colors'])}"
        print("COLORES: Cantidad correcta (5 colores)")
    
    def test_colors_are_unique(self, setup_database):
        """Prueba: Los colores generados deben ser diferentes"""
        response = client.post("/analyze", json={"text": "Emocionado", "method": "hybrid"})
        
        assert response.status_code == 200
        data = response.json()
        unique_colors = set(data["colors"])
        # Al menos 4 de 5 deben ser únicos (permitimos 1 coincidencia por probabilidad)
        assert len(unique_colors) >= 4, f"Colores muy repetitivos: {data['colors']}"
        print(f"COLORES: Variedad adecuada ({len(unique_colors)}/5 únicos)")

# ==========================================
# PRUEBAS UNITARIAS - API ENDPOINTS
# ==========================================

class TestAPIEndpoints:
    """Pruebas de endpoints de la API"""
    
    def test_health_endpoint(self):
        """Prueba: Endpoint /health debe responder"""
        response = client.get("/health")
        
        assert response.status_code == 200, "Health check falló"
        data = response.json()
        assert data["status"] == "healthy", "API no está saludable"
        print("API: Health check exitoso")
    
    def test_root_endpoint(self):
        """Prueba: Endpoint raíz debe responder"""
        response = client.get("/")
        
        assert response.status_code == 200, "Root endpoint falló"
        print("API: Root endpoint funcionando")
    
    def test_stats_endpoint(self, setup_database):
        """Prueba: Endpoint /stats debe retornar estadísticas"""
        # Crear algunas paletas
        client.post("/analyze", json={"text": "Feliz", "method": "hybrid"})
        client.post("/analyze", json={"text": "Triste", "method": "vader"})
        
        response = client.get("/stats")
        
        assert response.status_code == 200, "Stats endpoint falló"
        data = response.json()
        assert "total_palettes" in data, "Stats debe incluir total_palettes"
        assert data["total_palettes"] == 2, f"Esperaba 2 paletas, encontró {data['total_palettes']}"
        print(f"API: Estadísticas correctas ({data['total_palettes']} paletas)")

# ==========================================
# PRUEBAS DE NOTIFICACIÓN AUTOMÁTICA
# ==========================================

class TestAutomaticNotifications:
    """Pruebas que verifican avisos automáticos de errores"""
    
    def test_error_notification_invalid_data(self, setup_database):
        """Prueba: Sistema debe notificar errores de datos inválidos"""
        response = client.post("/analyze", json={"text": "", "method": "hybrid"})
        
        assert response.status_code in [400, 422], "No notificó error de validación"
        error_data = response.json()
        assert "detail" in error_data, "Error debe incluir detalles"
        print(f" NOTIFICACIÓN: Error reportado - {error_data.get('detail', 'Sin detalle')}")
    
    def test_error_notification_missing_field(self, setup_database):
        """Prueba: Sistema debe notificar campos faltantes"""
        response = client.post("/analyze", json={"method": "hybrid"})  # Falta 'text'
        
        assert response.status_code == 422, "No notificó campo faltante"
        print("NOTIFICACIÓN: Campo faltante reportado")
    
    def test_error_notification_wrong_type(self, setup_database):
        """Prueba: Sistema debe notificar tipos de datos incorrectos"""
        response = client.post("/analyze", json={"text": 12345, "method": "hybrid"})
        
        assert response.status_code == 422, "No notificó tipo incorrecto"
        print("NOTIFICACIÓN: Tipo incorrecto reportado")

# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================

if __name__ == "__main__":
    print("EJECUTANDO PRUEBAS UNITARIAS")
    print("=" * 60)
    pytest.main([__file__, "-v", "--tb=short", "--color=yes"])