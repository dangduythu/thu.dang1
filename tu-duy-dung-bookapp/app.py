# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from content import CHAPTERS
from learning_data import GLOSSARY, TOOLS, CASES, build_quiz_for_lesson
from stories import STORIES

APP_NAME = "Tư Duy Đúng – Book App"
VERSION = "2.6"
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
        self.geometry("1460x930")
        self.minsize(1180, 760)
        self.configure(bg=BG)

        self.state_data = self._load_state()
        self.bookmarks = set(self.state_data.get("bookmarks", []))
        self.read_lessons = set(self.state_data.get("read_lessons", []))
        self.quiz_scores = dict(self.state_data.get("quiz_scores", {}))
        self.case_results = dict(self.state_data.get("case_results", {}))
        self.last_lesson = self.state_data.get("last_lesson", "1.1")
        self.font_size = int(self.state_data.get("font_size", 12))

        self.lessons = [x for ch in CHAPTERS for x in ch["lessons"]]
        self.lesson_by_id = {x["id"]: x for x in self.lessons}
        self.quiz_bank = {x["id"]: build_quiz_for_lesson(x, self.lessons) for x in self.lessons}
        self.tool_by_id = {x["id"]: x for x in TOOLS}
        self.case_by_id = {x["id"]: x for x in CASES}

        self.current_view = "home"
        self.current_lesson = self.last_lesson if self.last_lesson in self.lesson_by_id else "1.1"
        self.current_quiz_lesson = self.current_lesson
        self.current_case_id = CASES[0]["id"] if CASES else None
        self.current_tool_id = TOOLS[0]["id"] if TOOLS else None
        self.history = []
        self.history_pos = -1
        self.block_tree_event = False

        self.search_var = tk.StringVar()
        self.progress_var = tk.StringVar()
        self.bookmark_var = tk.StringVar(value="☆ Lưu bài")
        self.glossary_search_var = tk.StringVar()
        self.tool_search_var = tk.StringVar()

        self._configure_styles()
        self._build_shell()
        self.populate_tree()
        self.show_home()

        self.bind_all("<MouseWheel>", self._global_mousewheel, add="+")
        self.bind_all("<Button-4>", self._global_mousewheel_linux, add="+")
        self.bind_all("<Button-5>", self._global_mousewheel_linux, add="+")
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def _configure_styles(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self.style.configure("TButton", padding=(10, 7), font=("Segoe UI", 10))
        self.style.configure("Nav.TButton", padding=(10, 8), font=("Segoe UI", 10, "bold"))
        self.style.configure("Treeview", rowheight=28, font=("Segoe UI", 10), fieldbackground="white", background="white")
        self.style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#0f172a")])
        self.style.configure("TNotebook.Tab", padding=(12, 8), font=("Segoe UI", 10, "bold"))

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
            "last_lesson": self.current_lesson,
            "font_size": self.font_size,
        }
        try:
            state_path().write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _build_shell(self):
        top = tk.Frame(self, bg="white", height=72)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="TƯ DUY ĐÚNG", bg="white", fg=NAVY, font=("Segoe UI", 21, "bold")).pack(side="left", padx=(20, 10))
        tk.Label(top, text=f"BOOK APP • V{VERSION}", bg="white", fg="#7a8aa0", font=("Segoe UI", 10, "bold")).pack(side="left")

        nav = tk.Frame(top, bg="white")
        nav.pack(side="right", padx=14)
        nav_items = [
            ("⌂ Trang chủ", self.show_home),
            ("📖 Học sách", self.continue_reading),
            ("🧠 Quiz", self.show_quiz),
            ("🎯 Case Study", self.show_cases),
            ("🧰 Công cụ", self.show_tools),
            ("🔤 Từ điển", self.show_glossary),
            ("📈 Tiến độ", self.show_progress),
        ]
        for label, cmd in nav_items:
            ttk.Button(nav, text=label, command=cmd, style="Nav.TButton").pack(side="left", padx=2, pady=16)
        ttk.Button(nav, text="A−", width=4, command=lambda: self.change_font(-1)).pack(side="left", padx=(8, 2), pady=16)
        ttk.Button(nav, text="A+", width=4, command=lambda: self.change_font(1)).pack(side="left", padx=2, pady=16)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        self.sidebar = tk.Frame(body, bg="white", width=335)
        self.sidebar.pack(side="left", fill="y", padx=(10, 8), pady=10)
        self.sidebar.pack_propagate(False)
        self.main = tk.Frame(body, bg=BG)
        self.main.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        self._build_sidebar()

        self.views = {}
        for name in ["home", "lesson", "quiz", "cases", "tools", "glossary", "progress"]:
            view = ScrollableFrame(self.main, BG)
            self.views[name] = view

    def _build_sidebar(self):
        banner = tk.Canvas(self.sidebar, height=118, bg="white", highlightthickness=0)
        banner.pack(fill="x", padx=14, pady=(14, 10))
        banner.create_rectangle(0, 0, 305, 118, fill="#8eb1df", outline="")
        banner.create_rectangle(0, 82, 305, 118, fill="#e6a8a8", outline="")
        banner.create_text(14, 15, anchor="nw", text="TƯ DUY", fill="#fff59d", font=("Segoe UI", 15, "bold"))
        banner.create_text(14, 43, anchor="nw", text="PHƯƠNG PHÁP QUẢN LÝ", fill="white", font=("Segoe UI", 16, "bold"))
        banner.create_text(14, 75, anchor="nw", text="ĐÚNG", fill="white", font=("Segoe UI", 23, "bold"))
        banner.create_text(290, 100, anchor="e", text=f"V{VERSION}", fill="white", font=("Segoe UI", 9, "bold"))

        sr = tk.Frame(self.sidebar, bg="white")
        sr.pack(fill="x", padx=14, pady=(0, 8))
        self.search_entry = ttk.Entry(sr, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self.search_lessons())
        ttk.Button(sr, text="Tìm", width=7, command=self.search_lessons).pack(side="left", padx=(5, 0))

        br = tk.Frame(self.sidebar, bg="white")
        br.pack(fill="x", padx=14, pady=(0, 8))
        ttk.Button(br, text="Mục lục", command=self.populate_tree).pack(side="left", fill="x", expand=True)
        ttk.Button(br, text="★ Đã lưu", command=self.show_bookmarks).pack(side="left", fill="x", expand=True, padx=(5, 0))

        tk.Label(self.sidebar, textvariable=self.progress_var, bg="white", fg=MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14)
        self.progress_bar = ttk.Progressbar(self.sidebar, maximum=100)
        self.progress_bar.pack(fill="x", padx=14, pady=(5, 10))

        tree_wrap = tk.Frame(self.sidebar, bg="white")
        tree_wrap.pack(fill="both", expand=True, padx=(10, 7), pady=(0, 10))
        self.tree = ttk.Treeview(tree_wrap, show="tree", selectmode="browse")
        sb = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._tree_pick)

    def _activate_view(self, name):
        for v in self.views.values():
            v.pack_forget()
        self.views[name].pack(fill="both", expand=True)
        self.current_view = name
        self.views[name].top()

    def _is_descendant(self, widget, ancestor):
        cur = widget
        while cur is not None:
            if cur == ancestor:
                return True
            try:
                cur = cur.master
            except Exception:
                return False
        return False

    def _scroll_target(self, event):
        try:
            w = self.winfo_containing(event.x_root, event.y_root)
        except Exception:
            return None
        if w is None or self._is_descendant(w, self.tree):
            return None
        v = self.views.get(self.current_view)
        if v and v.winfo_ismapped() and (self._is_descendant(w, v.canvas) or self._is_descendant(w, v.inner)):
            return v
        return None

    def _global_mousewheel(self, event):
        target = self._scroll_target(event)
        if target is None:
            return
        delta = event.delta
        if not delta:
            return "break"
        steps = max(1, abs(int(delta / 120))) if abs(delta) >= 120 else 1
        target.scroll_units(-steps if delta > 0 else steps)
        return "break"

    def _global_mousewheel_linux(self, event):
        target = self._scroll_target(event)
        if target is None:
            return
        target.scroll_units(-1 if event.num == 4 else 1)
        return "break"

    def populate_tree(self, items=None):
        self.block_tree_event = True
        self.tree.delete(*self.tree.get_children())
        if items is None:
            for ci, ch in enumerate(CHAPTERS):
                parent = self.tree.insert("", "end", iid=f"c{ci}", text=ch["title"], open=ci < 3)
                for lesson in ch["lessons"]:
                    prefix = "✓ " if lesson["id"] in self.read_lessons else ""
                    suffix = " ★" if lesson["id"] in self.bookmarks else ""
                    self.tree.insert(parent, "end", iid="l" + lesson["id"], text=f'{prefix}{lesson["id"]}  {lesson["title"]}{suffix}')
        else:
            for lesson in items:
                self.tree.insert("", "end", iid="l" + lesson["id"], text=f'{lesson["id"]}  {lesson["title"]}')
        self.block_tree_event = False
        self._update_progress_label()

    def _tree_pick(self, _event=None):
        # TreeviewSelect is also emitted by programmatic selection_set().
        # Never re-open the lesson that is already being rendered; otherwise
        # show_lesson -> _select_tree -> TreeviewSelect can recurse forever.
        if self.block_tree_event:
            return
        sel = self.tree.selection()
        if not sel or not sel[0].startswith("l"):
            return
        lid = sel[0][1:]
        if lid not in self.lesson_by_id:
            return
        if self.current_view == "lesson" and lid == self.current_lesson:
            return
        self.show_lesson(lid)

    def _select_tree(self, lid):
        iid = "l" + lid
        if not self.tree.exists(iid):
            return
        # Avoid generating redundant virtual selection events.
        if self.tree.selection() == (iid,):
            self.tree.see(iid)
            return
        self.block_tree_event = True
        try:
            self.tree.selection_set(iid)
            self.tree.see(iid)
        finally:
            self.block_tree_event = False

    def search_lessons(self):
        q = self.search_var.get().strip().lower()
        if not q:
            self.populate_tree()
            return
        found = []
        for l in self.lessons:
            blob = " ".join([
                l.get("id", ""), l.get("title", ""), l.get("summary", ""), l.get("concept", ""),
                l.get("apply", l.get("method", "")), l.get("example", ""), l.get("why", ""), l.get("practice", ""),
                " ".join(l.get("mistakes", [])), " ".join(l.get("reflect", [])),
            ]).lower()
            if q in blob:
                found.append(l)
        self.populate_tree(found)
        if not found:
            messagebox.showinfo("Tìm kiếm", "Không tìm thấy bài phù hợp.")

    def show_bookmarks(self):
        items = [x for x in self.lessons if x["id"] in self.bookmarks]
        self.populate_tree(items)
        if not items:
            messagebox.showinfo("Đã lưu", "Chưa có bài nào được đánh dấu.")

    def _update_progress_label(self):
        total = len(self.lessons)
        done = len([x for x in self.read_lessons if x in self.lesson_by_id])
        pct = round(done * 100 / total) if total else 0
        self.progress_var.set(f"TIẾN ĐỘ ĐỌC  {done}/{total} bài • {pct}%")
        self.progress_bar["value"] = pct

    def _clear(self, parent):
        for w in parent.winfo_children():
            w.destroy()

    def _section_title(self, parent, title, subtitle=None):
        box = tk.Frame(parent, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        box.pack(fill="x", pady=(0, 12))
        inner = tk.Frame(box, bg="white")
        inner.pack(fill="x", padx=22, pady=18)
        tk.Label(inner, text=title, bg="white", fg=TEXT, font=("Segoe UI", 25, "bold"), anchor="w").pack(fill="x")
        if subtitle:
            tk.Label(inner, text=subtitle, bg="white", fg=MUTED, font=("Segoe UI", 12), anchor="w", justify="left", wraplength=980).pack(fill="x", pady=(5, 0))
        return box

    def _card(self, parent, title, body, header_bg="#dbeafe", header_fg="#1d4ed8", width=510):
        c = tk.Frame(parent, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        h = tk.Frame(c, bg=header_bg)
        h.pack(fill="x")
        tk.Label(h, text=title, bg=header_bg, fg=header_fg, font=("Segoe UI", 15, "bold"), anchor="w").pack(fill="x", padx=14, pady=9)
        tk.Label(c, text=body, bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), justify="left", wraplength=width).pack(anchor="w", padx=15, pady=14)
        return c

    def _bullet_card(self, parent, title, items, header_bg, header_fg, width=500):
        c = tk.Frame(parent, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        h = tk.Frame(c, bg=header_bg)
        h.pack(fill="x")
        tk.Label(h, text=title, bg=header_bg, fg=header_fg, font=("Segoe UI", 15, "bold"), anchor="w").pack(fill="x", padx=14, pady=9)
        body = tk.Frame(c, bg="white")
        body.pack(fill="both", expand=True, padx=15, pady=10)
        if not items:
            tk.Label(body, text="Chưa có nội dung.", bg="white", fg=MUTED, font=("Segoe UI", self.font_size)).pack(anchor="w")
        for item in items:
            tk.Label(body, text="•  " + str(item), bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), justify="left", wraplength=width).pack(anchor="w", pady=4)
        return c

    def show_home(self):
        self._activate_view("home")
        v = self.views["home"].inner
        self._clear(v)
        hero = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        hero.pack(fill="x", pady=(0, 14))
        inner = tk.Frame(hero, bg="white")
        inner.pack(fill="x", padx=28, pady=26)
        tk.Label(inner, text="TƯ DUY • PHƯƠNG PHÁP • QUẢN LÝ", bg="white", fg="#7a8aa0", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(inner, text="Book App V2.5", bg="white", fg=TEXT, font=("Segoe UI", 32, "bold")).pack(anchor="w", pady=(8, 3))
        tk.Label(inner, text="Sách tương tác + Quiz + Case Study + Thinking Tools + Từ điển + Theo dõi tiến độ", bg="white", fg=MUTED, font=("Segoe UI", 13)).pack(anchor="w")
        actions = tk.Frame(inner, bg="white")
        actions.pack(anchor="w", pady=(16, 0))
        ttk.Button(actions, text="▶ Tiếp tục bài đang đọc", command=self.continue_reading).pack(side="left")
        ttk.Button(actions, text="🧠 Luyện Quiz", command=self.show_quiz).pack(side="left", padx=6)
        ttk.Button(actions, text="🎯 Case Study", command=self.show_cases).pack(side="left", padx=6)

        stats = tk.Frame(v, bg=BG)
        stats.pack(fill="x", pady=(0, 10))
        done = len(self.read_lessons & set(self.lesson_by_id))
        quiz_done = len(self.quiz_scores)
        case_done = len(self.case_results)
        stat_data = [
            ("BÀI HỌC", f"{done}/{len(self.lessons)}", "#dbeafe", "#1d4ed8"),
            ("QUIZ ĐÃ LÀM", f"{quiz_done}/{len(self.lessons)}", "#ede9fe", "#7c3aed"),
            ("CASE STUDY", f"{case_done}/{len(CASES)}", "#dcfce7", "#15803d"),
            ("THINKING TOOLS", str(len(TOOLS)), "#fef3c7", "#b45309"),
        ]
        for title, value, bg, fg in stat_data:
            c = tk.Frame(stats, bg=bg, bd=1, relief="solid", highlightbackground=LINE)
            c.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(c, text=title, bg=bg, fg=fg, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
            tk.Label(c, text=value, bg=bg, fg=TEXT, font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=14, pady=(0, 12))

        grid = tk.Frame(v, bg=BG)
        grid.pack(fill="both", expand=True)
        for i, ch in enumerate(CHAPTERS):
            p = list(PALETTES.values())[i % len(PALETTES)]
            card = tk.Frame(grid, bg="white", bd=1, relief="solid", highlightbackground=LINE)
            card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
            grid.grid_columnconfigure(i % 2, weight=1)
            h = tk.Frame(card, bg=p["soft"])
            h.pack(fill="x")
            tk.Label(h, text=f"{i+1:02}", bg=p["soft"], fg=p["primary"], font=("Segoe UI", 20, "bold")).pack(side="left", padx=13, pady=11)
            tb = tk.Frame(h, bg=p["soft"])
            tb.pack(side="left", fill="both", expand=True, pady=10)
            tk.Label(tb, text=ch["title"], bg=p["soft"], fg=TEXT, font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
            tk.Label(tb, text=ch["subtitle"], bg=p["soft"], fg=MUTED, font=("Segoe UI", 9), anchor="w", wraplength=440, justify="left").pack(fill="x")
            f = tk.Frame(card, bg="white")
            f.pack(fill="x", padx=13, pady=11)
            tk.Label(f, text=f'{len(ch["lessons"])} bài', bg="white", fg=MUTED, font=("Segoe UI", 10, "bold")).pack(side="left")
            ttk.Button(f, text="Mở chương", command=lambda idx=i: self.open_chapter(idx)).pack(side="right")

    def continue_reading(self):
        self.show_lesson(self.current_lesson)

    def open_chapter(self, idx):
        if CHAPTERS[idx]["lessons"]:
            self.show_lesson(CHAPTERS[idx]["lessons"][0]["id"])

    def show_lesson(self, lid, add_history=True):
        if lid not in self.lesson_by_id:
            return
        if getattr(self, "_rendering_lesson", False):
            return
        self._rendering_lesson = True
        try:
            self._show_lesson_impl(lid, add_history)
        finally:
            self._rendering_lesson = False

    def _show_lesson_impl(self, lid, add_history=True):
        self.current_lesson = lid
        self.last_lesson = lid
        self._activate_view("lesson")
        v = self.views["lesson"].inner
        self._clear(v)
        lesson = self.lesson_by_id[lid]
        p = PALETTES.get(lesson.get("style"), PALETTES["flow"])

        head = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        head.pack(fill="x", pady=(0, 12))
        hi = tk.Frame(head, bg="white")
        hi.pack(fill="x", padx=22, pady=17)
        left = tk.Frame(hi, bg="white")
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text=f'BÀI {lesson["id"]}', bg="white", fg=p["primary"], font=("Segoe UI", 11, "bold")).pack(anchor="w")
        row = tk.Frame(left, bg="white")
        row.pack(fill="x", pady=(6, 0))
        tk.Frame(row, bg=p["primary"], width=8, height=52).pack(side="left", padx=(0, 13))
        tk.Label(row, text=lesson["title"], bg="white", fg=TEXT, font=("Segoe UI", 30, "bold"), anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(left, text=lesson["summary"], bg="white", fg=MUTED, font=("Segoe UI", 13), justify="left", wraplength=830).pack(anchor="w", pady=(7, 0))
        controls = tk.Frame(hi, bg="white")
        controls.pack(side="right")
        self.bookmark_var.set("★ Đã lưu" if lid in self.bookmarks else "☆ Lưu bài")
        ttk.Button(controls, textvariable=self.bookmark_var, command=self.toggle_bookmark).pack(side="left", padx=3)
        ttk.Button(controls, text="✓ Đã đọc", command=self.mark_read).pack(side="left", padx=3)
        ttk.Button(controls, text="🧠 Quiz bài này", command=lambda: self.show_quiz(lid)).pack(side="left", padx=3)

        self._render_diagram(v, lesson, p)
        self._render_story(v, lesson, p)

        row1 = tk.Frame(v, bg=BG); row1.pack(fill="x", pady=(0, 10))
        self._card(row1, "KHÁI NIỆM", lesson.get("concept", ""), p["soft"], p["primary"]).pack(side="left", fill="both", expand=True, padx=(0, 5))
        self._card(row1, "CÁCH ÁP DỤNG", lesson.get("apply", lesson.get("method", "")), p["accent2"], p["accent"]).pack(side="left", fill="both", expand=True, padx=(5, 0))

        row2 = tk.Frame(v, bg=BG); row2.pack(fill="x", pady=(0, 10))
        self._card(row2, "TẠI SAO QUAN TRỌNG?", lesson.get("why", ""), "#fff7ed", "#c2410c").pack(side="left", fill="both", expand=True, padx=(0, 5))
        self._bullet_card(row2, "SAI LẦM THƯỜNG GẶP", lesson.get("mistakes", []), "#fee2e2", "#b91c1c").pack(side="left", fill="both", expand=True, padx=(5, 0))

        row3 = tk.Frame(v, bg=BG); row3.pack(fill="x", pady=(0, 10))
        self._card(row3, "VÍ DỤ THỰC TẾ", lesson.get("example", ""), p["alt2"], p["alt"]).pack(side="left", fill="both", expand=True, padx=(0, 5))
        self._bullet_card(row3, "CHECKLIST", lesson.get("checklist", []), p["accent2"], p["accent"]).pack(side="left", fill="both", expand=True, padx=(5, 0))

        row4 = tk.Frame(v, bg=BG); row4.pack(fill="x", pady=(0, 10))
        self._card(row4, "BÀI TẬP ÁP DỤNG NGAY", lesson.get("practice", ""), "#f3e8ff", "#7e22ce").pack(side="left", fill="both", expand=True, padx=(0, 5))
        self._bullet_card(row4, "CÂU HỎI TỰ PHẢN TƯ", lesson.get("reflect", []), "#ecfeff", "#0e7490").pack(side="left", fill="both", expand=True, padx=(5, 0))

        bottom = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        bottom.pack(fill="x")
        bi = tk.Frame(bottom, bg="white"); bi.pack(fill="x", padx=16, pady=14)
        names = " → ".join(str(x[0]) for x in lesson.get("blocks", []))
        tk.Label(bi, text="BÀI HỌC CHÍNH", bg="white", fg=p["primary"], font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(bi, text=f"Chuỗi ghi nhớ: {names}. Hãy áp dụng ngay vào một tình huống thật thay vì chỉ đọc.", bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=980, justify="left").pack(anchor="w", pady=(6, 0))

        foot = tk.Frame(v, bg=BG); foot.pack(fill="x", pady=(12, 2))
        ttk.Button(foot, text="← Bài trước", command=self.prev_lesson).pack(side="left")
        tk.Label(foot, text=self.lesson_position(), bg=BG, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        ttk.Button(foot, text="Bài sau →", command=self.next_lesson).pack(side="right")

        if add_history:
            if self.history_pos < len(self.history) - 1:
                self.history = self.history[:self.history_pos + 1]
            if not self.history or self.history[-1] != lid:
                self.history.append(lid)
                self.history_pos = len(self.history) - 1
        self._select_tree(lid)
        self._save_state()

    def _render_story(self, parent, lesson, p):
        story = STORIES.get(lesson.get("id"))
        if not story:
            return
        box = tk.Frame(parent, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        box.pack(fill="x", pady=(0, 12))
        head = tk.Frame(box, bg="#fff7ed")
        head.pack(fill="x")
        tk.Label(head, text="📖  CÂU CHUYỆN GHI NHỚ", bg="#fff7ed", fg="#c2410c", font=("Segoe UI", 16, "bold")).pack(side="left", padx=14, pady=10)
        body = tk.Frame(box, bg="white")
        body.pack(fill="x", padx=18, pady=14)
        tk.Label(body, text=story.get("title",""), bg="white", fg=TEXT, font=("Segoe UI", 18, "bold"), wraplength=980, justify="left").pack(anchor="w")
        tk.Label(body, text=story.get("story",""), bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=1000, justify="left").pack(anchor="w", pady=(8, 12))
        memory = tk.Frame(body, bg=p["soft"], bd=1, relief="solid", highlightbackground=LINE)
        memory.pack(fill="x")
        tk.Label(memory, text="💡 Điểm cần nhớ", bg=p["soft"], fg=p["primary"], font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(9, 2))
        tk.Label(memory, text=story.get("memory",""), bg=p["soft"], fg=TEXT, font=("Segoe UI", self.font_size + 1, "bold"), wraplength=950, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

    def _render_diagram(self, parent, lesson, p):
        box = tk.Frame(parent, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        box.pack(fill="x", pady=(0, 12))
        inner = tk.Frame(box, bg="white"); inner.pack(fill="x", padx=14, pady=13)
        tk.Label(inner, text="SƠ ĐỒ GHI NHỚ", bg="white", fg=p["primary"], font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(0, 8))
        blocks = lesson.get("blocks") or []
        style = lesson.get("style", "flow")
        if style == "matrix":
            grid = tk.Frame(inner, bg="white"); grid.pack(fill="x")
            for col in range(2): grid.grid_columnconfigure(col, weight=1)
            for i, b in enumerate(blocks):
                self._diagram_block(grid, b, p, i).grid(row=i // 2, column=i % 2, sticky="nsew", padx=5, pady=5)
        elif style == "ladder":
            for i, b in enumerate(blocks):
                r = tk.Frame(inner, bg="white"); r.pack(fill="x", pady=3)
                tk.Label(r, text=str(i + 1).zfill(2), bg=p["primary"], fg="white", font=("Segoe UI", 12, "bold"), width=4).pack(side="left", ipady=7, padx=(0, 7))
                self._diagram_block(r, b, p, i).pack(side="left", fill="x", expand=True)
        elif style == "cycle" and len(blocks) >= 4:
            grid = tk.Frame(inner, bg="white"); grid.pack(fill="x")
            for col in range(2): grid.grid_columnconfigure(col, weight=1)
            order = [0, 1, 3, 2]
            for k, i in enumerate(order):
                self._diagram_block(grid, blocks[i], p, i).grid(row=k // 2, column=k % 2, sticky="nsew", padx=5, pady=5)
        else:
            r = tk.Frame(inner, bg="white"); r.pack(fill="x")
            for i, b in enumerate(blocks):
                self._diagram_block(r, b, p, i).pack(side="left", fill="both", expand=True, padx=4)
                if i < len(blocks) - 1:
                    tk.Label(r, text="➜", bg="white", fg=p["primary"], font=("Segoe UI", 25, "bold")).pack(side="left")

    def _diagram_block(self, parent, block, p, index):
        schemes = [(p["soft"], p["primary"]), (p["alt2"], p["alt"]), (p["accent2"], p["accent"]), ("#f1f5f9", "#334155")]
        bg, fg = schemes[index % len(schemes)]
        c = tk.Frame(parent, bg=bg, bd=1, relief="solid", highlightbackground=LINE)
        title = str(block[0]) if len(block) > 0 else ""
        body = str(block[1]) if len(block) > 1 else ""
        tk.Label(c, text=title, bg=bg, fg=fg, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=12, pady=(11, 4))
        tk.Label(c, text=body, bg=bg, fg=TEXT, font=("Segoe UI", self.font_size + 1), justify="left", wraplength=270).pack(anchor="w", padx=12, pady=(0, 11))
        return c

    def toggle_bookmark(self):
        if self.current_lesson in self.bookmarks:
            self.bookmarks.remove(self.current_lesson)
        else:
            self.bookmarks.add(self.current_lesson)
        self.populate_tree(); self.show_lesson(self.current_lesson, add_history=False)

    def mark_read(self):
        self.read_lessons.add(self.current_lesson)
        self.populate_tree(); self.show_lesson(self.current_lesson, add_history=False)

    def lesson_position(self):
        idx = next((i for i, x in enumerate(self.lessons) if x["id"] == self.current_lesson), 0)
        return f"Bài {idx+1}/{len(self.lessons)}"

    def prev_lesson(self):
        idx = next((i for i, x in enumerate(self.lessons) if x["id"] == self.current_lesson), 0)
        if idx > 0:
            self.show_lesson(self.lessons[idx - 1]["id"])

    def next_lesson(self):
        idx = next((i for i, x in enumerate(self.lessons) if x["id"] == self.current_lesson), 0)
        if idx < len(self.lessons) - 1:
            self.show_lesson(self.lessons[idx + 1]["id"])

    def show_quiz(self, lesson_id=None):
        if lesson_id in self.lesson_by_id:
            self.current_quiz_lesson = lesson_id
        elif self.current_quiz_lesson not in self.lesson_by_id:
            self.current_quiz_lesson = self.current_lesson
        self._activate_view("quiz")
        v = self.views["quiz"].inner
        self._clear(v)
        self._section_title(v, "Learning Mode – Quiz", "Mỗi bài có bài kiểm tra nhanh. Điểm cao nhất được lưu để theo dõi tiến độ.")

        chooser = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        chooser.pack(fill="x", pady=(0, 10))
        ci = tk.Frame(chooser, bg="white"); ci.pack(fill="x", padx=16, pady=12)
        tk.Label(ci, text="Chọn bài:", bg="white", fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        values = [f'{x["id"]} – {x["title"]}' for x in self.lessons]
        combo = ttk.Combobox(ci, values=values, state="readonly", width=54)
        current_index = next((i for i, x in enumerate(self.lessons) if x["id"] == self.current_quiz_lesson), 0)
        combo.current(current_index)
        combo.pack(side="left", padx=8)
        combo.bind("<<ComboboxSelected>>", lambda e: self._select_quiz_lesson(combo.current()))
        ttk.Button(ci, text="Mở bài học", command=lambda: self.show_lesson(self.current_quiz_lesson)).pack(side="right")

        lesson = self.lesson_by_id[self.current_quiz_lesson]
        questions = self.quiz_bank.get(self.current_quiz_lesson, [])
        tk.Label(v, text=f'{lesson["id"]}  {lesson["title"]}', bg=BG, fg=TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=(4, 8))
        previous = self.quiz_scores.get(self.current_quiz_lesson)
        if previous is not None:
            tk.Label(v, text=f"Điểm cao nhất đã lưu: {previous}%", bg=BG, fg="#15803d", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        answer_vars = []
        for qi, q in enumerate(questions):
            card = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
            card.pack(fill="x", pady=6)
            tk.Label(card, text=f"Câu {qi+1}. {q['question']}", bg="white", fg=TEXT, font=("Segoe UI", 13, "bold"), wraplength=1000, justify="left").pack(anchor="w", padx=16, pady=(14, 8))
            var = tk.IntVar(value=-1); answer_vars.append(var)
            for oi, opt in enumerate(q["options"]):
                tk.Radiobutton(card, text=opt, variable=var, value=oi, bg="white", fg=TEXT, activebackground="white", font=("Segoe UI", self.font_size), wraplength=940, justify="left", anchor="w").pack(fill="x", padx=20, pady=3)
            tk.Frame(card, bg="white", height=10).pack()

        if not questions:
            tk.Label(v, text="Bài này chưa có câu hỏi quiz.", bg=BG, fg=MUTED, font=("Segoe UI", 12)).pack(anchor="w")
        else:
            ttk.Button(v, text="Chấm điểm", command=lambda: self._grade_quiz(self.current_quiz_lesson, questions, answer_vars)).pack(anchor="w", pady=12)

    def _select_quiz_lesson(self, index):
        self.current_quiz_lesson = self.lessons[index]["id"]
        self.show_quiz(self.current_quiz_lesson)

    def _grade_quiz(self, lid, questions, vars_):
        if any(v.get() < 0 for v in vars_):
            messagebox.showinfo("Quiz", "Hãy trả lời tất cả câu hỏi trước khi chấm điểm.")
            return
        correct = sum(1 for q, v in zip(questions, vars_) if v.get() == q["answer"])
        score = round(correct * 100 / len(questions))
        old = int(self.quiz_scores.get(lid, 0))
        if score > old:
            self.quiz_scores[lid] = score
        self._save_state()
        explanations = []
        for i, (q, v) in enumerate(zip(questions, vars_), 1):
            status = "Đúng" if v.get() == q["answer"] else "Chưa đúng"
            explanations.append(f"Câu {i}: {status}. {q['explain']}")
        messagebox.showinfo("Kết quả Quiz", f"Điểm: {score}% ({correct}/{len(questions)})\n\n" + "\n".join(explanations))
        self.show_quiz(lid)

    def show_cases(self, case_id=None):
        if case_id in self.case_by_id:
            self.current_case_id = case_id
        self._activate_view("cases")
        v = self.views["cases"].inner
        self._clear(v)
        self._section_title(v, "Case Study Mode", "Đọc tình huống, chọn hướng xử lý và xem giải thích. Mục tiêu là luyện cách nghĩ, không chỉ nhớ định nghĩa.")

        nav = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        nav.pack(fill="x", pady=(0, 10))
        ni = tk.Frame(nav, bg="white"); ni.pack(fill="x", padx=14, pady=10)
        tk.Label(ni, text="Tình huống:", bg="white", fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        values = [f'{c["id"][-2:]} – {c["title"]}' for c in CASES]
        combo = ttk.Combobox(ni, values=values, state="readonly", width=55)
        idx = next((i for i, c in enumerate(CASES) if c["id"] == self.current_case_id), 0)
        combo.current(idx); combo.pack(side="left", padx=8)
        combo.bind("<<ComboboxSelected>>", lambda e: self._select_case(combo.current()))

        case = self.case_by_id[self.current_case_id]
        card = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        card.pack(fill="x")
        tk.Label(card, text=case["category"].upper(), bg="white", fg="#7c3aed", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(15, 2))
        tk.Label(card, text=case["title"], bg="white", fg=TEXT, font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=18)
        tk.Label(card, text=case["situation"], bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=1000, justify="left").pack(anchor="w", padx=18, pady=(10, 16))
        tk.Label(card, text=case["question"], bg="#f8fafc", fg=TEXT, font=("Segoe UI", 13, "bold"), wraplength=1000, justify="left").pack(fill="x", padx=18, pady=(0, 8))
        var = tk.IntVar(value=-1)
        for i, opt in enumerate(case["options"]):
            tk.Radiobutton(card, text=opt, variable=var, value=i, bg="white", activebackground="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=970, justify="left", anchor="w").pack(fill="x", padx=25, pady=4)
        actions = tk.Frame(card, bg="white"); actions.pack(fill="x", padx=18, pady=15)
        ttk.Button(actions, text="Kiểm tra lựa chọn", command=lambda: self._grade_case(case, var)).pack(side="left")
        tk.Label(actions, text="Công cụ liên quan: " + " • ".join(case.get("tools", [])), bg="white", fg=MUTED, font=("Segoe UI", 10, "bold")).pack(side="right")
        if case["id"] in self.case_results:
            ok = self.case_results[case["id"]]
            tk.Label(v, text="Đã hoàn thành đúng" if ok else "Đã thử – nên xem lại giải thích", bg=BG, fg="#15803d" if ok else "#b45309", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=8)

    def _select_case(self, index):
        self.current_case_id = CASES[index]["id"]
        self.show_cases(self.current_case_id)

    def _grade_case(self, case, var):
        if var.get() < 0:
            messagebox.showinfo("Case Study", "Hãy chọn một phương án.")
            return
        ok = var.get() == case["answer"]
        self.case_results[case["id"]] = ok
        self._save_state()
        prefix = "Chính xác." if ok else "Chưa phải phương án phù hợp nhất."
        messagebox.showinfo("Case Study", prefix + "\n\n" + case["explain"])
        self.show_cases(case["id"])

    def show_tools(self, tool_id=None):
        if tool_id in self.tool_by_id:
            self.current_tool_id = tool_id
        self._activate_view("tools")
        v = self.views["tools"].inner
        self._clear(v)
        self._section_title(v, "Thinking & Management Tools", f"{len(TOOLS)} công cụ thực hành. Chọn công cụ theo tình huống, không dùng form theo thói quen.")

        search = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        search.pack(fill="x", pady=(0, 10))
        si = tk.Frame(search, bg="white"); si.pack(fill="x", padx=14, pady=10)
        tk.Label(si, text="Tìm công cụ:", bg="white", fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        ent = ttk.Entry(si, textvariable=self.tool_search_var, width=38); ent.pack(side="left", padx=8)
        ttk.Button(si, text="Lọc", command=self._filter_tools).pack(side="left")
        ttk.Button(si, text="Tất cả", command=self._reset_tools).pack(side="left", padx=5)

        content = tk.Frame(v, bg=BG); content.pack(fill="x")
        listbox = tk.Frame(content, bg="white", bd=1, relief="solid", highlightbackground=LINE, width=300)
        listbox.pack(side="left", fill="y", padx=(0, 8)); listbox.pack_propagate(False)
        self.tool_list_frame = listbox
        self.tool_detail_frame = tk.Frame(content, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        self.tool_detail_frame.pack(side="left", fill="both", expand=True)
        self._render_tool_list(TOOLS)
        self._render_tool_detail(self.current_tool_id)

    def _render_tool_list(self, tools):
        self._clear(self.tool_list_frame)
        for t in tools:
            b = tk.Button(self.tool_list_frame, text=f'{t["icon"]}  {t["name"]}', command=lambda tid=t["id"]: self._choose_tool(tid), bg="white", fg=TEXT, relief="flat", anchor="w", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
            b.pack(fill="x", padx=5, pady=2)

    def _choose_tool(self, tid):
        self.current_tool_id = tid
        self._render_tool_detail(tid)

    def _filter_tools(self):
        q = self.tool_search_var.get().strip().lower()
        items = [t for t in TOOLS if q in (t["name"] + " " + t["category"] + " " + t["when"]).lower()]
        self._render_tool_list(items)
        if items:
            self._choose_tool(items[0]["id"])

    def _reset_tools(self):
        self.tool_search_var.set("")
        self._render_tool_list(TOOLS)
        if TOOLS:
            self._choose_tool(TOOLS[0]["id"])

    def _render_tool_detail(self, tid):
        self._clear(self.tool_detail_frame)
        t = self.tool_by_id.get(tid)
        if not t:
            return
        tk.Label(self.tool_detail_frame, text=t["category"].upper(), bg="white", fg="#7c3aed", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(self.tool_detail_frame, text=f'{t["icon"]}  {t["name"]}', bg="white", fg=TEXT, font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=18)
        tk.Label(self.tool_detail_frame, text="KHI NÀO DÙNG", bg="white", fg="#1d4ed8", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        tk.Label(self.tool_detail_frame, text=t["when"], bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=720, justify="left").pack(anchor="w", padx=18)
        tk.Label(self.tool_detail_frame, text="CÁC BƯỚC", bg="white", fg="#15803d", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        for i, step in enumerate(t["steps"], 1):
            tk.Label(self.tool_detail_frame, text=f"{i}. {step}", bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=720, justify="left").pack(anchor="w", padx=24, pady=2)
        tk.Label(self.tool_detail_frame, text="OUTPUT", bg="white", fg="#b45309", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        tk.Label(self.tool_detail_frame, text=t["output"], bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=720, justify="left").pack(anchor="w", padx=18)
        tk.Label(self.tool_detail_frame, text="SAI LẦM THƯỜNG GẶP", bg="white", fg="#b91c1c", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        for item in t["mistakes"]:
            tk.Label(self.tool_detail_frame, text="• " + item, bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=720, justify="left").pack(anchor="w", padx=24, pady=2)
        tk.Frame(self.tool_detail_frame, bg="white", height=15).pack()

    def show_glossary(self):
        self._activate_view("glossary")
        v = self.views["glossary"].inner
        self._clear(v)
        self._section_title(v, "Từ điển quản lý & tư duy", f"{len(GLOSSARY)} thuật ngữ. Tra cứu nhanh mà không cần rời ứng dụng.")
        search = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
        search.pack(fill="x", pady=(0, 10))
        si = tk.Frame(search, bg="white"); si.pack(fill="x", padx=14, pady=10)
        tk.Label(si, text="Từ khóa:", bg="white", fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        ent = ttk.Entry(si, textvariable=self.glossary_search_var, width=38); ent.pack(side="left", padx=8)
        ent.bind("<KeyRelease>", lambda e: self._render_glossary_results())
        ttk.Button(si, text="Xóa", command=lambda: (self.glossary_search_var.set(""), self._render_glossary_results())).pack(side="left")
        self.glossary_result_frame = tk.Frame(v, bg=BG); self.glossary_result_frame.pack(fill="x")
        self._render_glossary_results()

    def _render_glossary_results(self):
        f = self.glossary_result_frame
        self._clear(f)
        q = self.glossary_search_var.get().strip().lower()
        items = [(k, v) for k, v in GLOSSARY.items() if not q or q in k.lower() or q in v.lower()]
        for term, definition in sorted(items, key=lambda x: x[0].lower()):
            card = tk.Frame(f, bg="white", bd=1, relief="solid", highlightbackground=LINE)
            card.pack(fill="x", pady=4)
            tk.Label(card, text=term, bg="white", fg="#1d4ed8", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 3))
            tk.Label(card, text=definition, bg="white", fg=TEXT, font=("Segoe UI", self.font_size + 1), wraplength=1000, justify="left").pack(anchor="w", padx=15, pady=(0, 11))
        if not items:
            tk.Label(f, text="Không tìm thấy thuật ngữ phù hợp.", bg=BG, fg=MUTED, font=("Segoe UI", 12)).pack(anchor="w", pady=10)

    def show_progress(self):
        self._activate_view("progress")
        v = self.views["progress"].inner
        self._clear(v)
        self._section_title(v, "Tiến độ học tập", "Tổng hợp đọc sách, quiz và case study. Dữ liệu được lưu tại máy và giữ lại khi cập nhật EXE.")

        overall = tk.Frame(v, bg=BG); overall.pack(fill="x", pady=(0, 10))
        done = len(self.read_lessons & set(self.lesson_by_id))
        quiz_done = len(self.quiz_scores)
        avg_quiz = round(sum(int(x) for x in self.quiz_scores.values()) / quiz_done) if quiz_done else 0
        case_correct = sum(1 for x in self.case_results.values() if x)
        data = [
            ("Đọc sách", f"{done}/{len(self.lessons)}", "#dbeafe", "#1d4ed8"),
            ("Quiz hoàn thành", f"{quiz_done}/{len(self.lessons)}", "#ede9fe", "#7c3aed"),
            ("Quiz TB", f"{avg_quiz}%", "#fef3c7", "#b45309"),
            ("Case đúng", f"{case_correct}/{len(CASES)}", "#dcfce7", "#15803d"),
        ]
        for title, value, bg, fg in data:
            c = tk.Frame(overall, bg=bg, bd=1, relief="solid", highlightbackground=LINE)
            c.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(c, text=title.upper(), bg=bg, fg=fg, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=13, pady=(11, 2))
            tk.Label(c, text=value, bg=bg, fg=TEXT, font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=13, pady=(0, 11))

        for ch in CHAPTERS:
            ids = [l["id"] for l in ch["lessons"]]
            ch_done = len([x for x in ids if x in self.read_lessons])
            ch_quiz = [int(self.quiz_scores[x]) for x in ids if x in self.quiz_scores]
            pct = round(ch_done * 100 / len(ids)) if ids else 0
            qavg = round(sum(ch_quiz) / len(ch_quiz)) if ch_quiz else 0
            card = tk.Frame(v, bg="white", bd=1, relief="solid", highlightbackground=LINE)
            card.pack(fill="x", pady=4)
            top = tk.Frame(card, bg="white"); top.pack(fill="x", padx=14, pady=(10, 5))
            tk.Label(top, text=ch["title"], bg="white", fg=TEXT, font=("Segoe UI", 12, "bold")).pack(side="left")
            tk.Label(top, text=f"Đọc {ch_done}/{len(ids)} • Quiz TB {qavg}%", bg="white", fg=MUTED, font=("Segoe UI", 10, "bold")).pack(side="right")
            bar = ttk.Progressbar(card, maximum=100, value=pct)
            bar.pack(fill="x", padx=14, pady=(0, 10))

    def change_font(self, delta):
        self.font_size = max(11, min(17, self.font_size + delta))
        self._save_state()
        if self.current_view == "lesson":
            self.show_lesson(self.current_lesson, add_history=False)
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

    def close_app(self):
        self._save_state()
        if messagebox.askyesno("Thoát ứng dụng", "Bạn muốn thoát Tư Duy Đúng – Book App?"):
            self.destroy()


if __name__ == "__main__":
    App().mainloop()
