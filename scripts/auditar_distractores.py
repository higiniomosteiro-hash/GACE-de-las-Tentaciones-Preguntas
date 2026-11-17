#!/usr/bin/env python3
"""Auditoría conservadora de distractores del banco GACE A2.

Evalúa el banco COMPLETO por categorías y alerta sobre opciones que
no pertenecen a la misma clase de respuesta (plazos, números, leyes).
No inventa alternativas conceptuales: pueden surgir varias correctas
si se cambian frases jurídicas mediante sustituciones indiscriminadas.
"""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = json.loads((ROOT / "questions.json").read_text(encoding="utf-8"))
CUR = json.loads((ROOT / "data/curacion-defensor-conceptos.json").read_text(encoding="utf-8"))
EXTRA = json.loads((ROOT / "data/ampliacion-defensor-unica-2026.json").read_text(encoding="utf-8"))
RETIRED = set(CUR["inactiveIds"])

DURATION = re.compile(r"^(\\d+)\\s+(d[ií]as?|mes(?:es)?|a[ñn]os?|horas?|semanas?)$", re.I)
DIGITS = re.compile(r"^\\d+$")
PERCENT = re.compile(r"^\\d+(?:[.,]\\d+)?\\s?%$")
LAW = re.compile(r"^Ley(?: Orgánica)? \\d+/\\d{4}$", re.I)


def kind_of_unit(token: str) -> str:
    t = token.lower()
    if t.startswith("d"): return "días"
    if t.startswith("mes"): return "meses"
    if t.startswith("a"): return "años"
    if t.startswith("hor"): return "horas"
    return "semanas"


def audit(question):
    answer = question["answer"].strip()
    wrong = [v for v in question["options"] if v != question["answer"]]
    if len(wrong) != 3:
        return ["Número incorrecto de alternativas distintas de la correcta"]
    findings = []
    if DIGITS.fullmatch(answer) and any(not DIGITS.fullmatch(v.strip()) for v in wrong):
        findings.append("Cifras mezcladas con respuestas de distinta naturaleza")
    if PERCENT.fullmatch(answer) and any(not PERCENT.fullmatch(v.strip()) for v in wrong):
        findings.append("Porcentajes mezclados con respuestas sin porcentaje")
    m = DURATION.fullmatch(answer)
    if m:
        unit = kind_of_unit(m.group(2))
        units = [DURATION.fullmatch(v.strip()) for v in wrong]
        if any(z is None or kind_of_unit(z.group(2)) != unit for z in units):
            findings.append("Plazos expresados con unidades diferentes (revisar equivalencias)")
        if unit == "meses" and any(re.search(r"^1 meses$", v.strip(), re.I) for v in wrong):
            findings.append("Error gramatical: 1 meses")
    if LAW.fullmatch(answer):
        same = sum(bool(LAW.fullmatch(v.strip())) for v in wrong)
        if same < 2:
            findings.append("Identificación de ley con distractores de naturaleza normativa distinta")
    avg = sum(len(v) for v in wrong) / 3
    if len(answer) > 70 and avg < len(answer) * 0.42:
        findings.append("Opciones de longitud muy desigual; posible pista formal")
    return findings


def main():
    findings = collections.defaultdict(list)
    scanned = 0
    for q in BANK + EXTRA:
        if q["id"] in RETIRED:
            continue
        scanned += 1
        for msg in audit(q):
            findings[msg].append((q["id"], q["category"], q.get("topic", "")))
    print(f"Revisadas {scanned} preguntas activas y sus distractores.")
    for name, examples in sorted(findings.items(), key=lambda x: -len(x[1])):
        print(f"AVISO: {name}: {len(examples)}")
        for number, category, topic in examples[:8]:
            print(f"  ID {number} | {category} | {topic}")
    print("El control de coherencia no certifica la corrección jurídica; se requiere revisión editorial.")
    # La auditoría es informativa: no bloquea un banco compatible por posibles
    # excepciones legítimas. Las reglas estructurales estrictas están en validar_banco.py.


if __name__ == "__main__":
    main()
