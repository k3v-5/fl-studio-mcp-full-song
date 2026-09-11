# Documentación Técnica de FL Studio MCP

## 1. Introducción
**fl-studio-mcp** es un servidor Model Context Protocol (MCP) que permite a los asistentes de inteligencia artificial controlar FL Studio de Image-Line de forma programática. El proyecto logra esto actuando como un puente bidireccional entre el cliente de IA (como Claude o Cursor) y FL Studio a través de controladores MIDI virtuales, archivos JSON y scripts dentro de FL Studio (Keystroke triggers).

Este documento detalla a fondo el funcionamiento, la arquitectura subyacente y las herramientas de desarrollo implementadas en este sistema.

---

## 2. Arquitectura General

El proyecto utiliza una arquitectura híbrida para saltarse las limitaciones de automatización externa de FL Studio. Se compone de dos mecanismos principales de comunicación:

1. **MIDI + JSON (Control en tiempo real):**
   - Utilizado para Transporte, Mezclador (Mixer), Rack de canales (Channels) y manipulación de Plugins.
   - El servidor MCP escribe los comandos en un archivo `mcp_command.json`.
   - Se envía un disparador o "trigger" MIDI (Nota 127) a través de un puerto virtual (IAC Driver en Mac / loopMIDI en Windows).
   - El script `device_FLStudioMCP.py` integrado como controlador de FL Studio escucha esta nota, lee el archivo JSON, ejecuta la API de FL Studio (módulos `transport`, `mixer`, `channels`, `plugins`) y escribe el resultado en `mcp_response.json`.
   - El servidor MCP espera, lee la respuesta y devuelve el resultado al cliente IA.

2. **Piano Roll Scripts (JSON + Keystroke Trigger):**
   - Utilizado para añadir, eliminar o limpiar notas en el Piano Roll de manera persistente.
   - El servidor guarda una lista de comandos y notas en `mcp_request.json`.
   - Se ejecuta un evento de teclado del sistema operativo (Cmd+Opt+Y en Mac, Ctrl+Alt+Y en Windows) para disparar el script `ComposeWithLLM.pyscript` dentro de la interfaz activa de FL Studio.
   - Dicho script procesa los comandos alterando la partitura interna mediante la API `flpianoroll`, y luego exporta todo el estado a `piano_roll_state.json`.

---

## 3. Componentes del Sistema

### 3.1. Servidor FastMCP (`src/fl_studio_mcp/server.py`)
Punto de entrada de la aplicación que inicializa el servidor MCP con la librería `fastmcp`. Expone información y define los recursos (estado y proyecto) y registra las herramientas (tools) empaquetadas en la carpeta `tools/`.

### 3.2. Scripts de FL Studio
- `fl_controller/device_FLStudioMCP.py`: Script cargado en el Hardware de FL Studio que habilita el soporte al controlador MIDI virtual y reacciona al evento `OnMidiMsg(event)`. Expone rutinas para interactuar con canales, mixer, transporte y plugins usando la API nativa `flapi`.
- `scripts/ComposeWithLLM.pyscript`: Script del entorno "Piano roll scripts" que debe lanzarse desde FL Studio. Trabaja leyendo solicitudes y operando sobre el grid musical con el módulo local `flpianoroll`.

### 3.3. Utils (Manejo de conexión)
- `utils/midi_connection.py`: Envuelve la funcionalidad de la librería `mido` para encontrar puertos MIDI virtuales, enviar las notas trigger de sincronización y gestionar la lectura/escritura de los JSON de comandos con timeout.
- `utils/fl_trigger.py`: Módulo multiplataforma (`pynput` u osascript) para desencadenar eventos de teclado hacia el cliente de FL Studio y accionar el script de Piano Roll.

---

## 4. Referencia Detallada de Herramientas (Tools API)

El servidor expone herramientas categorizadas. Estas pueden ser llamadas directamente por el asistente de IA:

### 4.1. Conexión (`server.py`)
- `fl_connect`: Reconecta o inicializa la conexión con FL Studio por MIDI.
- `fl_connection_status`: Entrega los detalles y estado del puerto MIDI actual.

### 4.2. Transporte (`transport.py`)
- `fl_play` / `fl_stop`: Controla la reproducción.
- `fl_record`: Activa/desactiva la grabación.
- `fl_get_transport_status`: Retorna un diccionario con detalles del estado de reproducción actual y si el modo de bucle (loop) está en "pattern" o "song".
- `fl_set_song_position`: Establece la posición de reproducción usando diversos formatos de tiempo o métricas.
- `fl_get_song_length`: Obtiene la duración del patrón o pista.
- `fl_set_loop_mode`: Cambia entre modo patrón (pattern) o canción (song).
- `fl_set_playback_speed`: Multiplicador de velocidad (0.25x a 4.0x).

