import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import cv2
import os
import numpy as np
import json
import csv
from datetime import datetime

# ══════════════════════════════════════════════
#  SETUP
# ══════════════════════════════════════════════
for folder in ["Student_Images", "Attendance_Logs", "Reports"]:
    os.makedirs(folder, exist_ok=True)

DB_FILE           = "student_database.json"
TOTAL_COURSE_DAYS = 22

# ══════════════════════════════════════════════
#  NEON DARK THEME
# ══════════════════════════════════════════════
BG          = "#050810"
BG2         = "#0A0F1E"
BG3         = "#0F1629"
CARD        = "#111827"
CARD2       = "#161D30"
BORDER      = "#1E2A45"

NEON_BLUE   = "#00D4FF"
NEON_GREEN  = "#00FF88"
NEON_PINK   = "#FF006E"
NEON_PURPLE = "#BF5FFF"
NEON_YELLOW = "#FFE600"
NEON_ORANGE = "#FF6B00"

TXT         = "#E2E8F0"
TXT2        = "#64748B"
TXT3        = "#94A3B8"

FT          = "Courier"       # monospace — techy look
FT2         = "Helvetica"

FTITLE  = (FT,  20, "bold")
FHEAD   = (FT,  12, "bold")
FBODY   = (FT,  10)
FSMALL  = (FT,   9)
FSTAT   = (FT,  26, "bold")
FMONO   = (FT,  11, "bold")

# ══════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DB_FILE, "w") as f:
        json.dump(student_db, f, indent=2)

student_db = load_data()

recognizer   = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def train_engine():
    faces, ids = [], []
    for roll in student_db:
        p = f"Student_Images/{roll}.jpg"
        if os.path.exists(p):
            img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces.append(img)
                ids.append(int(roll))
    if faces:
        recognizer.train(faces, np.array(ids))
        return True
    return False

if student_db:
    train_engine()

# ══════════════════════════════════════════════
#  HELPER: ensure student has all fields
# ══════════════════════════════════════════════
def ensure_fields(d):
    d.setdefault("present",         0)
    d.setdefault("attendance_log",  [])
    d.setdefault("subjects",        {})   # {subj: [marks list]}
    d.setdefault("remarks",         [])   # [{date, text, teacher}]
    d.setdefault("cgpa",            0.0)
    return d

for r in student_db:
    ensure_fields(student_db[r])

# ══════════════════════════════════════════════
#  ROOT WINDOW
# ══════════════════════════════════════════════
root = tk.Tk()
root.title("SmartAttend PRO  ◈  Academic Management System")
root.geometry("1200x750")
root.resizable(False, False)
root.configure(bg=BG)

# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════
sidebar = tk.Frame(root, bg=BG2, width=230)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

# Sidebar glow border
tk.Frame(root, bg=NEON_BLUE, width=1).place(x=230, y=0, relheight=1)

# Logo area
logo_frame = tk.Frame(sidebar, bg=BG2)
logo_frame.pack(fill="x", pady=(28, 0))
tk.Label(logo_frame, text="◈", font=(FT, 38, "bold"),
         bg=BG2, fg=NEON_BLUE).pack()
tk.Label(logo_frame, text="SmartAttend", font=(FT, 13, "bold"),
         bg=BG2, fg=TXT).pack()
# Neon tag
tag = tk.Label(logo_frame, text=" PRO ", font=(FT, 8, "bold"),
               bg=NEON_PURPLE, fg="white", padx=6, pady=1)
tag.pack(pady=(2, 18))
tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=18, pady=4)

# ══════════════════════════════════════════════
#  MAIN AREA
# ══════════════════════════════════════════════
main_area = tk.Frame(root, bg=BG)
main_area.pack(side="left", fill="both", expand=True)

# Top bar
topbar = tk.Frame(main_area, bg=BG2, height=56)
topbar.pack(fill="x")
topbar.pack_propagate(False)
tk.Frame(topbar, bg=NEON_BLUE, height=2).pack(fill="x", side="bottom")

title_lbl = tk.Label(topbar, text="DASHBOARD", font=FHEAD,
                     bg=BG2, fg=NEON_BLUE)
title_lbl.pack(side="left", padx=22, pady=16)

clock_lbl = tk.Label(topbar, text="", font=FSMALL, bg=BG2, fg=NEON_GREEN)
clock_lbl.pack(side="right", padx=22)

def update_clock():
    clock_lbl.config(text=datetime.now().strftime("◈  %A  %d %b %Y  ●  %I:%M:%S %p"))
    root.after(1000, update_clock)
update_clock()

container = tk.Frame(main_area, bg=BG)
container.pack(fill="both", expand=True)

# All pages
pages = {}
page_names = ["dashboard", "register", "scan", "records", "marks", "remarks"]
for name in page_names:
    f = tk.Frame(container, bg=BG)
    f.place(x=0, y=0, relwidth=1, relheight=1)
    pages[name] = f

# ══════════════════════════════════════════════
#  CARD helper
# ══════════════════════════════════════════════
def neon_card(parent, px=14, py=12, color=NEON_BLUE, expand=False, fill="both"):
    wrap = tk.Frame(parent, bg=color, padx=1, pady=1)
    inner = tk.Frame(wrap, bg=CARD, padx=px, pady=py)
    inner.pack(fill=fill, expand=expand)
    return wrap, inner

