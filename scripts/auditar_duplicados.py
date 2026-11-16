#!/usr/bin/env python3
"""Revisión conservadora del banco: elimina pares casi idénticos sin alterar IDs."""
import json, difflib, re
from pathlib import Path
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"questions.json"
REPL=ROOT/"data/reemplazos_duplicados_constitucion_2026.json"
AUDIT=ROOT/"auditorias/duplicados_2026_11_16.json"

def scan(items):
    groups=defaultdict(list)
    for q in items:
        groups[(q["category"],q["topic"],q["answer"],q.get("reference",""))].append(q)
    suspects=[]
    for (cat,topic,answer,reference),members in groups.items():
        if len(members)<2:continue
        for i,a in enumerate(members):
            for b in members[i+1:]:
                sim=difflib.SequenceMatcher(None,a["question"].casefold(),b["question"].casefold()).ratio()
                if sim>=.72:
                    suspects.append({
                        "id1":a["id"],"id2":b["id"],
                        "ratio":round(sim,3),"category":cat,"topic":topic,
                        "answer":answer,"reference":reference,
                        "question1":a["question"],"question2":b["question"],
                        "revision":"pendiente de revisión humana; similitud no implica duplicación",
                    })
    return sorted(suspects,key=lambda x:(-x["ratio"],x["id1"]))

def main():
    items=json.loads(BANK.read_text(encoding="utf-8"))
    defs=json.loads(REPL.read_text(encoding="utf-8"))["replacements"]
    assert len(items)>=2584,len(items)
    assert len(defs)==38,len(defs)
    before=scan(items)
    updated=0
    for entry in defs:
        id=entry["id"]
        q=items[id-1]
        assert q["id"]==id
        if q["question"]==entry["question"]:continue
        if id<=138:assert q["category"]=="Constitución"
        else:assert q["category"]=="RRHH"
        opts=entry["alternatives"].copy()
        opts.insert((id*7)%4,entry["answer"])
        assert len(opts)==4 and len(set(opts))==4
        q.update(question=entry["question"],answer=entry["answer"],options=opts,
                 reference=entry["reference"],difficulty=entry["difficulty"],
                 format=entry["format"],explanation="Fuente: "+entry["reference"]+".")
        updated+=1
    assert all(x["id"]==i+1 and len(x["options"])==4 and
               x["answer"] in x["options"] and
               x.get("format","memoria") in ("memoria","inap")
               for i,x in enumerate(items))
    after=scan(items)
    audit={
        "date":"2026-11-16","version":"1.0",
        "questions_total":len(items),
        "replacement_count":len(defs),
        "replacement_ids":[e["id"] for e in defs],
        "similarity_threshold":0.72,
        "possible_duplicate_pairs_before":len(before),
        "possible_duplicate_pairs_after":len(after),
        "note":"Pares pendientes pueden ser correctos y distintos por umbral, institución, sujeto o contexto; NO se han reescrito indiscriminadamente.",
        "pending_review":after,
    }
    BANK.write_text(json.dumps(items,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    AUDIT.parent.mkdir(parents=True,exist_ok=True)
    AUDIT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("AUDITORÍA CORREGIDA: "+str(updated)+" pares sustituidos; "+str(len(before))+
          " sospechosos antes y "+str(len(after))+" después. Banco "+str(len(items))+" preguntas")

if __name__=="__main__":
    main()
