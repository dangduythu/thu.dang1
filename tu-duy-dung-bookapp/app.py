# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from content import CHAPTERS
from stories import STORIES
from learning_data import GLOSSARY, TOOLS, CASES, build_quiz_for_lesson
from i18n_en import UI, EN_CHAPTERS, EN_LESSONS
from i18n_extra import EN_STORIES, EN_GLOSSARY, EN_TOOLS, EN_CASES
from v42_data import MULTI_CASES, WORKBENCH_TEMPLATES, default_review_state, next_review, flashcard_for_lesson

APP_NAME = "Tư Duy Đúng / Think Right – Book App"
VERSION = "4.2"
APP_DIR = "TuDuyDungBookApp"

BG = "#edf3fb"
PANEL = "#ffffff"
TEXT = "#14213d"
MUTED = "#64748b"
LINE = "#d8e3f0"
NAVY = "#274472"

PALETTES = {
    "flow": dict(primary="#2563eb", soft="#dbeafe", accent="#16a34a", accent2="#dcfce7", alt="#f59e0b", alt2="#fef3c7"),
    "steps": dict(primary="#7c3aed", soft="#ede9fe", accent="#0ea5e9", accent2="#e0f2fe", alt="#f97316", alt2="#ffedd5"),
    "matrix": dict(primary="#059669", soft="#d1fae5", accent="#0f766e", accent2="#ccfbf1", alt="#f59e0b", alt2="#fef3c7"),
    "compare": dict(primary="#dc2626", soft="#fee2e2", accent="#2563eb", accent2="#dbeafe", alt="#7c3aed", alt2="#f3e8ff"),
    "ladder": dict(primary="#ea580c", soft="#ffedd5", accent="#2563eb", accent2="#dbeafe", alt="#16a34a", alt2="#dcfce7"),
    "cycle": dict(primary="#0f766e", soft="#ccfbf1", accent="#7c3aed", accent2="#ede9fe", alt="#2563eb", alt2="#dbeafe"),
}


def state_path():
    p = Path(os.getenv("APPDATA", str(Path.home()))) / APP_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p / "state.json"


def build_quiz_en(lesson_id):
    """Four deterministic English review questions per lesson."""
    l=EN_LESSONS[lesson_id]
    q=[]
    blocks=l.get("blocks",[])

    def other_values(field):
        vals=[]
        for oid,other in EN_LESSONS.items():
            if oid==lesson_id: continue
            value=other.get(field)
            if isinstance(value,str) and value.strip() and value not in vals:
                vals.append(value)
        return vals

    if blocks:
        correct=blocks[0][1]
        distractors=[b[1] for b in blocks[1:4]]
        for oid,other in EN_LESSONS.items():
            if len(distractors)>=3: break
            ob=other.get("blocks",[])
            if oid!=lesson_id and ob:
                val=ob[0][1]
                if val!=correct and val not in distractors:distractors.append(val)
        q.append({"question":f'In “{l["title"]}”, what best describes {blocks[0][0]}?',
                  "options":[correct]+distractors[:3],"answer":0,"explain":f'{blocks[0][0]}: {correct}'})

    mistakes=l.get("mistakes",[])
    if mistakes:
        correct=mistakes[0]
        distractors=[]
        for text in l.get("reflect",[])+["Always wait for perfect data before deciding","Follow habit without defining the objective","Use activity as the outcome"]:
            if text!=correct and text not in distractors:distractors.append(text)
        q.append({"question":f'Which is a common mistake when applying “{l["title"]}”?',
                  "options":[correct]+distractors[:3],"answer":0,"explain":correct})

    why=l.get("why","")
    if why:
        q.append({"question":f'Why does “{l["title"]}” matter?',
                  "options":[why]+other_values("why")[:3],"answer":0,"explain":why})

    practice=l.get("practice","")
    if practice:
        q.append({"question":f'Which exercise best applies “{l["title"]}”?',
                  "options":[practice]+other_values("practice")[:3],"answer":0,"explain":practice})
    return q[:4]


