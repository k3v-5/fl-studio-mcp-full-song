# Hito 1: Gobernanza, Causal Memory y Policy Engine (FL Studio)

Este documento detalla la implementación del núcleo de toma de decisiones (PIE Brain) para el entorno FL Studio MCP.

## 1. El Grafo Causal (Production Graph)
A diferencia de un script imperativo simple, PIE utiliza un Grafo Causal Aclíclico para modelar las intenciones del usuario, las decisiones de la IA y el estado resultante.

### Implementación Técnica
- **Ubicación:** Dentro del servidor FastMCP (Python 3.10+). Se creará una estructura en memoria (`NetworkX` o diccionario anidado) que relacione cada nodo.
- **Nodos:**
  - `IntentNode`: Lo que pide el usuario ("Haz un bajo agresivo").
  - `PlanNode`: La descomposición de PIE ("1. Seleccionar track de bajo, 2. Bajar octava, 3. Añadir saturador").
  - `ActionNode`: La llamada real a las Tools de MCP (`fl_set_plugin_param_value`, `fl_send_notes`).
  - `VerificationNode`: La confirmación del nuevo estado.
- **Trazabilidad:** Cada acción ejecutada a través del puente MIDI de FL Studio se asocia a su nodo causal, permitiendo usar la herramienta `production_explain`.

## 2. Decision Memory
El servidor FastMCP mantendrá un log en disco (`sqlite` o `JSON lines`) de qué combinaciones de parámetros (hasheados) produjeron resultados que el Policy Engine aprobó acústicamente. No auto-ejecuta, pero provee contexto a la IA en futuras sesiones.

## 3. Policy Engine (Guardarraíles)
El Policy Engine se implementará como un decorador o un middleware antes de que los comandos MIDI de FL Studio sean despachados.

### Ejemplos de Políticas Restrictivas
- **Volumen (Gain Staging):** Si se pide un `fl_set_track_volume` por encima de 0dBFS (80% en la escala interna de FL), el Policy Engine lo bloquea y devuelve un error causal (obligando a la IA a replanear y usar compresión en vez de subir el fader principal).
- **Safe Panning:** Los sub-bajos (frecuencias inferiores a 100Hz detectadas teóricamente por el instrumento seleccionado) no pueden tener un `fl_set_track_pan` diferente de 0% (Mono estricto).
- **Polyphony Overlap:** Antes de un `fl_send_notes`, el motor valida que el instrumento de destino pueda manejar la polifonía, evitando choques de fase destructivos.

## 4. API de Herramientas Propuestas (FastMCP)
Estas herramientas se añadirán al `server.py` actual:
- `production_status()`: Devuelve el nodo actual y el estado del Grafo Causal.
- `production_plan(intent)`: Somete una intención para su análisis causal.
- `production_validate(plan_id)`: Pasa el plan por el Policy Engine.
- `production_execute(plan_id)`: Ejecuta las acciones en FL Studio y bloquea si alguna falla.
- `production_rollback(plan_id)`: Invoca la reversión (ver Fase 1 Foundation).
