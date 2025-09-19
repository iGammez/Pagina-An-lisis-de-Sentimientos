document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias a Elementos del DOM ---
    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');
    const galleryBtn = document.getElementById('gallery-btn');
    const textInput = document.getElementById('text-input');
    const paletteContainer = document.getElementById('palette-container');
    const galleryContainer = document.getElementById('gallery-container');
    const galleryGrid = document.getElementById('gallery-grid');

    const API_URL = 'http://127.0.0.1:8000';

    // --- Lógica para Generar Paleta ---
    const generatePalette = async () => {
        const userText = textInput.value;
        if (!userText.trim()) {
            alert('Por favor, escribe algo para analizar.');
            return;
        }
        paletteContainer.innerHTML = '<div class="loading">Analizando...</div>';
        try {
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: userText }) 
            });
            if (!response.ok) throw new Error('Error en la respuesta del servidor.');
            const data = await response.json();
            paletteContainer.innerHTML = '';
            data.colors.forEach(color => {
                const colorSwatch = document.createElement('div');
                colorSwatch.classList.add('color-swatch');
                colorSwatch.style.backgroundColor = color;
                paletteContainer.appendChild(colorSwatch);
            });
            // Al generar una nueva paleta, actualizamos la galería en segundo plano
            loadGallery();
        } catch (error) {
            console.error("Error al contactar la API:", error);
            paletteContainer.innerHTML = '<div class="error">No se pudo generar la paleta.</div>';
        }
    };

    // --- Lógica de Descarga ---
    const downloadPalette = () => {
        html2canvas(paletteContainer).then(canvas => {
            const link = document.createElement('a');
            link.download = 'mi_paleta_emocional.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        });
    };

    // --- Lógica para la Galería ---
    const loadGallery = async () => {
        try {
            const response = await fetch(`${API_URL}/gallery`);
            if (!response.ok) throw new Error('No se pudo cargar la galería.');
            
            const palettes = await response.json();
            galleryGrid.innerHTML = ''; // Limpiamos la galería antes de cargarla

            palettes.forEach(palette => {
                const card = document.createElement('div');
                card.className = 'gallery-card';

                const miniPalette = document.createElement('div');
                miniPalette.className = 'mini-palette';
                const colors = palette.colors.split(',');
                colors.forEach(color => {
                    const colorDiv = document.createElement('div');
                    colorDiv.style.backgroundColor = color;
                    miniPalette.appendChild(colorDiv);
                });

                const text = document.createElement('p');
                text.textContent = `"${palette.input_text}"`;
                
                const date = document.createElement('small');
                date.textContent = new Date(palette.created_at).toLocaleString();

                card.appendChild(miniPalette);
                card.appendChild(text);
                card.appendChild(date);
                galleryGrid.appendChild(card);
            });
        } catch (error) {
            console.error("Error al cargar la galería:", error);
            galleryGrid.innerHTML = '<p>No se pudieron cargar las paletas.</p>';
        }
    };
    
    // Función para mostrar/ocultar el panel de la galería
    const toggleGallery = () => {
        galleryContainer.classList.toggle('show');
    };

    // --- Asignación de Eventos ---
    generateBtn.addEventListener('click', generatePalette);
    downloadBtn.addEventListener('click', downloadPalette);
    galleryBtn.addEventListener('click', () => {
        loadGallery(); // Carga los datos frescos cada vez que se abre
        toggleGallery();
    });

    // Carga inicial de la galería al entrar a la página
    loadGallery();
});