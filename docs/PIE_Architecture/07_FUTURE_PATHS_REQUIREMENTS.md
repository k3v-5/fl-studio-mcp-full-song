# Documento de Requerimientos Técnicos: Rutas de Expansión (Future Paths)

Este documento detalla exhaustiva y quirúrgicamente los requerimientos, la arquitectura y las tareas para las tres rutas de expansión de PIE en FL Studio. El objetivo de estas fases es romper las limitaciones nativas de la API de FL Studio (sandbox de Python) y lograr una integración de nivel de producción profesional.

Estas rutas se desarrollarán de manera iterativa y progresiva.

---

## Camino 1: Integración MIDI y Piano Roll Real (Conexión Lógica-Física)

**Objetivo:** Conectar los motores de inteligencia musical (`MusicEngine` y `ArrangementEngine`) que actualmente devuelven JSON simulado, con el puente físico de FL Studio (`fl_send_notes`) para inyectar las notas generadas directamente en los clips del Playlist (basado en el Smart Template).

### 1.1 Arquitectura y Flujo de Datos
1. **Intención:** El usuario envía "Genera un drop de House en el compás 33".
2. **Generación (FastMCP):** `ArrangementEngine` calcula los offsets temporales. `MusicEngine` genera listas de diccionarios con `[note, time, duration, velocity]`.
3. **Orquestación (Adapter):** Un nuevo adaptador intercepta esta salida.
4. **Ejecución (FL Studio Bridge):** El adaptador itera sobre los canales objetivo y ejecuta la herramienta `fl_send_notes`.
5. **UI Automation Trigger:** Como la API de FL Studio requiere una acción del usuario para disparar scripts de Piano Roll (`ComposeWithLLM`), el servidor `FastMCP` ejecutará una macro nativa del sistema operativo (`pyautogui` o `pynput` ya presentes) para presionar `Ctrl+Alt+Y` de forma imperceptible para inyectar los JSON cacheados a FL Studio.

### 1.2 Requerimientos Técnicos
- **`fl_trigger.py` Enhancement:** Mejorar el módulo actual que presiona `Ctrl+Alt+Y` para manejar ráfagas (bursts) de comandos de manera asíncrona sin bloquear o crashear FL Studio.
- **Queue System (Cola de Tareas):** Dado que modificar 5 pistas requiere 5 inyecciones al Piano Roll, PIE debe encolar las peticiones de escritura y disparar el hotkey secuencialmente con un `timeout` (ej. 200ms) para respetar el hilo de UI de FL Studio.

### 1.3 Lista de Tareas (Milestone 1)
- [ ] Tarea 1.1: Refactorizar `MusicEngine.generate_*` para asegurar que el output coincida 1:1 con el schema JSON que espera el script `ComposeWithLLM.pyscript` de FL Studio.
- [ ] Tarea 1.2: Construir el `MIDIAdapter` que toma las notas del `ArrangementEngine`, setea el track seleccionado (`fl_select_channel`), guarda el JSON, y dispara `fl_trigger_script`.
- [ ] Tarea 1.3: Escribir tests de estrés para verificar que el envío rápido de atajos de teclado no rompa el foco de la ventana del DAW en Windows/Mac.

---

## Camino 2: Digital Ear - VST Audio Interceptor (DSP Real)

**Objetivo:** FL Studio ejecuta el scripting en el hilo de interfaz, sin acceso al flujo de audio (DSP). Para la mezcla (Fase 5), mastering (Fase 6) y análisis forense (Fase 7), necesitamos construir un plugin VST que actúe como un "Espía de Audio".

### 2.1 Arquitectura y Flujo de Datos
1. **Plugin C++/Rust:** Se desarrolla un plugin VST3 ultraligero sin interfaz gráfica (GUI) usando frameworks como JUCE (C++) o `nih-plug` (Rust).
2. **Posición:** Se inserta manualmente en el Master de FL Studio dentro de la Smart Template.
3. **IPC (Inter-Process Communication):** El VST lee los buffers (frames) de audio (`float32` arrays) y los envía a un socket TCP local (ej. `localhost:9878`) usando ZeroMQ o WebSockets, o en su defecto los escribe a un bloque de *Shared Memory*.
4. **Receptor Python (FastMCP):** `DigitalEarEngine` se conecta al socket TCP/Shared Memory, captura el stream de `float32` y lo convierte a un array de `numpy`.
5. **Análisis DSP:** Se utiliza `librosa` para transformar el dominio temporal a espectral (FFT), detectar resonancias cruzadas (masking) y medir LUFS (norma ITU-R BS.1770) con la librería `pyloudnorm`.

