# -*- coding: utf-8 -*-
"""Export the desktop V4.2 content into one offline JSON asset for the mobile app."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOBILE = HERE.parent
ROOT = MOBILE.parent
DESKTOP = ROOT / "tu-duy-dung-bookapp"
OUT = MOBILE / "src" / "data" / "book.json"
sys.path.insert(0, str(DESKTOP))

from content import CHAPTERS
from stories import STORIES
from learning_data import GLOSSARY, TOOLS, CASES, build_quiz_for_lesson
from i18n_en import UI, EN_CHAPTERS, EN_LESSONS
from i18n_extra import EN_STORIES, EN_GLOSSARY, EN_TOOLS, EN_CASES
from v42_data import MULTI_CASES, WORKBENCH_TEMPLATES, flashcard_for_lesson

lessons = [lesson for chapter in CHAPTERS for lesson in chapter["lessons"]]


def build_quiz_en(lesson_id):
    lesson = EN_LESSONS[lesson_id]
    questions = []
    blocks = lesson.get("blocks", [])

    def other_values(field):
        values = []
        for oid, other in EN_LESSONS.items():
            if oid == lesson_id:
                continue
            value = other.get(field)
            if isinstance(value, str) and value.strip() and value not in values:
                values.append(value)
        return values

    if blocks:
        correct = blocks[0][1]
        distractors = [b[1] for b in blocks[1:4]]
        for oid, other in EN_LESSONS.items():
            if len(distractors) >= 3:
                break
            ob = other.get("blocks", [])
            if oid != lesson_id and ob:
                val = ob[0][1]
                if val != correct and val not in distractors:
                    distractors.append(val)
        questions.append({
            "question": f'In “{lesson["title"]}”, what best describes {blocks[0][0]}?',
            "options": [correct] + distractors[:3],
            "answer": 0,
            "explain": f'{blocks[0][0]}: {correct}',
        })

    mistakes = lesson.get("mistakes", [])
    if mistakes:
        correct = mistakes[0]
        distractors = []
        for text in lesson.get("reflect", []) + [
            "Always wait for perfect data before deciding",
            "Follow habit without defining the objective",
            "Use activity as the outcome",
        ]:
            if text != correct and text not in distractors:
                distractors.append(text)
        questions.append({
            "question": f'Which is a common mistake when applying “{lesson["title"]}”?',
            "options": [correct] + distractors[:3],
            "answer": 0,
            "explain": correct,
        })

    why = lesson.get("why", "")
    if why:
        questions.append({
            "question": f'Why does “{lesson["title"]}” matter?',
            "options": [why] + other_values("why")[:3],
            "answer": 0,
            "explain": why,
        })

    practice = lesson.get("practice", "")
    if practice:
        questions.append({
            "question": f'Which exercise best applies “{lesson["title"]}”?',
            "options": [practice] + other_values("practice")[:3],
            "answer": 0,
            "explain": practice,
        })
    return questions[:4]


payload = {
    "version": "4.2",
    "chapters": CHAPTERS,
    "stories": STORIES,
    "glossary": GLOSSARY,
    "tools": TOOLS,
    "cases": CASES,
    "ui": UI,
    "enChapters": EN_CHAPTERS,
    "enLessons": EN_LESSONS,
    "enStories": EN_STORIES,
    "enGlossary": EN_GLOSSARY,
    "enTools": EN_TOOLS,
    "enCases": EN_CASES,
    "multiCases": MULTI_CASES,
    "workbenchTemplates": WORKBENCH_TEMPLATES,
    "quizVi": {lesson["id"]: build_quiz_for_lesson(lesson, lessons) for lesson in lessons},
    "quizEn": {lesson["id"]: build_quiz_en(lesson["id"]) for lesson in lessons},
    "flashcards": {
        lesson["id"]: flashcard_for_lesson(lesson, EN_LESSONS[lesson["id"]])
        for lesson in lessons
    },
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Exported mobile data: {OUT} ({OUT.stat().st_size} bytes)")
