# Documento de Refactorización: Eliminación de Hardcoding (Dynamic AI Control)

Este documento detalla la refactorización arquitectónica que eliminó todos los valores fijos ("hardcoded") y mocks rígidos de las herramientas de PIE, delegando el control absoluto a los asistentes de inteligencia artificial (LLMs como Claude o Antigravity).

## Por qué este cambio es fundamental
Anteriormente, los motores tenían "conocimiento propio" rígido. Por ejemplo, si se pedía una batería "house", el motor en Python internamente escupía un patrón pre-programado. Esto convertía a PIE en un bot tonto. Al eliminar el hardcoding, **el LLM asume la responsabilidad total de la creatividad y las decisiones acústicas**, mientras que PIE vuelve a ser puramente un ejecutor físico (MIDI/DSP).

---

## Cambios por Motor (Engine Refactors)

### 1. MusicEngine (`music_engine.py`)
- **Antes:** Generaba tríadas rígidas en C Minor, rítmicas estáticas de 8vas, y un drum loop pre-programado de "house".
- **Ahora:**
  - `generate_harmony` recibe un array explícito de `chords` (matrices de enteros MIDI), y un array de `durations`.
  - `generate_bass` recibe una lista de enteros MIDI.
  - `generate_drums` recibe un diccionario explícito (`{"kick": [True, False...], "hat": ...}`).
- **Empoderamiento:** El LLM ahora debe usar su propio conocimiento de teoría musical para calcular las disonancias, las inversiones de acordes y los ritmos exactos de batería.

### 2. ArrangementEngine (`arrangement.py`)
- **Antes:** El motor tenía en memoria un diccionario estático de 128 BPM con Intro, Verse, Build, Drop a intervalos rígidos de 16 compases.
- **Ahora:**
  - Se eliminó el diccionario interno.
  - Se introdujo `update_structure()`. El LLM debe leer (o deducir) el proyecto y suministrar dinámicamente un objeto JSON con los `start_beats` y la energía de cada sección de la plantilla activa.

### 3. SoundDesignEngine (`sound_design.py`)
- **Antes:** Contenía tres perfiles fijos ("aggressive_reece_bass", "pluck_house_bass", "ethereal_lead") y buscaba 5 keywords mágicas ("warmth", "brightness", etc).
- **Ahora:**
  - El LLM debe usar `set_semantic_keywords` para enseñarle a PIE qué macros buscar.
  - El LLM usa `add_profile` para crear perfiles dinámicos basándose en el análisis acústico actual del proyecto.
  - El linter de macros ahora acepta `custom_rules` (reglas lógicas dictadas por el LLM en lugar de condicionales fijos de > 0.8 en Python).

### 4. PolicyEngine (`policy_engine.py`)
- **Antes:** Tenía reglas escritas en Python que bloqueaban canales llamados "SUB" si no estaban en mono, o volúmenes mayores a 0.8.
- **Ahora:**
  - El LLM usa `set_rules` pasándole un array de objetos JSON con lógica evaluativa (condición `greater_than`, `less_than`, etc).
- **Empoderamiento:** Permite que las políticas cambien según el género musical. (Ej: en EDM un fader alto es peligroso, en música clásica acústica los faders pueden comportarse distinto).

### 5. DigitalEarEngine (`digital_ear.py`)
- **Antes:** Fase 6 tenía un objetivo de limitador rígido (-9 LUFS). Fase 7 tenía thresholds fijos. Se borraron los comandos "mock" de la Fase 5 y 6 que devolvían strings de texto en vez de procesar sonido.
- **Ahora:** Las funciones `measure_readiness` y `forensics_report` aceptan dinámicamente los objetivos (ej. `target_lufs`) y umbrales proporcionados por la IA.

### 6. ProjectHackerEngine (`project_hacker.py`)
- **Antes:** El intento de inyección de patrones usaba un nombre de patrón estático y falso.
- **Ahora:** La herramienta `inject_pattern` permite al LLM proveer el string exacto y el código de color hexadecimal `0xRRGGBB` para el patrón modificado en la inyección de PyFLP.

---

## Conclusión
La arquitectura PIE está ahora completamente guiada por el Agente. Todas las funciones de las herramientas MCP se han reescrito para no hacer suposiciones. El LLM es el cerebro, y el MCP es únicamente un teclado, ratón y micrófono virtual para FL Studio.
