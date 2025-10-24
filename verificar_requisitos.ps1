# verificar_requisitos.ps1
Write-Host "VERIFICACIÓN DE REQUISITOS" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Health Check
Write-Host "Verificando Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
    if ($health.status -eq "healthy") {
        Write-Host "Backend funcionando correctamente" -ForegroundColor Green
    }
} catch {
    Write-Host "Backend no responde" -ForegroundColor Red
    Write-Host "   Asegúrate de que esté ejecutándose en localhost:8000" -ForegroundColor Yellow
}

Write-Host ""

# 2. Verificar endpoint AGREGAR
Write-Host "Verificando endpoint AGREGAR (POST)..." -ForegroundColor Yellow
try {
    $body = @{
        text = "Test de verificación"
        method = "hybrid"
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method POST -Body $body -ContentType "application/json"
    
    if ($result.colors -and $result.colors.Count -eq 5) {
        Write-Host "AGREGAR funciona correctamente" -ForegroundColor Green
        Write-Host "   Colores generados: $($result.colors -join ', ')" -ForegroundColor Gray
    }
} catch {
    Write-Host "Error en endpoint AGREGAR" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 3. Verificar endpoint VISUALIZAR
Write-Host "Verificando endpoint VISUALIZAR (GET)..." -ForegroundColor Yellow
try {
    $gallery = Invoke-RestMethod -Uri "http://localhost:8000/gallery"
    Write-Host "VISUALIZAR funciona correctamente" -ForegroundColor Green
    Write-Host "   Total de paletas: $($gallery.total)" -ForegroundColor Gray
} catch {
    Write-Host "Error en endpoint VISUALIZAR" -ForegroundColor Red
}

Write-Host ""

# 4. Verificar endpoint ELIMINAR
Write-Host "Verificando endpoint ELIMINAR (DELETE)..." -ForegroundColor Yellow
try {
    # Obtener primera paleta para eliminar
    $gallery = Invoke-RestMethod -Uri "http://localhost:8000/gallery"
    
    if ($gallery.palettes.Count -gt 0) {
        $firstId = $gallery.palettes[0].id
        $delete = Invoke-RestMethod -Uri "http://localhost:8000/palettes/$firstId" -Method DELETE
        Write-Host "ELIMINAR funciona correctamente" -ForegroundColor Green
        Write-Host "   Paleta $firstId eliminada" -ForegroundColor Gray
    } else {
        Write-Host " No hay paletas para eliminar (crear alguna primero)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error en endpoint ELIMINAR" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 5. Verificar estructura de base de datos
Write-Host "Verificando estructura de base de datos..." -ForegroundColor Yellow
if (Test-Path "data\palettes.db") {
    Write-Host "Base de datos existe" -ForegroundColor Green
    $dbSize = (Get-Item "data\palettes.db").Length / 1KB
    Write-Host "   Tamaño: $([math]::Round($dbSize, 2)) KB" -ForegroundColor Gray
} else {
    Write-Host "Base de datos no encontrada" -ForegroundColor Red
}

Write-Host ""

# 6. Verificar pruebas unitarias
Write-Host "Verificando pruebas unitarias..." -ForegroundColor Yellow
if (Test-Path "test_unit.py") {
    Write-Host "Archivo de pruebas existe" -ForegroundColor Green
    Write-Host "   Ejecuta: pytest test_unit.py -v" -ForegroundColor Gray
} else {
    Write-Host "Archivo test_unit.py no encontrado" -ForegroundColor Red
}

Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "Verificación completa" -ForegroundColor Cyan