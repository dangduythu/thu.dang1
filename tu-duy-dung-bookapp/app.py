import json, os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from content import CHAPTERS

APP_NAME="Tư Duy Đúng – Book App"
VERSION="1.4.3"
APP_DIR="TuDuyDungBookApp"

PALETTES={
"flow":dict(primary="#2563eb",soft="#dbeafe",accent="#16a34a",accent2="#dcfce7",alt="#f59e0b",alt2="#fef3c7"),
"steps":dict(primary="#7c3aed",soft="#ede9fe",accent="#0ea5e9",accent2="#e0f2fe",alt="#f97316",alt2="#ffedd5"),
"matrix":dict(primary="#059669",soft="#d1fae5",accent="#0f766e",accent2="#ccfbf1",alt="#f59e0b",alt2="#fef3c7"),
"compare":dict(primary="#dc2626",soft="#fee2e2",accent="#2563eb",accent2="#dbeafe",alt="#7c3aed",alt2="#f3e8ff"),
"ladder":dict(primary="#ea580c",soft="#ffedd5",accent="#2563eb",accent2="#dbeafe",alt="#16a34a",alt2="#dcfce7"),
"cycle":dict(primary="#0f766e",soft="#ccfbf1",accent="#7c3aed",accent2="#ede9fe",alt="#2563eb",alt2="#dbeafe"),
}

def state_path():
    p=Path(os.getenv("APPDATA",str(Path.home())))/APP_DIR
    p.mkdir(parents=True,exist_ok=True)
    return p/"state.json"

