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

## Actualización: formatos y distractores
- Commit de banco: `6031b3a29783b911d04b0709c9f133d7d2e807db`; blob `a5750a555e36c5f16638b349ae98c9883f9c269c`.
- 713 registros históricos sin `format` clasificados como `memoria` por su carácter de recuerdo directo (524 activos, 189 retirados); no se ha cambiado `topic` ni `category`. Total activo por formato: {"memoria":2535,"inap":1192}. Esta decisión editorial debe contrastarse con el comportamiento del selector de los clientes.
- 19 preguntas con distractores revisados: 482, 1433, 1435, 1591, 2581, 3059, 3092, 3104, 3105, 3113, 3123, 3153, 3154, 3405, 3406, 3713, 3715, 3765, 4668. Se conservan enunciados, respuestas correctas, índice de respuesta, IDs y orden; las alternativas falsas se han hecho comparables y más plausibles. Referencias: CE, LOTC, TREBEP art. 10, LCSP arts. 25 y 66, TFUE art. 289.4 y materiales del proyecto. No constituye validación jurídica de todas las opciones del banco.
- Filtro temporal encontró 82 preguntas principales activas con distractores de distintas unidades; no es un defecto por sí mismo. Filtro de longitud estricto encontró 12 preguntas; se conservaron los distractores válidos del ID 2009. El inventario original de 54 avisos no tiene lista de IDs o algoritmo recuperable; no se puede certificar su resolución individual.
- Verificación sobre el blob remoto: {"all":4738,"active":3727,"inactive":1011,"formatsMissing":0,"activeFormats":{"memoria":2535,"inap":1192},"changedOptions":19,"changedOptionIDs":[482,1433,1435,1591,2581,3059,3092,3104,3105,3113,3123,3153,3154,3405,3406,3713,3715,3765,4668],"changedActive":19,"regression":0,"invalid":0,"dupes":0,"examDeficits":[],"crossCategory":[],"missingSubtopicActive":262,"missingSubtopicAll":351}.
- Pendientes: revisar los subtemas históricos ausentes (fuera de la regla de metadatos para IDs nuevos), clasificación temática fina y semántica, plausibilidad del resto de distractores, preguntas con enunciados ambiguos (p. ej. ID 1260 pregunta por el tiempo que falta pero su respuesta indica el requisito total; ID 3104 distingue el plazo de rectificación del plazo para plantear conflicto), workflow y pruebas reales. No publicar.

## Actualización: ambigüedades 1260 y 3104 (25/11/2026)

- Commit de banco: `3d49835229526dc8a97d6a779e7210af848998f2`; blob: `fd620444dad6914741da150830f5509f3d3b6899`. Modificados **únicamente** los registros 1260 y 3104, manteniendo sus IDs, orden de registro, carácter activo y **posición de la respuesta correcta**. No se han añadido ni retirado preguntas.
- **1260 (LCSP, artículo 103.5)**: el enunciado original preguntaba qué tiempo *faltaba* después de diez meses, pero respondía con el requisito total de un año. Se reformula como cálculo de tiempo restante; respuesta correcta **2 meses** (posición 3), con distractores expresados también en meses y explicación de que alcanzar ese plazo no basta por sí solo para que proceda revisar precios. Fuente normativa: https://www.boe.es/buscar/act.php?id=BOE-A-2017-12902 .
- **3104 (LOTC, artículo 73.2)**: se pregunta expresamente por el **plazo de rectificación** (un mes desde la recepción, posición 2), distinto del **mes siguiente para plantear el conflicto**. Se revisan el enunciado y la explicación, sin cambiar la respuesta ni las opciones. Fuente normativa: https://www.boe.es/buscar/act.php?id=BOE-A-1979-23709 .
- Verificación previa al commit: el JSON parsea, conserva 4.705 registros principales con IDs exactamente iguales a sus posiciones; exactamente dos objetos distintos respecto al blob anterior; cuatro alternativas válidas en los dos casos y respuestas correctas en el mismo índice. **Pendiente** ejecutar el validador completo, las regresiones del cliente y la revisión jurídica del resto del banco.
- Continúa la prohibición de fusionar con `main` o publicar V7 sin validación y autorización expresa de lanzamiento.
