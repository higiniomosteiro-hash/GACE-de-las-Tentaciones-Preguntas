#!/usr/bin/env python3
"""Validación editorial y estructural del banco remoto GACE A2.

Los IDs históricos no se borran: los duplicados se desactivan por el fichero de curación.
Este control no sustituye la revisión jurídica de cada nueva pregunta.
"""
import json
import re
import sys
import unicodedata
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
        if isinstance(number, int) and 2585 <= number < 900000:
            if q.get("format") not in {"memoria", "inap"}:
                errors.append(f"Formato faltante en nueva pregunta {number}")
            if len(set(q.get("options", []))) != 4:
                errors.append(f"Opciones repetidas en nueva pregunta {number}")
            if not q.get("reference") or not q.get("subtopic") or not q.get("explanation"):
                errors.append(f"Fundamento/subtema/explicación ausente: {number}")
        if number not in retired:
            active.append(q)

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
        if date in seen_dates or ident in seen_lesson_ids:
            errors.append(f"Lección o fecha duplicada en calendario: {date} {ident}")
        seen_dates.add(date)
        seen_lesson_ids.add(ident)
        path = item.get("path", "")
        file = (ROOT / path).resolve()
        if not str(file).startswith(str(ROOT.resolve()) + "/") or not file.is_file():
            errors.append(f"Falta dossier: {ident} ({path})")
            continue
        words = len(file.read_text(encoding="utf-8").split())
        if words < 1100:
            errors.append(f"Dossier corto: {ident} ({words} palabras)")

    print(f"Banco: {len(questions)} principales + {len(extra)} ampliadas; "
          f"{len(retired)} retiradas; {len(active)} activas; "
          f"{len(program.get('published', []))} lecciones publicadas.")
    if errors:
        for e in errors[:100]:
            print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
    print("OK: IDs, opciones, duplicados activos, fundamentos de nuevas preguntas y dossiers.")


if __name__ == "__main__":
    main()
