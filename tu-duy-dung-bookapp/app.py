import json, os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from content import CHAPTERS

APP_NAME="Tư Duy Đúng – Book App"; VERSION="1.1.1"; APP_DIR="TuDuyDungBookApp"

def state_path():
    p=Path(os.getenv("APPDATA",Path.home()))/APP_DIR; p.mkdir(parents=True,exist_ok=True); return p/"state.json"

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title(f"{APP_NAME} V{VERSION}"); self.geometry("1260x800"); self.minsize(1020,650)
        st=self.load(); self.theme=st.get("theme","light"); self.fs=int(st.get("font_size",13)); self.bookmarks=set(st.get("bookmarks",[])); self.read=set(st.get("read_lessons",[])); self.current=st.get("last_lesson","1.1")
        self.lessons=[l for c in CHAPTERS for l in c["lessons"]]; self.byid={l["id"]:l for l in self.lessons}; self.hist=[]; self.hpos=-1; self.mode="home"
        self.q=tk.StringVar(); self.status=tk.StringVar(); self.bm=tk.StringVar(value="☆ Lưu bài")
        self.style=ttk.Style(self)
        try:self.style.theme_use("clam")
        except:pass
        self.build(); self.apply_theme(); self.populate(); self.show_home(); self.protocol("WM_DELETE_WINDOW",self.exit_confirm)
        self.bind("<Control-f>",lambda e:self.search_entry.focus_set()); self.bind("<Alt-Left>",lambda e:self.back()); self.bind("<Alt-Right>",lambda e:self.forward())
    def load(self):
        try:return json.loads(state_path().read_text(encoding="utf-8"))
        except:return {}
    def save(self):
        d={"theme":self.theme,"font_size":self.fs,"bookmarks":sorted(self.bookmarks),"read_lessons":sorted(self.read),"last_lesson":self.current}
        try:state_path().write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
        except:pass
    def build(self):
        self.top=tk.Frame(self,height=60); self.top.pack(fill="x"); self.top.pack_propagate(False)
        self.brand=tk.Label(self.top,text="TƯ DUY ĐÚNG",font=("Segoe UI",16,"bold")); self.brand.pack(side="left",padx=(18,8)); self.ver=tk.Label(self.top,text=f"BOOK APP • V{VERSION}",font=("Segoe UI",9,"bold")); self.ver.pack(side="left")
        for txt,cmd,w in [("⌂ Trang chủ",self.show_home,None),("◐",self.toggle_theme,4),("A+",lambda:self.font(1),4),("A−",lambda:self.font(-1),4),("→",self.forward,4),("←",self.back,4)]: ttk.Button(self.top,text=txt,command=cmd,width=w).pack(side="right",padx=3,pady=13)
        self.body=tk.Frame(self); self.body.pack(fill="both",expand=True); self.side=tk.Frame(self.body,width=330); self.side.pack(side="left",fill="y"); self.side.pack_propagate(False); self.main=tk.Frame(self.body); self.main.pack(side="left",fill="both",expand=True)
        self.cover=tk.Canvas(self.side,width=294,height=112,highlightthickness=0); self.cover.pack(padx=18,pady=(18,12))
        s=tk.Frame(self.side); s.pack(fill="x",padx=18,pady=(0,10)); self.search_entry=ttk.Entry(s,textvariable=self.q); self.search_entry.pack(side="left",fill="x",expand=True); self.search_entry.bind("<Return>",lambda e:self.search()); ttk.Button(s,text="Tìm",width=6,command=self.search).pack(side="left",padx=(6,0))
        n=tk.Frame(self.side); n.pack(fill="x",padx=18,pady=(0,10)); ttk.Button(n,text="Mục lục",command=self.show_all).pack(side="left",fill="x",expand=True); ttk.Button(n,text="★ Đã lưu",command=self.show_bookmarks).pack(side="left",fill="x",expand=True,padx=(6,0))
        self.progtext=tk.Label(self.side,anchor="w",font=("Segoe UI",9,"bold")); self.progtext.pack(fill="x",padx=18); self.prog=ttk.Progressbar(self.side,maximum=100); self.prog.pack(fill="x",padx=18,pady=(5,12))
        tw=tk.Frame(self.side); tw.pack(fill="both",expand=True,padx=(12,8),pady=(0,12)); self.tree=ttk.Treeview(tw,show="tree",selectmode="browse"); sc=ttk.Scrollbar(tw,orient="vertical",command=self.tree.yview); self.tree.configure(yscrollcommand=sc.set); self.tree.pack(side="left",fill="both",expand=True); sc.pack(side="right",fill="y"); self.tree.bind("<<TreeviewSelect>>",self.pick)
        self.home=tk.Frame(self.main); self.reader=tk.Frame(self.main); self.build_home(); self.build_reader()
    def build_home(self):
        h=tk.Frame(self.home); h.pack(fill="x",padx=34,pady=(28,12)); self.kicker=tk.Label(h,text="SÁCH TƯƠNG TÁC VỀ TƯ DUY & QUẢN LÝ",font=("Segoe UI",10,"bold"),anchor="w"); self.kicker.pack(fill="x"); self.htitle=tk.Label(h,text="Tư duy đúng. Phương pháp đúng.\nQuản lý đúng.",font=("Segoe UI",28,"bold"),justify="left",anchor="w"); self.htitle.pack(fill="x",pady=(7,7)); self.hdesc=tk.Label(h,text="Đọc ngắn • Hiểu nhanh • Áp dụng ngay vào công việc",font=("Segoe UI",12),anchor="w"); self.hdesc.pack(fill="x")
        a=tk.Frame(h); a.pack(fill="x",pady=(16,0)); ttk.Button(a,text="▶ Tiếp tục đọc",command=self.continue_reading).pack(side="left"); ttk.Button(a,text="Mở mục lục",command=self.show_all).pack(side="left",padx=8)
        self.cards_canvas=tk.Canvas(self.home,highlightthickness=0); sb=ttk.Scrollbar(self.home,orient="vertical",command=self.cards_canvas.yview); self.cards=tk.Frame(self.cards_canvas); self.cards.bind("<Configure>",lambda e:self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))); self.cards_canvas.create_window((0,0),window=self.cards,anchor="nw",tags="cards"); self.cards_canvas.configure(yscrollcommand=sb.set); self.cards_canvas.bind("<Configure>",lambda e:self.cards_canvas.itemconfigure("cards",width=e.width)); self.cards_canvas.pack(side="left",fill="both",expand=True,padx=(26,0),pady=(0,20)); sb.pack(side="right",fill="y",pady=(0,20),padx=(0,18)); self.render_cards()
    def render_cards(self):
        for w in self.cards.winfo_children():w.destroy()
        for i,c in enumerate(CHAPTERS):
            card=tk.Frame(self.cards); card.pack(fill="x",padx=8,pady=6); tk.Label(card,text=f"{i+1:02}",font=("Segoe UI",16,"bold"),width=4).pack(side="left",padx=(10,8),pady=14); t=tk.Frame(card); t.pack(side="left",fill="both",expand=True,pady=10); tk.Label(t,text=c["title"],font=("Segoe UI",12,"bold"),anchor="w").pack(fill="x"); tk.Label(t,text=c["subtitle"],font=("Segoe UI",9),anchor="w").pack(fill="x",pady=(3,0)); cnt=len(c["lessons"]); ttk.Button(card,text=f"Mở {cnt} bài" if cnt else "Đang biên soạn",state="normal" if cnt else "disabled",command=lambda x=i:self.open_chapter(x)).pack(side="right",padx=14,pady=18)
    def build_reader(self):
        h=tk.Frame(self.reader); h.pack(fill="x",padx=34,pady=(26,8)); self.lid=tk.Label(h,font=("Segoe UI",10,"bold"),anchor="w"); self.lid.pack(fill="x"); self.ltitle=tk.Label(h,font=("Segoe UI",25,"bold"),anchor="w",justify="left"); self.ltitle.pack(fill="x",pady=(4,6)); self.lsum=tk.Label(h,font=("Segoe UI",11),anchor="w",justify="left",wraplength=780); self.lsum.pack(fill="x")
        tools=tk.Frame(self.reader); tools.pack(fill="x",padx=34,pady=(2,8)); ttk.Button(tools,textvariable=self.bm,command=self.toggle_bookmark).pack(side="left"); ttk.Button(tools,text="✓ Đã đọc",command=self.mark_read).pack(side="left",padx=6); self.rstatus=tk.Label(tools,textvariable=self.status,font=("Segoe UI",9,"bold")); self.rstatus.pack(side="right")
        tw=tk.Frame(self.reader); tw.pack(fill="both",expand=True,padx=34,pady=(0,10)); self.text=tk.Text(tw,wrap="word",relief="flat",bd=0,padx=24,pady=20,cursor="arrow"); sc=ttk.Scrollbar(tw,orient="vertical",command=self.text.yview); self.text.configure(yscrollcommand=sc.set); self.text.pack(side="left",fill="both",expand=True); sc.pack(side="right",fill="y"); self.text.configure(state="disabled")
        f=tk.Frame(self.reader,height=52); f.pack(fill="x",padx=34,pady=(0,16)); f.pack_propagate(False); ttk.Button(f,text="← Bài trước",command=self.prev).pack(side="left",pady=9); self.finfo=tk.Label(f,font=("Segoe UI",9)); self.finfo.pack(pady=15); ttk.Button(f,text="Bài sau →",command=self.next).pack(side="right",pady=9)
    def apply_theme(self):
        c={"bg":"#101827","side":"#121d2f","panel":"#18253a","card":"#1d2b42","text":"#f4f7fb","muted":"#9fb0c6","accent":"#78a9ff","navy":"#19345d","red":"#9f2f39"} if self.theme=="dark" else {"bg":"#eef3f9","side":"#ffffff","panel":"#ffffff","card":"#f8fafc","text":"#172033","muted":"#667085","accent":"#215ea7","navy":"#173d73","red":"#c73743"}; self.c=c
        self.configure(bg=c["bg"]); self.top.configure(bg=c["panel"]); self.body.configure(bg=c["bg"]); self.side.configure(bg=c["side"]); self.main.configure(bg=c["bg"]); self.home.configure(bg=c["bg"]); self.reader.configure(bg=c["bg"]); self.walk(self); self.style.configure("Treeview",background=c["side"],fieldbackground=c["side"],foreground=c["text"],rowheight=28,borderwidth=0); self.style.map("Treeview",background=[("selected",c["accent"])],foreground=[("selected","white")]); self.style.configure("TButton",padding=(9,6)); self.style.configure("TEntry",padding=5); self.text.configure(bg=c["panel"],fg=c["text"],selectbackground=c["accent"],font=("Segoe UI",self.fs),spacing3=7); self.tags(); self.draw_cover()
        for card in self.cards.winfo_children():
            card.configure(bg=c["card"])
            for w in card.winfo_children():
                if isinstance(w,tk.Frame):w.configure(bg=c["card"])
    def walk(self,w):
        for x in w.winfo_children():
            try:
                if isinstance(x,tk.Frame): x.configure(bg=x.master.cget("bg"))
                elif isinstance(x,tk.Label): x.configure(bg=x.master.cget("bg"),fg=self.c["text"])
                elif isinstance(x,tk.Canvas) and x is not self.cover: x.configure(bg=x.master.cget("bg"))
            except:pass
            self.walk(x)
    def tags(self):
        self.text.tag_configure("body",font=("Segoe UI",self.fs),foreground=self.c["text"],spacing3=7); self.text.tag_configure("head",font=("Segoe UI",self.fs+2,"bold"),foreground=self.c["accent"],spacing1=12,spacing3=6); self.text.tag_configure("lead",font=("Segoe UI",self.fs+1,"bold"),foreground=self.c["text"],spacing3=6)
    def draw_cover(self):
        c=self.c; self.cover.delete("all"); self.cover.configure(bg=c["side"]); self.cover.create_rectangle(0,0,294,112,fill=c["navy"],outline=""); self.cover.create_rectangle(0,87,294,112,fill=c["red"],outline=""); self.cover.create_text(18,22,text="TƯ DUY",anchor="w",fill="#f7d928",font=("Segoe UI",13,"bold")); self.cover.create_text(18,49,text="PHƯƠNG PHÁP QUẢN LÝ",anchor="w",fill="white",font=("Segoe UI",15,"bold")); self.cover.create_text(18,76,text="ĐÚNG",anchor="w",fill="white",font=("Segoe UI",22,"bold")); self.cover.create_text(280,100,text=f"V{VERSION}",anchor="e",fill="white",font=("Segoe UI",8,"bold"))
    def populate(self,items=None):
        self.tree.delete(*self.tree.get_children())
        if items is not None:
            for l in items:self.tree.insert("","end",iid="l"+l["id"],text=f'{l["id"]}  {l["title"]}')
        else:
            for i,c in enumerate(CHAPTERS):
                p=self.tree.insert("","end",iid=f"c{i}",text=c["title"],open=i<3)
                for l in c["lessons"]:self.tree.insert(p,"end",iid="l"+l["id"],text=("✓ " if l["id"] in self.read else "")+f'{l["id"]}  {l["title"]}'+(" ★" if l["id"] in self.bookmarks else ""))
                if not c["lessons"]:self.tree.insert(p,"end",iid=f"e{i}",text="   Đang biên soạn")
        self.progress()
    def progress(self):
        total=len(self.lessons); done=len(self.read & set(self.byid)); pct=round(done*100/total) if total else 0; self.prog["value"]=pct; self.progtext.configure(text=f"TIẾN ĐỘ ĐỌC  {done}/{total} bài • {pct}%")
    def show_home(self):self.mode="home"; self.reader.pack_forget(); self.home.pack(fill="both",expand=True); self.progress()
    def show_reader(self):self.mode="reader"; self.home.pack_forget(); self.reader.pack(fill="both",expand=True)
    def continue_reading(self):self.show_lesson(self.current if self.current in self.byid else "1.1")
    def show_all(self):self.populate(); self.show_home()
    def show_bookmarks(self):
        x=[l for l in self.lessons if l["id"] in self.bookmarks]; self.populate(x)
        if not x:messagebox.showinfo("Đã lưu","Chưa có bài nào được đánh dấu.")
    def search(self):
        q=self.q.get().strip().lower()
        if not q:self.show_all();return
        x=[l for l in self.lessons if q in (l["id"]+l["title"]+l["summary"]+l["content"]).lower()]; self.populate(x)
        if not x:messagebox.showinfo("Tìm kiếm","Không tìm thấy nội dung phù hợp.")
    def open_chapter(self,i):
        if CHAPTERS[i]["lessons"]:self.show_lesson(CHAPTERS[i]["lessons"][0]["id"])
    def pick(self,_=None):
        s=self.tree.selection()
        if s and s[0].startswith("l") and s[0][1:] in self.byid:self.show_lesson(s[0][1:])
    def show_lesson(self,lid,add=True):
        if lid not in self.byid:return
        self.show_reader(); self.current=lid; l=self.byid[lid]; self.lid.configure(text=f"BÀI {lid}"); self.ltitle.configure(text=l["title"]); self.lsum.configure(text=l["summary"]); self.bm.set("★ Đã lưu" if lid in self.bookmarks else "☆ Lưu bài"); self.status.set("Đã đọc" if lid in self.read else "Chưa đánh dấu đã đọc")
        self.text.configure(state="normal"); self.text.delete("1.0","end")
        for i,line in enumerate(l["content"].splitlines()):
            z=line.strip(); tag="lead" if i==0 and z else ("head" if z and z.isupper() else "body"); self.text.insert("end",line+"\n",tag)
        self.text.configure(state="disabled"); self.text.yview_moveto(0); self.finfo.configure(text=f"Bài {self.lessons.index(l)+1}/{len(self.lessons)}")
        if add:
            if self.hpos<len(self.hist)-1:self.hist=self.hist[:self.hpos+1]
            if not self.hist or self.hist[-1]!=lid:self.hist.append(lid); self.hpos=len(self.hist)-1
        self.save(); self.populate(); self.select(lid)
    def select(self,lid):
        i="l"+lid
        if self.tree.exists(i):self.tree.selection_set(i); self.tree.see(i)
    def back(self):
        if self.mode=="home":self.exit_confirm();return
        if self.hpos>0:self.hpos-=1; self.show_lesson(self.hist[self.hpos],False)
        else:self.show_home()
    def forward(self):
        if self.hpos<len(self.hist)-1:self.hpos+=1; self.show_lesson(self.hist[self.hpos],False)
    def prev(self):
        i=next((n for n,l in enumerate(self.lessons) if l["id"]==self.current),0)
        if i>0:self.show_lesson(self.lessons[i-1]["id"])
    def next(self):
        i=next((n for n,l in enumerate(self.lessons) if l["id"]==self.current),0)
        if i<len(self.lessons)-1:self.show_lesson(self.lessons[i+1]["id"])
    def toggle_bookmark(self):
        if self.current in self.bookmarks:self.bookmarks.remove(self.current)
        else:self.bookmarks.add(self.current)
        self.bm.set("★ Đã lưu" if self.current in self.bookmarks else "☆ Lưu bài"); self.save(); self.populate(); self.select(self.current)
    def mark_read(self):self.read.add(self.current); self.status.set("Đã đọc"); self.save(); self.populate(); self.select(self.current)
    def font(self,d):self.fs=max(10,min(20,self.fs+d)); self.tags(); self.save()
    def toggle_theme(self):self.theme="dark" if self.theme=="light" else "light"; self.apply_theme(); self.save()
    def exit_confirm(self):
        self.save()
        if messagebox.askyesno("Thoát ứng dụng","Bạn muốn thoát Tư Duy Đúng – Book App?"):self.destroy()

if __name__=="__main__":App().mainloop()