class Scroll(tk.Frame):
    def __init__(self,master,bg):
        super().__init__(master,bg=bg)
        self.canvas=tk.Canvas(self,bg=bg,highlightthickness=0)
        self.sb=ttk.Scrollbar(self,orient="vertical",command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.sb.set)
        self.sb.pack(side="right",fill="y"); self.canvas.pack(side="left",fill="both",expand=True)
        self.inner=tk.Frame(self.canvas,bg=bg)
        self.win=self.canvas.create_window((0,0),window=self.inner,anchor="nw")
        self.inner.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",lambda e:self.canvas.itemconfigure(self.win,width=e.width))
        # Mouse-wheel routing is handled globally by App so scrolling remains
        # reliable even when the pointer is over nested labels/cards/buttons.
    def scroll_units(self, units):
        self.canvas.yview_scroll(units,"units")
    def top(self): self.canvas.yview_moveto(0)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} V{VERSION}")
        self.geometry("1420x920"); self.minsize(1180,760)
        self.bg="#edf3fb"; self.panel="#ffffff"; self.text="#14213d"; self.muted="#64748b"; self.line="#d8e3f0"
        self.configure(bg=self.bg)
        st=self.load()
        self.bookmarks=set(st.get("bookmarks",[])); self.read=set(st.get("read_lessons",[]))
        self.current=st.get("last_lesson","1.1"); self.fs=int(st.get("font_size",12))
        self.lessons=[l for c in CHAPTERS for l in c["lessons"]]; self.byid={l["id"]:l for l in self.lessons}
        self.hist=[]; self.hpos=-1; self.block_tree=False
        self.q=tk.StringVar(); self.bookmark_var=tk.StringVar(); self.progress_var=tk.StringVar()
        self.style=ttk.Style(self)
        try:self.style.theme_use("clam")
        except:pass
        self.style.configure("TButton",padding=(10,7),font=("Segoe UI",10))
        self.style.configure("Treeview",rowheight=28,font=("Segoe UI",10),fieldbackground="white",background="white")
        self.style.map("Treeview",background=[("selected","#dbeafe")],foreground=[("selected","#0f172a")])
        self.build(); self.populate(); self.show_home(); self.protocol("WM_DELETE_WINDOW",self.close)
        self.bind_all("<MouseWheel>", self.global_mousewheel, add="+")
        self.bind_all("<Button-4>", self.global_mousewheel_linux, add="+")
        self.bind_all("<Button-5>", self.global_mousewheel_linux, add="+")

    def _is_descendant(self, widget, ancestor):
        cur=widget
        while cur is not None:
            if cur==ancestor:return True
            try:cur=cur.master
            except:return False
        return False

    def _scroll_target_under_pointer(self, event):
        try:
            w=self.winfo_containing(event.x_root,event.y_root)
        except:
            w=None
        if w is None:return None
        # Sidebar Treeview keeps its own native scrolling behavior.
        if self._is_descendant(w,self.tree):return None
        if self.reader.winfo_ismapped() and (self._is_descendant(w,self.reader.canvas) or self._is_descendant(w,self.reader.inner)):
            return self.reader
        if self.home.winfo_ismapped() and (self._is_descendant(w,self.home.canvas) or self._is_descendant(w,self.home.inner)):
            return self.home
        return None

    def global_mousewheel(self,event):
        target=self._scroll_target_under_pointer(event)
        if target is None:return
        delta=event.delta
        if delta==0:return "break"
        # Windows normally sends multiples of 120. Use a minimum of one unit
        # for high-resolution touchpads that send smaller deltas.
        steps=max(1,abs(int(delta/120))) if abs(delta)>=120 else 1
        target.scroll_units(-steps if delta>0 else steps)
        return "break"

    def global_mousewheel_linux(self,event):
        target=self._scroll_target_under_pointer(event)
        if target is None:return
        target.scroll_units(-1 if event.num==4 else 1)
        return "break"

    def load(self):
        try:return json.loads(state_path().read_text(encoding="utf-8"))
        except:return {}
    def save(self):
        try: state_path().write_text(json.dumps({"bookmarks":sorted(self.bookmarks),"read_lessons":sorted(self.read),"last_lesson":self.current,"font_size":self.fs},ensure_ascii=False,indent=2),encoding="utf-8")
        except:pass

    def build(self):
        top=tk.Frame(self,bg="white",height=72); top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top,text="TƯ DUY ĐÚNG",bg="white",fg="#274472",font=("Segoe UI",21,"bold")).pack(side="left",padx=(22,10))
        tk.Label(top,text=f"BOOK APP • V{VERSION}",bg="white",fg="#7a8aa0",font=("Segoe UI",10,"bold")).pack(side="left")
        ctr=tk.Frame(top,bg="white"); ctr.pack(side="right",padx=18)
        for text,cmd,w in [("A−",lambda:self.font(-1),4),("A+",lambda:self.font(1),4),("←",self.back,4),("→",self.forward,4),("⌂ Trang chủ",self.show_home,None)]:
            ttk.Button(ctr,text=text,command=cmd,width=w).pack(side="left",padx=3,pady=18)

        body=tk.Frame(self,bg=self.bg); body.pack(fill="both",expand=True)
        self.side=tk.Frame(body,bg="white",width=345); self.side.pack(side="left",fill="y",padx=(12,8),pady=12); self.side.pack_propagate(False)
        self.main=tk.Frame(body,bg=self.bg); self.main.pack(side="left",fill="both",expand=True,padx=(0,12),pady=12)
        self.build_sidebar()
        self.home=Scroll(self.main,self.bg); self.reader=Scroll(self.main,self.bg)
        self.render_home()

    def build_sidebar(self):
        b=tk.Canvas(self.side,height=128,bg="white",highlightthickness=0); b.pack(fill="x",padx=16,pady=(16,12))
        b.create_rectangle(0,0,310,128,fill="#8eb1df",outline=""); b.create_rectangle(0,90,310,128,fill="#e6a8a8",outline="")
        b.create_text(16,18,anchor="nw",text="TƯ DUY",fill="#fff59d",font=("Segoe UI",16,"bold"))
        b.create_text(16,47,anchor="nw",text="PHƯƠNG PHÁP QUẢN LÝ",fill="white",font=("Segoe UI",17,"bold"))
        b.create_text(16,80,anchor="nw",text="ĐÚNG",fill="white",font=("Segoe UI",24,"bold"))
        b.create_text(293,112,anchor="e",text=f"V{VERSION}",fill="white",font=("Segoe UI",9,"bold"))
        sr=tk.Frame(self.side,bg="white"); sr.pack(fill="x",padx=16,pady=(0,10))
        ent=ttk.Entry(sr,textvariable=self.q); ent.pack(side="left",fill="x",expand=True); ent.bind("<Return>",lambda e:self.search())
        ttk.Button(sr,text="Tìm",width=7,command=self.search).pack(side="left",padx=(6,0))
        br=tk.Frame(self.side,bg="white"); br.pack(fill="x",padx=16,pady=(0,10))
        ttk.Button(br,text="Mục lục",command=lambda:self.populate()).pack(side="left",fill="x",expand=True)
        ttk.Button(br,text="★ Đã lưu",command=self.show_bookmarks).pack(side="left",fill="x",expand=True,padx=(6,0))
        tk.Label(self.side,textvariable=self.progress_var,bg="white",fg="#64748b",font=("Segoe UI",10,"bold")).pack(anchor="w",padx=16)
        self.prog=ttk.Progressbar(self.side,maximum=100); self.prog.pack(fill="x",padx=16,pady=(6,12))
        tw=tk.Frame(self.side,bg="white"); tw.pack(fill="both",expand=True,padx=(12,8),pady=(0,12))
        self.tree=ttk.Treeview(tw,show="tree",selectmode="browse"); sb=ttk.Scrollbar(tw,orient="vertical",command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set); self.tree.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")
        self.tree.bind("<<TreeviewSelect>>",self.pick)

    def render_home(self):
        for w in self.home.inner.winfo_children():w.destroy()
        hero=tk.Frame(self.home.inner,bg="white",bd=1,relief="solid",highlightbackground=self.line); hero.pack(fill="x",pady=(0,16))
        inn=tk.Frame(hero,bg="white"); inn.pack(fill="x",padx=28,pady=28)
        tk.Label(inn,text="SÁCH TƯƠNG TÁC VỀ TƯ DUY & QUẢN LÝ",bg="white",fg="#7a8aa0",font=("Segoe UI",11,"bold")).pack(anchor="w")
        tk.Label(inn,text="Đọc sâu hơn. Dễ nhớ hơn.\nÁp dụng ngay vào công việc.",bg="white",fg=self.text,font=("Segoe UI",28,"bold"),justify="left").pack(anchor="w",pady=(10,8))
        tk.Label(inn,text="V1.4: 40 bài học có sơ đồ màu + lý do quan trọng + sai lầm thường gặp + bài tập áp dụng + câu hỏi phản tư.",bg="white",fg=self.muted,font=("Segoe UI",12),wraplength=900,justify="left").pack(anchor="w")
        rr=tk.Frame(inn,bg="white"); rr.pack(anchor="w",pady=(18,0))
        ttk.Button(rr,text="▶ Tiếp tục đọc",command=self.continue_reading).pack(side="left")
        ttk.Button(rr,text="★ Bài đã lưu",command=self.show_bookmarks).pack(side="left",padx=8)
        grid=tk.Frame(self.home.inner,bg=self.bg); grid.pack(fill="both",expand=True)
        for i,c in enumerate(CHAPTERS):
            p=list(PALETTES.values())[i%len(PALETTES)]
            card=tk.Frame(grid,bg="white",bd=1,relief="solid",highlightbackground=self.line); card.grid(row=i//2,column=i%2,sticky="nsew",padx=8,pady=8)
            grid.grid_columnconfigure(i%2,weight=1)
            h=tk.Frame(card,bg=p["soft"]); h.pack(fill="x")
            tk.Label(h,text=f"{i+1:02}",bg=p["soft"],fg=p["primary"],font=("Segoe UI",20,"bold")).pack(side="left",padx=14,pady=12)
            tb=tk.Frame(h,bg=p["soft"]); tb.pack(side="left",fill="both",expand=True,pady=12)
            tk.Label(tb,text=c["title"],bg=p["soft"],fg=self.text,font=("Segoe UI",13,"bold"),anchor="w").pack(fill="x")
            tk.Label(tb,text=c["subtitle"],bg=p["soft"],fg=self.muted,font=("Segoe UI",10),anchor="w",wraplength=430,justify="left").pack(fill="x")
            ft=tk.Frame(card,bg="white"); ft.pack(fill="x",padx=14,pady=12)
            tk.Label(ft,text=f'{len(c["lessons"])} bài',bg="white",fg=self.muted,font=("Segoe UI",10,"bold")).pack(side="left")
            ttk.Button(ft,text="Mở chương",command=lambda x=i:self.open_chapter(x)).pack(side="right")

    def show_home(self):
        self.reader.pack_forget(); self.home.pack(fill="both",expand=True); self.render_home(); self.update_progress()

    def show_lesson(self,lid,add=True):
        if lid not in self.byid:return
        self.current=lid; l=self.byid[lid]
        self.home.pack_forget(); self.reader.pack(fill="both",expand=True)
        self.render_lesson(l); self.reader.top()
        if add:
            if self.hpos<len(self.hist)-1:self.hist=self.hist[:self.hpos+1]
            if not self.hist or self.hist[-1]!=lid:self.hist.append(lid); self.hpos=len(self.hist)-1
        self.select(lid); self.save()

    def render_lesson(self,l):
        for w in self.reader.inner.winfo_children():w.destroy()
        p=PALETTES.get(l["style"],PALETTES["flow"])
        head=tk.Frame(self.reader.inner,bg="white",bd=1,relief="solid",highlightbackground=self.line); head.pack(fill="x",pady=(0,14))
        hi=tk.Frame(head,bg="white"); hi.pack(fill="x",padx=22,pady=18)
        left=tk.Frame(hi,bg="white"); left.pack(side="left",fill="both",expand=True)
        tk.Label(left,text=f'BÀI {l["id"]}',bg="white",fg=p["primary"],font=("Segoe UI",11,"bold")).pack(anchor="w")
        row=tk.Frame(left,bg="white"); row.pack(fill="x",pady=(8,0))
        tk.Frame(row,bg=p["primary"],width=9,height=54).pack(side="left",padx=(0,14))
        tk.Label(row,text=l["title"],bg="white",fg=self.text,font=("Segoe UI",31,"bold"),anchor="w",justify="left").pack(side="left",fill="x",expand=True)
        tk.Label(left,text=l["summary"],bg="white",fg=self.muted,font=("Segoe UI",14),anchor="w",justify="left",wraplength=850).pack(anchor="w",pady=(8,0))
        right=tk.Frame(hi,bg="white"); right.pack(side="right",padx=(16,0))
        self.bookmark_var.set("★ Đã lưu" if l["id"] in self.bookmarks else "☆ Lưu bài")
        ttk.Button(right,textvariable=self.bookmark_var,command=self.toggle_bookmark).pack(side="left",padx=4)
        ttk.Button(right,text="✓ Đã đọc",command=self.mark_read).pack(side="left",padx=4)

        self.diagram(l,p)

        r1=tk.Frame(self.reader.inner,bg=self.bg); r1.pack(fill="x",pady=(0,12))
        self.card(r1,"KHÁI NIỆM",l["concept"],p["soft"],p["primary"]).pack(side="left",fill="both",expand=True,padx=(0,7))
        self.card(r1,"CÁCH ÁP DỤNG",l["method"],p["accent2"],p["accent"]).pack(side="left",fill="both",expand=True,padx=(7,0))

        r2=tk.Frame(self.reader.inner,bg=self.bg); r2.pack(fill="x",pady=(0,12))
        self.card(r2,"TẠI SAO QUAN TRỌNG?",l["why"],"#fff7ed","#c2410c").pack(side="left",fill="both",expand=True,padx=(0,7))
        self.mistake_card(r2,l["mistakes"]).pack(side="left",fill="both",expand=True,padx=(7,0))

        r3=tk.Frame(self.reader.inner,bg=self.bg); r3.pack(fill="x",pady=(0,12))
        self.card(r3,"VÍ DỤ THỰC TẾ",l["example"],p["alt2"],p["alt"]).pack(side="left",fill="both",expand=True,padx=(0,7))
        self.check_card(r3,l["checklist"],p).pack(side="left",fill="both",expand=True,padx=(7,0))

        r4=tk.Frame(self.reader.inner,bg=self.bg); r4.pack(fill="x",pady=(0,12))
        self.card(r4,"BÀI TẬP ÁP DỤNG NGAY",l["practice"],"#f3e8ff","#7e22ce").pack(side="left",fill="both",expand=True,padx=(0,7))
        self.reflect_card(r4,l["reflect"]).pack(side="left",fill="both",expand=True,padx=(7,0))

        take=tk.Frame(self.reader.inner,bg="white",bd=1,relief="solid",highlightbackground=self.line); take.pack(fill="x")
        ti=tk.Frame(take,bg="white"); ti.pack(fill="x",padx=18,pady=16)
        tk.Label(ti,text="BÀI HỌC CHÍNH",bg="white",fg=p["primary"],font=("Segoe UI",16,"bold")).pack(anchor="w")
        names=" → ".join([x[0] for x in l["blocks"]])
        tk.Label(ti,text=f"Hãy nhớ chuỗi: {names}. Đừng chỉ đọc; hãy thử áp dụng bài tập của bài này vào một tình huống thật trong công việc.",bg="white",fg=self.text,font=("Segoe UI",self.fs+1),wraplength=930,justify="left").pack(anchor="w",pady=(8,0))
        ft=tk.Frame(self.reader.inner,bg=self.bg); ft.pack(fill="x",pady=(14,2))
        ttk.Button(ft,text="← Bài trước",command=self.prev).pack(side="left")
        tk.Label(ft,text=self.position(),bg=self.bg,fg=self.muted,font=("Segoe UI",10,"bold")).pack(side="left",padx=12)
        ttk.Button(ft,text="Bài sau →",command=self.next).pack(side="right")

    def diagram(self,l,p):
        out=tk.Frame(self.reader.inner,bg="white",bd=1,relief="solid",highlightbackground=self.line); out.pack(fill="x",pady=(0,14))
        f=tk.Frame(out,bg="white"); f.pack(fill="x",padx=14,pady=14)
        tk.Label(f,text="SƠ ĐỒ GHI NHỚ",bg="white",fg=p["primary"],font=("Segoe UI",17,"bold")).pack(anchor="w",pady=(0,10))
        style=l["style"]; blocks=l["blocks"]
        if style=="matrix":
            g=tk.Frame(f,bg="white"); g.pack(fill="x")
            for c in range(2):g.grid_columnconfigure(c,weight=1)
            for i,b in enumerate(blocks):
                self.block(g,b,p,i).grid(row=i//2,column=i%2,sticky="nsew",padx=6,pady=6)
        elif style=="ladder":
            for i,b in enumerate(blocks):
                rr=tk.Frame(f,bg="white"); rr.pack(fill="x",pady=4)
                tk.Label(rr,text=str(i+1).zfill(2),bg=p["primary"],fg="white",font=("Segoe UI",12,"bold"),width=4).pack(side="left",ipady=7,padx=(0,8))
                self.block(rr,b,p,i).pack(side="left",fill="x",expand=True)
        elif style=="cycle" and len(blocks)>=4:
            g=tk.Frame(f,bg="white"); g.pack(fill="x")
            for c in range(2):g.grid_columnconfigure(c,weight=1)
            order=[0,1,3,2]
            for k,i in enumerate(order):
                self.block(g,blocks[i],p,i).grid(row=k//2,column=k%2,sticky="nsew",padx=6,pady=6)
        else:
            rr=tk.Frame(f,bg="white"); rr.pack(fill="x")
            for i,b in enumerate(blocks):
                self.block(rr,b,p,i).pack(side="left",fill="both",expand=True,padx=5)
                if i<len(blocks)-1:tk.Label(rr,text="➜",bg="white",fg=p["primary"],font=("Segoe UI",26,"bold")).pack(side="left")

    def block(self,parent,b,p,i):
        schemes=[(p["soft"],p["primary"]),(p["alt2"],p["alt"]),(p["accent2"],p["accent"]),("#f1f5f9","#334155")]
        bg,fg=schemes[i%len(schemes)]
        z=tk.Frame(parent,bg=bg,bd=1,relief="solid",highlightbackground=self.line)
        tk.Label(z,text=b[0],bg=bg,fg=fg,font=("Segoe UI",15,"bold")).pack(anchor="w",padx=14,pady=(12,5))
        tk.Label(z,text=b[1],bg=bg,fg=self.text,font=("Segoe UI",self.fs+1),wraplength=260,justify="left").pack(anchor="w",padx=14,pady=(0,12))
        return z

    def card(self,parent,title,body,bg,fg):
        c=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=self.line)
        h=tk.Frame(c,bg=bg); h.pack(fill="x")
        tk.Label(h,text=title,bg=bg,fg=fg,font=("Segoe UI",16,"bold")).pack(anchor="w",padx=14,pady=10)
        tk.Label(c,text=body,bg="white",fg=self.text,font=("Segoe UI",self.fs+1),wraplength=505,justify="left").pack(anchor="w",padx=16,pady=16)
        return c

    def mistake_card(self,parent,items):
        c=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=self.line)
        h=tk.Frame(c,bg="#fee2e2"); h.pack(fill="x")
        tk.Label(h,text="SAI LẦM THƯỜNG GẶP",bg="#fee2e2",fg="#b91c1c",font=("Segoe UI",16,"bold")).pack(anchor="w",padx=14,pady=10)
        for x in items: tk.Label(c,text="✕  "+x,bg="white",fg=self.text,font=("Segoe UI",self.fs+1),wraplength=490,justify="left").pack(anchor="w",padx=16,pady=5)
        tk.Frame(c,bg="white",height=8).pack()
        return c

    def check_card(self,parent,items,p):
        c=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=self.line)
        h=tk.Frame(c,bg=p["accent2"]); h.pack(fill="x")
        tk.Label(h,text="CHECKLIST",bg=p["accent2"],fg=p["accent"],font=("Segoe UI",16,"bold")).pack(anchor="w",padx=14,pady=10)
        for x in items: tk.Label(c,text="☐  "+x,bg="white",fg=self.text,font=("Segoe UI",self.fs+1),wraplength=490,justify="left").pack(anchor="w",padx=16,pady=5)
        tk.Frame(c,bg="white",height=8).pack()
        return c

    def reflect_card(self,parent,items):
        c=tk.Frame(parent,bg="white",bd=1,relief="solid",highlightbackground=self.line)
        h=tk.Frame(c,bg="#e0f2fe"); h.pack(fill="x")
        tk.Label(h,text="CÂU HỎI TỰ PHẢN TƯ",bg="#e0f2fe",fg="#0369a1",font=("Segoe UI",16,"bold")).pack(anchor="w",padx=14,pady=10)
        for i,x in enumerate(items,1): tk.Label(c,text=f"{i}.  {x}",bg="white",fg=self.text,font=("Segoe UI",self.fs+1),wraplength=490,justify="left").pack(anchor="w",padx=16,pady=7)
        tk.Frame(c,bg="white",height=8).pack()
        return c

    def populate(self,items=None):
        self.block_tree=True; self.tree.delete(*self.tree.get_children())
        if items is None:
            for i,c in enumerate(CHAPTERS):
                p=self.tree.insert("","end",iid=f"c{i}",text=c["title"],open=i<3)
                for l in c["lessons"]:
                    tx=("✓ " if l["id"] in self.read else "")+l["id"]+"  "+l["title"]+("  ★" if l["id"] in self.bookmarks else "")
                    self.tree.insert(p,"end",iid="l"+l["id"],text=tx)
        else:
            for l in items:self.tree.insert("","end",iid="l"+l["id"],text=l["id"]+"  "+l["title"])
        self.block_tree=False; self.update_progress()

    def update_progress(self):
        done=len([x for x in self.read if x in self.byid]); total=len(self.lessons); pct=round(done*100/total) if total else 0
        self.prog["value"]=pct; self.progress_var.set(f"TIẾN ĐỘ ĐỌC  {done}/{total} bài • {pct}%")

    def pick(self,e=None):
        if self.block_tree:return
        s=self.tree.selection()
        if s and s[0].startswith("l"):
            lid=s[0][1:]
            if lid in self.byid and lid!=self.current:self.show_lesson(lid)

    def select(self,lid):
        iid="l"+lid
        if self.tree.exists(iid):
            self.block_tree=True; self.tree.selection_set(iid); self.tree.see(iid); self.block_tree=False

    def search(self):
        q=self.q.get().strip().lower()
        if not q:self.populate();return
        out=[]
        for l in self.lessons:
            blob=" ".join([l["id"],l["title"],l["summary"],l["concept"],l["method"],l["example"],l["why"],l["practice"]," ".join(l["mistakes"])," ".join(l["reflect"])]).lower()
            if q in blob:out.append(l)
        self.populate(out)
        if not out:messagebox.showinfo("Tìm kiếm","Không tìm thấy nội dung phù hợp.")

    def show_bookmarks(self):
        x=[l for l in self.lessons if l["id"] in self.bookmarks]; self.populate(x)
        if not x:messagebox.showinfo("Đã lưu","Chưa có bài nào được đánh dấu.")

    def open_chapter(self,i):
        if CHAPTERS[i]["lessons"]:self.show_lesson(CHAPTERS[i]["lessons"][0]["id"])
    def continue_reading(self):self.show_lesson(self.current if self.current in self.byid else "1.1")
    def toggle_bookmark(self):
        if self.current in self.bookmarks:self.bookmarks.remove(self.current)
        else:self.bookmarks.add(self.current)
        self.populate(); self.select(self.current); self.show_lesson(self.current,False)
    def mark_read(self):
        self.read.add(self.current); self.populate(); self.select(self.current); self.show_lesson(self.current,False)
    def font(self,d):
        self.fs=max(11,min(17,self.fs+d)); self.show_lesson(self.current,False); self.save()
    def position(self):
        i=next((n for n,l in enumerate(self.lessons) if l["id"]==self.current),0); return f"Bài {i+1}/{len(self.lessons)}"
    def prev(self):
        i=next((n for n,l in enumerate(self.lessons) if l["id"]==self.current),0)
        if i>0:self.show_lesson(self.lessons[i-1]["id"])
    def next(self):
        i=next((n for n,l in enumerate(self.lessons) if l["id"]==self.current),0)
        if i<len(self.lessons)-1:self.show_lesson(self.lessons[i+1]["id"])
    def back(self):
        if self.hpos>0:self.hpos-=1; self.show_lesson(self.hist[self.hpos],False)
        else:self.show_home()
    def forward(self):
        if self.hpos<len(self.hist)-1:self.hpos+=1; self.show_lesson(self.hist[self.hpos],False)
    def close(self):
        self.save()
        if messagebox.askyesno("Thoát ứng dụng","Bạn muốn thoát Tư Duy Đúng – Book App?"):self.destroy()

if __name__=="__main__":App().mainloop()
