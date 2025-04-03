# Sistema de Análisis de Paradas de Máquina


## Descripción

El sistema permite a los usuarios interactuar con un agente que responde preguntas sobre machine stops.


## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/jerecoder/assesment.git
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar las variables de entorno:
   - Crear un archivo `.env` en el directorio raíz
   - Agregar tu clave API de OpenAI:
     ```
     OPENAI_API_KEY=tu-clave-api
     ```

## Uso

Ejecutar el archivo stops_qa.py

## Características

- **Interfaz Interactiva**: Preguntas en lenguaje natural
- **Caché Inteligente**: Almacena y reutiliza consultas frecuentes
- **Visualización Clara**: Resultados en formato tabular
- **Manejo de Errores**: Validación y mensajes claros

## Ejemplos de Preguntas

- ¿Cuántas paradas ocurrieron el 1 de enero?
- Lista todas las paradas causadas por 'Die Head Cleaning'
- ¿Cuál es la duración promedio de cada tipo de parada?
- ¿Qué hora del día tuvo la duración total de paradas más larga?


## Decisiones Técnicas

1. **Proveedor LLM**: OpenAI GPT-3.5-turbo + LangChain/Graph
   - Excelente rendimiento en tareas de generación de SQL
   - Cost-effective 

2. **Base de Datos**: SQLite
   - Almacenamiento local y simplicidad
   - No requiere configuración adicional
   - Ideal para datos de tamaño moderado

3. **Interfaz de Usuario**: Rich
   - Interfaz interactiva y amigable
   - Visualización clara de resultados
   - Formato mejorado para la terminal


## Documentación

- `model.md`: Documentación detallada del modelo de datos y esquema
- `README.md`: Guía de instalación y uso
- Docstrings en el código: Documentación de funciones y clases


 