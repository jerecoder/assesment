## 1. Elección del LLM y Librerías

- **Modelo seleccionado:**  
  Se utiliza `gpt-3.5-turbo` a través de LangChain, usando el wrapper `ChatOpenAI`.

    - Buen balance entre costo, rendimiento y velocidad.
    - Temperatura en `0` para respuestas deterministas.
    - LangChain simplifica el manejo de prompts y la integración con SQLite.
    - Fácil de escalar y mantener.

- **Otras opciones evaluadas:**

  - **LlamaIndex:** Útil con esquemas grandes o distribuidos. No aporta valor en este caso con una única tabla.
  - **Dataherald Engine:** Pensado para entornos productivos complejos. Sobredimensionado para uso local.
  - **Chat2DB:** Enfocado en usuarios finales vía UI gráfica. No se integra bien como componente backend.
  - **Uso directo del API de OpenAI:** Válido, pero LangChain ya resuelve mucho del trabajo manual y permite modularidad.
---

## 2. Inferencia de Esquema y Tipado

- **Definición del esquema:**  
  La tabla `stops` se define explícitamente, tipando correctamente campos de texto, fechas y números reales.

- **Carga de datos:**  
  Se utiliza `pandas` para leer el CSV. Fechas convertidas con `pd.to_datetime()` antes de insertar a SQLite, asegurando consistencia de tipos.

---

## 3. Manejo de Errores y Validaciones

- **Ejecución segura:**  
  `execute_query` ejecuta las consultas y captura excepciones (sintaxis SQL, columnas inexistentes, etc). Los errores se reportan, no crashea.

- **Contención de errores del modelo:**  
  El prompt fuerza al modelo a devolver solo SQL plano, sin comentarios ni explicaciones.  
  Se ajusta a la sintaxis de SQLite, minimizando incompatibilidades o resultados inesperados.

- **Ejemplos:**  
  Los mensajes de sistema indican qué tipo de preguntas se pueden hacer. Si no hay resultados, se devuelve un mensaje simple y claro.