# ══════════════════════════════════════════════
#  UTILITY FUNCTIONS  (defined early)
# ══════════════════════════════════════════════
rec_tree = None

def att_pct(d):
    return (d["present"] / TOTAL_COURSE_DAYS) * 100

def calc_cgpa(d):
    """Average of average marks per subject, scaled to 4.0"""
    subjs = d.get("subjects", {})
    if not subjs:
        return 0.0
    avgs = []
    for marks in subjs.values():
        if marks:
            avgs.append(sum(marks) / len(marks))
    if not avgs:
        return 0.0
    overall = sum(avgs) / len(avgs)
    # scale 0-100 → 0-4.0
    return round((overall / 100) * 4.0, 2)

def grade_from_cgpa(cgpa):
    if cgpa >= 3.7: return "A+", NEON_GREEN
    if cgpa >= 3.3: return "A",  NEON_GREEN
    if cgpa >= 3.0: return "A-", NEON_GREEN
    if cgpa >= 2.7: return "B+", NEON_BLUE
    if cgpa >= 2.3: return "B",  NEON_BLUE
    if cgpa >= 2.0: return "B-", NEON_BLUE
    if cgpa >= 1.5: return "C",  NEON_YELLOW
    if cgpa >= 1.0: return "D",  NEON_ORANGE
    return "F", NEON_PINK

def update_records_table(query=""):
    if rec_tree is None:
        return
    for item in rec_tree.get_children():
        rec_tree.delete(item)
    for i, (roll, d) in enumerate(student_db.items(), 1):
        ensure_fields(d)
        pct   = att_pct(d)
        cgpa  = calc_cgpa(d)
        grade, _ = grade_from_cgpa(cgpa)
        att_s = "✅ Good" if pct >= 75 else ("⚡ Avg" if pct >= 50 else "❌ Low")
        row   = (i, d["name"], roll, d["dept"], d["phone"],
                 d["present"], f"{int(pct)}%", att_s,
                 f"{cgpa:.2f}", grade)
        if query:
            if query not in f"{d['name']} {roll} {d['dept']}".lower():
                continue
        rec_tree.insert("", tk.END, values=row)

def export_csv():
    if not student_db:
        messagebox.showwarning("Empty", "Koi data nahi hai export karne ke liye!")
        return
    fname = f"Reports/report_{datetime.now().strftime('%d%m%Y_%H%M%S')}.csv"
    with open(fname, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["#","Name","Roll","Dept","Phone",
                    "Days","Att%","CGPA","Grade","Status"])
        for i, (roll, d) in enumerate(student_db.items(), 1):
            ensure_fields(d)
            pct  = att_pct(d)
            cgpa = calc_cgpa(d)
            grade, _ = grade_from_cgpa(cgpa)
            att_s = "Good" if pct >= 75 else ("Average" if pct >= 50 else "Low")
            w.writerow([i, d["name"], roll, d["dept"], d["phone"],
                        d["present"], f"{int(pct)}%", f"{cgpa:.2f}", grade, att_s])
    messagebox.showinfo("Exported ✅", f"Report saved:\n{fname}")

def delete_student_action():
    if rec_tree is None: return
    sel = rec_tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Pehle ek student select karein table mein")
        return
    vals = rec_tree.item(sel[0])["values"]
    roll = str(vals[2]); name = vals[1]
    if messagebox.askyesno("Delete?", f"'{name}' (Roll:{roll}) delete karein?\nYe wapis nahi aayega!"):
        student_db.pop(roll, None)
        img = f"Student_Images/{roll}.jpg"
        if os.path.exists(img): os.remove(img)
        save_data()
        if student_db: train_engine()
        update_records_table()
        messagebox.showinfo("Done", f"{name} deleted!")

def show_page(name):
    title_lbl.config(text=name.upper())
    if name == "records":
        update_records_table()
    pages[name].tkraise()

