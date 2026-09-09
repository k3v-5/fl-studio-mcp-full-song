# Fase 4: Sound Design & Semantic Macros (FL Studio)

El diseño de sonido en PIE no consiste en mover cientos de knobs aleatorios en un sintetizador complejo (como Serum), sino en mapear intenciones acústicas a controles simplificados (Semantic Macros).

En Ableton, esto se logra fácilmente con "Audio Effect Racks" y "Instrument Racks". En FL Studio, la alternativa nativa es **Patcher** o el plugin **Control Surface**.

## 1. El Enfoque Patcher / Control Surface
Dado que no podemos cargar VSTs vía API, PIE interactuará exclusivamente con parámetros ya expuestos en la plantilla (Smart Template).

### Convención de Macros Semánticos
Cada canal importante (Bajos, Leads) tendrá insertado un `Control Surface` o `Patcher` configurado con knobs pre-asignados a parámetros internos del VST (ej. Serum Cutoff, FM Amount).
Los nombres de estos controles deben seguir una convención semántica:
- `Brightness` (Filtros Lowpass / FM)
- `Warmth` (Saturación / Tubos)
- `Space` (Reverb Mix / Size)
- `Punch` (Ataque de Envolvente / Compresión transitoria)
- `Movement` (LFO Rate / Amount)

## 2. Interacción desde FastMCP
Usando las herramientas de `plugins.py` ya existentes en `fl-studio-mcp`:
1. El motor escanea el canal para encontrar el plugin `Control Surface`.
2. Llama a `fl_get_plugin_params` para obtener los IDs (índices) de los parámetros nombrados semánticamente.
3. El motor de Sound Design calcula el valor deseado (0.0 a 1.0) para lograr el perfil tímbrico.
4. Se ejecuta `fl_set_plugin_param_value(index, value)`.

## 3. Generación de Perfiles Tímbricos (Sound Profiles)
PIE mantendrá internamente diccionarios de "Perfiles Tímbricos" para mapear intenciones a valores de macros:
- **"Aggressive Reece Bass"**: `Brightness`: 0.8, `Warmth`: 0.9, `Movement`: 0.6.
- **"Pluck House Bass"**: `Punch`: 1.0, `Brightness`: 0.4, `Space`: 0.1.

## 4. Herramientas Propuestas (FastMCP Tools)
- `sound_get_macros(channel_id)`: Filtra los parámetros del plugin `Control Surface` y devuelve solo los "Semantic Macros" disponibles.
- `sound_apply_profile(channel_id, profile_name)`: Busca el perfil en la base de datos de PIE y setea los valores macro correspondientes.
- `sound_set_macro(channel_id, macro_name, value)`: Setea un macro individual de forma precisa.
- `sound_lint(channel_id)`: Valida que los macros del canal actual no produzcan un sonido destructivo (ej. demasiado `Warmth` y `Brightness` podría romper el techo de gain staging, advirtiendo a la fase de mezcla).
