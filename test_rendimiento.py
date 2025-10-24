#!/usr/bin/env python3
"""
Pruebas de Rendimiento - Análisis Emocional a Color
Ejecutar desde la carpeta raíz: python test_rendimiento.py
"""

import requests
import time
import asyncio
import aiohttp
import random
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:8000"
MAX_WORKERS = 10
RESULTADOS_FILE = "resultados_rendimiento.json"

# Datos de prueba variados
TEXTOS_PRUEBA = [
    "Me siento muy feliz hoy",
    "Estoy un poco triste por la situación actual", 
    "Siento una mezcla de nostalgia y esperanza por el futuro",
    "I'm feeling anxious about tomorrow's presentation",
    "Je me sens très optimiste aujourd'hui",
    "Estoy emocionado por este nuevo proyecto",
    "Me encuentro melancólico esta tarde de lluvia",
    "I feel incredibly energetic and motivated right now",
    "Tengo sentimientos encontrados sobre esta decisión importante",
    "Me siento en paz y tranquilo después de meditar",
    "Estoy nervioso pero emocionado por los cambios que vienen",
    "I'm overwhelmed with joy seeing my family again",
    "Siento una profunda satisfacción por el trabajo realizado",
    "Me encuentro frustrado por los obstáculos constantes",
    "I feel grateful for all the opportunities I've been given",
    "Estoy preocupado por el futuro pero mantengo la esperanza",
    "Me siento inspirado por las historias que escucho",
    "I'm feeling contemplative about life's big questions",
    "Siento una calidez especial cuando pienso en mis amigos",
    "Me encuentro reflexivo sobre mis decisiones pasadas"
]

METODOS_ANALISIS = ["textblob", "vader", "hybrid", "enhanced"]

