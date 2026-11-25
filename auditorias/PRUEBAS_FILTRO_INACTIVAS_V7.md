# V7 · Pruebas de filtrado de inactivas sin perder progreso

Fecha: 25/11/2026 · Estado: **pendiente de implementación y ejecución**. Este documento no certifica un resultado de pruebas.

## Problema corroborado en el código Android V6.2.5
- `MainActivity.java` guarda `s<index>` (racha), `a<index>` (intentos), `c<index>` (aciertos), `e<index>` (errores). Los índices provienen de la posición del registro dentro de `JSONArray bank`.
- `QuestionUpdateService.validate()` exige `id == index+1` y no acepta reordenaciones. La aplicación descarga `questions.json` de la rama pública `main` y guarda caché local.
- El banco de curación en `data/curacion-defensor-conceptos.json` contiene `inactiveIds` (1.013 IDs, según seguimiento). Los clientes Android revisados no consultan esa lista para sus recorridos. El APK V6.2.3 facilitado conserva 2.505 preguntas en `assets/questions.json` sin un asset de curación separado. La ausencia del asset, aislada, no demostraría ausencia de actualización remota; la lectura del código de V6.2.5 sí identifica los recorridos que falta filtrar.

## Contrato de compatibilidad V7
1. Mantener `questions.json` completo en idéntico orden: el índice 0 contiene ID 1; los ID 1–4705 no se eliminan, renumeran ni desplazan.
2. Construir una **máscara de elegibilidad** a partir de la lista `inactiveIds` de curación, por ID. No eliminar ni compactar registros del `JSONArray`.
3. Aplicar la máscara a TODA fuente de preguntas: Entrenamiento Memoria/INAP/Mixto, simulacros, Examen del día, Reto diario y Match. Incluir candidatas de colecciones especiales y ampliación donde corresponda.
4. Aplicarla también al total de preguntas activas, denominadores/porcentajes de dominio, gráficas, listas de materias, portada y cualquier otra estadística de contenido disponible, sin borrar respuestas históricas ni puntuaciones obtenidas.
5. Mantener progreso y rachas de las inactivas en `SharedPreferences`; simplemente no presentarlas mientras estén retiradas. Si una ID se reactiva, debe recuperar su mismo historial.
6. Asegurar correspondencia entre la versión del banco y el manifiesto de curación, gestionando caché, errores de red, reinicio y actualización. No tratar el archivo de curación como sustituto del banco ni asumir que estará disponible offline sin caché.
7. Evitar mezclar el canal de pruebas de la rama `auditoria-2026-11-25` con el canal público `main`. Ningún cliente público debe consumir accidentalmente material de auditoría.

## Pruebas de aceptación reproducibles
- **IDs retiradas:** 3421, 3427 y 23 no deben salir en ningún modo ni contar entre preguntas activas. Sus objetos han de seguir presentes en el array original.
- **IDs que se conservan:** 1235, 1239 y 2440 deben seguir disponibles según filtros aplicables. Las primeras dos sustituyen conceptualmente a las retiradas 3421 y 3427, respectivamente.
- **Progreso de índice contiguo:** guardar una racha conocida en un registro inmediatamente posterior a una ID retirada, actualizar y comprobar que corresponde al mismo ID, no al anterior.
- **Estadísticas:** comparar un móvil con progreso anterior al filtrado y después: la dominancia visible cuenta solo activas; los valores históricos permanecen íntegros; puntos y rankings ya asignados no se reinician.
- **Hoy estudiamos:** ninguno de los 23 exámenes debe incluir ID inactivas; los cupos configurados se cubren cuando hay candidatas activas.
- **Repetición y conexión:** probar arranque desde instalación anterior, arranque offline con caché anterior, recuperación de conexión, actualización manual/automática y reinicio del proceso.
- **Variantes:** ejecutar Android V7 candidata y versión web/iPhone; repetir selección Memoria, INAP, Reto, Match, exámenes diarios y estadística por tema.
- **Firebase:** contrastar ranking y seudónimo persistente; no modificar identificador anónimo de dispositivo ni migrar / limpiar almacenamiento salvo en una migración explícita, probada y reversible.

## Criterio para cerrar
Esta tarea solo podrá marcarse como cerrada después de inspección del código modificado, pruebas automatizadas y ejecución real en clientes Android e iPhone con progreso heredado y sin progreso. **Pendiente**.
