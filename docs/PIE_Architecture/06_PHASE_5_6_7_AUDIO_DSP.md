# Fases 5, 6 y 7: Audio DSP, Mezcla, Mastering y Forensics (Digital Ear en FL Studio)

La inteligencia musical pura no es suficiente si el resultado acústico presenta choques de frecuencia, enmascaramiento, distorsión (clipping) o problemas de fase. Para solucionar esto se introducen las fases finales.

El mayor desafío en FL Studio es que los scripts de Python no tienen acceso al flujo de audio (Digital Signal Processing). Para construir el "Digital Ear" se necesita un puente de audio externo.

## 1. Arquitectura del "Digital Ear" (Interceptor VST)
PIE en FL Studio utilizará un **Plugin VST Interceptor** (Audio Relay).
- **Ubicación:** Este plugin ligero se colocará en el Master de FL Studio (o en buses de mezcla clave como Drum Bus, Bass Bus dentro de la Smart Template).
- **Funcionamiento:** El VST lee los buffers de audio en tiempo real y los envía al servidor FastMCP (Python) usando `ZeroMQ` (TCP/UDP) o Memoria Compartida (Shared Memory).
- **Procesamiento:** El servidor Python usará librerías como `numpy`, `scipy` y `librosa` para calcular FFTs, LUFS (usando `pyloudnorm`), detección de picos y análisis de fase en tiempo real o casi-real.

## 2. Fase 5: Mix Intelligence
Analiza las interacciones entre múltiples pistas.
- **Detección de Enmascaramiento (Masking):** Compara el espectro frecuencial del Bass Bus y el Kick para identificar superposiciones en los 50-100Hz.
- **Acciones:** Si detecta masking severo, instruirá a FastMCP a ajustar los ecualizadores (que deben estar mapeados en la plantilla) mediante `fl_set_plugin_param_value`, o a ajustar la atenuación del Sidechain (ej. Fruity Peak Controller -> Volumen del bajo).

## 3. Fase 6: Mastering & Quality Control
Asegura que el producto final cumpla con los estándares de la industria (Loudness, True Peak).
- **Control de LUFS:** El Digital Ear captura el audio mientras FastMCP ejecuta un "Render Dummy" interno reproduciendo el drop principal (`fl_play`).
- **Ajuste de Limitador:** Basado en la medición, PIE usa la API para ajustar la ganancia (Gain) o el umbral (Ceiling) del Limitador maestro de la plantilla para alcanzar (ej.) -9 LUFS y -1.0 dBTP.

## 4. Fase 7: Audio Forensics Engine
Esta fase está encargada del diagnóstico de bajo nivel (sample-level accuracy).
- Detecta **In-sample clipping**, **DC Offset** y **Choques de Fase** extremos (Correlación negativa continua).
- Si la Fase 7 falla, emite una advertencia al Policy Engine para que prevenga cualquier exportación final (render), obligando a PIE a regresar a la Fase 5 (Mezcla) o Fase 4 (Sound Design).

## 5. Herramientas Propuestas (FastMCP Tools)
- `audio_capture(duration)`: Desencadena una grabación desde el VST Interceptor y guarda un `.wav` temporal o array de numpy.
- `mix_analyze_masking(track_a, track_b)`: Reproduce solo esas dos pistas, captura el audio y devuelve las zonas de conflicto espectral.
- `mix_apply_correction(track_id, frequency, q_factor, gain)`: Ajusta el EQ paramétrico pre-cargado de la plantilla para resolver el conflicto.
- `master_readiness()`: Mide LUFS y True Peak de la pista maestra y devuelve un diagnóstico (ej. "Too quiet, target -9, current -14").
- `master_apply_target(target_lufs)`: Intenta ajustar los macros del limitador maestro recursivamente hasta alcanzar el objetivo.
- `forensics_report()`: Genera un JSON con warnings si existen problemas matemáticos irresolubles en la señal (ej. Aliasing severo o correlación de fase < 0).
