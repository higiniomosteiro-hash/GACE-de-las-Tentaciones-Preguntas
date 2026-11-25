#!/usr/bin/env python3
"""Validación editorial y estructural del banco remoto GACE A2.

Los IDs históricos no se borran: los duplicados se desactivan por el fichero de curación.
Este control no sustituye la revisión jurídica de cada nueva pregunta.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def normalize(value):
    raw = unicodedata.normalize("NFD", str(value).lower())
    raw = "".join(c for c in raw if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[¿?.,:;“”\"']", "", raw)).strip()


def main():
    questions = load("questions.json")
    extra = load("data/ampliacion-defensor-unica-2026.json")
    cur = load("data/curacion-defensor-conceptos.json")
    program = load("hoy-estudiamos/programa.json")
    retired = set(cur["inactiveIds"])
    errors = []
    warnings = []
    if len(cur['inactiveIds']) != len(retired):
        errors.append('Curación con IDs repetidos')
    # Android V6.2.3 guarda el progreso por índice: el banco principal
    # debe mantener ID=posición (1, 2, ...), aunque los temas se reorganicen.
    for pos, q in enumerate(questions, start=1):
        if q.get("id") != pos:
            errors.append(f"INCOMPATIBLE CON ANDROID: posición {pos} tiene ID {q.get('id')}")
    if len(questions) > 15000:
        errors.append("Banco supera el máximo Android de 15.000 preguntas")
    if (ROOT / "questions.json").stat().st_size > 8 * 1024 * 1024:
        errors.append("Banco supera el máximo Android de 8 MiB")

    ids = set()
    active = []
    for q in questions + extra:
        number = q.get("id")
        if type(number) is not int or number in ids:
            errors.append(f"ID inválido o duplicado: {number}")
        ids.add(number)
        if not (isinstance(q.get("question"), str) and q["question"].strip()
                and isinstance(q.get("answer"), str) and q["answer"].strip()
                and isinstance(q.get("options"), list)
                and len(q["options"]) == 4
                and all(isinstance(o, str) for o in q["options"])
                and q["answer"] in q["options"]
                and isinstance(q.get("category"), str) and q["category"]
                and isinstance(q.get("topic"), str) and q["topic"]):
            errors.append(f"Pregunta mal formada: {number}")
        options = q.get('options')
        if isinstance(options, list) and all(isinstance(o, str) for o in options):
            normalized = [normalize(o) for o in options]
            if not all(normalized) or len(set(normalized)) != 4:
                errors.append(f'Opciones vacías o repetidas tras normalizar: {number}')
        if isinstance(number, int) and 2585 <= number < 900000:
            if q.get("format") not in {"memoria", "inap"}:
                errors.append(f"Formato faltante en nueva pregunta {number}")
            if not q.get("reference") or not q.get("subtopic") or not q.get("explanation"):
                errors.append(f"Fundamento/subtema/explicación ausente: {number}")
        if number not in retired:
            active.append(q)

    for number in sorted(retired - ids):
        errors.append(f'ID de curación inexistente: {number}')

    unique_content = {}
    for q in active:
        key = (normalize(q.get("question", "")), normalize(q.get("answer", "")))
        if key in unique_content:
            errors.append(f"Pregunta activa repetida: {unique_content[key]} y {q['id']}")
        else:
            unique_content[key] = q["id"]

    if len(program.get("order", [])) != len(set(program.get("order", []))):
        errors.append("Programa con IDs de lección duplicados")
    seen_dates = set()
    seen_lesson_ids = set()
    for item in program.get("published", []):
        date, ident = item.get("date"), item.get("id")
        if not ident or ident in seen_lesson_ids:
            errors.append(f'ID de lección vacío o duplicado: {ident}')
        seen_lesson_ids.add(ident)
        if not item.get('libraryOnly', False):
            if not isinstance(date, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
                errors.append(f'Fecha de lección inválida: {ident} {date}')
            elif date in seen_dates:
                errors.append(f'Fecha diaria duplicada en calendario: {date} {ident}')
            seen_dates.add(date)
        exam = item.get('exam', {})
        count = exam.get('count')
        included = set(exam.get('includeIds', []))
        subtopics = set(exam.get('includeSubtopics', []))
        for number in sorted(included - ids):
            errors.append(f'ID de examen inexistente: {ident} / {number}')
        # Verifica el conjunto explícito del manifiesto, no el fallback del cliente.
        candidates = [q for q in questions + extra
                      if (not exam.get('excludeInactive', True) or q['id'] not in retired)
                      and (q['id'] in included or q.get('subtopic') in subtopics)]
        if type(count) is not int or count < 1:
            errors.append(f'Cantidad de examen inválida: {ident} / {count}')
        elif len(candidates) < count:
            errors.append(f'Examen sin suficientes preguntas: {ident} / {len(candidates)} de {count}')
        else:
            print(f'EXAMEN: {ident}: {len(candidates)} disponibles de {count} solicitadas')
        path = item.get("path", "")
        file = (ROOT / path).resolve()
        if not str(file).startswith(str(ROOT.resolve()) + "/") or not file.is_file():
            errors.append(f"Falta dossier: {ident} ({path})")
            continue
        words = len(file.read_text(encoding="utf-8").split())
        if words < 1100:
            errors.append(f"Dossier corto: {ident} ({words} palabras)")

    base_sha = os.environ.get('GACE_BASE_SHA', '').strip()
    if base_sha and base_sha != '0' * 40:
        if not re.fullmatch(r'[0-9a-f]{40}', base_sha):
            errors.append('SHA base inválido para comprobar regresión')
        else:
            try:
                previous = json.loads(subprocess.check_output(
                    ['git', 'show', f'{base_sha}:questions.json'], cwd=ROOT, text=True))
                if len(questions) < len(previous):
                    errors.append(f'Regresión: banco reducido de {len(previous)} a {len(questions)}')
                for old, new in zip(previous, questions):
                    if old.get('id') != new.get('id'):
                        errors.append(f'Regresión: ID histórico cambiado: {old.get("id")}')
                    if old.get('question') != new.get('question') or old.get('answer') != new.get('answer'):
                        warnings.append(f'Revisión editorial requerida: enunciado o respuesta histórica modificada: {old.get("id")}')
                    old_options, new_options = old.get('options', []), new.get('options', [])
                    if old.get('answer') in old_options and new.get('answer') in new_options:
                        if old_options.index(old['answer']) != new_options.index(new['answer']):
                            warnings.append(f'Posición de respuesta histórica modificada: {old.get("id")}')
                print(f'REGRESIÓN: comparadas {min(len(previous), len(questions))} preguntas históricas con {base_sha[:12]}')
            except (subprocess.CalledProcessError, ValueError, TypeError) as exc:
                errors.append(f'No se pudo comprobar regresión contra la base: {exc}')
    for warning in warnings:
        print(f'AVISO: {warning}')

    print(f"Banco: {len(questions)} principales + {len(extra)} ampliadas; "
          f"{len(retired)} retiradas; {len(active)} activas; "
          f"{len(program.get('published', []))} lecciones publicadas.")
    if errors:
        print(f"Total de incidencias: {len(errors)}", file=sys.stderr)
        groups = Counter(re.sub(r":.*$", "", e) for e in errors)
        for name, count in sorted(groups.items()):
            print(f"RESUMEN: {name}: {count}", file=sys.stderr)
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
    print("OK: IDs, opciones, duplicados activos, fundamentos de nuevas preguntas y dossiers.")


if __name__ == "__main__":
    main()
