#!/usr/bin/env python3
"""Reconstruye questions.json sin cambiar ninguna identidad ni progreso previo.
Origen: apuntes de Cristina Corredoira, Temas 1 y 2, 50 páginas.
La auditoría de distractores nunca altera la respuesta correcta ni el enunciado.
"""
import json, re, hashlib, collections, pathlib, math
ROOT=pathlib.Path(__file__).resolve().parent.parent
source=ROOT/"questions.json"
original=json.loads(source.read_text(encoding="utf-8"))
old=json.loads(json.dumps(original,ensure_ascii=False))
assert len(old)>=1626
assert all(q["id"]==i+1 for i,q in enumerate(old))
SRC="Apuntes CEF, Gestión Financiera, Temas 1 y 2, Cristina Corredoira"
AUDIT=collections.Counter()
SAMPLES={}
def mark(category,reason,example=None):
    AUDIT[(category,reason)]+=1
    if example is not None and (category,reason) not in SAMPLES:
        SAMPLES[(category,reason)] = example
def stable(s):
    return int(hashlib.sha256(str(s).encode("utf-8")).hexdigest()[:16],16)
def shuffle4(answers,key):
    vals=list(answers)
    # Mezcla determinista: no se favorece a la primera respuesta.
    salt=stable(key)
    for i in range(3,0,-1):
        j=salt%(i+1);salt=(salt//(i+1))^stable(str(key)+"."+str(i))
        vals[i],vals[j]=vals[j],vals[i]
    return vals
def dedup(seq):
    seen=set();out=[]
    for v in seq:
        x=str(v).strip()
        if not x or x in seen: continue
        seen.add(x);out.append(x)
    return out
def update(q,new_wrong,reason):
    ans=q["answer"]
    alternatives=dedup([x for x in new_wrong if x!=ans])
    if len(alternatives)<3:return
    new=shuffle4([ans]+alternatives[:3],q["id"])
    if set(new)!=set(q["options"]):
        q["options"]=new
        mark(q["category"],reason,{"id":q["id"],"answer":ans,"options":new})

# CE: localizar artículo con tres alternativas de la misma unidad constitucional.
RANGES=[(1,9),(10,13),(14,29),(30,38),(39,52),(52,55),(56,65),
        (66,96),(97,107),(108,116),(117,127),(128,136),
        (137,158),(159,165),(166,169)]
def unit(n):
    for a,b in RANGES:
        if a<=n<=b: return a,b
    return max(1,n-3),min(169,n+3)
def near_numbers(n,a,b,count=3):
    pool=[x for x in range(a,b+1) if x!=n]
    pool.sort(key=lambda v:(abs(v-n),stable(str(n)+"_"+str(v))))
    if len(pool)<count:
        pool += [v for v in [n-2,n-1,n+1,n+2,n-3,n+3] if v>0 and v!=n and v not in pool]
    return pool[:count]
ce_label={}
for q in old:
    if q.get("category")=="Constitución" and q.get("topic")=="Contenido de artículos":
        mt=re.search(r"\bart[íi]culo\s+(\d{1,3})\b",q["question"],re.I)
        if mt:ce_label[int(mt.group(1))]=q["answer"]
for q in original:
    AUDIT[(q.get("category",""),"examinadas")]+=1
    if q.get("category")=="Constitución" and q.get("topic")=="Localización de artículos":
        mt=re.match(r"Art[íi]culo\s+(\d{1,3})$",q["answer"],re.I)
        if mt:
            n=int(mt.group(1));a,b=unit(n)
            update(q,[f"Artículo {v}" for v in near_numbers(n,a,b)],"CE artículos próximos")
    elif q.get("category")=="Constitución" and q.get("topic")=="Contenido de artículos":
        mt=re.search(r"\bart[íi]culo\s+(\d{1,3})\b",q["question"],re.I)
        if mt:
            n=int(mt.group(1));a,b=unit(n)
            vals=[ce_label.get(v) for v in near_numbers(n,a,b,5)]
            vals=[x for x in vals if x and x!=q["answer"]]
            if len(vals)>=3:update(q,vals[:3],"CE contenidos del mismo bloque")
    # Sustituciones de alta confianza: plazos y cantidades junto al valor correcto.
    ans=q.get("answer","").strip()
    topic=q.get("topic","")
    if q.get("category")!="Constitución" and not ans.lower().startswith(("sí","no","solo ","únicamente")):
        m=re.fullmatch(r"(\d{1,3})\s*(días?|mes(?:es)?|años?|magistrados?)",ans,re.I)
        if m:
            n=int(m.group(1));u=m.group(2)
            ds=near_numbers(n,max(1,n-3),n+3)
            update(q,[f"{v} {u}" for v in ds],"números y plazos cercanos")
        elif re.fullmatch(r"\d{1,3}",ans):
            n=int(ans);ds=near_numbers(n,max(1,n-2),n+3)
            update(q,[str(v) for v in ds],"cantidades cercanas")
        elif re.fullmatch(r"\d{1,2}(?:,\d+)?\s*%",ans):
            value=float(ans.replace("%","").replace(",","."));step=1 if value>=2 else .1
            vals=[]
            for off in [-step,step,2*step]:
                x=value+off
                if x>0:
                    vals.append((f"{x:.1f}" if x!=int(x) else str(int(x))).replace(".",",")+" %")
            update(q,vals,"porcentajes vecinos")
        elif ans in ("Providencia","Auto","Sentencia","Acuerdo") and q.get("category")=="Tribunal Constitucional":
            update(q,[v for v in ("Providencia","Auto","Sentencia","Acuerdo") if v!=ans],"resoluciones procesales verosímiles")
        elif ans in ("El Pleno del TC","La Sala del TC","Una Sala del TC","Una Sección del TC","El Presidente del TC") and q.get("category")=="Tribunal Constitucional":
            update(q,[v for v in ("El Pleno del TC","Una Sala del TC","Una Sección del TC","El Presidente del TC") if v!=ans],"órganos internos del TC")
    # No alteramos otras opciones jurídicamente delicadas sin contraste de contenido.
    # Todas las respuestas existentes se reordenan para no crear patrones en el JSON.
    q["options"]=shuffle4([q["answer"]]+[x for x in q["options"] if x!=q["answer"]],q["id"])

def parse_groups(text):
    groups=[];g=None
    for ln in text.splitlines():
        s=ln.strip()
        if not s or s.startswith("#"):continue
        if s.startswith("@"):
            a=s[1:].split("|")
            if len(a)!=4:raise ValueError("Cabecera de mapa inválida: "+s)
            g={"name":a[0],"norm":a[1],"topic":a[2],"page":a[3],"rows":[]}
            groups.append(g)
        else:
            a=s.split("|")
            if len(a)!=2:raise ValueError("Entrada de mapa inválida: "+s)
            g["rows"].append((a[0],a[1]))
    return groups
def parse_ones(text):
    groups=[];g=None
    for ln in text.splitlines():
        s=ln.strip()
        if not s or s.startswith("#"):continue
        if s.startswith("@"):
            a=s[1:].split("|")
            if len(a)!=3:raise ValueError("Cabecera pregunta inválida: "+s)
            g={"topic":a[0],"pages":a[1],"reference":a[2],"rows":[]}
            groups.append(g)
        else:
            a=s.split("|")
            if len(a)!=7:raise ValueError("Pregunta inválida, "+str(len(a))+" campos: "+s)
            g["rows"].append(a)
    return groups
groups=parse_groups((ROOT/"preparacion-financiera/mapas_fuente.txt").read_text(encoding="utf-8"))
one_groups=parse_ones((ROOT/"preparacion-financiera/preguntas_fuente.txt").read_text(encoding="utf-8"))
added=[]
existing_texts={q["question"].casefold() for q in original}
def add(q,answer,wrong,topic,reference,fmt="memoria",level=3):
    if len(wrong)!=3:raise AssertionError((q,wrong))
    opts=dedup([answer]+wrong)
    if len(opts)!=4:raise AssertionError(("Opciones duplicadas",q,opts))
    key=q.casefold()
    if key in existing_texts: raise AssertionError(("Pregunta repetida",q))
    existing_texts.add(key)
    i=len(original)+len(added)+1
    cat="Gestión Financiera · Tema 1" if topic.startswith("Tema 1") else "Gestión Financiera · Tema 2"
    item={"id":i,"question":q,"answer":answer,"options":shuffle4(opts,i),
          "reference":reference,"category":cat,"topic":topic,
          "difficulty":int(level),"format":fmt,"source":SRC}
    added.append(item)
def numkey(s):
    try:return float(s)
    except ValueError:return None
def code_label(group,code):
    name=group["name"]
    if "artículos" in name or "CE · presupuesto" in name:return "Artículo "+code
    if "Secciones" in name:return "Sección "+code
    if "Capítulos del presupuesto" in name:return "Capítulo "+code
    if "Conceptos y subconceptos" in name or "Códigos de estructura" in name:return "Código "+code
    return code
def link_questions(g,key,label):
    n=g["name"];norm=g["norm"]
    if "artículos" in n or "CE · presupuesto" in n:
        front=f"Según {norm}, ¿en qué artículo se regula {label[0].lower()+label[1:]}?"
        back=f"Según {norm}, ¿qué materia aborda el artículo {key}?"
    elif "Secciones" in n:
        front=f"En los PGE, ¿qué sección corresponde a {label}?"
        back=f"En la clasificación orgánica de los PGE, ¿qué corresponde a la sección {key}?"
    elif "Capítulos del presupuesto" in n:
        side="gastos" if "gastos" in n else "ingresos"
        front=f"En el presupuesto de {side}, ¿a qué capítulo corresponde {label[0].lower()+label[1:]}?"
        back=f"En la clasificación económica de {side}, ¿qué recoge el capítulo {key}?"
    elif "Conceptos y subconceptos" in n:
        side="gastos" if "gastos" in n else "ingresos"
        front=f"Según la clasificación económica de {side}, ¿cuál es el código de {label[0].lower()+label[1:]}?"
        back=f"En el presupuesto de {side}, ¿qué concepto o subconcepto designa el código {key}?"
    elif "Códigos de estructura" in n:
        front=f"En la estructura por programas de los PGE, ¿qué código corresponde a {label[0].lower()+label[1:]}?"
        back=f"En la clasificación por programas, ¿a qué actividad se refiere el programa {key}?"
    else:
        front=f"En {norm}, ¿qué denominación corresponde a «{label[0].lower()+label[1:]}»?"
        back=f"En {norm}, ¿a qué se refiere «{key}»?"
    return front,back
skipped=collections.Counter()
for g in groups:
    rows=g["rows"]
    if len(rows)<4:
        skipped[g["name"]]+=len(rows)
        continue # tres distractores coherentes de la misma familia
    for i,(key,label) in enumerate(rows):
        others=[(k,l) for k,l in rows if k!=key]
        if numkey(key)is not None:
            others.sort(key=lambda x:(abs(numkey(x[0])-numkey(key)) if numkey(x[0])is not None else 999999,
                                      stable(key+":"+x[0])))
        else:
            others.sort(key=lambda x:(abs(rows.index(x)-i),stable(key+":"+x[0])))
        chosen=others[:3]
        forward,reverse=link_questions(g,key,label)
        ref=f'{g["norm"]}; CEF, Tema {1 if g["topic"].startswith("Tema 1") else 2}, p. {g["page"]}'
        add(forward,code_label(g,key),[code_label(g,k) for k,l in chosen],g["topic"],ref,"memoria",2 if len(rows)>12 else 3)
        add(reverse,label,[l for k,l in chosen],g["topic"],ref,"inap",3)
for g in one_groups:
    for row in g["rows"]:
        prompt,ans,a,b,c,level,fmt=row
        ref=f'{g["reference"]}; CEF, págs. {g["pages"]}'
        add(prompt,ans,[a,b,c],g["topic"],ref,fmt,int(level))
original.extend(added)
assert len(added)>=500, f"Solo {len(added)} preguntas nuevas"
assert all(q["id"]==i+1 for i,q in enumerate(original))
for i,q in enumerate(original):
    assert isinstance(q["id"],int) and q["id"]==i+1
    assert q["answer"] in q["options"] and len(set(q["options"]))==4
    assert q["difficulty"] in (1,2,3)
    assert q.get("format","memoria") in ("memoria","inap")
    assert q["question"] and q["category"] and q["topic"]
for a,b in zip(old,original):
    assert a["id"]==b["id"] and a["question"]==b["question"] and a["answer"]==b["answer"]
    assert a["category"]==b["category"] and a["topic"]==b["topic"]
changes=[]
for a,b in zip(old,original):
    if set(a["options"])!=set(b["options"]):
        changes.append({"id":a["id"],"category":a["category"],"old":a["options"],"new":b["options"]})
with open(source,"w",encoding="utf-8") as out:json.dump(original,out,ensure_ascii=False,indent=2);out.write("\n")
summary={"old":len(old),"new":len(added),"total":len(original),"modified_distractors":len(changes),
         "changed_by_category":dict(collections.Counter(x["category"] for x in changes)),
         "new_by_topic":dict(collections.Counter(q["topic"] for q in added)),
         "new_by_format":dict(collections.Counter(q["format"] for q in added)),
         "maps_skipped":dict(skipped),"first_changes":changes[:12],
         "audit":{f"{k[0]} / {k[1]}":v for k,v in AUDIT.items()}}
(ROOT/"preparacion-financiera"/"informe_auditoria.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in summary.items() if k not in ("first_changes","audit")},ensure_ascii=False,indent=2))
