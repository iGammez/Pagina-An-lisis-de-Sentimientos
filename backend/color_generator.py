import numpy as np
import colorsys
from typing import List, Dict, Tuple
import random
import math

class AdvancedColorGenerator:
    """Generador avanzado de paletas de colores basado en emociones y teoría del color"""
    
    # Mapeo detallado de emociones a configuraciones de color
    EMOTION_COLOR_MAPS = {
        "very_positive": {
            "name": "Euforia",
            "base_hues": [45, 60, 30, 120],  # Amarillos brillantes, naranjas, verdes
            "saturation_range": (0.75, 0.95),
            "lightness_range": (0.65, 0.85),
            "temperature": "warm",
            "energy": "high",
            "harmony": "complementary",
            "mood": "energetic"
        },
        "positive": {
            "name": "Alegria",
            "base_hues": [30, 50, 160, 200],  # Naranjas cálidos, azul-verde
            "saturation_range": (0.6, 0.85),
            "lightness_range": (0.55, 0.75),
            "temperature": "warm",
            "energy": "medium-high",
            "harmony": "triadic",
            "mood": "optimistic"
        },
        "slightly_positive": {
            "name": "Serenidad",
            "base_hues": [180, 200, 220, 160],  # Azules suaves, verdes agua
            "saturation_range": (0.4, 0.7),
            "lightness_range": (0.65, 0.8),
            "temperature": "cool",
            "energy": "low",
            "harmony": "analogous",
            "mood": "peaceful"
        },
        "neutral": {
            "name": "Equilibrio",
            "base_hues": [210, 30, 120, 270],  # Espectro balanceado
            "saturation_range": (0.3, 0.6),
            "lightness_range": (0.5, 0.7),
            "temperature": "balanced",
            "energy": "medium",
            "harmony": "tetradic",
            "mood": "balanced"
        },
        "slightly_negative": {
            "name": "Melancolia",
            "base_hues": [200, 220, 240, 280],  # Azules grisáceos, violetas suaves
            "saturation_range": (0.3, 0.6),
            "lightness_range": (0.4, 0.65),
            "temperature": "cool",
            "energy": "low",
            "harmony": "analogous",
            "mood": "contemplative"
        },
        "negative": {
            "name": "Tristeza",
            "base_hues": [220, 240, 260, 200],  # Azules profundos, violetas
            "saturation_range": (0.4, 0.7),
            "lightness_range": (0.3, 0.55),
            "temperature": "cool",
            "energy": "low",
            "harmony": "monochromatic",
            "mood": "somber"
        },
        "very_negative": {
            "name": "Angustia",
            "base_hues": [0, 20, 320, 280],  # Rojos oscuros, violetas profundos
            "saturation_range": (0.6, 0.9),
            "lightness_range": (0.2, 0.45),
            "temperature": "dark",
            "energy": "intense",
            "harmony": "split_complementary",
            "mood": "intense"
        }
    }
    
    @classmethod
    def generate_advanced_palette(cls, sentiment_key: str, confidence: float, 
                                num_colors: int = 5) -> Dict:
        """
        Genera una paleta de colores avanzada con información detallada
        """
        # Normalizar clave de sentimiento
        sentiment_key = sentiment_key.replace(" ", "_").lower()
        if sentiment_key not in cls.EMOTION_COLOR_MAPS:
            sentiment_key = "neutral"
            
        config = cls.EMOTION_COLOR_MAPS[sentiment_key]
        confidence_factor = max(0.3, min(1.0, confidence))
        
        # Generar paleta según esquema de armonía
        colors = cls._generate_harmonic_palette(config, confidence_factor, num_colors)
        
        # Aplicar variaciones dinámicas basadas en confianza
        colors = cls._apply_confidence_variations(colors, confidence_factor, config)
        
        # Información detallada de la paleta
        palette_info = {
            "colors": colors,
            "emotion": config["name"],
            "temperature": config["temperature"],
            "energy": config["energy"],
            "harmony": config["harmony"],
            "mood": config["mood"],
            "confidence": confidence_factor,
            "description": cls._get_palette_description(config, confidence_factor),
            "color_meanings": cls._get_color_meanings(colors, config)
        }
        
        return palette_info
    
    @classmethod
    def _generate_harmonic_palette(cls, config: Dict, confidence: float, 
                                 num_colors: int) -> List[str]:
        """Genera paleta basada en diferentes esquemas de armonía cromática"""
        
        harmony = config["harmony"]
        base_hues = config["base_hues"]
        
        # Seleccionar matiz principal con variación aleatoria
        primary_hue = random.choice(base_hues)
        primary_hue += random.uniform(-15, 15)  # Añadir variación natural
        primary_hue = primary_hue % 360
        
        if harmony == "complementary":
            colors = cls._complementary_harmony(primary_hue, config, confidence, num_colors)
        elif harmony == "triadic":
            colors = cls._triadic_harmony(primary_hue, config, confidence, num_colors)
        elif harmony == "analogous":
            colors = cls._analogous_harmony(primary_hue, config, confidence, num_colors)
        elif harmony == "split_complementary":
            colors = cls._split_complementary_harmony(primary_hue, config, confidence, num_colors)
        elif harmony == "tetradic":
            colors = cls._tetradic_harmony(primary_hue, config, confidence, num_colors)
        else:  # monochromatic
            colors = cls._monochromatic_harmony(primary_hue, config, confidence, num_colors)
            
        return colors
    
    @classmethod
    def _complementary_harmony(cls, base_hue: float, config: Dict, 
                             confidence: float, num_colors: int) -> List[str]:
        """Esquema complementario - colores opuestos"""
        colors = []
        sat_min, sat_max = config["saturation_range"]
        light_min, light_max = config["lightness_range"]
        
        # Hues principales y de apoyo
        main_hues = [
            base_hue,
            (base_hue + 180) % 360,  # Complementario directo
            (base_hue + 30) % 360,   # Variación cálida
            (base_hue + 210) % 360,  # Variación fría
            (base_hue + 150) % 360   # Intermedio
        ]
        
        for i, hue in enumerate(main_hues[:num_colors]):
            # Crear variaciones naturales
            sat_variation = 0.15 * np.sin(i * np.pi / 3) * confidence
            light_variation = 0.2 * np.cos(i * np.pi / 2)
            
            saturation = np.clip(
                sat_min + (sat_max - sat_min) * confidence + sat_variation, 
                0.15, 0.95
            )
            
            # Distribución más natural de luminosidad
            light_base = light_min + (light_max - light_min) * (0.3 + 0.4 * i / (num_colors - 1))
            lightness = np.clip(light_base + light_variation, 0.15, 0.9)
            
            colors.append(cls._hsl_to_hex(hue, saturation, lightness))
        
        return colors
    
    @classmethod
    def _triadic_harmony(cls, base_hue: float, config: Dict, 
                       confidence: float, num_colors: int) -> List[str]:
        """Esquema triádico - tres colores equidistantes"""
        colors = []
        sat_min, sat_max = config["saturation_range"]
        light_min, light_max = config["lightness_range"]
        
        # Triádico básico más variaciones
        base_triadic = [base_hue, (base_hue + 120) % 360, (base_hue + 240) % 360]
        additional_hues = [(base_hue + 60) % 360, (base_hue + 300) % 360]
        all_hues = base_triadic + additional_hues
        
        for i, hue in enumerate(all_hues[:num_colors]):
            # Mayor variación en triádico para crear dinamismo
            sat_factor = 0.7 + 0.3 * confidence * (0.8 + 0.4 * np.sin(i * np.pi))
            saturation = np.clip(sat_min + (sat_max - sat_min) * sat_factor, 0.2, 0.9)
            
            light_factor = 0.4 + 0.5 * (i / (num_colors - 1)) + 0.1 * np.cos(i * np.pi / 2)
            lightness = np.clip(light_min + (light_max - light_min) * light_factor, 0.2, 0.85)
            
            colors.append(cls._hsl_to_hex(hue, saturation, lightness))
        
        return colors
    
    @classmethod
    def _analogous_harmony(cls, base_hue: float, config: Dict, 
                         confidence: float, num_colors: int) -> List[str]:
        """Esquema análogo - colores adyacentes"""
        colors = []
        sat_min, sat_max = config["saturation_range"]
        light_min, light_max = config["lightness_range"]
        
        # Rango de variación más amplio con alta confianza
        hue_spread = 50 + 30 * confidence
        
        for i in range(num_colors):
            # Distribución no lineal para mayor naturalidad
            position_factor = (i / (num_colors - 1)) ** 0.8
            hue_offset = (position_factor - 0.5) * hue_spread
            hue = (base_hue + hue_offset) % 360
            
            # Variaciones orgánicas
            sat_variation = 0.2 * np.sin(i * np.pi * 2 / num_colors)
            saturation = np.clip(
                sat_min + (sat_max - sat_min) * confidence + sat_variation, 
                0.25, 0.9
            )
            
            # Curva de luminosidad más suave
            light_curve = 0.3 + 0.4 * position_factor + 0.2 * np.sin(i * np.pi / 3)
            lightness = np.clip(light_min + (light_max - light_min) * light_curve, 0.25, 0.8)
            
            colors.append(cls._hsl_to_hex(hue, saturation, lightness))
        
        return colors
    
    @classmethod
    def _split_complementary_harmony(cls, base_hue: float, config: Dict, 
                                   confidence: float, num_colors: int) -> List[str]:
        """Esquema complementario dividido"""
        colors = []
        sat_min, sat_max = config["saturation_range"]
        light_min, light_max = config["lightness_range"]
        
        # Complementario dividido: base + dos colores adyacentes al complementario
        comp_base = (base_hue + 180) % 360
        hues = [
            base_hue,
            (comp_base - 30) % 360,
            (comp_base + 30) % 360,
            (base_hue + 60) % 360,
            (base_hue - 60) % 360
        ]
        
        for i, hue in enumerate(hues[:num_colors]):
            # Intensidad variable para crear jerarquía
            intensity = 1.0 - (i * 0.15)
            saturation = np.clip(
                sat_min + (sat_max - sat_min) * confidence * intensity, 
                0.2, 0.9
            )
            
            lightness = np.clip(
                light_min + (light_max - light_min) * (0.4 + 0.3 * i / num_colors),
                0.2, 0.8
            )
            
            colors.append(cls._hsl_to_hex(hue, saturation, lightness))
        
        return colors
    
    @classmethod
    def _tetradic_harmony(cls, base_hue: float, config: Dict, 
                        confidence: float, num_colors: int) -> List[str]:
        """Esquema tetrádico - cuatro colores formando un rectángulo"""
        colors = []
        sat_min, sat_max = config["saturation_range"]
        light_min, light_max = config["lightness_range"]
        
        # Tetrádico: cuatro colores separados por 90 grados
        hues = [
            base_hue,
            (base_hue + 90) % 360,
            (base_hue + 180) % 360,
            (base_hue + 270) % 360,
            (base_hue + 45) % 360  # Color intermedio
        ]
        
        for i, hue in enumerate(hues[:num_colors]):
            # Balancear saturación para evitar sobrecarga visual
            sat_balance = 0.6 + 0.4 * confidence * (0.8 + 0.2 * np.cos(i * np.pi))
            saturation = np.clip(
                sat_min + (sat_max - sat_min) * sat_balance, 
                0.3, 0.8
            )
            
            lightness = np.clip(
                light_min + (light_max - light_min) * (0.3 + 0.4 * i / (num_colors - 1)),
                0.3, 0.75
            )
            
            colors.append(cls._hsl_to_hex(hue, saturation, lightness))
        
        return colors
    
    @classmethod
    def _monochromatic_harmony(cls, base_hue: float, config: Dict, 
                             confidence: float, num_colors: int) -> List[str]:
        """Esquema monocromático - variaciones de un solo matiz"""
        colors = []
        sat_min, sat_max = config["saturation_range"]
        light_min, light_max = config["lightness_range"]
        
        for i in range(num_colors):
            # Variaciones sutiles en el matiz para mayor interés
            hue_variation = random.uniform(-8, 8)
            hue = (base_hue + hue_variation) % 360
            
            # Progresión no lineal en saturación
            sat_progress = (i / (num_colors - 1)) ** 0.7
            saturation = np.clip(
                sat_min + (sat_max - sat_min) * (0.4 + 0.6 * sat_progress),
                0.2, 0.9
            )
            
            # Curva suave de luminosidad
            light_progress = i / (num_colors - 1)
            light_curve = 0.3 + 0.5 * light_progress + 0.1 * np.sin(light_progress * np.pi)
            lightness = np.clip(light_min + (light_max - light_min) * light_curve, 0.2, 0.85)
            
            colors.append(cls._hsl_to_hex(hue, saturation, lightness))
        
        return colors
    
    @classmethod
    def _apply_confidence_variations(cls, colors: List[str], confidence: float, config: Dict) -> List[str]:
        """Aplica variaciones basadas en el nivel de confianza"""
        if confidence < 0.5:
            # Baja confianza: atenuar colores
            return [cls._adjust_color_intensity(color, 0.8) for color in colors]
        elif confidence > 0.8:
            # Alta confianza: intensificar ligeramente
            return [cls._adjust_color_intensity(color, 1.1) for color in colors]
        return colors
    
    @classmethod
    def _adjust_color_intensity(cls, hex_color: str, factor: float) -> str:
        """Ajusta la intensidad de un color"""
        # Convertir hex a RGB
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Convertir a HSL
        r, g, b = [x/255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        
        # Ajustar saturación
        s = min(1.0, s * factor)
        
        # Convertir de vuelta
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        rgb = tuple(int(x * 255) for x in (r, g, b))
        
        return f"#{''.join(f'{c:02x}' for c in rgb)}"
    
    @classmethod
    def _hsl_to_hex(cls, hue: float, saturation: float, lightness: float) -> str:
        """Convierte HSL a formato hexadecimal"""
        rgb = colorsys.hls_to_rgb(hue / 360.0, lightness, saturation)
        hex_color = f"#{''.join(f'{int(c * 255):02x}' for c in rgb)}"
        return hex_color
    
    @classmethod
    def _get_palette_description(cls, config: Dict, confidence: float) -> str:
        """Genera descripción poética de la paleta"""
        descriptions = {
            "warm": [
                "colores cálidos que abrazan el alma",
                "tonos vibrantes llenos de energía vital",
                "matices dorados que danzan con pasión"
            ],
            "cool": [
                "colores frescos que susurran serenidad",
                "tonos azulados que invitan a la contemplación",
                "matices glaciales que calman el espíritu"
            ],
            "balanced": [
                "colores equilibrados en perfecta armonía",
                "tonos neutros que transmiten estabilidad",
                "matices balanceados como un jardín zen"
            ],
            "dark": [
                "colores profundos cargados de misterio",
                "tonos intensos que reflejan la complejidad emocional",
                "matices sombríos con una belleza melancólica"
            ]
        }
        
        temp_desc = random.choice(descriptions.get(config["temperature"], ["colores únicos y expresivos"]))
        
        intensity_words = {
            "high": "intensamente",
            "medium-high": "vigorosamente", 
            "medium": "suavemente",
            "low": "delicadamente",
            "intense": "profundamente"
        }
        
        intensity = intensity_words.get(config["energy"], "")
        confidence_adj = "muy" if confidence > 0.7 else "moderadamente" if confidence > 0.4 else "sutilmente"
        
        return f"{confidence_adj} {intensity} expresados a través de {temp_desc}"
    
    @classmethod
    def _get_color_meanings(cls, colors: List[str], config: Dict) -> List[str]:
        """Genera significados psicológicos para cada color"""
        meanings = []
        color_psychology = {
            "red": ["pasión", "energía", "fuerza"],
            "orange": ["creatividad", "entusiasmo", "calidez"],
            "yellow": ["alegría", "optimismo", "claridad"],
            "green": ["crecimiento", "armonía", "naturaleza"],
            "blue": ["tranquilidad", "confianza", "profundidad"],
            "purple": ["misterio", "espiritualidad", "transformación"],
            "pink": ["ternura", "compasión", "amor"],
            "brown": ["estabilidad", "confort", "autenticidad"],
            "gray": ["equilibrio", "neutralidad", "sofisticación"]
        }
        
        for color in colors:
            # Determinar color dominante basado en matiz
            hue = cls._get_dominant_hue(color)
            if hue < 15 or hue >= 345: category = "red"
            elif hue < 45: category = "orange"
            elif hue < 75: category = "yellow"
            elif hue < 165: category = "green"
            elif hue < 255: category = "blue"
            elif hue < 285: category = "purple"
            elif hue < 315: category = "pink"
            else: category = "red"
            
            meanings.append(random.choice(color_psychology.get(category, ["expresión única"])))
        
        return meanings
    
    @classmethod
    def _get_dominant_hue(cls, hex_color: str) -> float:
        """Obtiene el matiz dominante de un color hex"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = [x/255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return h * 360