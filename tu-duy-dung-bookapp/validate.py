# -*- coding: utf-8 -*-
from content import CHAPTERS
from learning_data import GLOSSARY, TOOLS, CASES, build_quiz_for_lesson

VALID_STYLES={"flow","steps","matrix","compare","ladder","cycle"}
lessons=[l for c in CHAPTERS for l in c["lessons"]]
assert len(CHAPTERS)==10, f"Expected 10 chapters, got {len(CHAPTERS)}"
assert len(lessons)==40, f"Expected 40 lessons, got {len(lessons)}"
ids=[l["id"] for l in lessons]
assert len(ids)==len(set(ids)), "Duplicate lesson ids"
required=["id","title","summary","concept","apply","example","checklist","blocks","style","why","mistakes","practice","reflect"]
for l in lessons:
    miss=[k for k in required if k not in l]
    assert not miss, f"{l.get('id','?')} missing {miss}"
    assert l["title"].strip(), f"{l['id']} empty title"
    assert l["concept"].strip(), f"{l['id']} empty concept"
    assert l["apply"].strip(), f"{l['id']} empty apply"
    assert l["example"].strip(), f"{l['id']} empty example"
    assert isinstance(l["checklist"],list) and len(l["checklist"])>=3, f"{l['id']} invalid checklist"
    assert isinstance(l["blocks"],list) and len(l["blocks"])>=3, f"{l['id']} invalid blocks"
    assert all(isinstance(b,(list,tuple)) and len(b)>=2 for b in l["blocks"]), f"{l['id']} bad block"
    assert l["style"] in VALID_STYLES, f"{l['id']} invalid style"
    assert isinstance(l["mistakes"],list) and l["mistakes"], f"{l['id']} no mistakes"
    assert l["practice"].strip(), f"{l['id']} no practice"
    assert isinstance(l["reflect"],list) and l["reflect"], f"{l['id']} no reflect"
    quiz=build_quiz_for_lesson(l,lessons)
    assert len(quiz)>=2, f"{l['id']} quiz missing"
    for q in quiz:
        assert len(q["options"])>=3, f"{l['id']} quiz options"
        assert 0 <= q["answer"] < len(q["options"]), f"{l['id']} invalid answer"

assert len(GLOSSARY)>=35, "Glossary too small"
assert len(TOOLS)>=12, "Tool library too small"
assert len({t['id'] for t in TOOLS})==len(TOOLS), "Duplicate tool ids"
assert len(CASES)>=8, "Case library too small"
assert len({c['id'] for c in CASES})==len(CASES), "Duplicate case ids"
for c in CASES:
    assert len(c['options'])>=3 and 0<=c['answer']<len(c['options']), f"Bad case {c['id']}"

print(f"Validated V2.5: {len(CHAPTERS)} chapters, {len(lessons)} lessons, {len(TOOLS)} tools, {len(CASES)} cases, {len(GLOSSARY)} glossary terms.")
