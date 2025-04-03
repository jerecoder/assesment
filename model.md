## 1. Elección del LLM y Librerías

- **Modelo seleccionado:**  
  Se utiliza LangGraph's ReAct Agent para responder preguntas que requieren ejecutar consultas SQL sobre una base de datos estructurada.

    - Prompt templates para facilitar interaccion.
    - Integracion simple.
    - Modular

- **Otras opciones evaluadas:**

| Opción | Capacidades relevantes | Memoria de diálogo | Comentario |
|--------|------------------------|---------------------|------------|
| **LangChain** | Prompt templates para SQL, o agente ReAct con herramienta SQL. Validación de queries y manejo de errores. Compatible con cualquier DB SQLAlchemy. | Sí, incluye memoria integrada. | Completo pero más pesado y generalista. |
| **LlamaIndex** | SQL vía `NLSQLQueryEngine`, puede usar RAG para schema. Fácil de encadenar con otros pasos. | Parcial, puede integrarse con motores de diálogo. | Útil si se mezcla SQL con texto no estructurado. |
| **Semantic Kernel** | Prompting o function-calling usando skill SQL. Evita mover datos; sólo usa el esquema. | Sí, con variables de contexto y planners. | Flexible, pensado para entornos enterprise. |
| **HF Transformers Agents** | Agente estilo ReAct con herramientas Python personalizadas. Stack open-source. | Limitada (por ejecución); el usuario gestiona la memoria. | Ideal si se usa un modelo local. |
| **Microsoft AutoGen** | Sistema multi-agente (planificador y agentes especializados, incluyendo SQL). | Sí, diseñado para diálogo multi-turno. | Muy flexible pero complejo de integrar. |

---

## 2. Inferencia de Esquema y Tipado

- **Definición del esquema:**
  Tabla `stops` con campos de texto, fechas y números reales, tipados explícitamente.

- **Carga de datos:**
  Uso de `pandas` para leer CSV y convertir fechas con `pd.to_datetime()` antes de insertar en SQLite.

---

## 3. Manejo de Errores y Validaciones

- **Ejecución segura:**
  `execute_query` captura excepciones SQL sin detener el sistema.

- **Validación del modelo:**
  Prompt estricto: solo SQL plano, sin explicaciones. Compatible con SQLite.

- **Mensajes claros:**
  Se informa si no hay resultados o si hay errores de entrada.

---

## Modelo de Datos y Esquema

```sql
CREATE TABLE stops (
    stop_id TEXT PRIMARY KEY,
    stop_type_id TEXT,
    stop_type_name TEXT,
    start_at DATETIME,
    ends_at DATETIME,
    duration_minutes REAL
)
```

### Campos

- `stop_id`: ID único (TEXT, PRIMARY KEY)
- `stop_type_id`: ID de tipo (TEXT)
- `stop_type_name`: Nombre del tipo (TEXT)
- `start_at` / `ends_at`: Fechas de inicio y fin (DATETIME)
- `duration_minutes`: Duración en minutos (REAL)

---

## Conversión de Tipos

- Fechas (`start_at`, `ends_at`) convertidas a `datetime` con formato ISO 8601.
- `duration_minutes` calculado como diferencia de tiempo.

---

## Integración con LangGraph ReAct Agent

- **Modelo:** LangGraph ReAct Agent
  - Generación de SQL desde preguntas en lenguaje natural.
  - Compatible con flujos interactivos React.


- **Validación:**
  Verificación previa a la ejecución, manejo de errores SQL, y validación de sintaxis.

---

## Ejemplos de Consultas

1. **Conteo de Paradas**:
   ```sql
   SELECT COUNT(*) FROM stops WHERE DATE(start_at) = '2025-01-01';
   ```

2. **Duración Promedio por Tipo**:
   ```sql
   SELECT stop_type_name, AVG(duration_minutes) as avg_duration
   FROM stops
   GROUP BY stop_type_name;
   ```

3. **Paradas por Hora**:
   ```sql
   SELECT strftime('%H', start_at) as hour,
          SUM(duration_minutes) as total_duration
   FROM stops
   GROUP BY hour
   ORDER BY total_duration DESC;
   ```

---

## Consideraciones de Rendimiento

- `stop_id` indexado (PRIMARY KEY).
- Tipos de datos apropiados y conversiones eficientes.
- SQLite es adecuado para volúmenes moderados.
- Arquitectura permite agregar campos sin romper compatibilidad.

