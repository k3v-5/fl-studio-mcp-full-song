# Fase 1: Foundation y Sistema Transaccional (FL Studio)

Para que el modelo IA tome decisiones precisas, necesita estar seguro del estado actual de FL Studio sin tener que consultar todos los parámetros del proyecto antes de cada movimiento. Aquí entra el "Shadow Graph" y las transacciones.

## 1. Shadow Graph (Sincronización de Estado)
El Shadow Graph es una copia en memoria dentro de FastMCP del estado de FL Studio (pistas, volúmenes, plugins, notas en el piano roll).

### Estrategia de Sincronización
- **Polling Híbrido:** FL Studio no notifica activamente sobre todos los cambios. Por ello, el Shadow Graph utilizará las funciones existentes como `fl_get_all_mixer_tracks`, `fl_get_all_channels`, y `fl_get_transport_status` en un hilo de fondo (background thread) para mantener la caché actualizada cada "x" segundos, o tras cada `transaction_commit`.
- **Deltas:** Cuando la IA propone un cambio, primero evalúa el "Shadow Graph". El sistema usa `session_diff` para entender la diferencia entre el estado actual y el deseado.

## 2. Sistema de Transacciones (ACID en Audio)
Uno de los pilares de PIE es que ninguna automatización debe romper la sesión irrevocablemente. Esto requiere transaccionalidad.

### Ciclo de Vida de una Transacción
1. `transaction_begin(id)`: El sistema toma un **Snapshot** (usando los comandos GET para volúmenes, paneos, macros, y notas MIDI afectadas de la pista objetivo).
2. Se despachan las acciones (ej: `fl_set_track_volume`, `fl_send_notes`).
3. `transaction_preview()`: (Opcional) Reproduce la sección (`fl_play` y un timer) para validación auditiva.
4. `transaction_commit()`: Consolida los cambios en el Shadow Graph y borra el snapshot.
5. `transaction_rollback()`: Si el Policy Engine falla o la IA decide revertir, el sistema lee el Snapshot y re-envía comandos MIDI/JSON inversos para restaurar el estado anterior.

### Limitaciones de Rollback en FL Studio
Debido a que no se pueden eliminar patrones a través de la API actual, los rollbacks de "Arreglo" o "Piano Roll" requerirán invocar `fl_delete_notes` explícitamente para deshacer `fl_send_notes` o revertir el `fl_set_grid_bit` del Channel Rack.

## 3. API de Herramientas Propuestas (FastMCP)
Estas herramientas se construirán utilizando el puente actual `midi_connection.py` y `piano_roll.py`:
- `session_inspect(scope)`: Lee del Shadow Graph y devuelve JSON.
- `session_refresh()`: Fuerza un resincronismo agresivo pidiendo toda la info a FL Studio a través de MIDI.
- `transaction_begin()`, `transaction_commit()`, `transaction_rollback()`.
- `snapshot_create()`, `snapshot_restore()`: Serializan la vista actual de canales/mezclador a un archivo JSON en disco (como backup).