### 4.3. Mezclador / Mixer (`mixer.py`)
- `fl_get_mixer_track_count`: Obtiene el número total de pistas (habitualmente 125, donde el 0 es el Master).
- `fl_get_mixer_track_info` / `fl_get_all_mixer_tracks`: Lectura de parámetros como paneo, volumen (en float y dB), color y ruteo de cualquier pista.
- `fl_set_track_volume` / `fl_set_track_pan`: Permite modificar la ganancia (0.0 a 1.25) o paneo (-1.0 a 1.0).
- `fl_mute_track` / `fl_solo_track` / `fl_arm_track`: Alterna estados de la pista para ser silenciada, puesta en solo o armada para grabación.
- Modificaciones visuales y estéreo a través de `fl_set_track_name`, `fl_set_track_color` y `fl_set_stereo_separation`.

### 4.4. Rack de Canales / Channels (`channels.py`)
- `fl_get_channel_count` / `fl_get_channel_info` / `fl_get_all_channels`: Listado y metadatos de los instrumentos creados en el rack de canales.
- `fl_select_channel` / `fl_select_one_channel` / `fl_get_selected_channel`: Selección de canales en la interfaz.
- **Acciones Rápidas / MIDI:**
  - `fl_trigger_note`: Envía un note-on MIDI en tiempo real a un canal (las notas no persisten en el patrón a menos que se esté grabando).
- **Control de Secuenciador de Pasos (Step Sequencer):**
  - `fl_get_grid_bit` / `fl_set_grid_bit`: Activa o desactiva pasos individuales (útil para percusión).
  - `fl_get_step_sequence` / `fl_set_step_sequence`: Permite introducir patrones completos mediante arreglos booleanos (arrays de True/False).
- Control de mezcla a través de `fl_set_channel_volume`, `fl_set_channel_pan`, `fl_route_channel_to_mixer`.

### 4.5. Plugins (`plugins.py`)
**Importante:** Solo es posible manipular plugins ya insertados. No se puede instanciar nuevos plugins.
- `fl_is_plugin_valid` / `fl_get_plugin_name`: Valida si existe un plugin en un índice de canal o un slot de efectos de una pista del mixer.
- `fl_get_plugin_param_count` / `fl_get_plugin_params`: Lista la cantidad de parámetros automatizables y sus valores actuales (limitado a 50 parámetros por defecto por eficiencia).
- `fl_get_plugin_param_value` / `fl_set_plugin_param_value`: Lee o modifica valores de síntesis o efectos internos de los plugins.
- `fl_next_preset` / `fl_prev_preset`: Navegación de ajustes preestablecidos del plugin.

### 4.6. Piano Roll (`piano_roll.py`)
**Importante:** El script requiere confirmación inicial en la interfaz y permiso del sistema operativo (accesibilidad).
- `fl_send_notes`: Toma una lista de diccionarios (con midi, duracion, tiempo, velocidad) y los pone en cola. Un `mode="replace"` puede usarse para limpiar notas anteriores antes de añadir nuevas.
- `fl_send_chord`: Agrega un acorde completo enviando una lista de notas MIDI simultáneas en un tiempo específico.
- `fl_delete_notes` / `fl_clear_piano_roll`: Permite vaciar el entorno del piano roll.
- `fl_get_piano_roll_state`: Lee el archivo `piano_roll_state.json` el cual expone todas las notas existentes actualizadas.
- `fl_trigger_script` / `fl_clear_request_queue`: Métodos manuales para enviar el atajo del teclado (ej: Cmd+Opt+Y) o limpiar el archivo de la cola en caso de fallos.

---

## 5. Limitaciones Técnicas y Consideraciones

1. **Gestión de Instancias de Plugins:**
   No se puede programar la carga de plugins AU/VST directamente desde el servidor. Una arquitectura de "Plantillas Inteligentes" (Smart Templates) usando proyectos `.flp` preconfigurados es la solución recomendada.

2. **Creación Dinámica de Patrones:**
   FL Studio no cuenta con API para crear nuevos patrones al vuelo. Las notas deben insertarse sobre el patrón activo actualmente abierto en la interfaz.

3. **Restricciones del Teclado (Piano Roll):**
   Ya que Python no puede disparar directamente los scripts del piano roll de forma nativa a través de sockets o MIDI, la aplicación simula un atajo de teclado físico (Keystroke). En Windows, esto requerirá temporalmente dar foco a la ventana de FL Studio, interrumpiendo brevemente al usuario. Si el usuario no tiene FL Studio en primer plano o maximizado, el script podría fallar requiriendo un disparador manual.

4. **Entorno y Puertos Virtuales:**
   El controlador depende obligatoriamente de buses MIDI Virtuales (IAC Driver / loopMIDI). Si estos buses se desconectan o el sistema entra en suspensión temporal, la IA debe usar la herramienta `fl_connect` para forzar un reinicio del contexto.