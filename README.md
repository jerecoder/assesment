# Sistema de Análisis de Paradas de Máquina


## Descripción

El sistema permite a los usuarios hacer preguntas en lenguaje natural sobre los datos de `machine stops`, que se convierten automáticamente en consultas SQL y se ejecutan contra una base de datos SQLite.


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

El sistema se ejecuta a través del notebook `stops_qa.ipynb`, que proporciona una interfaz interactiva.

Para usar el sistema:
- Ingresa tus preguntas en lenguaje natural
- El sistema generará y ejecutará las consultas SQL correspondientes
- Los resultados se mostrarán en formato tabular
- Escribe `exit` para salir

## Ejemplos de Preguntas

- ¿Cuántas paradas ocurrieron el 1 de enero?
- Lista todas las paradas causadas por 'Die Head Cleaning'
- ¿Cuál es la duración promedio de cada tipo de parada?
- ¿Qué hora del día tuvo la duración total de paradas más larga?

## Estructura del Proyecto

```
.
├── README.md
├── requirements.txt
├── stops_qa.py
├── stops_qa.ipynb
├── simulated_stops.csv
├── model.md
└── .env
```

## Decisiones Técnicas

1. **Proveedor LLM**: OpenAI GPT-3.5-turbo
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

4. **Manejo de Errores**:
   - Validación de consultas SQL
   - Manejo de casos sin resultados
   - Logging para debugging

## Documentación

- `model.md`: Documentación detallada del modelo de datos y esquema
- `README.md`: Guía de instalación y uso
- Docstrings en el código: Documentación de funciones y clases

 