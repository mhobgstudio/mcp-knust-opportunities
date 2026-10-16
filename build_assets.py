#!/usr/bin/env python3
"""Parse the master table from the report and emit CSV, ICS, dashboard.tex, action-cards.tex."""
import re, csv, datetime, os

TEX = "/home/heavenly-dev/Documents/MCP/mcp-knust-workshops-report.tex"
OUT = "/home/heavenly-dev/Documents/MCP"
TODAY = datetime.date(2026, 10, 16)

MONTHS = {m: i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}

def norm(d):
    d = d.replace("\\textbf{", "").replace("}", "").replace("$\\sim$", "").replace("~", " ")
    m = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})', d)
    if m:
        return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(2)], int(m.group(1)))
    m = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*', d)
    if m:
        mon = MONTHS[m.group(2)]
        year = 2026 if mon >= 10 else 2027
        return "%d-%02d-%02d" % (year, mon, int(m.group(1)))
    m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})', d)
    if m:
        return "%s-%02d-01" % (m.group(2), MONTHS[m.group(1)])
    return None

def esc(s):
    s = s.replace("\\&", "\x01").replace("\\%", "\x02").replace("\\_", "\x03")
    s = s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
    s = s.replace("\x01", "\\&").replace("\x02", "\\%").replace("\x03", "\\_")
    return s

with open(TEX, encoding="utf-8") as f:
    lines = f.readlines()

start = next(i for i, l in enumerate(lines) if l.startswith("\\part{Master Table"))
b = next(i for i in range(start, len(lines)) if "\\begin{longtable}" in lines[i])
e = next(i for i in range(b, len(lines)) if "\\end{longtable}" in lines[i])

rows = []
category = ""
for i in range(b, e):
    line = lines[i].rstrip("\n")
    mc = re.search(r'---\s*([A-Z][A-Z ,&/\\-]+?)\s*---', line)
    if "\\multicolumn" in line and mc:
        category = mc.group(1).replace("\\&", "&").strip()
        continue
    if " & " not in line or not line.endswith("\\\\"):
        continue
    if "\\textbf{Event}" in line:
        continue
    parts = line[:-2].split(" & ")
    if len(parts) != 4:
        continue
    first, desc, deadline, members = parts
    hm = re.match(r'\\href\{([^}]+)\}\{(.*)\}$', first.strip())
    if hm:
        url, name = hm.group(1), hm.group(2)
    else:
        url, name = "", first.strip()
    rows.append({
        "name": name, "url": url, "desc": desc, "deadline_text": deadline,
        "deadline": norm(deadline), "members": members, "category": category,
    })

# CSV
with open(os.path.join(OUT, "mcp-opportunities.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category","name","description","deadline_text","deadline_iso","members","url"])
    for r in rows:
        w.writerow([r["category"], r["name"], r["desc"], r["deadline_text"], r["deadline"] or "", r["members"], r["url"]])

# ICS
def ics_esc(s):
    return s.replace("\\", "").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")
ics = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//MCP KNUST//Opportunities//EN","CALSCALE:GREGORIAN"]
n = 0
for r in rows:
    if not r["deadline"]:
        continue
    n += 1
    d = r["deadline"].replace("-", "")
    ics += ["BEGIN:VEVENT",
            "UID:mcp-%d@knust" % n,
            "DTSTAMP:20261016T000000Z",
            "DTSTART;VALUE=DATE:%s" % d,
            "SUMMARY:%s" % ics_esc(r["name"] + " — deadline"),
            "DESCRIPTION:%s" % ics_esc(r["desc"] + " | Members: " + r["members"]),
            "CATEGORIES:%s" % ics_esc(r["category"])]
    if r["url"]:
        ics.append("URL:%s" % r["url"])
    ics.append("END:VEVENT")
ics.append("END:VCALENDAR")
with open(os.path.join(OUT, "mcp-deadlines.ics"), "w", encoding="utf-8") as f:
    f.write("\n".join(ics) + "\n")

# Dashboard (next 90 days)
horizon = TODAY + datetime.timedelta(days=90)
soon = [r for r in rows if r["deadline"] and TODAY <= datetime.date.fromisoformat(r["deadline"]) <= horizon]
soon.sort(key=lambda r: r["deadline"])
with open(os.path.join(OUT, "dashboard.tex"), "w", encoding="utf-8") as f:
    f.write("\\section{Next 90 Days --- Live Deadlines Dashboard}\n\n")
    f.write("\\noindent Every deadline between \\textbf{16 October 2026} and \\textbf{14 January 2027}, "
            "sorted by date. A machine-readable calendar of \\emph{all} dated deadlines is shipped alongside this "
            "report as \\texttt{mcp-deadlines.ics} (import into any calendar app).\n\n")
    f.write("\\begin{longtable}{@{}p{2.0cm}p{4.4cm}p{5.2cm}p{3.0cm}@{}}\n\\toprule\n")
    f.write("\\textbf{Deadline} & \\textbf{Event / Grant} & \\textbf{Description} & \\textbf{Members} \\\\\n\\midrule\n\\endhead\n")
    for r in soon:
        dt = datetime.date.fromisoformat(r["deadline"]).strftime("%d %b %Y")
        nm = ("\\href{%s}{%s}" % (r["url"], esc(r["name"]))) if r["url"] else esc(r["name"])
        f.write("%s & %s & %s & %s \\\\\n\\midrule\n" % (dt, nm, esc(r["desc"]), esc(r["members"])))
    f.write("\\bottomrule\n\\end{longtable}\n\n")
    f.write("\\noindent\\emph{%d live deadlines in the next 90 days.}\n\n" % len(soon))

# Action cards (per member)
member_rows = {}
for r in rows:
    if not r["deadline"]:
        continue
    ms = re.sub(r'\\textbf\{([^}]*)\}', r'\1', r["members"])
    for m in [x.strip() for x in ms.split(",") if x.strip()]:
        member_rows.setdefault(m, []).append(r)
with open(os.path.join(OUT, "action-cards.tex"), "w", encoding="utf-8") as f:
    f.write("\\section{Per-Member Action Cards}\n\n")
    f.write("\\noindent Each member's dated opportunities, earliest first (top 6). "
            "Generated from the master table; deadlines are the next actionable date.\n\n")
    for m in sorted(member_rows):
        rs = sorted(member_rows[m], key=lambda r: r["deadline"])[:6]
        f.write("\\subsection*{%s}\n\\begin{itemize}[leftmargin=1.4em,itemsep=0.1em]\n" % esc(m))
        for r in rs:
            dt = datetime.date.fromisoformat(r["deadline"]).strftime("%d %b %Y")
            nm = ("\\href{%s}{%s}" % (r["url"], esc(r["name"]))) if r["url"] else esc(r["name"])
            f.write("  \\item \\textbf{%s} --- %s\n" % (dt, nm))
        f.write("\\end{itemize}\n\n")

print("rows:", len(rows), "| dated:", sum(1 for r in rows if r["deadline"]),
      "| next90:", len(soon), "| members:", len(member_rows))
