# Fase 3: Arrangement (FL Studio)

El arreglo (macro-estructura) es donde reside el mayor blocker de FL Studio API: **No se pueden crear ni colocar patrones en el Playlist dinámicamente desde los scripts de Python**.

Para solventarlo, PIE requiere una solución de compromiso basada en Plantillas Inteligentes (Smart Templates).

## 1. El Paradigma de la Plantilla de Arreglo (Arrangement Template)
En vez de crear un proyecto vacío, PIE iniciará y operará sobre un `.flp` pre-construido.

### Estructura del Playlist en el Template:
- **Timeline Dividido:** El Playlist se dividirá lógicamente en bloques (ej. Compases 1-17 Intro, 17-33 Verse, 33-49 Build, 49-81 Drop).
- **Patrones Pre-ubicados (Clips Dummy):** Cada track en el Playlist tendrá un clip de patrón vacío (Patrón 1, Patrón 2, etc.) estirado a lo largo de esas secciones.
- **Canales Fantasma para Automatización:** Habrá clips de automatización (Automation Clips) pre-dibujados de forma plana, enlazados a los macros principales (Filtros, Volumen, Reverb Wash).

## 2. Operaciones de PIE sobre el Arreglo
El Arrangement Engine ya no "crea" bloques de tiempo, sino que "inyecta" notas MIDI en los canales específicos para las coordenadas de tiempo (beats/bars) correspondientes a las secciones del template.

### Ejemplo de Flujo de Trabajo (Generar un Drop):
1. La intención es: "Crea un Drop de 32 compases empezando en el compás 49".
2. El Arrangement Engine usa el `Music Engine` para calcular 32 compases de MIDI (Bajo, Batería, Lead).
3. Pasa un "offset" de tiempo (+48 compases) a los comandos `fl_send_notes`.
4. Las notas se inyectan en los canales correctos usando el Piano Roll Script (`ComposeWithLLM`), pero desplazadas para que caigan exactamente donde el Playlist del template espera el "Drop".

## 3. Automatizaciones y Transition Weaver
Para crear curvas de energía (risers, filtros cerrándose antes del drop):
- Dado que no podemos editar Automation Clips vía API, usaremos Event Data del Piano Roll (si el script de piano roll de FL Studio lo permite modificar a través de JSON).
- Alternativamente, si el usuario debe grabar en vivo, PIE usará `fl_set_plugin_param_value` mientras avanza el transporte (`fl_play`), "imprimiendo" las automatizaciones al grabar (`fl_record`).

## 4. Herramientas Propuestas (FastMCP Tools)
- `arrangement_get_structure()`: Lee un JSON del proyecto que define dónde empiezan/terminan las secciones (Intro, Build, Drop) de la plantilla actual.
- `arrangement_generate_section(section_name, energy_level)`: Orquesta las llamadas a Music Engine aplicando el offset temporal correcto.
- `apply_transition_automation(macro_name, start_time, end_time, curve_type)`: Inyecta automatización MIDI (CC) en el Piano Roll para simular un sweep de filtro o washout.
- `build_song()`: Ejecuta secuencialmente la creación de Intro -> Verso -> Build -> Drop usando las macros anteriores.