### 2.2 Requerimientos Técnicos
- **Desarrollo de VST Externo:** Requiere conocimientos de C++ (JUCE) o Rust, y compilación cruzada para Windows (.vst3) y macOS (.vst3/.component).
- **Python DSP Stack:** Dependencias fuertes en `numpy`, `scipy`, `librosa` y `pyloudnorm`.
- **Rendimiento (CPU):** La captura de audio debe ejecutarse en un hilo secundario (Background Worker) dentro de FastMCP para no bloquear la respuesta de la IA.

### 2.3 Lista de Tareas (Milestone 2)
- [ ] Tarea 2.1: Diseñar y compilar el VST3 "PIE_Audio_Relay" (JUCE/Rust) con un servidor ZeroMQ PUB/SUB básico.
- [ ] Tarea 2.2: Implementar el hilo de escucha (Sub socket) dentro de `src/fl_studio_mcp/pie/digital_ear.py`.
- [ ] Tarea 2.3: Integrar `pyloudnorm` en `measure_readiness` para calcular Integrated LUFS y True Peak reales basados en el buffer recibido.
- [ ] Tarea 2.4: Escribir el algoritmo de detección de masking (Peak comparison en bandas de 50-200Hz).

---

## Camino 3: Inyección Binaria con PyFLP (El Hack Definitivo)

**Objetivo:** Sobrepasar la mayor limitación de la API de FL Studio (no poder crear patrones nuevos ni cargar plugins) editando directamente el archivo `.flp` guardado del proyecto.

### 3.1 Arquitectura y Flujo de Datos
1. La IA evalúa que necesita crear 3 patrones completamente nuevos o instanciar un sintetizador Serum (algo imposible vía MIDI).
2. PIE solicita al usuario (o vía simulación de teclado `Ctrl+S`) que guarde el proyecto.
3. El servidor FastMCP, utilizando la librería open-source `pyflp` (o una herramienta CLI escrita a medida), lee el archivo binario `.flp`.
4. **Mutación Binaria:** PIE inyecta los `EventData` (creando un PatternBlock) o añade un `PluginEntry` en la estructura binaria del Rack.
5. Guarda el archivo `.flp` y notifica al usuario: "He creado 3 patrones nuevos y cargado Serum. Por favor, pulsa `F12` (Revert to last save) o File > Revert to last backup en FL Studio".

### 3.2 Riesgos Críticos y Requerimientos
- **Riesgo de Corrupción (Alto):** Manipular archivos `.flp` (archivos binarios propietarios de Image-Line) es extremadamente peligroso. Un byte mal colocado corromperá el archivo.
- **Mitigación:** PIE **SIEMPRE** debe crear un clon exacto (Backup) del `.flp` original antes de inyectar datos usando el sistema de Transacciones de la Fase 1 (`transactions.py`).
- **Investigación de PyFLP:** Se debe auditar la capacidad actual de `pyflp` en GitHub para asegurar que soporta la mutación (escritura) de los FLPs creados en FL Studio 21/24, no solo lectura.

### 3.3 Lista de Tareas (Milestone 3)
- [ ] Tarea 3.1: Instalar y auditar `pyflp` (`pip install pyflp`).
- [ ] Tarea 3.2: Escribir un script de pure-python separado (`flp_sandbox.py`) que cargue un proyecto vacío e intente insertar un clip dummy.
- [ ] Tarea 3.3: Integrar la lógica exitosa al `TransactionManager` para manejar los backups del proyecto, asegurando 100% de reproducibilidad sin pérdida de datos del usuario.
- [ ] Tarea 3.4: Crear la herramienta `project_inject_pattern` y exponerla vía FastMCP.

---

## Resumen del Plan de Despliegue

La recomendación quirúrgica para minimizar la fricción del usuario y maximizar el impacto de la IA en FL Studio es ejecutar las fases en el siguiente orden:

1. **Camino 1 (Integración MIDI):** Es el más directo. Utiliza la infraestructura ya construida (Smart Templates y Piano Roll JSON). Su riesgo es bajo y el valor inmediato es masivo (generación de acordes y bases audibles en tiempo real).
2. **Camino 2 (VST Digital Ear):** Un poco más complejo por la necesidad de código compilado, pero fundamental para que PIE pueda "mezclar" y hacer "mastering" de forma verídica y no como un "juguete ciego".
3. **Camino 3 (PyFLP):** Debe tratarse como un proyecto de I+D (Research & Development). Es el Santo Grial porque independizaría a PIE de las templates, pero el riesgo técnico (corrupción de archivos) es severo.