class ScrollableFrame(tk.Frame):
    def __init__(self, master, bg=BG):
        super().__init__(master, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._sync_region)
        self.canvas.bind("<Configure>", self._sync_width)

    def _sync_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_width(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def scroll_units(self, units):
        self.canvas.yview_scroll(units, "units")

    def top(self):
        self.canvas.yview_moveto(0)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} V{VERSION}")
        self.geometry("1500x940")
        self.minsize(1200, 760)
        self.configure(bg=BG)

        st = self._load_state()
        self.bookmarks = set(st.get("bookmarks", []))
        self.read_lessons = set(st.get("read_lessons", []))
        self.quiz_scores = dict(st.get("quiz_scores", {}))
        self.case_results = dict(st.get("case_results", {}))
        self.notes = dict(st.get("notes", {}))
        self.workbench_docs = dict(st.get("workbench_docs", {}))
        self.review_state = dict(st.get("review_state", {}))
        self.lesson_scroll = dict(st.get("lesson_scroll", {}))
        self.current_lesson = st.get("last_lesson", "1.1")
        self.font_size = int(st.get("font_size", 12))
        self.language_mode = st.get("language_mode", "BI")
        if self.language_mode not in ("BI", "VI", "EN"):
            self.language_mode = "BI"

        self.lessons = [l for ch in CHAPTERS for l in ch["lessons"]]
        self.lesson_by_id = {l["id"]: l for l in self.lessons}
        if self.current_lesson not in self.lesson_by_id:
            self.current_lesson = "1.1"
        self.quiz_vi = {l["id"]: build_quiz_for_lesson(l, self.lessons) for l in self.lessons}
        self.quiz_en = {l["id"]: build_quiz_en(l["id"]) for l in self.lessons}
        self.tool_by_id = {x["id"]: x for x in TOOLS}
        self.case_by_id = {x["id"]: x for x in CASES}
        self.current_quiz_lesson = self.current_lesson
        self.current_case_id = CASES[0]["id"] if CASES else None
        self.current_tool_id = TOOLS[0]["id"] if TOOLS else None
        self.current_multi_case = MULTI_CASES[0]["id"] if MULTI_CASES else None
        self.current_workbench = WORKBENCH_TEMPLATES[0]["id"] if WORKBENCH_TEMPLATES else None
        self.current_flash_index = 0
        self.current_view = "home"
        self.focus_mode = False
        self.block_tree_event = False
        self._rendering_lesson = False

        self.search_var = tk.StringVar()
        self.progress_var = tk.StringVar()
        self.bookmark_var = tk.StringVar()
        self.glossary_search_var = tk.StringVar()
        self.tool_search_var = tk.StringVar()
        self.language_var = tk.StringVar(value=self.language_mode)
        self.note_status_var = tk.StringVar()
        self.flash_answer_visible = False

        for lid in self.lesson_by_id:
            if lid not in self.review_state:
                self.review_state[lid] = default_review_state([lid])[lid]

        self._configure_styles()
        self._build_shell()
        self.populate_tree()
        self.show_home()

        self.bind_all("<MouseWheel>", self._global_mousewheel, add="+")
        self.bind_all("<Button-4>", self._global_mousewheel_linux, add="+")
        self.bind_all("<Button-5>", self._global_mousewheel_linux, add="+")
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def _load_state(self):
        try:
            return json.loads(state_path().read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_state(self):
        payload = {
            "bookmarks": sorted(self.bookmarks),
            "read_lessons": sorted(self.read_lessons),
            "quiz_scores": self.quiz_scores,
            "case_results": self.case_results,
            "notes": self.notes,
            "workbench_docs": self.workbench_docs,
            "review_state": self.review_state,
            "lesson_scroll": self.lesson_scroll,
            "last_lesson": self.current_lesson,
            "font_size": self.font_size,
            "language_mode": self.language_mode,
        }
        try:
            state_path().write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _configure_styles(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self.style.configure("TButton", padding=(9, 7), font=("Segoe UI", 10))
        self.style.configure("Nav.TButton", padding=(9, 8), font=("Segoe UI", 9, "bold"))
        self.style.configure("Treeview", rowheight=30, font=("Segoe UI", 9), fieldbackground="white", background="white")
        self.style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#0f172a")])

    def _ui(self, key):
        vi, en = UI[key]
        if self.language_mode == "VI":
            return vi
        if self.language_mode == "EN":
            return en
        return f"{vi} / {en}"

    def _text(self, vi, en):
        if self.language_mode == "VI":
            return vi
        if self.language_mode == "EN":
            return en
        return f"{vi}\n{en}"

    def _build_shell(self):
        top = tk.Frame(self, bg="white", height=74)
        top.pack(fill="x")
        top.pack_propagate(False)
        brand = tk.Frame(top, bg="white")
        brand.pack(side="left", padx=(18, 6))
        tk.Label(brand, text="TƯ DUY ĐÚNG", bg="white", fg=NAVY, font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(brand, text="THINK RIGHT • BOOK APP • V4.2", bg="white", fg="#7a8aa0", font=("Segoe UI", 8, "bold")).pack(anchor="w")

        nav = tk.Frame(top, bg="white")
        nav.pack(side="right", padx=12)
        for key, cmd in [
            ("home", self.show_home), ("read", self.continue_reading), ("quiz", self.show_quiz),
            ("cases", self.show_cases), ("tools", self.show_tools), ("glossary", self.show_glossary),
            ("progress", self.show_progress)
        ]:
            ttk.Button(nav, text=self._ui(key), command=cmd, style="Nav.TButton").pack(side="left", padx=2, pady=16)
        ttk.Button(nav, text="A−", width=4, command=lambda: self.change_font(-1)).pack(side="left", padx=(6,2), pady=16)
        ttk.Button(nav, text="A+", width=4, command=lambda: self.change_font(1)).pack(side="left", padx=2, pady=16)
        self.lang_combo = ttk.Combobox(nav, values=["BI", "VI", "EN"], textvariable=self.language_var, state="readonly", width=4)
        self.lang_combo.pack(side="left", padx=(8,0), pady=16)
        self.lang_combo.bind("<<ComboboxSelected>>", self._change_language)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        self.sidebar = tk.Frame(body, bg="white", width=340)
        self.sidebar.pack(side="left", fill="y", padx=(10,8), pady=10)
        self.sidebar.pack_propagate(False)
        self.main = tk.Frame(body, bg=BG)
        self.main.pack(side="left", fill="both", expand=True, padx=(0,10), pady=10)

        self._build_sidebar()
        self.views = {}
        for name in ["home","lesson","quiz","cases","tools","glossary","progress"]:
            self.views[name] = ScrollableFrame(self.main, BG)

    def _build_sidebar(self):
        banner = tk.Canvas(self.sidebar, height=125, bg="white", highlightthickness=0)
        banner.pack(fill="x", padx=14, pady=(14,10))
        banner.create_rectangle(0,0,310,125,fill="#8eb1df",outline="")
        banner.create_rectangle(0,88,310,125,fill="#e6a8a8",outline="")
        banner.create_text(14,14,anchor="nw",text="TƯ DUY ĐÚNG",fill="#fff59d",font=("Segoe UI",15,"bold"))
        banner.create_text(14,42,anchor="nw",text="THINK RIGHT",fill="white",font=("Segoe UI",17,"bold"))
        banner.create_text(14,71,anchor="nw",text="VIỆT • ENGLISH",fill="white",font=("Segoe UI",12,"bold"))
        banner.create_text(294,105,anchor="e",text=f"V{VERSION}",fill="white",font=("Segoe UI",9,"bold"))

        sr = tk.Frame(self.sidebar,bg="white")
        sr.pack(fill="x",padx=14,pady=(0,8))
        self.search_entry = ttk.Entry(sr,textvariable=self.search_var)
        self.search_entry.pack(side="left",fill="x",expand=True)
        self.search_entry.bind("<Return>",lambda e:self.search_lessons())
        ttk.Button(sr,text=self._ui("search"),width=11,command=self.search_lessons).pack(side="left",padx=(5,0))

        br=tk.Frame(self.sidebar,bg="white")
        br.pack(fill="x",padx=14,pady=(0,8))
        ttk.Button(br,text=self._ui("contents"),command=self.populate_tree).pack(side="left",fill="x",expand=True)
        ttk.Button(br,text="★ "+self._ui("saved"),command=self.show_bookmarks).pack(side="left",fill="x",expand=True,padx=(5,0))

        tk.Label(self.sidebar,textvariable=self.progress_var,bg="white",fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=14)
        self.progress_bar=ttk.Progressbar(self.sidebar,maximum=100)
        self.progress_bar.pack(fill="x",padx=14,pady=(5,10))

        wrap=tk.Frame(self.sidebar,bg="white")
        wrap.pack(fill="both",expand=True,padx=(10,7),pady=(0,10))
        self.tree=ttk.Treeview(wrap,show="tree",selectmode="browse")
        sb=ttk.Scrollbar(wrap,orient="vertical",command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left",fill="both",expand=True)
        sb.pack(side="right",fill="y")
        self.tree.bind("<<TreeviewSelect>>",self._tree_pick)

    def _change_language(self, _event=None):
        self.language_mode = self.language_var.get()
        self._save_state()
        self.populate_tree()
        # top nav text is fixed until restart; content and reading areas update immediately
        if self.current_view == "home":
            self.show_home()
        elif self.current_view == "lesson":
            self.show_lesson(self.current_lesson)
        elif self.current_view == "quiz":
            self.show_quiz(self.current_quiz_lesson)
        elif self.current_view == "cases":
            self.show_cases(self.current_case_id)
        elif self.current_view == "tools":
            self.show_tools(self.current_tool_id)
        elif self.current_view == "glossary":
            self.show_glossary()
        elif self.current_view == "progress":
            self.show_progress()

    def _activate_view(self,name):
        for v in self.views.values():
            v.pack_forget()
        self.views[name].pack(fill="both",expand=True)
        self.views[name].top()
        self.current_view=name

    def _clear(self,parent):
        for w in parent.winfo_children():
            w.destroy()

    def _is_descendant(self,widget,ancestor):
        cur=widget
        while cur is not None:
            if cur==ancestor:return True
            try:cur=cur.master
            except Exception:return False
        return False

    def _scroll_target(self,event):
        try:w=self.winfo_containing(event.x_root,event.y_root)
        except Exception:return None
        if w is None or self._is_descendant(w,self.tree):return None
        v=self.views.get(self.current_view)
        if v and v.winfo_ismapped() and (self._is_descendant(w,v.canvas) or self._is_descendant(w,v.inner)):
            return v
        return None

    def _global_mousewheel(self,event):
        target=self._scroll_target(event)
        if target is None:return
        if not event.delta:return "break"
        steps=max(1,abs(int(event.delta/120))) if abs(event.delta)>=120 else 1
        target.scroll_units(-steps if event.delta>0 else steps)
        return "break"

    def _global_mousewheel_linux(self,event):
        target=self._scroll_target(event)
        if target is None:return
        target.scroll_units(-1 if event.num==4 else 1)
        return "break"

    def populate_tree(self,items=None):
        self.block_tree_event=True
        self.tree.delete(*self.tree.get_children())
        if items is None:
            for ci,ch in enumerate(CHAPTERS,1):
                ent=EN_CHAPTERS[ci]
                title=self._text(ch["title"],ent["title"]).replace("\n"," | ")
                parent=self.tree.insert("","end",iid=f"c{ci}",text=title,open=ci<=3)
                for l in ch["lessons"]:
                    en=EN_LESSONS[l["id"]]
                    name=self._text(l["title"],en["title"]).replace("\n"," | ")
                    pre="✓ " if l["id"] in self.read_lessons else ""
                    suf=" ★" if l["id"] in self.bookmarks else ""
                    self.tree.insert(parent,"end",iid="l"+l["id"],text=f'{pre}{l["id"]}  {name}{suf}')
        else:
            for l in items:
                en=EN_LESSONS[l["id"]]
                name=self._text(l["title"],en["title"]).replace("\n"," | ")
                self.tree.insert("","end",iid="l"+l["id"],text=f'{l["id"]}  {name}')
        self.block_tree_event=False
        self._update_progress_label()

    def _tree_pick(self,_event=None):
        if self.block_tree_event:return
        sel=self.tree.selection()
        if not sel or not sel[0].startswith("l"):return
        lid=sel[0][1:]
        if lid not in self.lesson_by_id:return
        if self.current_view=="lesson" and lid==self.current_lesson:return
        self.show_lesson(lid)

    def _select_tree(self,lid):
        iid="l"+lid
        if not self.tree.exists(iid):return
        if self.tree.selection()==(iid,):
            self.tree.see(iid); return
        self.block_tree_event=True
        try:
            self.tree.selection_set(iid); self.tree.see(iid)
        finally:
            self.block_tree_event=False

    def search_lessons(self):
        q=self.search_var.get().strip().lower()
        if not q:
            self.populate_tree(); return
        found=[]
        for l in self.lessons:
            e=EN_LESSONS[l["id"]]
            vi=" ".join([l.get("id",""),l.get("title",""),l.get("summary",""),l.get("concept",""),l.get("method",""),l.get("example",""),l.get("why",""),l.get("practice","")," ".join(l.get("mistakes",[]))," ".join(l.get("reflect",[]))]).lower()
            en=" ".join([e.get("title",""),e.get("summary",""),e.get("concept",""),e.get("method",""),e.get("example",""),e.get("why",""),e.get("practice","")," ".join(e.get("mistakes",[]))," ".join(e.get("reflect",[]))]).lower()
            if q in vi or q in en:found.append(l)
        self.populate_tree(found)
        if not found:messagebox.showinfo("Search / Tìm kiếm","Không tìm thấy / No matching lesson.")

    def show_bookmarks(self):
        items=[l for l in self.lessons if l["id"] in self.bookmarks]
        self.populate_tree(items)
        if not items:messagebox.showinfo("Saved / Đã lưu","Chưa có bài nào được lưu / No saved lessons yet.")

    def _update_progress_label(self):
        total=len(self.lessons)
        done=len(self.read_lessons & set(self.lesson_by_id))
        pct=round(done*100/total) if total else 0
        self.progress_var.set(f"{self._ui('reading_progress').upper()}  {done}/{total} • {pct}%")
        self.progress_bar["value"]=pct

    def _section_title(self,parent,title_vi,title_en,sub_vi="",sub_en=""):
        box=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=LINE)
        box.pack(fill="x",pady=(0,12))
        inn=tk.Frame(box,bg="white"); inn.pack(fill="x",padx=22,pady=17)
        tk.Label(inn,text=self._text(title_vi,title_en),bg="white",fg=TEXT,font=("Segoe UI",23,"bold"),anchor="w",justify="left").pack(fill="x")
        if sub_vi or sub_en:
            tk.Label(inn,text=self._text(sub_vi,sub_en),bg="white",fg=MUTED,font=("Segoe UI",11),anchor="w",justify="left",wraplength=1050).pack(fill="x",pady=(5,0))

    def _static_label(self,parent,text,bg="white",fg=TEXT,font=None,wrap=490,bullet=False):
        """Stable wrapped label: no <Configure> binding and no after_idle loop."""
        label=tk.Label(
            parent,
            text=("• "+text if bullet else text),
            bg=bg,fg=fg,
            font=font or ("Segoe UI",self.font_size+1),
            justify="left",anchor="w",
            wraplength=max(180,int(wrap))
        )
        label.pack(anchor="w",fill="x")
        return label

    def _language_badge(self,parent,text,fg,bg="white"):
        tk.Label(parent,text=text,bg=bg,fg=fg,font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(0,3))

    def _bi_body(self,parent,vi,en,width=490,bg="white"):
        """
        Stable bilingual layout for V2.7.2.
        In BI mode the content is stacked VI -> EN, so each language uses the
        full card width. No dynamic Configure handlers are used.
        """
        wrap=max(220,int(width))
        if self.language_mode=="VI":
            self._static_label(parent,vi,bg=bg,wrap=wrap)
            return
        if self.language_mode=="EN":
            self._static_label(parent,en,bg=bg,wrap=wrap)
            return

        vi_box=tk.Frame(parent,bg=bg)
        vi_box.pack(fill="x")
        self._language_badge(vi_box,"VI • TIẾNG VIỆT","#2563eb",bg)
        self._static_label(vi_box,vi,bg=bg,wrap=wrap)

        tk.Frame(parent,bg="#e5e7eb",height=1).pack(fill="x",pady=9)

        en_box=tk.Frame(parent,bg=bg)
        en_box.pack(fill="x")
        self._language_badge(en_box,"EN • ENGLISH","#7c3aed",bg)
        self._static_label(en_box,en,bg=bg,wrap=wrap)

    def _card(self,parent,title_vi,title_en,vi,en,hbg="#dbeafe",hfg="#1d4ed8"):
        c=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=LINE)
        h=tk.Frame(c,bg=hbg); h.pack(fill="x")
        title=self._text(title_vi,title_en).replace("\n"," / ")
        tk.Label(
            h,text=title,bg=hbg,fg=hfg,font=("Segoe UI",14,"bold"),
            anchor="w",justify="left",wraplength=520
        ).pack(fill="x",padx=14,pady=9)

        body=tk.Frame(c,bg="white")
        body.pack(fill="both",expand=True,padx=15,pady=13)
        self._bi_body(body,vi,en,width=500)
        return c

    def _list_card(self,parent,title_vi,title_en,vi_items,en_items,hbg,hfg):
        c=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=LINE)
        h=tk.Frame(c,bg=hbg); h.pack(fill="x")
        title=self._text(title_vi,title_en).replace("\n"," / ")
        tk.Label(
            h,text=title,bg=hbg,fg=hfg,font=("Segoe UI",14,"bold"),
            anchor="w",justify="left",wraplength=520
        ).pack(fill="x",padx=14,pady=9)

        body=tk.Frame(c,bg="white")
        body.pack(fill="both",expand=True,padx=15,pady=10)

        def render_list(container,items,badge=None,badge_fg="#2563eb"):
            if badge:
                self._language_badge(container,badge,badge_fg,"white")
            if not items:
                self._static_label(container,self._text("Chưa có nội dung.","No content yet."),bg="white",fg=MUTED,wrap=500)
                return
            for item in items:
                holder=tk.Frame(container,bg="white")
                holder.pack(fill="x",pady=2)
                self._static_label(holder,str(item),bg="white",bullet=True,wrap=500)

        if self.language_mode=="VI":
            render_list(body,vi_items)
        elif self.language_mode=="EN":
            render_list(body,en_items)
        else:
            vi_box=tk.Frame(body,bg="white")
            vi_box.pack(fill="x")
            render_list(vi_box,vi_items,"VI • TIẾNG VIỆT","#2563eb")

            tk.Frame(body,bg="#e5e7eb",height=1).pack(fill="x",pady=9)

            en_box=tk.Frame(body,bg="white")
            en_box.pack(fill="x")
            render_list(en_box,en_items,"EN • ENGLISH","#7c3aed")
        return c

    def show_home(self):
        self._activate_view("home")
        v=self.views["home"].inner; self._clear(v)
        hero=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); hero.pack(fill="x",pady=(0,12))
        inn=tk.Frame(hero,bg="white"); inn.pack(fill="x",padx=28,pady=25)
        tk.Label(inn,text="TƯ DUY ĐÚNG • THINK RIGHT",bg="white",fg="#7a8aa0",font=("Segoe UI",11,"bold")).pack(anchor="w")
        tk.Label(inn,text="Book App V2.7.2 • Vietnamese – English",bg="white",fg=TEXT,font=("Segoe UI",30,"bold")).pack(anchor="w",pady=(7,3))
        tk.Label(inn,text=self._text("Sách tương tác song ngữ: đọc – hiểu – nhớ – áp dụng.","A bilingual interactive book: read – understand – remember – apply."),bg="white",fg=MUTED,font=("Segoe UI",12),justify="left").pack(anchor="w")
        actions=tk.Frame(inn,bg="white"); actions.pack(anchor="w",pady=(15,0))
        ttk.Button(actions,text="▶ "+self._ui("continue"),command=self.continue_reading).pack(side="left")
        ttk.Button(actions,text=self._ui("quiz"),command=self.show_quiz).pack(side="left",padx=6)
        ttk.Button(actions,text=self._ui("cases"),command=self.show_cases).pack(side="left",padx=6)

        grid=tk.Frame(v,bg=BG); grid.pack(fill="both",expand=True)
        for i,ch in enumerate(CHAPTERS,1):
            e=EN_CHAPTERS[i]; p=list(PALETTES.values())[(i-1)%len(PALETTES)]
            card=tk.Frame(grid,bg="white",bd=1,relief="solid",highlightbackground=LINE)
            card.grid(row=(i-1)//2,column=(i-1)%2,sticky="nsew",padx=6,pady=6)
            grid.grid_columnconfigure((i-1)%2,weight=1)
            h=tk.Frame(card,bg=p["soft"]); h.pack(fill="x")
            tk.Label(h,text=f"{i:02}",bg=p["soft"],fg=p["primary"],font=("Segoe UI",20,"bold")).pack(side="left",padx=13,pady=12)
            tb=tk.Frame(h,bg=p["soft"]); tb.pack(side="left",fill="both",expand=True,pady=9)
            tk.Label(tb,text=self._text(ch["title"],e["title"]),bg=p["soft"],fg=TEXT,font=("Segoe UI",11,"bold"),anchor="w",justify="left",wraplength=500).pack(fill="x")
            tk.Label(tb,text=self._text(ch["subtitle"],e["subtitle"]),bg=p["soft"],fg=MUTED,font=("Segoe UI",9),anchor="w",justify="left",wraplength=500).pack(fill="x",pady=(2,0))
            ft=tk.Frame(card,bg="white"); ft.pack(fill="x",padx=13,pady=10)
            tk.Label(ft,text=f'{len(ch["lessons"])} {self._ui("lesson").lower()}',bg="white",fg=MUTED,font=("Segoe UI",9,"bold")).pack(side="left")
            ttk.Button(ft,text=self._text("Mở chương","Open chapter").replace("\n"," / "),command=lambda idx=i-1:self.open_chapter(idx)).pack(side="right")

    def continue_reading(self):
        self.show_lesson(self.current_lesson)

    def open_chapter(self,idx):
        if CHAPTERS[idx]["lessons"]:self.show_lesson(CHAPTERS[idx]["lessons"][0]["id"])

    def show_lesson(self,lid):
        if lid not in self.lesson_by_id or self._rendering_lesson:return
        self._rendering_lesson=True
        try:self._show_lesson_impl(lid)
        finally:self._rendering_lesson=False

    def _show_lesson_impl(self,lid):
        self.current_lesson=lid
        self._activate_view("lesson")
        v=self.views["lesson"].inner; self._clear(v)
        vi=self.lesson_by_id[lid]; en=EN_LESSONS[lid]
        p=PALETTES.get(vi.get("style"),PALETTES["flow"])

        head=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); head.pack(fill="x",pady=(0,12))
        hi=tk.Frame(head,bg="white"); hi.pack(fill="x",padx=20,pady=16)
        left=tk.Frame(hi,bg="white"); left.pack(side="left",fill="both",expand=True)
        tk.Label(left,text=f'{self._ui("lesson").upper()} {lid}',bg="white",fg=p["primary"],font=("Segoe UI",10,"bold")).pack(anchor="w")
        tk.Label(left,text=self._text(vi["title"],en["title"]),bg="white",fg=TEXT,font=("Segoe UI",27,"bold"),anchor="w",justify="left",wraplength=870).pack(anchor="w",pady=(5,4))
        tk.Label(left,text=self._text(vi["summary"],en["summary"]),bg="white",fg=MUTED,font=("Segoe UI",12),anchor="w",justify="left",wraplength=880).pack(anchor="w")
        controls=tk.Frame(hi,bg="white"); controls.pack(side="right",padx=(12,0))
        self.bookmark_var.set(("★ " if lid in self.bookmarks else "☆ ")+self._ui("saved" if lid in self.bookmarks else "save_lesson"))
        ttk.Button(controls,textvariable=self.bookmark_var,command=self.toggle_bookmark).pack(side="left",padx=3)
        ttk.Button(controls,text="✓ "+self._ui("mark_read"),command=self.mark_read).pack(side="left",padx=3)
        ttk.Button(controls,text=self._ui("lesson_quiz"),command=lambda:self.show_quiz(lid)).pack(side="left",padx=3)

        self._render_diagram(v,vi,en,p)
        self._render_story(v,lid,p)

        r1=tk.Frame(v,bg=BG); r1.pack(fill="x",pady=(0,10))
        self._card(r1,*UI["concept"],vi["concept"],en["concept"],p["soft"],p["primary"]).pack(side="left",fill="both",expand=True,padx=(0,5))
        self._card(r1,*UI["application"],vi.get("method",""),en["method"],p["accent2"],p["accent"]).pack(side="left",fill="both",expand=True,padx=(5,0))

        r2=tk.Frame(v,bg=BG); r2.pack(fill="x",pady=(0,10))
        self._card(r2,*UI["why"],vi.get("why",""),en["why"],"#fff7ed","#c2410c").pack(side="left",fill="both",expand=True,padx=(0,5))
        self._list_card(r2,*UI["mistakes"],vi.get("mistakes",[]),en["mistakes"],"#fee2e2","#b91c1c").pack(side="left",fill="both",expand=True,padx=(5,0))

        r3=tk.Frame(v,bg=BG); r3.pack(fill="x",pady=(0,10))
        self._card(r3,*UI["example"],vi.get("example",""),en["example"],p["alt2"],p["alt"]).pack(side="left",fill="both",expand=True,padx=(0,5))
        self._list_card(r3,*UI["checklist"],vi.get("checklist",[]),self._english_checklist(en),p["accent2"],p["accent"]).pack(side="left",fill="both",expand=True,padx=(5,0))

        r4=tk.Frame(v,bg=BG); r4.pack(fill="x",pady=(0,10))
        self._card(r4,*UI["practice"],vi.get("practice",""),en["practice"],"#f3e8ff","#7e22ce").pack(side="left",fill="both",expand=True,padx=(0,5))
        self._list_card(r4,*UI["reflection"],vi.get("reflect",[]),en["reflect"],"#ecfeff","#0e7490").pack(side="left",fill="both",expand=True,padx=(5,0))

        bottom=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); bottom.pack(fill="x")
        bi=tk.Frame(bottom,bg="white"); bi.pack(fill="x",padx=16,pady=13)
        tk.Label(bi,text=self._ui("main_lesson").upper(),bg="white",fg=p["primary"],font=("Segoe UI",14,"bold")).pack(anchor="w")
        vnames=" → ".join(str(x[0]) for x in vi.get("blocks",[]))
        enames=" → ".join(str(x[0]) for x in en.get("blocks",[]))
        self._bi_body(bi,f"Chuỗi ghi nhớ: {vnames}. Hãy áp dụng vào một tình huống thật.",f"Memory chain: {enames}. Apply it to a real situation.",900)

        foot=tk.Frame(v,bg=BG); foot.pack(fill="x",pady=(12,2))
        ttk.Button(foot,text="← "+self._ui("previous"),command=self.prev_lesson).pack(side="left")
        tk.Label(foot,text=self.lesson_position(),bg=BG,fg=MUTED,font=("Segoe UI",9,"bold")).pack(side="left",padx=10)
        ttk.Button(foot,text=self._ui("next")+" →",command=self.next_lesson).pack(side="right")

        self._select_tree(lid)
        self._save_state()

    def _english_checklist(self,en):
        out=[]
        for b in en.get("blocks",[])[:3]:
            out.append(f"Have we clearly defined {str(b[0]).lower()}?")
        out.append("Do we have data or a practical example to verify it?")
        return out

    def _render_diagram(self,parent,vi,en,p):
        box=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=LINE); box.pack(fill="x",pady=(0,12))
        inn=tk.Frame(box,bg="white"); inn.pack(fill="x",padx=14,pady=13)
        tk.Label(inn,text=self._ui("memory_map").upper(),bg="white",fg=p["primary"],font=("Segoe UI",16,"bold")).pack(anchor="w",pady=(0,8))
        vb=vi.get("blocks",[]); eb=en.get("blocks",[])
        style=vi.get("style","flow")
        pairs=[(vb[i],eb[i] if i<len(eb) else ("","")) for i in range(len(vb))]
        if style=="matrix":
            grid=tk.Frame(inn,bg="white"); grid.pack(fill="x")
            for col in range(2):grid.grid_columnconfigure(col,weight=1)
            for i,pair in enumerate(pairs):self._diagram_block(grid,pair[0],pair[1],p,i).grid(row=i//2,column=i%2,sticky="nsew",padx=5,pady=5)
        elif style=="ladder":
            for i,pair in enumerate(pairs):
                rr=tk.Frame(inn,bg="white"); rr.pack(fill="x",pady=3)
                tk.Label(rr,text=str(i+1).zfill(2),bg=p["primary"],fg="white",font=("Segoe UI",11,"bold"),width=4).pack(side="left",ipady=7,padx=(0,7))
                self._diagram_block(rr,pair[0],pair[1],p,i).pack(side="left",fill="x",expand=True)
        elif style=="cycle" and len(pairs)>=4:
            grid=tk.Frame(inn,bg="white"); grid.pack(fill="x")
            for col in range(2):grid.grid_columnconfigure(col,weight=1)
            for k,i in enumerate([0,1,3,2]):self._diagram_block(grid,pairs[i][0],pairs[i][1],p,i).grid(row=k//2,column=k%2,sticky="nsew",padx=5,pady=5)
        else:
            rr=tk.Frame(inn,bg="white"); rr.pack(fill="x")
            for i,pair in enumerate(pairs):
                self._diagram_block(rr,pair[0],pair[1],p,i).pack(side="left",fill="both",expand=True,padx=4)
                if i<len(pairs)-1:tk.Label(rr,text="➜",bg="white",fg=p["primary"],font=("Segoe UI",23,"bold")).pack(side="left")

    def _diagram_block(self,parent,vb,eb,p,index):
        schemes=[(p["soft"],p["primary"]),(p["alt2"],p["alt"]),(p["accent2"],p["accent"]),("#f1f5f9","#334155")]
        bg,fg=schemes[index%len(schemes)]
        c=tk.Frame(parent,bg=bg,bd=1,relief="solid",highlightbackground=LINE)
        vtitle,vbody=str(vb[0]),str(vb[1]); etitle,ebody=str(eb[0]),str(eb[1])
        tk.Label(c,text=self._text(vtitle,etitle).replace("\n"," / "),bg=bg,fg=fg,font=("Segoe UI",13,"bold"),wraplength=280,justify="left").pack(anchor="w",padx=12,pady=(10,3))
        tk.Label(c,text=self._text(vbody,ebody),bg=bg,fg=TEXT,font=("Segoe UI",self.font_size),wraplength=285,justify="left").pack(anchor="w",padx=12,pady=(0,10))
        return c

    def _render_story(self,parent,lid,p):
        vs=STORIES[lid]; es=EN_STORIES[lid]
        box=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=LINE); box.pack(fill="x",pady=(0,12))
        head=tk.Frame(box,bg="#fff7ed"); head.pack(fill="x")
        tk.Label(head,text="📖  "+self._ui("story").upper(),bg="#fff7ed",fg="#c2410c",font=("Segoe UI",15,"bold")).pack(anchor="w",padx=14,pady=9)
        body=tk.Frame(box,bg="white"); body.pack(fill="x",padx=17,pady=13)
        tk.Label(body,text=self._text(vs["title"],es["title"]),bg="white",fg=TEXT,font=("Segoe UI",17,"bold"),wraplength=1030,justify="left").pack(anchor="w")
        self._bi_body(body,vs["story"],es["story"],500)
        mem=tk.Frame(body,bg=p["soft"],bd=1,relief="solid",highlightbackground=LINE); mem.pack(fill="x",pady=(12,0))
        tk.Label(mem,text="💡 "+self._ui("memory_point"),bg=p["soft"],fg=p["primary"],font=("Segoe UI",10,"bold")).pack(anchor="w",padx=12,pady=(8,2))
        tk.Label(mem,text=self._text(vs["memory"],es["memory"]),bg=p["soft"],fg=TEXT,font=("Segoe UI",self.font_size,"bold"),wraplength=980,justify="left").pack(anchor="w",padx=12,pady=(0,9))

    def toggle_bookmark(self):
        if self.current_lesson in self.bookmarks:self.bookmarks.remove(self.current_lesson)
        else:self.bookmarks.add(self.current_lesson)
        self.populate_tree(); self.show_lesson(self.current_lesson)

    def mark_read(self):
        self.read_lessons.add(self.current_lesson)
        self.populate_tree(); self.show_lesson(self.current_lesson)

    def lesson_position(self):
        idx=next((i for i,x in enumerate(self.lessons) if x["id"]==self.current_lesson),0)
        return f'{self._ui("lesson")} {idx+1}/{len(self.lessons)}'

    def prev_lesson(self):
        idx=next((i for i,x in enumerate(self.lessons) if x["id"]==self.current_lesson),0)
        if idx>0:self.show_lesson(self.lessons[idx-1]["id"])

    def next_lesson(self):
        idx=next((i for i,x in enumerate(self.lessons) if x["id"]==self.current_lesson),0)
        if idx<len(self.lessons)-1:self.show_lesson(self.lessons[idx+1]["id"])

    def show_quiz(self,lid=None):
        if lid in self.lesson_by_id:self.current_quiz_lesson=lid
        self._activate_view("quiz")
        v=self.views["quiz"].inner; self._clear(v)
        self._section_title(v,"Learning Mode – Quiz","Learning Mode – Quiz","Kiểm tra nhanh sau mỗi bài; lưu điểm cao nhất.","Quick review after each lesson; best score is saved.")

        choose=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); choose.pack(fill="x",pady=(0,10))
        ci=tk.Frame(choose,bg="white"); ci.pack(fill="x",padx=14,pady=10)
        tk.Label(ci,text=self._ui("choose_lesson")+":",bg="white",fg=TEXT,font=("Segoe UI",10,"bold")).pack(side="left")
        vals=[]
        for l in self.lessons:
            vals.append(f'{l["id"]} – {self._text(l["title"],EN_LESSONS[l["id"]]["title"]).replace(chr(10)," | ")}')
        combo=ttk.Combobox(ci,values=vals,state="readonly",width=72)
        idx=next((i for i,x in enumerate(self.lessons) if x["id"]==self.current_quiz_lesson),0)
        combo.current(idx); combo.pack(side="left",padx=8)
        combo.bind("<<ComboboxSelected>>",lambda e:self._select_quiz(combo.current()))
        ttk.Button(ci,text=self._ui("read"),command=lambda:self.show_lesson(self.current_quiz_lesson)).pack(side="right")

        viq=self.quiz_vi[self.current_quiz_lesson]; enq=self.quiz_en[self.current_quiz_lesson]
        lesson=self.lesson_by_id[self.current_quiz_lesson]; enl=EN_LESSONS[self.current_quiz_lesson]
        tk.Label(v,text=self._text(f'{lesson["id"]}  {lesson["title"]}',f'{lesson["id"]}  {enl["title"]}'),bg=BG,fg=TEXT,font=("Segoe UI",20,"bold"),justify="left").pack(anchor="w",pady=(4,8))
        if self.current_quiz_lesson in self.quiz_scores:
            tk.Label(v,text=f'{self._ui("best_score")}: {self.quiz_scores[self.current_quiz_lesson]}%',bg=BG,fg="#15803d",font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(0,7))

        vars_=[]
        for qi in range(min(len(viq),len(enq))):
            qv,qe=viq[qi],enq[qi]
            card=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); card.pack(fill="x",pady=5)
            tk.Label(card,text=self._text(f'Câu {qi+1}. {qv["question"]}',f'Question {qi+1}. {qe["question"]}'),bg="white",fg=TEXT,font=("Segoe UI",12,"bold"),wraplength=1050,justify="left").pack(anchor="w",padx=15,pady=(12,7))
            var=tk.IntVar(value=-1); vars_.append(var)
            n=min(len(qv["options"]),len(qe["options"]))
            for oi in range(n):
                txt=self._text(qv["options"][oi],qe["options"][oi])
                tk.Radiobutton(card,text=txt,variable=var,value=oi,bg="white",activebackground="white",fg=TEXT,font=("Segoe UI",self.font_size),wraplength=1000,justify="left",anchor="w").pack(fill="x",padx=20,pady=3)
            tk.Frame(card,bg="white",height=8).pack()
        ttk.Button(v,text=self._ui("score"),command=lambda:self._grade_quiz(self.current_quiz_lesson,viq,enq,vars_)).pack(anchor="w",pady=10)

    def _select_quiz(self,index):
        self.current_quiz_lesson=self.lessons[index]["id"]; self.show_quiz(self.current_quiz_lesson)

    def _grade_quiz(self,lid,viq,enq,vars_):
        if any(v.get()<0 for v in vars_):
            messagebox.showinfo("Quiz","Hãy trả lời tất cả câu hỏi / Please answer all questions."); return
        total=min(len(viq),len(vars_))
        correct=sum(1 for i,v in enumerate(vars_) if v.get()==viq[i]["answer"])
        score=round(correct*100/total) if total else 0
        self.quiz_scores[lid]=max(int(self.quiz_scores.get(lid,0)),score); self._save_state()
        lines=[]
        for i,v in enumerate(vars_):
            ok=v.get()==viq[i]["answer"]
            vi="Đúng" if ok else "Chưa đúng"; en="Correct" if ok else "Not correct"
            lines.append(f'{i+1}. {vi} / {en}\n{viq[i]["explain"]}\n{enq[i]["explain"]}')
        messagebox.showinfo("Quiz Result / Kết quả",f'{score}% ({correct}/{total})\n\n'+"\n\n".join(lines))
        self.show_quiz(lid)

    def show_cases(self,case_id=None):
        if case_id in self.case_by_id:self.current_case_id=case_id
        self._activate_view("cases")
        v=self.views["cases"].inner; self._clear(v)
        self._section_title(v,"Case Study Mode","Case Study Mode","Đọc tình huống, chọn hướng xử lý và xem giải thích.","Read the scenario, choose an action, and review the reasoning.")
        bar=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); bar.pack(fill="x",pady=(0,10))
        bi=tk.Frame(bar,bg="white"); bi.pack(fill="x",padx=14,pady=10)
        tk.Label(bi,text=self._ui("choose_case")+":",bg="white",fg=TEXT,font=("Segoe UI",10,"bold")).pack(side="left")
        vals=[]
        for c in CASES:
            e=EN_CASES[c["id"]]
            vals.append(self._text(c["title"],e["title"]).replace("\n"," | "))
        combo=ttk.Combobox(bi,values=vals,state="readonly",width=72)
        idx=next((i for i,c in enumerate(CASES) if c["id"]==self.current_case_id),0)
        combo.current(idx); combo.pack(side="left",padx=8)
        combo.bind("<<ComboboxSelected>>",lambda e:self._select_case(combo.current()))

        c=self.case_by_id[self.current_case_id]; e=EN_CASES[self.current_case_id]
        card=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); card.pack(fill="x")
        tk.Label(card,text=self._text(c["category"],e["category"]).upper(),bg="white",fg="#7c3aed",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=17,pady=(14,2))
        tk.Label(card,text=self._text(c["title"],e["title"]),bg="white",fg=TEXT,font=("Segoe UI",21,"bold"),wraplength=1030,justify="left").pack(anchor="w",padx=17)
        story=tk.Frame(card,bg="white"); story.pack(fill="x",padx=17,pady=(9,12))
        self._bi_body(story,c["situation"],e["situation"],500)
        tk.Label(card,text=self._text(c["question"],e["question"]),bg="#f8fafc",fg=TEXT,font=("Segoe UI",12,"bold"),wraplength=1030,justify="left").pack(fill="x",padx=17,pady=(0,8))
        var=tk.IntVar(value=-1)
        for i in range(min(len(c["options"]),len(e["options"]))):
            tk.Radiobutton(card,text=self._text(c["options"][i],e["options"][i]),variable=var,value=i,bg="white",activebackground="white",fg=TEXT,font=("Segoe UI",self.font_size),wraplength=1000,justify="left",anchor="w").pack(fill="x",padx=24,pady=3)
        acts=tk.Frame(card,bg="white"); acts.pack(fill="x",padx=17,pady=14)
        ttk.Button(acts,text=self._ui("check_choice"),command=lambda:self._grade_case(c,e,var)).pack(side="left")
        tk.Label(acts,text=self._ui("related_tools")+": "+" • ".join(c.get("tools",[])),bg="white",fg=MUTED,font=("Segoe UI",9,"bold")).pack(side="right")

    def _select_case(self,index):
        self.current_case_id=CASES[index]["id"]; self.show_cases(self.current_case_id)

    def _grade_case(self,c,e,var):
        if var.get()<0:
            messagebox.showinfo("Case Study","Hãy chọn một phương án / Please choose an option."); return
        ok=var.get()==c["answer"]; self.case_results[c["id"]]=ok; self._save_state()
        prefix=self._text("Chính xác." if ok else "Chưa phải phương án phù hợp nhất.","Correct." if ok else "Not the best option yet.")
        messagebox.showinfo("Case Study",prefix+"\n\n"+self._text(c["explain"],e["explain"]))
        self.show_cases(c["id"])

    def show_tools(self,tid=None):
        if tid in self.tool_by_id:self.current_tool_id=tid
        self._activate_view("tools")
        v=self.views["tools"].inner; self._clear(v)
        self._section_title(v,"Thinking & Management Tools","Thinking & Management Tools",f"{len(TOOLS)} công cụ thực hành song ngữ.",f"{len(TOOLS)} bilingual practical tools.")
        search=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); search.pack(fill="x",pady=(0,10))
        si=tk.Frame(search,bg="white"); si.pack(fill="x",padx=14,pady=10)
        tk.Label(si,text=self._text("Tìm công cụ","Find tool")+":",bg="white",fg=TEXT,font=("Segoe UI",10,"bold")).pack(side="left")
        ttk.Entry(si,textvariable=self.tool_search_var,width=40).pack(side="left",padx=8)
        ttk.Button(si,text=self._ui("filter"),command=self._filter_tools).pack(side="left")
        ttk.Button(si,text=self._ui("all"),command=self._reset_tools).pack(side="left",padx=5)
        body=tk.Frame(v,bg=BG); body.pack(fill="x")
        self.tool_list_frame=tk.Frame(body,bg="white",bd=1,relief="solid",highlightbackground=LINE,width=310); self.tool_list_frame.pack(side="left",fill="y",padx=(0,8)); self.tool_list_frame.pack_propagate(False)
        self.tool_detail_frame=tk.Frame(body,bg="white",bd=1,relief="solid",highlightbackground=LINE); self.tool_detail_frame.pack(side="left",fill="both",expand=True)
        self._render_tool_list(TOOLS); self._render_tool_detail(self.current_tool_id)

    def _render_tool_list(self,items):
        self._clear(self.tool_list_frame)
        for t in items:
            e=EN_TOOLS[t["id"]]
            label=f'{t["icon"]}  {t["name"]}'
            if self.language_mode=="BI":label+=f' | {e["category"]}'
            tk.Button(self.tool_list_frame,text=label,command=lambda x=t["id"]:self._choose_tool(x),bg="white",fg=TEXT,relief="flat",anchor="w",font=("Segoe UI",9,"bold"),padx=9,pady=7).pack(fill="x",padx=4,pady=2)

    def _choose_tool(self,tid):
        self.current_tool_id=tid; self._render_tool_detail(tid)

    def _filter_tools(self):
        q=self.tool_search_var.get().strip().lower()
        out=[]
        for t in TOOLS:
            e=EN_TOOLS[t["id"]]
            blob=(t["name"]+" "+t["category"]+" "+t["when"]+" "+e["category"]+" "+e["when"]).lower()
            if q in blob:out.append(t)
        self._render_tool_list(out)
        if out:self._choose_tool(out[0]["id"])

    def _reset_tools(self):
        self.tool_search_var.set(""); self._render_tool_list(TOOLS)
        if TOOLS:self._choose_tool(TOOLS[0]["id"])

    def _render_tool_detail(self,tid):
        self._clear(self.tool_detail_frame)
        t=self.tool_by_id.get(tid); e=EN_TOOLS.get(tid)
        if not t or not e:return
        tk.Label(self.tool_detail_frame,text=self._text(t["category"],e["category"]).upper(),bg="white",fg="#7c3aed",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=17,pady=(15,2))
        tk.Label(self.tool_detail_frame,text=f'{t["icon"]}  {t["name"]}',bg="white",fg=TEXT,font=("Segoe UI",22,"bold")).pack(anchor="w",padx=17)
        for key,vi,en,fg in [
            ("when_use",t["when"],e["when"],"#1d4ed8"),
            ("output",t["output"],e["output"],"#b45309")
        ]:
            tk.Label(self.tool_detail_frame,text=self._ui(key).upper(),bg="white",fg=fg,font=("Segoe UI",11,"bold")).pack(anchor="w",padx=17,pady=(14,3))
            wrap=tk.Frame(self.tool_detail_frame,bg="white"); wrap.pack(fill="x",padx=17)
            self._bi_body(wrap,vi,en,360)
        tk.Label(self.tool_detail_frame,text=self._ui("steps").upper(),bg="white",fg="#15803d",font=("Segoe UI",11,"bold")).pack(anchor="w",padx=17,pady=(14,3))
        self._list_card(self.tool_detail_frame,"","",t["steps"],e["steps"],"#ffffff","#15803d").pack(fill="x",padx=12,pady=(0,4))
        self._list_card(self.tool_detail_frame,*UI["mistakes"],t["mistakes"],e["mistakes"],"#fee2e2","#b91c1c").pack(fill="x",padx=12,pady=(0,12))

    def show_glossary(self):
        self._activate_view("glossary")
        v=self.views["glossary"].inner; self._clear(v)
        self._section_title(v,"Từ điển quản lý & tư duy","Management & Thinking Glossary",f"{len(GLOSSARY)} thuật ngữ song ngữ.",f"{len(GLOSSARY)} bilingual terms.")
        bar=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); bar.pack(fill="x",pady=(0,10))
        bi=tk.Frame(bar,bg="white"); bi.pack(fill="x",padx=14,pady=10)
        tk.Label(bi,text=self._ui("keyword")+":",bg="white",fg=TEXT,font=("Segoe UI",10,"bold")).pack(side="left")
        ent=ttk.Entry(bi,textvariable=self.glossary_search_var,width=42); ent.pack(side="left",padx=8)
        ent.bind("<KeyRelease>",lambda e:self._render_glossary())
        ttk.Button(bi,text=self._ui("clear"),command=lambda:(self.glossary_search_var.set(""),self._render_glossary())).pack(side="left")
        self.glossary_result_frame=tk.Frame(v,bg=BG); self.glossary_result_frame.pack(fill="x")
        self._render_glossary()

    def _render_glossary(self):
        f=self.glossary_result_frame; self._clear(f)
        q=self.glossary_search_var.get().strip().lower()
        keys=[k for k in GLOSSARY if not q or q in k.lower() or q in GLOSSARY[k].lower() or q in EN_GLOSSARY[k].lower()]
        for term in sorted(keys,key=str.lower):
            card=tk.Frame(f,bg="white",bd=1,relief="solid",highlightbackground=LINE); card.pack(fill="x",pady=4)
            tk.Label(card,text=term,bg="white",fg="#1d4ed8",font=("Segoe UI",13,"bold")).pack(anchor="w",padx=14,pady=(9,3))
            body=tk.Frame(card,bg="white"); body.pack(fill="x",padx=14,pady=(0,10))
            self._bi_body(body,GLOSSARY[term],EN_GLOSSARY[term],500)

    def show_progress(self):
        self._activate_view("progress")
        v=self.views["progress"].inner; self._clear(v)
        self._section_title(v,"Tiến độ học tập","Learning Progress","Theo dõi đọc sách, quiz và case study.","Track reading, quizzes, and case studies.")
        done=len(self.read_lessons & set(self.lesson_by_id)); qn=len(self.quiz_scores); avg=round(sum(map(int,self.quiz_scores.values()))/qn) if qn else 0; cc=sum(1 for x in self.case_results.values() if x)
        stats=[("Đọc sách","Reading",f"{done}/{len(self.lessons)}","#dbeafe","#1d4ed8"),("Quiz hoàn thành","Quizzes completed",f"{qn}/{len(self.lessons)}","#ede9fe","#7c3aed"),("Quiz trung bình","Average quiz",f"{avg}%","#fef3c7","#b45309"),("Case đúng","Correct cases",f"{cc}/{len(CASES)}","#dcfce7","#15803d")]
        row=tk.Frame(v,bg=BG); row.pack(fill="x",pady=(0,10))
        for vi,en,val,bg,fg in stats:
            c=tk.Frame(row,bg=bg,bd=1,relief="solid",highlightbackground=LINE); c.pack(side="left",fill="both",expand=True,padx=4)
            tk.Label(c,text=self._text(vi,en).replace("\n"," / ").upper(),bg=bg,fg=fg,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=12,pady=(10,2))
            tk.Label(c,text=val,bg=bg,fg=TEXT,font=("Segoe UI",22,"bold")).pack(anchor="w",padx=12,pady=(0,10))
        for i,ch in enumerate(CHAPTERS,1):
            e=EN_CHAPTERS[i]; ids=[l["id"] for l in ch["lessons"]]; rd=len([x for x in ids if x in self.read_lessons]); pct=round(rd*100/len(ids))
            qs=[int(self.quiz_scores[x]) for x in ids if x in self.quiz_scores]; qavg=round(sum(qs)/len(qs)) if qs else 0
            card=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); card.pack(fill="x",pady=4)
            top=tk.Frame(card,bg="white"); top.pack(fill="x",padx=13,pady=(9,4))
            tk.Label(top,text=self._text(ch["title"],e["title"]),bg="white",fg=TEXT,font=("Segoe UI",11,"bold"),justify="left").pack(side="left")
            tk.Label(top,text=self._text(f"Đọc {rd}/{len(ids)} • Quiz TB {qavg}%",f"Read {rd}/{len(ids)} • Quiz avg {qavg}%").replace("\n"," | "),bg="white",fg=MUTED,font=("Segoe UI",9,"bold")).pack(side="right")
            ttk.Progressbar(card,maximum=100,value=pct).pack(fill="x",padx=13,pady=(0,9))

    def change_font(self,d):
        self.font_size=max(10,min(17,self.font_size+d)); self._save_state()
        if self.current_view=="lesson":self.show_lesson(self.current_lesson)
        elif self.current_view=="quiz":self.show_quiz(self.current_quiz_lesson)
        elif self.current_view=="cases":self.show_cases(self.current_case_id)
        elif self.current_view=="tools":self.show_tools(self.current_tool_id)
        elif self.current_view=="glossary":self.show_glossary()
        elif self.current_view=="progress":self.show_progress()

    def close_app(self):
        self._save_state()
        if messagebox.askyesno("Thoát / Exit","Bạn muốn thoát ứng dụng?\nDo you want to exit?"):
            self.destroy()


if __name__=="__main__":
    App().mainloop()