class TestRendimiento:
    def __init__(self):
        self.resultados = {
            "timestamp": datetime.now().isoformat(),
            "pruebas": {},
            "resumen": {}
        }
    
    def verificar_api_disponible(self):
        """Verificar que la API esté funcionando"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API disponible y funcionando")
                return True
            else:
                print(f" API responde con código {response.status_code}")
                return False
        except Exception as e:
            print(f" No se puede conectar a la API: {e}")
            print(" Asegúrate de que el backend esté ejecutándose en localhost:8000")
            return False
    
    def prueba_individual(self, texto, metodo="hybrid"):
        """Realizar una prueba individual de análisis"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json={"text": texto, "method": metodo},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response_time": response_time,
                    "texto_length": len(texto),
                    "metodo": metodo,
                    "sentiment": data.get("sentiment", "unknown"),
                    "confidence": data.get("confidence", 0),
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e),
                "status_code": 0
            }
    
    def prueba_secuencial(self, num_requests=50):
        """Prueba secuencial - una request a la vez"""
        print(f"\n🔄 Iniciando prueba secuencial ({num_requests} requests)")
        
        resultados = []
        for i in range(num_requests):
            texto = random.choice(TEXTOS_PRUEBA)
            metodo = random.choice(METODOS_ANALISIS)
            resultado = self.prueba_individual(texto, metodo)
            resultados.append(resultado)
            
            if (i + 1) % 10 == 0:
                print(f"   Completadas {i + 1}/{num_requests} requests")
        
        return self.analizar_resultados(resultados, "secuencial")
    
    def prueba_concurrente(self, num_requests=50, max_workers=5):
        """Prueba concurrente - múltiples requests simultáneas"""
        print(f"\n⚡ Iniciando prueba concurrente ({num_requests} requests, {max_workers} workers)")
        
        def worker():
            texto = random.choice(TEXTOS_PRUEBA)
            metodo = random.choice(METODOS_ANALISIS)
            return self.prueba_individual(texto, metodo)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker) for _ in range(num_requests)]
            resultados = [future.result() for future in futures]
        
        return self.analizar_resultados(resultados, "concurrente")
    
    async def prueba_asincrona(self, num_requests=50):
        """Prueba asíncrona con aiohttp"""
        print(f"\n🚀 Iniciando prueba asíncrona ({num_requests} requests)")
        
        async def realizar_request(session, texto, metodo):
            start_time = time.time()
            try:
                async with session.post(
                    f"{API_BASE_URL}/analyze",
                    json={"text": texto, "method": metodo},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "response_time": response_time,
                            "texto_length": len(texto),
                            "metodo": metodo,
                            "sentiment": data.get("sentiment", "unknown"),
                            "confidence": data.get("confidence", 0),
                            "status_code": response.status
                        }
                    else:
                        return {
                            "success": False,
                            "response_time": response_time,
                            "error": f"HTTP {response.status}",
                            "status_code": response.status
                        }
            except Exception as e:
                return {
                    "success": False,
                    "response_time": time.time() - start_time,
                    "error": str(e),
                    "status_code": 0
                }
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(num_requests):
                texto = random.choice(TEXTOS_PRUEBA)
                metodo = random.choice(METODOS_ANALISIS)
                tasks.append(realizar_request(session, texto, metodo))
            
            resultados = await asyncio.gather(*tasks)
        
        return self.analizar_resultados(resultados, "asincrona")
    
    def prueba_volumen_datos(self):
        """Prueba con diferentes longitudes de texto"""
        print(f"\n📊 Iniciando prueba de volumen de datos")
        
        # Textos de diferentes longitudes
        textos_volumen = {
            "corto": "Feliz",
            "medio": "Me siento muy feliz y emocionado por este nuevo día",
            "largo": " ".join(TEXTOS_PRUEBA[:5]),  # Combinar varios textos
            "muy_largo": " ".join(TEXTOS_PRUEBA[:10])  # Texto muy largo
        }
        
        resultados_volumen = {}
        
        for categoria, texto in textos_volumen.items():
            print(f"   Probando texto {categoria} ({len(texto)} caracteres)")
            resultados = []
            
            # 10 pruebas por categoría
            for _ in range(10):
                resultado = self.prueba_individual(texto, "hybrid")
                resultados.append(resultado)
            
            resultados_volumen[categoria] = self.analizar_resultados(resultados, f"volumen_{categoria}")
        
        return resultados_volumen
    
    def prueba_estres_base_datos(self):
        """Prueba de estrés para la base de datos"""
        print(f"\n💾 Iniciando prueba de estrés de base de datos")
        
        # Generar muchos análisis para llenar la BD
        resultados = []
        num_inserts = 100
        
        for i in range(num_inserts):
            texto = random.choice(TEXTOS_PRUEBA)
            metodo = random.choice(METODOS_ANALISIS)
            resultado = self.prueba_individual(texto, metodo)
            resultados.append(resultado)
            
            if (i + 1) % 20 == 0:
                print(f"   Insertados {i + 1}/{num_inserts} registros")
        
        # Probar consulta de galería
        print("   Probando consulta de galería...")
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/gallery")
            gallery_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                total_palettes = data.get("total", 0)
                print(f"   ✅ Galería consultada: {total_palettes} paletas en {gallery_time:.2f}s")
            else:
                print(f"   ❌ Error en consulta de galería: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error en consulta de galería: {e}")
        
        return self.analizar_resultados(resultados, "estres_bd")
    
    def analizar_resultados(self, resultados, tipo_prueba):
        """Analizar y resumir resultados de las pruebas"""
        if not resultados:
            return {"error": "No hay resultados para analizar"}
        
        # Filtrar resultados exitosos
        exitosos = [r for r in resultados if r.get("success", False)]
        fallidos = [r for r in resultados if not r.get("success", False)]
        
        # Calcular métricas
        response_times = [r["response_time"] for r in exitosos]
        
        if response_times:
            metricas = {
                "total_requests": len(resultados),
                "exitosas": len(exitosos),
                "fallidas": len(fallidos),
                "tasa_exito": (len(exitosos) / len(resultados)) * 100,
                "tiempo_promedio": statistics.mean(response_times),
                "tiempo_mediano": statistics.median(response_times),
                "tiempo_min": min(response_times),
                "tiempo_max": max(response_times),
                "tiempo_p95": sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 1 else response_times[0],
                "desviacion_estandar": statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
        else:
            metricas = {
                "total_requests": len(resultados),
                "exitosas": 0,
                "fallidas": len(fallidos),
                "tasa_exito": 0,
                "error": "Todas las requests fallaron"
            }
        
        # Imprimir resultados
        print(f"\n📈 Resultados de prueba {tipo_prueba}:")
        print(f"   Total requests: {metricas['total_requests']}")
        print(f"   Exitosas: {metricas['exitosas']}")
        print(f"   Fallidas: {metricas['fallidas']}")
        print(f"   Tasa de éxito: {metricas.get('tasa_exito', 0):.1f}%")
        
        if 'tiempo_promedio' in metricas:
            print(f"   Tiempo promedio: {metricas['tiempo_promedio']:.3f}s")
            print(f"   Tiempo mediano: {metricas['tiempo_mediano']:.3f}s")
            print(f"   Tiempo P95: {metricas['tiempo_p95']:.3f}s")
            print(f"   Rango: {metricas['tiempo_min']:.3f}s - {metricas['tiempo_max']:.3f}s")
        
        self.resultados["pruebas"][tipo_prueba] = metricas
        return metricas
    
    def ejecutar_todas_las_pruebas(self):
        """Ejecutar todas las pruebas de rendimiento"""
        print("🚀 INICIANDO BATERÍA COMPLETA DE PRUEBAS DE RENDIMIENTO")
        print("=" * 60)
        
        if not self.verificar_api_disponible():
            print("❌ No se pueden ejecutar las pruebas sin API disponible")
            return
        
        # 1. Prueba secuencial básica
        self.prueba_secuencial(30)
        
        # 2. Prueba concurrente
        self.prueba_concurrente(30, 5)
        
        # 3. Prueba asíncrona
        try:
            asyncio.run(self.prueba_asincrona(30))
        except Exception as e:
            print(f"❌ Error en prueba asíncrona: {e}")
        
        # 4. Prueba de volumen
        resultados_volumen = self.prueba_volumen_datos()
        self.resultados["pruebas"]["volumen_datos"] = resultados_volumen
        
        # 5. Prueba de estrés de BD
        self.prueba_estres_base_datos()
        
        # Generar resumen final
        self.generar_resumen_final()
        
        # Guardar resultados
        self.guardar_resultados()
        
        print("\n🎯 TODAS LAS PRUEBAS COMPLETADAS")
        print(f"📄 Resultados guardados en: {RESULTADOS_FILE}")
    
    def generar_resumen_final(self):
        """Generar resumen ejecutivo de todas las pruebas"""
        pruebas = self.resultados["pruebas"]
        
        # Promedios generales
        tiempos_promedio = []
        tasas_exito = []
        
        for nombre, datos in pruebas.items():
            if isinstance(datos, dict) and 'tiempo_promedio' in datos:
                tiempos_promedio.append(datos['tiempo_promedio'])
                tasas_exito.append(datos['tasa_exito'])
        
        resumen = {
            "tiempo_promedio_general": statistics.mean(tiempos_promedio) if tiempos_promedio else 0,
            "tasa_exito_promedio": statistics.mean(tasas_exito) if tasas_exito else 0,
            "pruebas_ejecutadas": len(pruebas),
            "recomendaciones": self.generar_recomendaciones(tiempos_promedio, tasas_exito)
        }
        
        self.resultados["resumen"] = resumen
        
        print("\n📊 RESUMEN EJECUTIVO:")
        print(f"   Tiempo promedio general: {resumen['tiempo_promedio_general']:.3f}s")
        print(f"   Tasa de éxito promedio: {resumen['tasa_exito_promedio']:.1f}%")
        print(f"   Pruebas ejecutadas: {resumen['pruebas_ejecutadas']}")
    
    def generar_recomendaciones(self, tiempos, tasas):
        """Generar recomendaciones basadas en los resultados"""
        recomendaciones = []
        
        if tiempos:
            tiempo_promedio = statistics.mean(tiempos)
            if tiempo_promedio > 3:
                recomendaciones.append("Optimizar algoritmos de procesamiento - tiempo promedio alto")
            elif tiempo_promedio < 1:
                recomendaciones.append("Rendimiento excelente - sistema optimizado")
        
        if tasas:
            tasa_promedio = statistics.mean(tasas)
            if tasa_promedio < 95:
                recomendaciones.append("Mejorar manejo de errores - tasa de fallo alta")
            elif tasa_promedio >= 99:
                recomendaciones.append("Estabilidad excelente del sistema")
        
        if not recomendaciones:
            recomendaciones.append("Sistema funcionando dentro de parámetros normales")
        
        return recomendaciones
    
    def guardar_resultados(self):
        """Guardar resultados en archivo JSON"""
        try:
            with open(RESULTADOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, indent=2, ensure_ascii=False)
            print(f"✅ Resultados guardados en {RESULTADOS_FILE}")
        except Exception as e:
            print(f"❌ Error guardando resultados: {e}")

if __name__ == "__main__":
    print("🎨 PRUEBAS DE RENDIMIENTO - Análisis Emocional a Color")
    print("=" * 60)
    
    tester = TestRendimiento()
    tester.ejecutar_todas_las_pruebas()