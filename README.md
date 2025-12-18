Aquí tienes una propuesta completa y profesional para tu archivo README.md. Está diseñado para que cualquier persona entienda qué hace el proyecto, cómo instalarlo y cómo usarlo.

Puedes copiar y pegar este contenido directamente en GitHub.

🇨🇱 Scraper de Mociones - Cámara de Diputadas y Diputados de Chile
Este proyecto es una herramienta de automatización escrita en Python que extrae, analiza y visualiza la actividad legislativa de los parlamentarios chilenos desde el sitio web oficial de la Cámara de Diputadas y Diputados.

Utiliza Playwright para navegar e interactuar con la compleja estructura del sitio (ASP.NET WebForms, UpdatePanels) y Matplotlib/Pandas para generar estadísticas visuales sobre el éxito de los proyectos de ley.

🚀 Características
Extracción Automática: Recorre todos los años disponibles en la ficha del parlamentario sin intervención manual.

Manejo de ASP.NET: Interactúa correctamente con los eventos __doPostBack y esperas de red (networkidle) para asegurar la carga de datos.

Datos Completos: Extrae proyectos tanto Admisibles como Inadmisibles.

Contexto Parlamentario: Detecta y extrae los periodos en los que el diputado ha ejercido.

Visualización de Datos: Genera automáticamente dos gráficos de alta calidad:

📊 Gráfico de Barras: Cantidad de proyectos por estado (En tramitación, Publicado, Archivado, etc.).

🍰 Gráfico Circular: Distribución porcentual de la efectividad legislativa.

Resiliencia: Incluye manejo de errores para tiempos de espera y URLs inválidas.

📋 Requisitos Previos
Python 3.8 o superior.

Conexión a internet estable (el script navega en tiempo real).

🛠️ Instalación
Clona este repositorio:

Bash

git clone https://github.com/tu-usuario/camara-scraper.git
cd camara-scraper
Crea un entorno virtual (Opcional pero recomendado):

Bash

python -m venv venv
source venv/bin/activate  # En Mac/Linux
venv\Scripts\activate     # En Windows
Instala las dependencias:

Bash

pip install pandas matplotlib playwright
Instala los navegadores de Playwright: Este paso es crucial para que el script funcione.

Bash

playwright install chromium
💻 Uso
Ejecuta el script principal:

Bash

python camara_completo.py
El programa te solicitará la URL de la ficha del diputado.

Ejemplo de URL válida: https://www.camara.cl/diputados/detalle/mociones.aspx?prmID=948

Espera el proceso:

Verás en la consola cómo el script recorre año por año.

Al finalizar, se generarán dos archivos de imagen en la carpeta del proyecto.

📊 Resultados (Ejemplo)
El script generará los siguientes archivos en tu directorio local:

proyectos_barras.png: Muestra el volumen total de mociones agrupadas por su estado actual.

proyectos_torta.png: Muestra el porcentaje de éxito o archivo de las iniciativas.

📂 Estructura del Proyecto
Plaintext

camara-scraper/
├── camara_completo.py    # Script principal
├── README.md             # Documentación
├── proyectos_barras.png  # Output generado (Ejemplo)
└── proyectos_torta.png   # Output generado (Ejemplo)
⚠️ Aviso Legal
Este software ha sido desarrollado con fines educativos y de análisis de datos públicos. La estructura del sitio web camara.cl puede cambiar sin previo aviso, lo que podría requerir actualizaciones en los selectores del script.

Se recomienda utilizar esta herramienta de manera responsable, respetando los términos de servicio del sitio web gubernamental.

📄 Licencia
Este proyecto está bajo la Licencia MIT - eres libre de usarlo y modificarlo.
