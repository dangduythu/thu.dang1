# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from v42_data import MULTI_CASES, WORKBENCH_TEMPLATES, next_review, flashcard_for_lesson
from i18n_en import EN_LESSONS
from i18n_extra import EN_STORIES

BG="#edf3fb"
TEXT="#14213d"
MUTED="#64748b"
LINE="#d8e3f0"
NAVY="#274472"


class V42Mixin:
    def toggle_focus_mode(self):
        if not getattr(self,"focus_mode",False):
            try:self.topbar.pack_forget()
            except Exception:pass
            try:self.sidebar.pack_forget()
            except Exception:pass
            self.focus_mode=True
        else:
            try:self.topbar.pack(fill="x",before=self.body)
            except Exception:self.topbar.pack(fill="x")
            try:self.sidebar.pack(side="left",fill="y",padx=(10,8),pady=10,before=self.main)
            except Exception:self.sidebar.pack(side="left",fill="y",padx=(10,8),pady=10)
            self.focus_mode=False

    def show_notes(self,lid=None):
        if lid in self.lesson_by_id:self.current_lesson=lid
        self._activate_view("notes")
        v=self.views["notes"].inner; self._clear(v)
        self._section_title(v,"Ghi chú cá nhân","Personal Notes",
                            "Ghi lại điều quan trọng theo từng bài. Dữ liệu được lưu cùng tiến độ.",
                            "Capture what matters for each lesson. Notes are saved with your progress.")

        bar=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); bar.pack(fill="x",pady=(0,10))
        bi=tk.Frame(bar,bg="white"); bi.pack(fill="x",padx=14,pady=10)
        vals=[f'{l["id"]} – {self._text(l["title"],EN_LESSONS[l["id"]]["title"]).replace(chr(10)," | ")}' for l in self.lessons]
        combo=ttk.Combobox(bi,values=vals,state="readonly",width=72)
        pos=next((i for i,l in enumerate(self.lessons) if l["id"]==self.current_lesson),0)
        combo.current(pos); combo.pack(side="left",padx=(0,8))
        combo.bind("<<ComboboxSelected>>",lambda e:self.show_notes(self.lessons[combo.current()]["id"]))
        ttk.Button(bi,text=self._text("Mở bài","Open lesson").replace("\n"," / "),command=lambda:self.show_lesson(self.current_lesson)).pack(side="right")

        editor_card=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); editor_card.pack(fill="x")
        tk.Label(editor_card,text=self._text("Ghi chú của tôi","My notes"),bg="white",fg=TEXT,font=("Segoe UI",16,"bold")).pack(anchor="w",padx=16,pady=(14,6))
        self.note_editor=tk.Text(editor_card,height=18,wrap="word",font=("Segoe UI",self.font_size+1),undo=True)
        self.note_editor.pack(fill="x",padx=16,pady=(0,10))
        self.note_editor.insert("1.0",self.notes.get(self.current_lesson,""))
        acts=tk.Frame(editor_card,bg="white"); acts.pack(fill="x",padx=16,pady=(0,14))
        ttk.Button(acts,text=self._text("Lưu ghi chú","Save note").replace("\n"," / "),command=self._save_current_note).pack(side="left")
        ttk.Button(acts,text=self._text("Xuất tất cả ghi chú","Export all notes").replace("\n"," / "),command=self._export_notes).pack(side="left",padx=6)
        tk.Label(acts,textvariable=self.note_status_var,bg="white",fg="#15803d",font=("Segoe UI",9,"bold")).pack(side="left",padx=8)

        saved=[lid for lid,n in self.notes.items() if str(n).strip()]
        if saved:
            tk.Label(v,text=self._text(f"Đã có ghi chú ở {len(saved)} bài.",f"Notes saved for {len(saved)} lessons."),
                     bg=BG,fg=MUTED,font=("Segoe UI",10,"bold")).pack(anchor="w",pady=8)

    def _save_current_note(self):
        if not hasattr(self,"note_editor"):return
        value=self.note_editor.get("1.0","end").strip()
        if value:self.notes[self.current_lesson]=value
        else:self.notes.pop(self.current_lesson,None)
        self.note_status_var.set(self._text("Đã lưu","Saved").replace("\n"," / "))
        self._save_state()

    def _export_notes(self):
        if not self.notes:
            messagebox.showinfo("Notes / Ghi chú","Chưa có ghi chú / No notes to export."); return
        path=filedialog.asksaveasfilename(title="Export notes",defaultextension=".txt",
                                          filetypes=[("Text file","*.txt"),("All files","*.*")])
        if not path:return
        lines=["TƯ DUY ĐÚNG / THINK RIGHT – NOTES","="*60,""]
        for l in self.lessons:
            note=self.notes.get(l["id"],"").strip()
            if not note:continue
            lines.append(f'{l["id"]} {l["title"]} / {EN_LESSONS[l["id"]]["title"]}')
            lines.append(note); lines.append("-"*60)
        Path(path).write_text("\n".join(lines),encoding="utf-8")
        messagebox.showinfo("Notes / Ghi chú","Đã xuất file / Export completed.")

    def _due_flash_ids(self):
        today=date.today().isoformat()
        due=[lid for lid,s in self.review_state.items() if s.get("due","")<=today and lid in self.lesson_by_id]
        return sorted(due,key=lambda x:float(x))

    def show_review(self):
        self._activate_view("review")
        v=self.views["review"].inner; self._clear(v)
        due=self._due_flash_ids()
        self._section_title(v,"Ôn tập thông minh","Smart Review",
                            "Flashcard + spaced repetition. Bài khó sẽ quay lại sớm hơn.",
                            "Flashcards + spaced repetition. Difficult material returns sooner.")
        ids=due if due else [l["id"] for l in self.lessons]
        if not ids:return
        if self.current_flash_index>=len(ids):self.current_flash_index=0
        lid=ids[self.current_flash_index]
        data=flashcard_for_lesson(self.lesson_by_id[lid],EN_LESSONS[lid])

        status=tk.Frame(v,bg=BG); status.pack(fill="x",pady=(0,8))
        tk.Label(status,text=self._text(f"Đến hạn hôm nay: {len(due)}",f"Due today: {len(due)}"),
                 bg=BG,fg=MUTED,font=("Segoe UI",10,"bold")).pack(side="left")
        st=self.review_state[lid]
        tk.Label(status,text=f'Level {st.get("level",0)} • Reviews {st.get("reviews",0)} • Due {st.get("due","")}',
                 bg=BG,fg=MUTED,font=("Segoe UI",9)).pack(side="right")

        card=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); card.pack(fill="x")
        tk.Label(card,text=f'{lid}  {self._text(data["front_vi"],data["front_en"])}',
                 bg="white",fg=TEXT,font=("Segoe UI",24,"bold"),wraplength=1000,justify="left").pack(anchor="w",padx=22,pady=(22,12))
        tk.Label(card,text=self._text("Hãy tự nhớ lại ý chính trước khi mở đáp án.","Recall the key idea before revealing the answer."),
                 bg="white",fg=MUTED,font=("Segoe UI",11),justify="left").pack(anchor="w",padx=22,pady=(0,16))

        self.flash_answer_frame=tk.Frame(card,bg="#f8fafc")
        self.flash_answer_frame.pack(fill="x",padx=22,pady=(0,16))
        if self.flash_answer_visible:self._render_flash_answer(data)
        else:ttk.Button(self.flash_answer_frame,text=self._text("Hiện đáp án","Reveal answer").replace("\n"," / "),
                        command=self._reveal_flash).pack(anchor="center",pady=18)

        nav=tk.Frame(v,bg=BG); nav.pack(fill="x",pady=10)
        ttk.Button(nav,text="←",command=lambda:self._move_flash(-1,len(ids))).pack(side="left")
        tk.Label(nav,text=f'{self.current_flash_index+1}/{len(ids)}',bg=BG,fg=MUTED,font=("Segoe UI",10,"bold")).pack(side="left",padx=8)
        ttk.Button(nav,text="→",command=lambda:self._move_flash(1,len(ids))).pack(side="left")

    def _render_flash_answer(self,data):
        self._clear(self.flash_answer_frame)
        tk.Label(self.flash_answer_frame,text=self._text("ĐÁP ÁN","ANSWER"),bg="#f8fafc",fg="#7c3aed",
                 font=("Segoe UI",10,"bold")).pack(anchor="w",padx=15,pady=(12,5))
        body=tk.Frame(self.flash_answer_frame,bg="#f8fafc"); body.pack(fill="x",padx=15)
        self._bi_body(body,data["back_vi"],data["back_en"],900,bg="#f8fafc")
        rate=tk.Frame(self.flash_answer_frame,bg="#f8fafc"); rate.pack(fill="x",padx=15,pady=12)
        ttk.Button(rate,text=self._text("Khó","Hard").replace("\n"," / "),command=lambda:self._rate_flash("hard")).pack(side="left")
        ttk.Button(rate,text=self._text("Tốt","Good").replace("\n"," / "),command=lambda:self._rate_flash("good")).pack(side="left",padx=6)
        ttk.Button(rate,text=self._text("Dễ","Easy").replace("\n"," / "),command=lambda:self._rate_flash("easy")).pack(side="left")

    def _reveal_flash(self):
        self.flash_answer_visible=True
        self.show_review()

    def _move_flash(self,delta,total):
        if total:self.current_flash_index=(self.current_flash_index+delta)%total
        self.flash_answer_visible=False
        self.show_review()

    def _rate_flash(self,rating):
        ids=self._due_flash_ids() or [l["id"] for l in self.lessons]
        if not ids:return
        lid=ids[self.current_flash_index%len(ids)]
        st=self.review_state.get(lid,{"level":0,"reviews":0,"due":date.today().isoformat()})
        level=int(st.get("level",0))
        if rating=="hard":
            level=max(0,level-1); due=(date.today()+timedelta(days=1)).isoformat()
        elif rating=="easy":
            level,due=next_review(min(level+1,5))
        else:
            level,due=next_review(level)
        self.review_state[lid]={"level":level,"due":due,"reviews":int(st.get("reviews",0))+1}
        self._save_state()
        self.flash_answer_visible=False
        self.current_flash_index+=1
        self.show_review()

    def show_case_lab(self,case_id=None,reset=False):
        if case_id and any(x["id"]==case_id for x in MULTI_CASES):self.current_multi_case=case_id
        if reset or not hasattr(self,"multi_step_index"):
            self.multi_step_index=0; self.multi_score=0
        self._activate_view("cases")
        v=self.views["cases"].inner; self._clear(v)
        self._section_title(v,"Case Lab – Tình huống nhiều bước","Case Lab – Multi-step scenarios",
                            "Ra quyết định từng bước và nhận feedback ngay.",
                            "Make decisions step by step and receive immediate feedback.")

        bar=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); bar.pack(fill="x",pady=(0,10))
        bi=tk.Frame(bar,bg="white"); bi.pack(fill="x",padx=14,pady=10)
        vals=[self._text(x["title_vi"],x["title_en"]).replace("\n"," | ") for x in MULTI_CASES]
        combo=ttk.Combobox(bi,values=vals,state="readonly",width=68)
        pos=next((i for i,x in enumerate(MULTI_CASES) if x["id"]==self.current_multi_case),0)
        combo.current(pos); combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>",lambda e:self.show_case_lab(MULTI_CASES[combo.current()]["id"],True))
        ttk.Button(bi,text=self._text("Case cổ điển","Classic cases").replace("\n"," / "),command=self.show_cases).pack(side="right")

        case=next(x for x in MULTI_CASES if x["id"]==self.current_multi_case)
        tk.Label(v,text=self._text(case["title_vi"],case["title_en"]),bg=BG,fg=TEXT,font=("Segoe UI",22,"bold"),justify="left").pack(anchor="w",pady=(4,5))
        tk.Label(v,text=self._text(case["intro_vi"],case["intro_en"]),bg=BG,fg=MUTED,font=("Segoe UI",11),wraplength=1000,justify="left").pack(anchor="w",pady=(0,10))

        if self.multi_step_index>=len(case["steps"]):
            pct=round(self.multi_score*100/len(case["steps"]))
            done=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); done.pack(fill="x")
            tk.Label(done,text=self._text("HOÀN THÀNH CASE","CASE COMPLETED"),bg="white",fg="#15803d",font=("Segoe UI",17,"bold")).pack(anchor="w",padx=18,pady=(16,5))
            tk.Label(done,text=f'{self.multi_score}/{len(case["steps"])} • {pct}%',bg="white",fg=TEXT,font=("Segoe UI",28,"bold")).pack(anchor="w",padx=18)
            ttk.Button(done,text=self._text("Làm lại","Restart").replace("\n"," / "),command=lambda:self.show_case_lab(case["id"],True)).pack(anchor="w",padx=18,pady=16)
            self.case_results[case["id"]]=pct; self._save_state(); return

        step=case["steps"][self.multi_step_index]
        card=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); card.pack(fill="x")
        tk.Label(card,text=f'{self._text("Bước","Step")} {self.multi_step_index+1}/{len(case["steps"])}',
                 bg="white",fg="#7c3aed",font=("Segoe UI",10,"bold")).pack(anchor="w",padx=18,pady=(14,4))
        tk.Label(card,text=self._text(step["q_vi"],step["q_en"]),bg="white",fg=TEXT,font=("Segoe UI",16,"bold"),
                 wraplength=1000,justify="left").pack(anchor="w",padx=18,pady=(0,10))
        var=tk.IntVar(value=-1)
        for i in range(len(step["options_vi"])):
            tk.Radiobutton(card,text=self._text(step["options_vi"][i],step["options_en"][i]),variable=var,value=i,
                           bg="white",activebackground="white",fg=TEXT,font=("Segoe UI",self.font_size),
                           wraplength=980,justify="left",anchor="w").pack(fill="x",padx=24,pady=4)
        ttk.Button(card,text=self._text("Trả lời","Submit").replace("\n"," / "),
                   command=lambda:self._grade_multi_step(case,step,var)).pack(anchor="w",padx=18,pady=15)

    def _grade_multi_step(self,case,step,var):
        if var.get()<0:
            messagebox.showinfo("Case Lab","Hãy chọn phương án / Please choose an option."); return
        ok=var.get()==step["answer"]
        if ok:self.multi_score+=1
        prefix=self._text("Chính xác.","Correct.") if ok else self._text("Chưa đúng.","Not correct.")
        messagebox.showinfo("Case Lab",prefix+"\n\n"+self._text(step["why_vi"],step["why_en"]))
        self.multi_step_index+=1
        self.show_case_lab(case["id"])

    def show_workbench(self,tid=None):
        if tid and any(x["id"]==tid for x in WORKBENCH_TEMPLATES):self.current_workbench=tid
        self._activate_view("workbench")
        v=self.views["workbench"].inner; self._clear(v)
        self._section_title(v,"Workbench – Công cụ áp dụng thật","Workbench – Apply the tools",
                            "Điền trực tiếp 5 Why, PDCA, A3, RACI, Risk, Decision và Skill Matrix.",
                            "Fill in 5 Why, PDCA, A3, RACI, Risk, Decision, and Skill Matrix directly.")

        top=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); top.pack(fill="x",pady=(0,10))
        ti=tk.Frame(top,bg="white"); ti.pack(fill="x",padx=14,pady=10)
        vals=[self._text(x["name_vi"],x["name_en"]).replace("\n"," | ") for x in WORKBENCH_TEMPLATES]
        combo=ttk.Combobox(ti,values=vals,state="readonly",width=55)
        pos=next((i for i,x in enumerate(WORKBENCH_TEMPLATES) if x["id"]==self.current_workbench),0)
        combo.current(pos); combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>",lambda e:self.show_workbench(WORKBENCH_TEMPLATES[combo.current()]["id"]))
        ttk.Button(ti,text=self._text("Thư viện công cụ","Tool library").replace("\n"," / "),command=self.show_tools).pack(side="right")

        template=next(x for x in WORKBENCH_TEMPLATES if x["id"]==self.current_workbench)
        saved=self.workbench_docs.get(template["id"],{})
        form=tk.Frame(v,bg="white",bd=1,relief="solid",highlightbackground=LINE); form.pack(fill="x")
        tk.Label(form,text=f'{template["name_vi"]} / {template["name_en"]}',bg="white",fg=TEXT,font=("Segoe UI",20,"bold")).pack(anchor="w",padx=16,pady=(15,10))
        self.workbench_entries={}
        for key,label in template["fields"]:
            row=tk.Frame(form,bg="white"); row.pack(fill="x",padx=16,pady=5)
            tk.Label(row,text=label,bg="white",fg=NAVY,font=("Segoe UI",10,"bold"),width=32,anchor="nw",justify="left").pack(side="left",padx=(0,8))
            box=tk.Text(row,height=2,wrap="word",font=("Segoe UI",self.font_size))
            box.pack(side="left",fill="x",expand=True)
            box.insert("1.0",str(saved.get(key,"")))
            self.workbench_entries[key]=box
        acts=tk.Frame(form,bg="white"); acts.pack(fill="x",padx=16,pady=14)
        ttk.Button(acts,text=self._text("Lưu worksheet","Save worksheet").replace("\n"," / "),command=self._save_workbench).pack(side="left")
        ttk.Button(acts,text=self._text("Tính/Phân tích","Calculate/Analyze").replace("\n"," / "),command=self._analyze_workbench).pack(side="left",padx=6)
        ttk.Button(acts,text=self._text("Xuất TXT","Export TXT").replace("\n"," / "),command=self._export_workbench).pack(side="left")
        self.workbench_result=tk.Label(v,text="",bg=BG,fg=TEXT,font=("Segoe UI",11,"bold"),wraplength=1000,justify="left")
        self.workbench_result.pack(anchor="w",pady=10)

    def _workbench_values(self):
        return {k:w.get("1.0","end").strip() for k,w in getattr(self,"workbench_entries",{}).items()}

    def _save_workbench(self):
        self.workbench_docs[self.current_workbench]=self._workbench_values()
        self._save_state()
        messagebox.showinfo("Workbench","Đã lưu worksheet / Worksheet saved.")

    def _analyze_workbench(self):
        vals=self._workbench_values(); tid=self.current_workbench
        result=""
        if tid=="risk":
            try:
                p=int(vals.get("probability","0")); i=int(vals.get("impact","0"))
                rp=int(vals.get("residual_p","0")); ri=int(vals.get("residual_i","0"))
                result=f'Initial Risk = {p*i} ({p}×{i})   |   Residual Risk = {rp*ri} ({rp}×{ri})'
            except Exception:
                result=self._text("Hãy nhập Probability/Impact dạng số 1–5.","Enter Probability/Impact as numbers 1–5.")
        elif tid=="decision":
            try:
                options=[x.strip() for x in vals.get("options","").split(",") if x.strip()]
                criteria=[x.strip() for x in vals.get("criteria","").split(",") if x.strip()]
                weights=[float(x.strip()) for x in vals.get("weights","").split(",") if x.strip()]
                rows=[r.strip() for r in vals.get("scores","").split(";") if r.strip()]
                scores=[[float(x.strip()) for x in r.split(",")] for r in rows]
                if len(criteria)!=len(weights):raise ValueError("weights")
                if len(options)!=len(scores):raise ValueError("rows")
                totals=[]
                for name,row in zip(options,scores):
                    if len(row)!=len(weights):raise ValueError("cols")
                    totals.append((name,sum(s*w for s,w in zip(row,weights))/sum(weights)))
                totals.sort(key=lambda x:x[1],reverse=True)
                result="Weighted totals:  "+"  |  ".join(f"{n}: {v:.2f}" for n,v in totals)
            except Exception:
                result=self._text("Scores: mỗi phương án một hàng, ngăn bằng ';'. Ví dụ 8,7,9;7,9,8",
                                  "Scores: one row per option separated by ';'. Example 8,7,9;7,9,8")
        else:
            filled=sum(1 for x in vals.values() if x.strip())
            result=self._text(f"Đã điền {filled}/{len(vals)} trường. Kiểm tra logic và bằng chứng trước khi chốt.",
                              f"{filled}/{len(vals)} fields completed. Check logic and evidence before closing.")
        self.workbench_result.configure(text=result)

    def _export_workbench(self):
        vals=self._workbench_values()
        path=filedialog.asksaveasfilename(title="Export worksheet",defaultextension=".txt",filetypes=[("Text file","*.txt")])
        if not path:return
        template=next(x for x in WORKBENCH_TEMPLATES if x["id"]==self.current_workbench)
        labels=dict(template["fields"])
        lines=[f'{template["name_vi"]} / {template["name_en"]}',"="*60]
        for key,_ in template["fields"]:
            lines.extend(["",labels[key],vals.get(key,"")])
        Path(path).write_text("\n".join(lines),encoding="utf-8")
        messagebox.showinfo("Workbench","Đã xuất file / Export completed.")
