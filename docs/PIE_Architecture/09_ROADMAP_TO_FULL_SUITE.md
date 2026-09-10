# Roadmap hacia la Suite PIE Completa (FL Studio)

Este documento es un registro vivo de todo lo que falta por construir o mejorar para que PIE pase de ser un prototipo funcional a una suite de producción 100% autónoma y profesional en FL Studio.

*Cada vez que se complete un hito, este documento debe actualizarse marcando la casilla correspondiente `[x]`.*

---

## 1. Núcleo Musical y Generativo (Music & Arrangement)
Actualmente, el LLM envía arreglos crudos y acordes a PIE. Podemos potenciar esto con herramientas especializadas:
- [ ] **Integradora LLM Directa:** Crear una sub-herramienta que se conecte directamente a modelos musicales (como Suno, Magenta o herramientas de Audio-to-MIDI) para extraer teoría musical avanzada, en lugar de depender únicamente del razonamiento lógico del texto del LLM base.
- [x] **Librería de Ritmos (Groove Pool):** Implementar funciones de cuantización con *Swing*, *Micro-timing* y *Humanization* real. Que el MIDI Adapter no solo envíe notas perfectas a la grilla, sino que aplique ruido gaussiano a los tiempos (Phase 2).
- [x] **Generador de Transiciones (Transition Weaver):** Una herramienta que calcule automatizaciones de LOM (sweeps de filtro, pitch risers, noise sweeps) y las inyecte automáticamente en el `ArrangementEngine` para los 4 compases previos a un Drop.

## 2. Inyección MIDI y UI Automation (Path 1)
El `MIDIAdapter` funciona y encola tareas mediante el atajo `Ctrl+Alt+Y`. Sin embargo, esto es un hack de interfaz de usuario.
- [x] **Cola de inyección implementada** (Se agregó en Milestone 1).
- [ ] **Verificación de Foco (Window Focus Check):** Implementar llamadas nativas del sistema operativo (Win32 API o AppleScript) para asegurar que la ventana de FL Studio esté en primer plano antes de enviar el atajo de teclado, evitando que las notas se escriban en otro programa.
- [ ] **Manejo de Errores UI:** Si FL Studio no responde al atajo (ej. la ventana emergente de un VST roba el foco), PIE debe detectarlo, abortar la cola, y notificar al LLM para reintentar.

## 3. Audición Digital y DSP (Path 2)
El UDP listener en Python funciona, pero falta la pieza central que envía el audio.
- [x] **Receptor UDP y Lógica DSP (librosa, pyloudnorm) implementado** (Se completó en Milestone 2).
- [x] **Generador Sidechain Automático (Ducking)** (Se implementó como Mejora C).
- [ ] **Desarrollo del VST en C++ (El Sender):** Programar un VST3 real en JUCE o Rust (`nih-plug`) que se instale en el Master de FL Studio y envíe el stream estéreo a `localhost:9878`.
- [ ] **Análisis Multi-Pista Estéreo:** Actualizar el VST para que pueda enviarse desde pistas individuales (ej. enviar Bass Bus y Kick Bus por puertos UDP separados) para que el `analyze_masking` funcione en tiempo real sin depender de la masterización general.
- [ ] **Phase Analyzer:** Incorporar análisis de fase y correlación estéreo (Goniometer) usando `numpy.corrcoef` para reportar si la mezcla es segura para sistemas Mono.

## 4. Hackeo de Proyectos (Path 3 - PyFLP)
Se demostró que PyFLP puede leer el proyecto y hacer backups, pero la inyección es rudimentaria.
- [x] **Lector de estructura y Backup en Sandbox** (Se completó en Milestone 3).
- [ ] **Inyección de VSTs Dinámica:** Descifrar la estructura binaria de un `PluginEntry` en el `.flp` para que el LLM pueda solicitar "Cargar Serum" y PIE lo inyecte directamente en el Channel Rack apagado.
- [ ] **Orquestación Automática de Carga:** Que PIE detecte si un proyecto inyectado requiere recarga, y envíe comandos al OS (ej. cerrar el proceso actual de FL y abrir el nuevo archivo de backup modificado de forma automática).

## 5. Diseño de Sonido (Sound Design)
- [x] **Eliminación de Hardcoding Semántico** (El LLM ahora define los keywords y reglas).
- [ ] **Banco de Presets Reales (FST):** Desarrollar una herramienta que lea y asigne archivos `.fst` (FL Studio State) a los canales, permitiendo cambiar el diseño de sonido completo de un sintetizador (no solo mover 5 macros, sino cargar un preset distinto).
- [ ] **Feedback Auditivo para Timbres:** Enviar el audio capturado por el VST Interceptor de una pista de sintetizador aislada a una API multimodal (ej. un LLM que pueda escuchar audio o analizar un espectrograma generado en imagen) para evaluar empíricamente si el bajo suena "agresivo".

## 6. Gobernanza y Transacciones (Foundation)
- [x] **Policy Engine Dinámico** (Implementado).
- [x] **Sistema de Snapshot JSON** (Implementado).
- [ ] **Rollback Físico Completo:** Actualmente el `TransactionManager` guarda el snapshot, pero la función `rollback()` necesita implementarse físicamente: debe iterar sobre el JSON anterior y enviar todos los comandos MIDI invertidos (Volumen, Paneos, Macros) a FL Studio para restaurar la sesión acústicamente.
- [ ] **Garbage Collector:** Limpiar los snapshots antiguos o proyectos `.pie_backup` de la carpeta temporal para evitar saturar el disco duro después de sesiones largas con la IA.