# ══════════════════════════════════════════════
#  PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════
def build_dashboard():
    pg = pages["dashboard"]

    tk.Label(pg, text="◈  SYSTEM DASHBOARD", font=FTITLE,
             bg=BG, fg=NEON_BLUE).pack(anchor="w", padx=28, pady=(22, 4))
    tk.Label(pg, text="Real-time academic overview",
             font=FSMALL, bg=BG, fg=TXT2).pack(anchor="w", padx=28)

    # ── Stat cards ──
    sr = tk.Frame(pg, bg=BG)
    sr.pack(fill="x", padx=24, pady=14)

    stat_vars = {}
    defs = [
        ("👥 Total",    "total",   NEON_BLUE),
        ("✅ Today",    "today",   NEON_GREEN),
        ("📊 Avg Att",  "avg_att", NEON_PURPLE),
        ("🎓 Avg CGPA", "avg_cgp", NEON_YELLOW),
        ("❌ Low Att",  "low",     NEON_PINK),
    ]
    for title, key, col in defs:
        w, inn = neon_card(sr, px=12, py=10, color=col)
        w.pack(side="left", expand=True, fill="both", padx=4)
        tk.Label(inn, text=title, font=FSMALL, bg=CARD, fg=TXT2).pack(anchor="w")
        v = tk.StringVar(value="—")
        stat_vars[key] = v
        tk.Label(inn, textvariable=v, font=FSTAT, bg=CARD, fg=col).pack(anchor="w")

    # ── Middle row ──
    mid = tk.Frame(pg, bg=BG)
    mid.pack(fill="both", expand=True, padx=24, pady=4)

    # Today log
    lw, li = neon_card(mid, color=NEON_BLUE)
    lw.pack(side="left", fill="both", expand=True, padx=(0, 6))
    tk.Label(li, text="⚡ TODAY'S ATTENDANCE LOG", font=FHEAD,
             bg=CARD, fg=NEON_BLUE).pack(anchor="w", pady=(0, 8))
    log_cols = ("time", "name", "roll", "pct")
    log_tree = ttk.Treeview(li, columns=log_cols, show="headings", height=7)
    for c, h, w in zip(log_cols, ("Time","Name","Roll","Att%"), (90,160,80,60)):
        log_tree.heading(c, text=h)
        log_tree.column(c, width=w, anchor="center")
    log_tree.pack(fill="both", expand=True)

    # Quick actions
    rw, ri = neon_card(mid, color=NEON_PURPLE, px=16)
    rw.pack(side="left", fill="y", padx=(6, 0))
    tk.Label(ri, text="◈ QUICK ACTIONS", font=FHEAD,
             bg=CARD, fg=NEON_PURPLE).pack(anchor="w", pady=(0, 10))

    actions = [
        ("📸  Register",   NEON_BLUE,   "register"),
        ("🎥  Scan Face",  NEON_GREEN,  "scan"),
        ("📋  Records",    NEON_PURPLE, "records"),
        ("📝  Add Marks",  NEON_YELLOW, "marks"),
        ("💬  Remarks",    NEON_PINK,   "remarks"),
        ("📤  Export CSV", NEON_ORANGE, None),
    ]
    for txt, col, pg_name in actions:
        cmd = (lambda p=pg_name: show_page(p)) if pg_name else export_csv
        b = tk.Button(ri, text=txt, font=FBODY, bg=BG3, fg=col,
                      bd=0, padx=12, pady=9, width=18, cursor="hand2",
                      activebackground=CARD2, activeforeground=col,
                      relief="flat", command=cmd)
        b.pack(fill="x", pady=3)
        # neon left border effect
        tk.Frame(ri, bg=col, width=3, height=28).place(in_=b, x=0, y=0, relheight=1)

    # Top 3 leaderboard
    bw, bi = neon_card(mid, color=NEON_YELLOW, px=14)
    bw.pack(side="left", fill="y", padx=(6, 0))
    tk.Label(bi, text="🏆 CGPA LEADERS", font=FHEAD,
             bg=CARD, fg=NEON_YELLOW).pack(anchor="w", pady=(0, 8))
    lead_var = tk.StringVar(value="No data yet")
    tk.Label(bi, textvariable=lead_var, font=FBODY, bg=CARD,
             fg=TXT, justify="left", width=22).pack(anchor="w")

    def refresh():
        today = datetime.now().strftime("%d-%m-%Y")
        total = len(student_db)
        present_today = sum(
            1 for d in student_db.values()
            if any(e.startswith(today) for e in d.get("attendance_log", [])))
        avg_att = avg_cgp = low = 0
        if total:
            atts = [att_pct(d) for d in student_db.values()]
            cgps = [calc_cgpa(d) for d in student_db.values()]
            avg_att = int(sum(atts) / total)
            avg_cgp = round(sum(cgps) / total, 2)
            low = sum(1 for a in atts if a < 50)
        stat_vars["total"].set(str(total))
        stat_vars["today"].set(str(present_today))
        stat_vars["avg_att"].set(f"{avg_att}%")
        stat_vars["avg_cgp"].set(str(avg_cgp))
        stat_vars["low"].set(str(low))

        for i in log_tree.get_children(): log_tree.delete(i)
        entries = []
        for roll, d in student_db.items():
            for e in d.get("attendance_log", []):
                if e.startswith(today):
                    parts = e.split(" ")
                    t = parts[1] if len(parts) > 1 else "--"
                    pct = f"{int(att_pct(d))}%"
                    entries.append((t, d["name"], roll, pct))
        for e in sorted(entries, reverse=True)[:8]:
            log_tree.insert("", "end", values=e)

        # leaderboard
        ranked = sorted(student_db.items(),
                        key=lambda x: calc_cgpa(x[1]), reverse=True)[:5]
        if ranked:
            txt = ""
            medals = ["🥇","🥈","🥉","④","⑤"]
            for idx, (roll, d) in enumerate(ranked):
                cgpa = calc_cgpa(d)
                g, _ = grade_from_cgpa(cgpa)
                txt += f"{medals[idx]} {d['name'][:14]:<14}\n"
                txt += f"   CGPA: {cgpa:.2f}  [{g}]\n\n"
            lead_var.set(txt.strip())
        else:
            lead_var.set("No students yet")

        root.after(6000, refresh)

    refresh()

build_dashboard()

