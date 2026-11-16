#!/usr/bin/env python3
"""Corrección no destructiva: Defensor del Pueblo V6, conserva IDs y estadísticas."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"questions.json"
DATA=ROOT/"data/defensor_refuerzo_2026.json"
OLD_TOPIC="Tema 2 · Derechos, garantías, suspensión y Defensor del Pueblo"
RIGHTS_TOPIC="Tema 2 · Derechos fundamentales, garantías y suspensión"
CATEGORY="Organización del Estado"
START=2505
REPLACE_IDS=(50,52,54,56,58,60,62,64,66)

def new_question(data,id):
    options=data["alternatives"][:]
    options.insert((id*7)%4,data["answer"])
    return dict(
        id=id,question=data["question"],answer=data["answer"],options=options,
        reference=data["reference"],category=CATEGORY,topic=OLD_TOPIC,
        difficulty=data["difficulty"],format=data["format"],
        explanation="Base jurídica: "+data["reference"]+".",
    )

def validate(bank):
    assert len(bank)==len({q["id"] for q in bank})
    for i,q in enumerate(bank):
        assert q["id"]==i+1,(i,q["id"])
        assert len(q["options"])==4 and len(set(q["options"]))==4
        assert q["answer"] in q["options"]
        assert 1<=q["difficulty"]<=3
        assert q.get("format","memoria") in ("memoria","inap")

def main():
    items=json.loads(BANK.read_text(encoding="utf-8"))
    data=json.loads(DATA.read_text(encoding="utf-8"))
    rows=data["rows"]
    if len(items)>START:
        # No deshacer una ampliación ya aplicada, ni reordenar nuevos IDs.
        print("El banco ya está ampliado, no repetir la operación:",len(items))
        return
    if len(items)!=START:
        raise ValueError("Banco inicial inesperado: %d"%len(items))
    original_ids={q["id"] for q in items}
    for i,question in enumerate(items):
        if question["category"]==CATEGORY and question["topic"]==OLD_TOPIC and question["id"] not in range(49,67):
            question["topic"]=RIGHTS_TOPIC

    for i,identifier in enumerate(REPLACE_IDS):
        previous=items[identifier-1]
        assert previous["id"]==identifier and previous["category"]==CATEGORY
        previous.update(new_question(rows[i],identifier))

    for d in rows[len(REPLACE_IDS):]:
        items.append(new_question(d,len(items)+1))

    validate(items)
    assert all(q["id"] in original_ids for q in items[:START])
    focus=[q for q in items if q["category"]==CATEGORY and q["topic"]==OLD_TOPIC]
    assert len(focus)==18+len(rows)-len(REPLACE_IDS),(len(focus),len(rows))
    questions=[q["question"].casefold().strip("¿? ") for q in focus]
    assert len(set(questions))==len(questions),"Existen enunciados duplicados en el examen del Defensor"
    assert len(focus)>=75
    BANK.write_text(json.dumps(items,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("REFUERZO DEFENSOR OK: preguntas",len(items),"especializadas",len(focus),
          "duplicados corregidos",len(REPLACE_IDS),"nuevas",len(rows)-len(REPLACE_IDS),
          "banco original de",START)

if __name__=="__main__":
    main()
