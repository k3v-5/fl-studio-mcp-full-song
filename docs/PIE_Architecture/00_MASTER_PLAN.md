# 00 MASTER PLAN: Ableton PIE a FL Studio MCP

## 1. Visión General y Filosofía
El objetivo de este proyecto es adaptar y portar la arquitectura del **Production Intelligence Engine (PIE)** originalmente diseñada para Ableton Live hacia **FL Studio**.

Al igual que en Ableton PIE, el sistema se regirá bajo el principio de que la IA (el modelo de lenguaje) decide la "intención musical", mientras que el motor (PIE) central:
- Planifica y valida la viabilidad acústica de la intención.
- Mantiene reglas estrictas de gobernanza (Policies & Guardrails).
- Ejecuta transacciones atómicas de manera segura con verificación de estado.
- Utiliza a FL Studio meramente como un **ejecutor físico y proveedor de estado base**.

## 2. Estado Actual de FL Studio MCP
Actualmente, el repositorio `fl-studio-mcp` proporciona un servidor FastMCP sólido que se comunica con FL Studio a través de un puente bidireccional (MIDI + Archivos JSON).

### **Lo que funciona "Out of the Box" (Fuera de la caja):**
1. **Control de Transporte:** Reproducir, pausar, detener, loop y tempo.
2. **Control de Mezclador:** Volumen, paneo, mute, solo, colores y nombres.
3. **Control de Channel Rack:** Modificación del Step Sequencer (grid bits), ruteo a canales del mixer.
4. **Control de Plugins:** Leer y escribir valores en parámetros existentes (macros/knobs).
5. **Piano Roll:** Escribir notas y acordes en patrones existentes mediante un script secundario invocado por un atajo de teclado (`Ctrl+Alt+Y`).

### **Limitaciones Graves y Blockers en FL Studio API:**
- 🔴 **No se pueden cargar plugins (VST/AU) dinámicamente:** La API de Python de FL Studio no permite instanciar nuevos plugins en el rack.
- 🔴 **No se pueden crear Patrones (Patterns) dinámicamente:** La API de scripting no expone ninguna función para crear nuevos patrones en el Playlist (Arrangement).
- 🔴 **No hay una forma nativa de capturar audio en tiempo real:** Los scripts de Python se ejecutan dentro del hilo de interfaz/MIDI, no tienen acceso a los buffers de audio (DSP).

## 3. Workarounds y Soluciones Propuestas (El Enfoque "Template-Driven")
Para replicar las capacidades de Ableton PIE sorteando los blockers de FL Studio, la arquitectura dependerá fuertemente de una **Plantilla Maestra de FL Studio (`.flp`) pre-configurada**.

1. **Gestión de Instrumentos y Sonidos:**
   - En lugar de cargar VSTs dinámicamente, la plantilla maestra contendrá un "Pool" de canales pre-cargados (ej. 10 sintes, un Drum Machine, bajos, etc.) ruteados a canales de mezcla específicos.
   - PIE asignará ("mapeará") las intenciones musicales a los canales disponibles basándose en el inventario que reporta el servidor.

2. **Gestión de Arreglo (Arrangement) y Patrones:**
   - La plantilla debe contener un número grande de patrones pre-creados (ej. Pattern 1 al 50) e insertados en el Playlist simulando una macro-estructura (Intro, Verse, Build, Drop).
   - PIE no creará patrones, sino que *mutará el contenido MIDI* dentro de esos bloques pre-ubicados utilizando las herramientas de Piano Roll y Step Sequencer.
   - Las automatizaciones (LOM equivalentes) se simularán enviando CCs MIDI a parámetros vinculados previamente en la plantilla, o modificando los `Event Data` si la API lo permite.

3. **Digital Ear y Captura de Audio:**
   - Para las fases de análisis DSP, mezcla y mastering, se desarrollará o utilizará un **Plugin VST Interceptor** (Audio Relay/Spy) colocado en el Master de FL Studio.
   - Este plugin enviará los buffers de audio directamente al servidor PIE en Python a través de sockets UDP/TCP o memoria compartida para ser procesados con `numpy` y `librosa`.

## 4. Fases de Desarrollo (Blueprint)

El desarrollo del PIE Engine para FL Studio se dividirá en las siguientes fases (cada una detallada en su propio documento técnico):

- **Fase 1 (Foundation):** Construcción del Shadow Graph, motor de Gobernanza y sistema de Transacciones y Snapshots usando las limitaciones actuales.
- **Fase 2 (Music Engine):** Adaptación del sistema de teoría musical, generadores de armonía, bajos, y baterías utilizando el protocolo de Piano Roll (JSON + Hotkey) del servidor actual.
- **Fase 3 (Arrangement):** Orquestación de macro-estructura basada en el workaround de "Plantilla de Patrones Fijos" y creación de curvas de energía musical.
- **Fase 4 (Sound Design):** Creación de perfiles tímbricos usando "Semantic Macros" mapeados a Patcher o al Control Surface de FL Studio.
- **Fase 5, 6 y 7 (Audio DSP, Mix, Mastering & Forensics):** Integración del "Digital Ear" usando un VST interceptor y análisis offline/online con librosa para solucionar choques de frecuencia y normativas de Loudness.

## 5. Resumen y Siguientes Pasos
El núcleo lógico del "PIE" (políticas, grafos causales, inteligencia musical) es casi 100% independiente del DAW y vivirá en el servidor `FastMCP`. El esfuerzo de esta adaptación radicará en construir la lógica adaptadora (`Adapter`) que traduzca las abstracciones de PIE a los comandos MIDI/JSON que actualmente soporta `fl-studio-mcp`, e instituir el paradigma de **"Plantillas Inteligentes"** para superar las restricciones de la API.