# ══════════════════════════════════════════════
#  PAGE 2 — REGISTER
# ══════════════════════════════════════════════
def build_register():
    pg = pages["register"]

    tk.Label(pg, text="◈  REGISTER STUDENT", font=FTITLE,
             bg=BG, fg=NEON_GREEN).pack(anchor="w", padx=28, pady=(22, 4))
    tk.Label(pg, text="Face capture + details entry",
             font=FSMALL, bg=BG, fg=TXT2).pack(anchor="w", padx=28)

    cw, ci = neon_card(pg, px=28, py=18, color=NEON_GREEN)
    cw.pack(padx=24, pady=14, fill="x")

    labels = ["Full Name", "Roll Number", "Department", "Semester", "Phone No", "Email"]
    placeholders = ["Ahmed Ali", "12345", "Computer Science", "e.g. 5th", "0300-XXXXXXX", "student@uni.edu"]
    entries_list = []

    cols_frame = tk.Frame(ci, bg=CARD)
    cols_frame.pack(fill="x")
    left_f  = tk.Frame(cols_frame, bg=CARD); left_f.pack(side="left",  fill="x", expand=True, padx=(0,16))
    right_f = tk.Frame(cols_frame, bg=CARD); right_f.pack(side="left", fill="x", expand=True)

    for idx, (lbl, ph) in enumerate(zip(labels, placeholders)):
        parent = left_f if idx < 3 else right_f
        tk.Label(parent, text=lbl.upper(), font=FSMALL, bg=CARD,
                 fg=NEON_GREEN).pack(anchor="w", pady=(8, 1))
        e = tk.Entry(parent, font=FBODY, bg=BG3, fg=TXT,
                     insertbackground=NEON_GREEN, bd=0, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=NEON_GREEN, width=28)
        e.insert(0, ph)
        e.bind("<FocusIn>",  lambda ev, _ph=ph, _e=e:
               _e.delete(0, "end") if _e.get() == _ph else None)
        e.bind("<FocusOut>", lambda ev, _ph=ph, _e=e:
               _e.insert(0, _ph) if _e.get() == "" else None)
        e.pack(fill="x", ipady=8, pady=(0, 2))
        entries_list.append((lbl, ph, e))

    status_v = tk.StringVar(value="")
    tk.Label(ci, textvariable=status_v, font=FBODY, bg=CARD, fg=NEON_GREEN).pack(pady=6)

    phs = [x[1] for x in entries_list]

    def clear():
        for _, ph, e in entries_list:
            e.delete(0, "end"); e.insert(0, ph)
        status_v.set("")

    def do_register():
        vals = {lbl: e.get().strip() for lbl, ph, e in entries_list}
        if any(v == "" or v == ph for (lbl, ph, e), v in zip(entries_list, vals.values())):
            messagebox.showerror("Error", "Saare fields theek se bharen!")
            return
        roll = vals["Roll Number"]
        if roll in student_db:
            if not messagebox.askyesno("Duplicate", f"Roll {roll} already hai. Overwrite karein?"): return

        status_v.set("📷 Camera open ho rahi hai... 'S' dabayein capture karne ke liye")
        root.update()

        cap = cv2.VideoCapture(0)
        captured = False
        while True:
            ret, frame = cap.read()
            if not ret: break
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x,y),(x+w,y+h), (0,255,136), 2)
                cv2.putText(frame, vals["Full Name"], (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,136), 2)
            cv2.putText(frame, "S=Save  Q=Quit", (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1)
            cv2.imshow("Register — SmartAttend PRO", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s') and len(faces):
                fc = gray[y:y+h, x:x+w]
                cv2.imwrite(f"Student_Images/{roll}.jpg", cv2.resize(fc,(200,200)))
                student_db[roll] = ensure_fields({
                    "name":     vals["Full Name"],
                    "dept":     vals["Department"],
                    "phone":    vals["Phone No"],
                    "email":    vals["Email"],
                    "semester": vals["Semester"],
                    "reg_date": datetime.now().strftime("%d-%m-%Y"),
                })
                save_data(); captured = True; break
            elif key == ord('q'): break

        cap.release(); cv2.destroyAllWindows()
        if captured:
            train_engine()
            status_v.set(f"✅ {vals['Full Name']} registered successfully!")
            messagebox.showinfo("Done ✅",
                f"◈ {vals['Full Name']} registered!\n"
                f"Roll: {roll}  |  Dept: {vals['Department']}")
            clear()
        else:
            status_v.set("❌ Cancelled.")

    btn_row = tk.Frame(ci, bg=CARD)
    btn_row.pack(pady=8)
    tk.Button(btn_row, text="📸  CAPTURE & REGISTER", font=FHEAD,
              bg=NEON_GREEN, fg=BG, bd=0, padx=22, pady=11,
              cursor="hand2", command=do_register).pack(side="left", padx=8)
    tk.Button(btn_row, text="🗑  CLEAR", font=FBODY,
              bg=BG3, fg=TXT2, bd=0, padx=18, pady=11,
              cursor="hand2", command=clear).pack(side="left", padx=8)

build_register()

# ══════════════════════════════════════════════
#  PAGE 3 — SCAN
# ══════════════════════════════════════════════
def build_scan():
    pg = pages["scan"]

    tk.Label(pg, text="◈  SCAN ATTENDANCE", font=FTITLE,
             bg=BG, fg=NEON_BLUE).pack(anchor="w", padx=28, pady=(22, 4))
    tk.Label(pg, text="Face recognition — automatic attendance marking",
             font=FSMALL, bg=BG, fg=TXT2).pack(anchor="w", padx=28)

    cw, ci = neon_card(pg, px=32, py=24, color=NEON_BLUE)
    cw.pack(padx=24, pady=20, fill="x")

    tk.Label(ci, text="🎥", font=(FT, 52), bg=CARD, fg=NEON_BLUE).pack()
    tk.Label(ci, text="FACE RECOGNITION ENGINE", font=FMONO, bg=CARD, fg=NEON_BLUE).pack(pady=(4,2))
    tk.Label(ci, text="Camera ke saamne kharen — system automatically pehchan karega",
             font=FSMALL, bg=CARD, fg=TXT3).pack()

    scan_v = tk.StringVar(value="◉ System ready")
    tk.Label(ci, textvariable=scan_v, font=FBODY, bg=CARD, fg=NEON_GREEN).pack(pady=10)

    # Stats row
    sr = tk.Frame(ci, bg=CARD)
    sr.pack(pady=6)
    ts = tk.StringVar(value="0")
    ps = tk.StringVar(value="0")
    for txt, var, col in [("Registered", ts, NEON_BLUE), ("Today", ps, NEON_GREEN)]:
        f = tk.Frame(sr, bg=BG3, padx=20, pady=8)
        f.pack(side="left", padx=8)
        tk.Label(f, text=txt, font=FSMALL, bg=BG3, fg=TXT2).pack()
        tk.Label(f, textvariable=var, font=(FT, 22, "bold"), bg=BG3, fg=col).pack()

    def refresh_counters():
        ts.set(str(len(student_db)))
        today = datetime.now().strftime("%d-%m-%Y")
        ps.set(str(sum(1 for d in student_db.values()
                       if any(e.startswith(today) for e in d.get("attendance_log",[])))))

    def do_scan():
        day = datetime.now().strftime("%A")
        if day in ["Saturday","Sunday"]:
            messagebox.showinfo("Holiday 🎉", f"Aaj {day} hai — chutti!"); return
        if not student_db:
            messagebox.showerror("Error", "Koi student registered nahi!"); return

        scan_v.set("📷 Camera shuru ho rahi hai..."); root.update()
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret: break
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                try:
                    rid, conf = recognizer.predict(gray[y:y+h, x:x+w])
                    sr = str(rid)
                    if conf < 70 and sr in student_db:
                        s      = student_db[sr]
                        today  = datetime.now().strftime("%d-%m-%Y")
                        now_t  = datetime.now().strftime("%H:%M:%S")
                        already = any(e.startswith(today) for e in s.get("attendance_log",[]))
                        if not already:
                            s["present"] += 1
                            s.setdefault("attendance_log",[]).append(f"{today} {now_t}")
                            save_data()
                            cap.release(); cv2.destroyAllWindows()
                            pct = att_pct(s); cgpa = calc_cgpa(s)
                            g, _ = grade_from_cgpa(cgpa)
                            icon = "✅" if pct >= 50 else "⚠️"
                            messagebox.showinfo("Marked ✅",
                                f"◈ Welcome, {s['name']}!\n\n"
                                f"📅 Date   : {today}\n"
                                f"🕐 Time   : {now_t}\n"
                                f"📊 Days   : {s['present']}/{TOTAL_COURSE_DAYS}\n"
                                f"{icon} Att%  : {int(pct)}%\n"
                                f"🎓 CGPA  : {cgpa:.2f}  [{g}]")
                            scan_v.set(f"✅ {s['name']} — {int(pct)}%")
                            refresh_counters(); return
                        else:
                            cap.release(); cv2.destroyAllWindows()
                            messagebox.showwarning("Already Marked",
                                f"{s['name']} ki attendance aaj already ho chuki hai!")
                            scan_v.set(f"⚠ {s['name']} already marked"); refresh_counters(); return
                    else:
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,80),2)
                        cv2.putText(frame,"Unknown",(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,80),2)
                except: pass
            cv2.putText(frame,"Q = Quit",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.6,(200,200,200),1)
            cv2.imshow("SmartAttend PRO — Face Scan", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        cap.release(); cv2.destroyAllWindows()
        scan_v.set("◉ Scan closed"); refresh_counters()

    tk.Button(ci, text="🚀  START FACE SCAN", font=FHEAD,
              bg=NEON_BLUE, fg=BG, bd=0, padx=36, pady=13,
              cursor="hand2", command=do_scan).pack(pady=14)
    tk.Label(ci,
             text="Tip: Achhi roshni mein kharen  ●  'Q' dabayein quit karne ke liye",
             font=FSMALL, bg=CARD, fg=TXT2).pack()
    refresh_counters()

build_scan()

# ══════════════════════════════════════════════
#  PAGE 4 — RECORDS
# ══════════════════════════════════════════════
def build_records():
    global rec_tree
    pg = pages["records"]

    hrow = tk.Frame(pg, bg=BG)
    hrow.pack(fill="x", padx=24, pady=(18,6))
    tk.Label(hrow, text="◈  STUDENT RECORDS", font=FTITLE,
             bg=BG, fg=NEON_PURPLE).pack(side="left")
    for txt, col, cmd in [
        ("📤 Export",  NEON_GREEN,  export_csv),
        ("🗑 Delete",  NEON_PINK,   delete_student_action),
        ("🔄 Refresh", NEON_BLUE,   update_records_table),
    ]:
        tk.Button(hrow, text=txt, font=FSMALL, bg=BG3, fg=col,
                  bd=0, padx=12, pady=6, cursor="hand2",
                  command=cmd).pack(side="right", padx=4)

    srow = tk.Frame(pg, bg=BG)
    srow.pack(fill="x", padx=24, pady=4)
    tk.Label(srow, text="🔍", font=FBODY, bg=BG, fg=NEON_PURPLE).pack(side="left")
    sv = tk.StringVar()
    tk.Entry(srow, textvariable=sv, font=FBODY, bg=CARD, fg=TXT,
             insertbackground=NEON_PURPLE, bd=0, relief="flat", width=30,
             highlightthickness=1, highlightbackground=BORDER,
             highlightcolor=NEON_PURPLE).pack(side="left", padx=8, ipady=7)
    sv.trace("w", lambda *a: update_records_table(sv.get().lower()))

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("N.Treeview",
                    background=CARD, foreground=TXT,
                    fieldbackground=CARD, rowheight=30,
                    font=FBODY, borderwidth=0)
    style.configure("N.Treeview.Heading",
                    background=BG2, foreground=NEON_PURPLE,
                    font=FHEAD, relief="flat")
    style.map("N.Treeview",
              background=[("selected", NEON_PURPLE)],
              foreground=[("selected", "white")])

    cols = ("n","name","roll","dept","phone","days","att","att_s","cgpa","grade")
    hdrs = ("#","Name","Roll","Department","Phone","Days","Att%","Status","CGPA","Grade")
    wids = (32,150,70,140,110,50,55,75,65,55)

    rec_tree = ttk.Treeview(pg, columns=cols, show="headings",
                            style="N.Treeview", height=16)
    for c, h, w in zip(cols, hdrs, wids):
        rec_tree.heading(c, text=h)
        rec_tree.column(c, width=w, anchor="center")

    vsb = ttk.Scrollbar(pg, orient="vertical",   command=rec_tree.yview)
    rec_tree.configure(yscrollcommand=vsb.set)
    rec_tree.pack(side="left", fill="both", expand=True, padx=(24,0), pady=10)
    vsb.pack(side="right", fill="y", pady=10, padx=(0,10))

build_records()

# ══════════════════════════════════════════════
#  PAGE 5 — MARKS / CGPA
# ══════════════════════════════════════════════
def build_marks():
    pg = pages["marks"]

    tk.Label(pg, text="◈  MARKS & CGPA TRACKER", font=FTITLE,
             bg=BG, fg=NEON_YELLOW).pack(anchor="w", padx=28, pady=(22,4))
    tk.Label(pg, text="Add exam marks per subject — CGPA auto calculate hoga",
             font=FSMALL, bg=BG, fg=TXT2).pack(anchor="w", padx=28)

    body = tk.Frame(pg, bg=BG)
    body.pack(fill="both", expand=True, padx=24, pady=10)

    # LEFT — Add marks form
    lw, li = neon_card(body, color=NEON_YELLOW, px=18, py=16)
    lw.pack(side="left", fill="y", padx=(0,8))
    tk.Label(li, text="ADD MARKS", font=FHEAD, bg=CARD, fg=NEON_YELLOW).pack(anchor="w", pady=(0,10))

    def lbl_entry(parent, label, width=22):
        tk.Label(parent, text=label, font=FSMALL, bg=CARD, fg=TXT3).pack(anchor="w", pady=(6,1))
        e = tk.Entry(parent, font=FBODY, bg=BG3, fg=TXT,
                     insertbackground=NEON_YELLOW, bd=0, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=NEON_YELLOW, width=width)
        e.pack(fill="x", ipady=7)
        return e

    roll_e  = lbl_entry(li, "ROLL NUMBER")
    subj_e  = lbl_entry(li, "SUBJECT NAME")
    marks_e = lbl_entry(li, "MARKS (0–100)")

    add_status = tk.StringVar(value="")
    tk.Label(li, textvariable=add_status, font=FSMALL, bg=CARD, fg=NEON_YELLOW).pack(pady=4)

    def do_add_marks():
        roll  = roll_e.get().strip()
        subj  = subj_e.get().strip()
        marks = marks_e.get().strip()
        if not all([roll, subj, marks]):
            messagebox.showerror("Error", "Saare fields bharen!"); return
        if roll not in student_db:
            messagebox.showerror("Error", f"Roll {roll} registered nahi hai!"); return
        try:
            m = float(marks)
            if not 0 <= m <= 100: raise ValueError
        except:
            messagebox.showerror("Error", "Marks 0–100 ke beech hone chahiye!"); return

        d = student_db[roll]
        d.setdefault("subjects", {}).setdefault(subj, []).append(m)
        d["cgpa"] = calc_cgpa(d)
        save_data()
        g, col = grade_from_cgpa(d["cgpa"])
        add_status.set(f"✅ Added! CGPA: {d['cgpa']:.2f} [{g}]")
        marks_e.delete(0, "end")
        refresh_marks_table()

    tk.Button(li, text="➕  ADD MARKS", font=FHEAD,
              bg=NEON_YELLOW, fg=BG, bd=0, padx=16, pady=10,
              cursor="hand2", command=do_add_marks).pack(fill="x", pady=8)

    # Marks summary per student
    tk.Label(li, text="QUICK LOOKUP", font=FHEAD, bg=CARD, fg=NEON_YELLOW).pack(anchor="w", pady=(12,4))
    lookup_e = lbl_entry(li, "Enter Roll No to view:")

    info_v = tk.StringVar(value="")
    tk.Label(li, textvariable=info_v, font=FSMALL, bg=CARD, fg=TXT, justify="left").pack(anchor="w")

    def do_lookup():
        roll = lookup_e.get().strip()
        if roll not in student_db:
            info_v.set("Roll not found!"); return
        d    = student_db[roll]
        cgpa = calc_cgpa(d)
        g, _ = grade_from_cgpa(cgpa)
        txt  = f"Name  : {d['name']}\n"
        txt += f"CGPA  : {cgpa:.2f}  [{g}]\n\n"
        for subj, marks in d.get("subjects", {}).items():
            avg = sum(marks)/len(marks) if marks else 0
            txt += f"• {subj[:18]:<18} avg={avg:.1f}\n"
        info_v.set(txt if d.get("subjects") else "No marks added yet")

    tk.Button(li, text="🔍 LOOKUP", font=FBODY, bg=BG3, fg=NEON_YELLOW,
              bd=0, padx=10, pady=8, cursor="hand2", command=do_lookup).pack(fill="x", pady=4)

    # RIGHT — Marks table
    rw, ri = neon_card(body, color=NEON_YELLOW, px=12, py=12)
    rw.pack(side="left", fill="both", expand=True)
    tk.Label(ri, text="ALL STUDENTS — CGPA OVERVIEW", font=FHEAD,
             bg=CARD, fg=NEON_YELLOW).pack(anchor="w", pady=(0,8))

    mk_cols = ("name","roll","dept","cgpa","grade","subjects")
    mk_hdrs = ("Name","Roll","Dept","CGPA","Grade","Subjects Added")
    mk_wids = (150, 70, 130, 70, 60, 120)

    mk_tree = ttk.Treeview(ri, columns=mk_cols, show="headings",
                           style="N.Treeview", height=14)
    for c, h, w in zip(mk_cols, mk_hdrs, mk_wids):
        mk_tree.heading(c, text=h)
        mk_tree.column(c, width=w, anchor="center")
    mk_tree.pack(fill="both", expand=True)

    def refresh_marks_table():
        for i in mk_tree.get_children(): mk_tree.delete(i)
        for roll, d in student_db.items():
            cgpa  = calc_cgpa(d)
            g, _  = grade_from_cgpa(cgpa)
            subjs = ", ".join(d.get("subjects", {}).keys()) or "—"
            mk_tree.insert("", tk.END, values=(
                d["name"], roll, d["dept"], f"{cgpa:.2f}", g, subjs))

    # make refresh_marks_table accessible to do_add_marks
    pg._refresh_marks = refresh_marks_table
    refresh_marks_table()

build_marks()

# ══════════════════════════════════════════════
#  PAGE 6 — REMARKS
# ══════════════════════════════════════════════
def build_remarks():
    pg = pages["remarks"]

    tk.Label(pg, text="◈  TEACHER REMARKS", font=FTITLE,
             bg=BG, fg=NEON_PINK).pack(anchor="w", padx=28, pady=(22,4))
    tk.Label(pg, text="Per-student remarks, warnings, commendations",
             font=FSMALL, bg=BG, fg=TXT2).pack(anchor="w", padx=28)

    body = tk.Frame(pg, bg=BG)
    body.pack(fill="both", expand=True, padx=24, pady=10)

    # LEFT form
    lw, li = neon_card(body, color=NEON_PINK, px=18, py=16)
    lw.pack(side="left", fill="y", padx=(0,8))

    tk.Label(li, text="ADD REMARK", font=FHEAD, bg=CARD, fg=NEON_PINK).pack(anchor="w", pady=(0,10))

    def lbl_entry(parent, label, width=22):
        tk.Label(parent, text=label, font=FSMALL, bg=CARD, fg=TXT3).pack(anchor="w", pady=(6,1))
        e = tk.Entry(parent, font=FBODY, bg=BG3, fg=TXT,
                     insertbackground=NEON_PINK, bd=0, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=NEON_PINK, width=width)
        e.pack(fill="x", ipady=7)
        return e

    roll_e    = lbl_entry(li, "ROLL NUMBER")
    teacher_e = lbl_entry(li, "TEACHER NAME")

    tk.Label(li, text="REMARK TYPE", font=FSMALL, bg=CARD, fg=TXT3).pack(anchor="w", pady=(6,1))
    rtype_v = tk.StringVar(value="📝 General")
    rtype_cb = ttk.Combobox(li, textvariable=rtype_v, font=FBODY, width=22,
                             values=["📝 General","⚠️ Warning","🌟 Commendation","❗ Urgent","📌 Note"])
    rtype_cb.pack(fill="x", ipady=4)

    tk.Label(li, text="REMARK TEXT", font=FSMALL, bg=CARD, fg=TXT3).pack(anchor="w", pady=(6,1))
    remark_txt = tk.Text(li, font=FBODY, bg=BG3, fg=TXT, insertbackground=NEON_PINK,
                         bd=0, relief="flat", highlightthickness=1,
                         highlightbackground=BORDER, highlightcolor=NEON_PINK,
                         width=24, height=4)
    remark_txt.pack(fill="x")

    add_v = tk.StringVar(value="")
    tk.Label(li, textvariable=add_v, font=FSMALL, bg=CARD, fg=NEON_PINK).pack(pady=4)

    def do_add_remark():
        roll    = roll_e.get().strip()
        teacher = teacher_e.get().strip()
        rtype   = rtype_v.get()
        text    = remark_txt.get("1.0", "end").strip()
        if not all([roll, teacher, text]):
            messagebox.showerror("Error", "Saare fields bharen!"); return
        if roll not in student_db:
            messagebox.showerror("Error", f"Roll {roll} registered nahi!"); return
        entry = {
            "date":    datetime.now().strftime("%d-%m-%Y %H:%M"),
            "teacher": teacher,
            "type":    rtype,
            "text":    text
        }
        student_db[roll].setdefault("remarks", []).append(entry)
        save_data()
        add_v.set("✅ Remark added!")
        remark_txt.delete("1.0", "end")
        refresh_rem_table()

    tk.Button(li, text="💬  ADD REMARK", font=FHEAD,
              bg=NEON_PINK, fg="white", bd=0, padx=16, pady=10,
              cursor="hand2", command=do_add_remark).pack(fill="x", pady=8)

    # View remarks for a student
    tk.Label(li, text="VIEW STUDENT REMARKS", font=FHEAD,
             bg=CARD, fg=NEON_PINK).pack(anchor="w", pady=(10,4))
    view_roll_e = lbl_entry(li, "Roll No:")
    view_v = tk.StringVar(value="")
    tk.Label(li, textvariable=view_v, font=FSMALL, bg=CARD, fg=TXT,
             justify="left", wraplength=200).pack(anchor="w")

    def do_view():
        roll = view_roll_e.get().strip()
        if roll not in student_db:
            view_v.set("Roll not found!"); return
        remarks = student_db[roll].get("remarks", [])
        if not remarks:
            view_v.set("Koi remark nahi hai"); return
        txt = ""
        for r in remarks[-4:]:
            txt += f"{r['type']}\n{r['date']}\nBy: {r['teacher']}\n{r['text'][:60]}\n─────\n"
        view_v.set(txt.strip())

    tk.Button(li, text="🔍 VIEW", font=FBODY, bg=BG3, fg=NEON_PINK,
              bd=0, padx=10, pady=8, cursor="hand2", command=do_view).pack(fill="x", pady=4)

    # RIGHT — all remarks table
    rw, ri = neon_card(body, color=NEON_PINK, px=12, py=12)
    rw.pack(side="left", fill="both", expand=True)
    tk.Label(ri, text="ALL REMARKS LOG", font=FHEAD, bg=CARD, fg=NEON_PINK).pack(anchor="w", pady=(0,8))

    rem_cols = ("date","name","roll","type","teacher","remark")
    rem_hdrs = ("Date","Name","Roll","Type","Teacher","Remark")
    rem_wids = (120,130,60,110,110,200)

    rem_tree = ttk.Treeview(ri, columns=rem_cols, show="headings",
                            style="N.Treeview", height=15)
    for c, h, w in zip(rem_cols, rem_hdrs, rem_wids):
        rem_tree.heading(c, text=h)
        rem_tree.column(c, width=w, anchor="w")

    vsb2 = ttk.Scrollbar(ri, orient="vertical", command=rem_tree.yview)
    rem_tree.configure(yscrollcommand=vsb2.set)
    rem_tree.pack(side="left", fill="both", expand=True)
    vsb2.pack(side="right", fill="y")

    def refresh_rem_table():
        for i in rem_tree.get_children(): rem_tree.delete(i)
        for roll, d in student_db.items():
            for r in d.get("remarks", []):
                rem_tree.insert("", tk.END, values=(
                    r["date"], d["name"], roll,
                    r["type"], r["teacher"], r["text"][:50]))

    refresh_rem_table()

build_remarks()

# ══════════════════════════════════════════════
#  SIDEBAR NAV
# ══════════════════════════════════════════════
nav_btns = []
nav_defs = [
    ("DASHBOARD",  "🏠", "dashboard", NEON_BLUE),
    ("REGISTER",   "📸", "register",  NEON_GREEN),
    ("SCAN FACE",  "🎥", "scan",      NEON_BLUE),
    ("RECORDS",    "📋", "records",   NEON_PURPLE),
    ("MARKS/CGPA", "📝", "marks",     NEON_YELLOW),
    ("REMARKS",    "💬", "remarks",   NEON_PINK),
]

def make_nav(text, icon, page, color):
    def click():
        show_page(page)
        for b, c in nav_btns:
            b.config(bg=BG2, fg=TXT2)
        btn.config(bg=CARD, fg=color)
    btn = tk.Button(sidebar, text=f" {icon}  {text}", font=FSMALL,
                    bg=BG2, fg=TXT2, bd=0, relief="flat", anchor="w",
                    padx=16, pady=11, cursor="hand2",
                    activebackground=CARD, activeforeground=color,
                    command=click)
    btn.pack(fill="x", padx=8, pady=1)
    nav_btns.append((btn, color))
    return btn

first_btn = None
for txt, icon, pg_key, col in nav_defs:
    b = make_nav(txt, icon, pg_key, col)
    if first_btn is None: first_btn = (b, col)

tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=8)
tk.Button(sidebar, text="📤  EXPORT CSV", font=FSMALL,
          bg=BG3, fg=NEON_ORANGE, bd=0, padx=14, pady=9,
          cursor="hand2", command=export_csv).pack(fill="x", padx=8, pady=1)
tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=8)
tk.Label(sidebar, text=f"Course Days: {TOTAL_COURSE_DAYS}",
         font=FSMALL, bg=BG2, fg=TXT2).pack()
tk.Label(sidebar, text="v3.0  ◈  PRO Edition",
         font=FSMALL, bg=BG2, fg=NEON_PURPLE).pack(pady=4)

# ══════════════════════════════════════════════
#  START
# ══════════════════════════════════════════════
show_page("dashboard")
if first_btn:
    first_btn[0].config(bg=CARD, fg=first_btn[1])

root.mainloop()
