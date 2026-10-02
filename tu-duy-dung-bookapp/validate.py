# -*- coding: utf-8 -*-
from content import CHAPTERS
from stories import STORIES
from learning_data import GLOSSARY, TOOLS, CASES, build_quiz_for_lesson
from i18n_en import UI, EN_CHAPTERS, EN_LESSONS
from i18n_extra import EN_STORIES, EN_GLOSSARY, EN_TOOLS, EN_CASES

VALID_STYLES={"flow","steps","matrix","compare","ladder","cycle"}
lessons=[l for c in CHAPTERS for l in c["lessons"]]
assert len(CHAPTERS)==10, f"Expected 10 chapters, got {len(CHAPTERS)}"
assert len(lessons)==40, f"Expected 40 lessons, got {len(lessons)}"
ids=[l["id"] for l in lessons]
assert len(ids)==len(set(ids)), "Duplicate lesson ids"

required=["id","title","summary","concept","example","checklist","blocks","style","why","mistakes","practice","reflect"]
for l in lessons:
    miss=[k for k in required if k not in l]
    assert not miss, f"{l.get('id','?')} missing {miss}"
    assert l["title"].strip(), f"{l['id']} empty title"
    assert l["concept"].strip(), f"{l['id']} empty concept"
    apply_text=l.get("apply", l.get("method", ""))
    assert isinstance(apply_text,str) and apply_text.strip(), f"{l['id']} empty apply/method"
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

assert len(STORIES)==40 and set(STORIES)==set(ids), "Vietnamese stories mismatch"

# V2.7 bilingual coverage
assert set(EN_CHAPTERS)==set(range(1,11)), "English chapter translations incomplete"
assert set(EN_LESSONS)==set(ids), "English lesson IDs must match all 40 lessons"
assert set(EN_STORIES)==set(ids), "English story IDs must match all 40 lessons"
en_required=["title","summary","concept","method","example","blocks","why","mistakes","practice","reflect"]
for lid in ids:
    e=EN_LESSONS[lid]
    miss=[k for k in en_required if k not in e]
    assert not miss, f"{lid} EN missing {miss}"
    assert all(str(e[k]).strip() for k in ["title","summary","concept","method","example","why","practice"]), f"{lid} empty EN field"
    assert isinstance(e["blocks"],list) and len(e["blocks"])>=3, f"{lid} EN blocks invalid"
    assert isinstance(e["mistakes"],list) and e["mistakes"], f"{lid} EN mistakes missing"
    assert isinstance(e["reflect"],list) and e["reflect"], f"{lid} EN reflect missing"
    s=EN_STORIES[lid]
    assert s["title"].strip() and len(s["story"].strip())>=120 and s["memory"].strip(), f"{lid} EN story invalid"

assert set(EN_GLOSSARY)==set(GLOSSARY), "English glossary coverage mismatch"
tool_ids={t["id"] for t in TOOLS}
case_ids={c["id"] for c in CASES}
assert set(EN_TOOLS)==tool_ids, "English tool translations mismatch"
assert set(EN_CASES)==case_ids, "English case translations mismatch"
assert len(UI)>=30, "Bilingual UI dictionary too small"

for tid in tool_ids:
    e=EN_TOOLS[tid]
    assert e["when"].strip() and e["output"].strip() and e["steps"] and e["mistakes"], f"{tid} EN tool invalid"
for cid in case_ids:
    e=EN_CASES[cid]
    assert e["title"].strip() and e["situation"].strip() and e["question"].strip(), f"{cid} EN case invalid"
    assert len(e["options"])>=3 and 0<=e["answer"]<len(e["options"]), f"{cid} EN case options invalid"

print(f"Validated V2.7 bilingual edition: 10 chapters, {len(lessons)} lessons, 40 stories, {len(TOOLS)} tools, {len(CASES)} cases, {len(GLOSSARY)} glossary terms.")
