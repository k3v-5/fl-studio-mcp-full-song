# Fase 2 & 2.5: Music Engine & Instruments (FL Studio)

Esta fase se encarga de la teoría musical, la rítmica y la armonía. Es el motor generativo que traduce las intenciones de alto nivel ("Haz un drop de tech house") a eventos MIDI concretos.

## 1. Adaptación a FL Studio MCP
La mayor ventaja de esta fase es que toda la lógica de **Teoría Musical** (escalas, acordes, duraciones, humanización de timing/velocidad) puede vivir completamente dentro del servidor FastMCP (Python) sin depender del DAW.

El `Music Engine` generará arrays de diccionarios (eventos MIDI), y el adaptador simplemente traducirá estos arrays a las llamadas que soporta el puente JSON de FL Studio (`fl_send_notes`).

### El Reto de la Sincronización (Hotkey vs API nativa)
Actualmente en `fl-studio-mcp`, enviar notas requiere generar un JSON y presionar `Ctrl+Alt+Y` para disparar el script `ComposeWithLLM.pyscript`.
- **Estrategia:** Para evitar que la UI salte constantemente durante la generación de múltiples partes (bajo, batería, melodía), el `Music Engine` compilará un "Mega-JSON" con los cambios de todas las pistas, o en su defecto, iterará rápidamente manejando las esperas (timeouts) del puente.
- Para baterías rápidas o sin swing complejo, se priorizará usar `fl_set_grid_bit` (Step Sequencer) que funciona vía MIDI sin requerir el hotkey de Piano Roll.

## 2. Herramientas Propuestas (FastMCP Tools)

- `music_generate_harmony(scale, chord_progression, length)`: Genera el MIDI y llama a `fl_send_chord`.
- `music_generate_bass(rhythm_pattern, root_notes)`: Genera línea de bajo.
- `music_generate_drums(genre, intensity)`: Utiliza `fl_set_grid_bit` en canales ruteados como Drum Machine en el Template.
- `music_generate_melody(scale, range, motif)`: Genera y mapea a `fl_send_notes`.
- `music_humanize(target_channel, velocity_variance, timing_variance)`: Lee (`fl_get_piano_roll_state`), aplica ruido pseudo-aleatorio gaussiano a los tiempos/velocidades, y re-escribe el patrón.

## 3. Manejo de Instrumentos ("Pool Mapping")
Dado que no podemos cargar VSTs con la API:
1. Al iniciar la sesión, el motor escanea los canales (`fl_get_all_channels`).
2. PIE espera que los nombres de los canales sigan una convención (ej. "PIE_BASS_1", "PIE_LEAD_2", "PIE_DRUMS").
3. Si el motor decide que necesita un Sub-Bajo, mapeará la salida de `music_generate_bass` al canal `PIE_BASS_1` o `PIE_SUB_1`.
