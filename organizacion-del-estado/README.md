# Organización del Estado y de la Administración Pública — GACE A2

**Fuente principal:** «Organizacion_del_Estado_CEF_Temas_1_2_3.pdf» facilitado por el usuario (CEF, 62 páginas). No se distribuye este PDF por razones de propiedad intelectual.

**Revisión:** 15 de noviembre de 2026.

## Materia unificada

- **Tema 1 — Constitución: estructura, contenido y reforma:** 128 preguntas activas.
- **Tema 2 — Derechos, garantías, suspensión y Defensor del Pueblo:** 186 preguntas activas (incluye 18 del bloque histórico de Defensor del Pueblo, ahora integrado).
- **Tema 3 — Tribunal Constitucional:** 221 preguntas activas (incluye 200 del antiguo bloque independiente, ahora integrado).
- **Total de la materia:** 535 preguntas activas.
- **Banco total de la aplicación:** 2.503 preguntas.

## Criterio de depuración

La primera carga de 900 entradas reutilizaba extensivamente las preguntas de toda la Constitución. Esa versión fue sustituida por una selección conservadora basada en la estructura y contenidos desarrollados en los tres temas del CEF. Se retiraron 628 preguntas y se añadieron 45 nuevas de contenido explícitamente localizado en el PDF. Se corrigieron 10 preguntas históricas de Tribunal Constitucional que trataban detalles no desarrollados por el CEF.

Los archivos `tema-1.json`, `tema-2.json` y `tema-3.json` **reflejan exactamente** las preguntas actualmente incluidas en el `questions.json` principal; los identificadores no son consecutivos dentro de los archivos por tema porque corresponden a los índices globales del banco.

## Compatibilidad y límites

- Se respetan el **orden e IDs de las 2.186 preguntas históricas** del banco, así como las preguntas ya presentes en la materia Constitución (468), Derecho Administrativo y las demás materias.
- Las nuevas entradas del primer lote de 900 fueron depuradas y renumeradas. Si alguien contestó algunas antes de esta actualización, **sus rachas locales pueden no corresponder ya a esas preguntas**: la V5 actual guarda el progreso por posición. No afirmar migración completa de ese progreso.
- Diez enunciados antiguos de TC fueron corregidos en su posición original. Su racha previa, si existía, no se restablece automáticamente.
- El banco conserva el requisito de IDs globales consecutivos, cuatro opciones distintas y respuesta válida.
- El cribado no equivale a una comprobación jurídica humana, individual y exhaustiva de **cada** pregunta. Antes de garantizar cobertura o exactitud total, sigue siendo necesaria esa revisión.
- La prioridad es fidelidad al contenido y distractores de calidad, **no mantener artificialmente 300 preguntas por tema**.
- Versiones de seguridad: rama `respaldo-3086-antes-depuracion-2026-11-15` (banco previo), rama `respaldo-antes-organizacion-2026-11-15` (banco previo a Organización).

**Publicación para Android V5:** `https://raw.githubusercontent.com/higiniomosteiro-hash/GACE-de-las-Tentaciones-Preguntas/main/questions.json`.
