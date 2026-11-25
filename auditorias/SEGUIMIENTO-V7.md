# Seguimiento auditoría V7 — 25/11/2026

Rama exclusiva: `auditoria-2026-11-25`. No fusionar con main hasta validación y autorización de lanzamiento.

## Estado comprobado
- 4.705 preguntas principales + 33 adicionales; 1.011 inactivas; 3.727 activas.
- Inventario inicial: 381 registros con metadatos incompletos. 169 ya estaban completados al retomar. Se completaron los 212 restantes (IDs 2989–3200) en cuatro commits.
- Último commit de banco: `09e7a2359f0d22633b40cd6d3331964ab398416d`; blob `1d93d417715d0e190efcfaeba52bfe022108cc9e`.
- Referencias rectificadas: 3105, 3110, 3139, 3168, 3175, 3184, 3190. Fuentes: https://www.boe.es/buscar/act.php?id=BOE-A-1979-23709 y https://www.boe.es/buscar/act.php?id=BOE-A-1978-31229 ; para Defensor: https://www.boe.es/buscar/act.php?id=BOE-A-1981-10325 .
- Comparación con blob previo a los cuatro commits: 212 registros modificados; cero cambios de enunciado, respuesta u opciones; IDs consecutivos y únicos. Cero opciones estructuralmente inválidas y cero duplicados exactos activos normalizados. Cero faltas de metadatos según umbral del validador (ID 2585–899999). Las 23 sesiones disponen de candidatos suficientes según selección explícita del manifiesto.
- Estas comprobaciones se ejecutaron sobre el contenido remoto; no equivalen a una ejecución completa del workflow ni a una auditoría jurídica exhaustiva.

## Pendiente
1. Recalcular avisos de distractores y clasificación temática, detectar preguntas semánticamente repetidas y ambiguas; revisión jurídica individual. Conservar IDs, posición y progreso; documentar cambios de contenido y desactivaciones.
2. Revisar correspondencia temática de las 23 sesiones, dossiers y comportamiento real del cliente.
3. Ejecutar workflow completo, regresiones contra main y pruebas de Android/iPhone, Firebase, sincronización, estadísticas y rankings antes de V7. No publicar durante auditoría.

El inventario JSON original se conserva como fotografía histórica, no como lista vigente de pendientes.
