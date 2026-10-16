#!/usr/bin/env python3
"""Generate the interactive MCP opportunities dashboard (index.html) + PWA + CI from the CSV."""
import csv, json, re, datetime, os

DIR = "/home/heavenly-dev/Documents/MCP"
CSV = os.path.join(DIR, "mcp-opportunities.csv")
OUT = os.path.join(DIR, "index.html")
TODAY = datetime.date(2026, 10, 16)
MONTHS = {m: i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}

PREDATORY = ["waset", "apste", "researchleagues", "research-leagues", "research foundation",
             "research plus", "researchfoundation", "researchplus", "iser", "iccpapm", "icmcp"]

# acceptance rates (name-substring -> label). Sources: official business meetings / CORE / OpenAccept.
RATES = {
 "QIP 2027": "~21% talks (QIP26: 20.6%)",
 "IEEE Quantum Week": "~47% papers (QCE25: 261/557)",
 "ISC High Performance": "~29% papers (ISC25)",
 "SC27": "~22% papers (SC25: 21.8%)",
 "EGU27": "high (convener-reviewed)",
 "APS Global Physics Summit": "high (contributed)",
 "GRC": "application-based",
 "EuroMOF": "peer-reviewed (rate n/p)",
 "SEG": "abstract-reviewed",
 "ML4SEG": "abstract-reviewed",
 "IUGG/IASPEI": "abstract-reviewed",
 "OCEANS 2027": "abstract-reviewed",
 "ICQE 2027": "abstract-reviewed",
 "E-MRS Spring 2027": "abstract-reviewed",
 "MRS Spring 2027": "abstract-reviewed",
 "AMRS 2026": "abstract-reviewed",
 "ACP2027": "abstract-reviewed",
 "SOAPHYS": "abstract-reviewed",
 "Deep Learning Indaba": "workshop-based",
 "AfriQA 2026": "abstract-reviewed",
 "AWaTEC27": "abstract-reviewed",
 "MIMAR 2027": "abstract-reviewed",
 "IWA LET27": "abstract-reviewed",
 "IC-AISMART 2027": "abstract-reviewed",
 "Optica Quantum 2.0": "abstract-reviewed",
 "CLEO 2027": "abstract-reviewed",
 "APS DAMOP 2027": "high (contributed)",
}

CITY_COORDS = {
 "accra":(5.6,-0.19),"kumasi":(6.69,-1.62),"kigali":(-1.94,30.06),"nairobi":(-1.29,36.82),
 "cape town":(-33.92,18.42),"johannesburg":(-26.20,28.05),"stellenbosch":(-33.93,18.86),
 "dakar":(14.72,-17.47),"rabat":(34.02,-6.84),"lagos":(6.52,3.38),"tunis":(36.81,10.18),
 "ouagadougou":(12.37,-1.52),"arusha":(-3.37,36.68),"dar es salaam":(-6.79,39.21),
 "livingstone":(-17.85,25.86),"ile-ife":(7.49,4.55),"zambia":(-13.13,27.85),
 "vienna":(48.21,16.37),"trieste":(45.65,13.78),"strasbourg":(48.57,7.75),"munich":(48.14,11.58),
 "hamburg":(53.55,9.99),"leuven":(50.88,4.70),"gothenburg":(57.71,11.97),"lausanne":(46.52,6.63),
 "cambridge":(52.20,0.12),"oxford":(51.75,-1.26),"london":(51.51,-0.13),"dublin":(53.35,-6.26),
 "madrid":(40.42,-3.70),"seville":(37.39,-5.98),"istanbul":(41.01,28.98),"ghent":(51.05,3.72),
 "varese":(45.82,8.83),"como":(45.81,9.09),"poitiers":(46.58,0.34),"modena":(44.65,10.93),
 "erlangen":(49.60,11.00),"delft":(52.01,4.36),"amsterdam":(52.37,4.90),"copenhagen":(55.68,12.57),
 "singapore":(1.35,103.82),"chicago":(41.88,-87.63),"denver":(39.74,-104.99),
 "long beach":(33.77,-118.19),"houston":(29.76,-95.37),"stanford":(37.43,-122.17),
 "woods hole":(41.53,-70.67),"waterloo":(43.46,-80.52),"new york":(40.71,-74.01),
 "sao paulo":(-23.55,-46.63),"beijing":(39.90,116.41),"xiamen":(24.48,118.09),
 "khobar":(26.28,50.21),"riyadh":(24.71,46.68),"hong kong":(22.32,114.17),"padova":(45.41,11.88),
 "bologna":(44.49,11.34),"sicily":(37.60,14.02),"murcia":(37.99,-1.13),"bled":(46.37,14.11),
 "dortmund":(51.51,7.47),"karlsruhe":(49.01,8.40),"bayreuth":(49.95,11.58),"aarhus":(56.16,10.20),
 "julich":(50.92,6.36),"freiburg":(47.99,7.85),"saarland":(49.24,6.99),"l'aquila":(42.35,13.40),
 "rome":(41.90,12.50),"tartu":(58.38,26.72),"gyumri":(40.79,43.85),"antalya":(36.90,30.71),
 "perth":(-31.95,115.86),"benin city":(6.34,5.62),"makerere":(0.33,32.57),"kampala":(0.35,32.58),
 "monastir":(35.78,10.83),"ziguinchor":(12.57,-16.27),"abidjan":(5.36,-4.01),
 "incheon":(37.46,126.71),"seattle":(47.61,-122.33),"washington":(38.91,-77.04),
 "boston":(42.36,-71.06),"toronto":(43.65,-79.38),"vancouver":(49.28,-123.12),
 "san francisco":(37.77,-122.42),"los angeles":(34.05,-118.24),"austin":(30.27,-97.74),
 "naples":(40.85,14.27),"gyumri ": (40.79,43.85),"taipei":(25.03,121.57),
}

# eligibility rules: name-substring -> dict(maxAge, maxYearsPhD, stages, region, note)
ELIG = {
 "TWAS SG-NAPI": {"maxAge":40,"maxYearsPhD":5,"region":"Africa","note":"PhD abroad within 5 yr, returned home within 36 mo"},
 "TWAS Research Grants: Individuals": {"maxAge":45,"note":"PhD required; S&T-lagging country"},
 "TWAS--FAPESP": {"stages":["Postdoc","Student"],"note":"postdoc in Brazil"},
 "ICTP Associateships (Junior": {"maxAge":35,"note":"Junior track <=35"},
 "Humboldt Research Fellowship": {"maxYearsPhD":12,"note":"postdoc <4 yr or experienced <12 yr"},
 "Royal Society Career Development": {"stages":["Postdoc","Staff"],"note":"early-career, under-represented groups"},
 "OWSD Early Career Fellowship": {"stages":["Postdoc","Staff"],"region":"Africa","note":"women in STEM, STLC"},
 "NVIDIA Graduate Fellowship": {"stages":["Student"],"note":"PhD students, 1+ yr"},
 "MathQuantum": {"stages":["Student","Postdoc"],"note":"HS/UG/grad/postdoc"},
 "USEQIP 2027": {"stages":["Student"],"note":"undergraduates"},
 "PSI master's": {"stages":["Student"],"note":"incoming MSc"},
 "DAAD Research Grants in Germany": {"stages":["Student","Postdoc"],"note":"PhD/postdoc"},
 "Bayreuth Humboldt Starter": {"stages":["Postdoc","Staff"],"note":"research stay"},
 "Afretec Seed Grants": {"stages":["Staff"],"note":"multi-institution teams"},
 "LAAAMP FAST": {"stages":["Staff"],"note":"faculty + PhD student pair"},
 "Young Leaders in Research": {"stages":["Student","Postdoc"],"region":"Africa","note":"early-career African researchers"},
 "beVisioneers": {"maxAge":28,"note":"young eco-innovators 18-28"},
 "ABCD Future Environmental": {"stages":["Student"],"note":"PhD research stay"},
 "UCT Africa Climate Collaborative": {"stages":["Student","Postdoc"],"region":"Africa","note":"African PhD grads"},
 "Cambridge Africa Climate": {"stages":["Staff"],"note":"Cambridge + African PI pair"},
 "Grand Challenges Africa / SFA": {"region":"Africa","note":"Africa-led (80% to African orgs)"},
 "Novo Nordisk Challenge 2027": {"stages":["Staff"],"region":"Europe","note":"EU-based main applicant"},
 "NordForsk G7-Nordic": {"stages":["Staff"],"region":"Europe","note":"Nordic host required"},
 "Wellcome Awards": {"stages":["Postdoc","Staff"],"note":"UK/Africa LMIC host"},
 "NSF DMREF": {"stages":["Staff"],"region":"Other","note":"US-based teams"},
 "AFOSR--Taiwan NSTC": {"stages":["Staff"],"region":"Other","note":"US-Taiwan investigators"},
 "Google Academic Research Awards": {"stages":["Staff"],"note":"professors advising students"},
 "NVIDIA Academic Grant Program": {"stages":["Staff"],"note":"full-time faculty"},
 "IPAM UCLA": {"stages":["Postdoc","Staff"],"note":"researchers in AI+materials"},
 "Psi-k activity funding": {"stages":["Staff"],"note":"organisers of events"},
 "CECAM flagship / Lorentz": {"stages":["Staff"],"note":"organisers of events"},
 "African Water Facility": {"stages":["Staff"],"region":"Africa","note":"African water programmes"},
 "BMBF": {"stages":["Staff"],"region":"Europe","note":"German partner required"},
 "EWAP Research Fellowship": {"stages":["Student","Postdoc"],"region":"Africa","note":"African climate/agriculture"},
 "TWAS Collaborative Grants": {"note":"prior TWAS recipients only"},
 "ICTP Associateships (Junior/Regular/Senior)": {"maxAge":65,"note":"Junior<=35, Regular 36-45, Senior 46-65"},
}

def clean(s):
    s = s or ""
    s = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:textbf|emph|textit|texttt)\{([^}]*)\}", r"\1", s)
    s = s.replace("\\textless", "<").replace("\\textgreater", ">")
    s = s.replace("\\textbar", "|").replace("\\&", "&").replace("\\%", "%")
    s = s.replace("\\_", "_").replace("\\#", "#").replace("\\$", "$")
    s = s.replace("$\\sim$", "~").replace("$\\rightarrow$", "\u2192")
    s = s.replace("$\\leq$", "\u2264").replace("$\\geq$", "\u2265")
    s = s.replace("$\\pm$", "\u00b1").replace("\\ldots", "\u2026")
    s = s.replace("\\rightarrow", "\u2192").replace("\\to ", "\u2192 ")
    s = s.replace("\\pounds", "\u00a3").replace("\\euro", "\u20ac")
    s = s.replace("$+$", "+").replace("$-$", "-").replace("$", "")
    s = s.replace("\\ ", " ").replace("~", " ")
    s = s.replace("--", "\u2013")
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()

def parse_dates(name):
    """Return (start_iso, end_iso) parsed from the event-name parenthetical, else (None,None)."""
    m = re.search(r"\(([^)]*)\)", name)
    if not m:
        return None, None
    t = m.group(1)
    y = re.search(r"(20\d\d)", t)
    year = int(y.group(1)) if y else None
    if not year:
        return None, None
    # 20--26 Feb 2027
    m2 = re.search(r"(\d{1,2})\s*[\u2013-]+\s*(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", t)
    if m2:
        mo = MONTHS[m2.group(3)]
        return ("%d-%02d-%02d" % (year, mo, int(m2.group(1))),
                "%d-%02d-%02d" % (year, mo, int(m2.group(2))))
    # 30 Nov -- 4 Dec 2026
    m3 = re.search(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s*[\u2013-]+\s*(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", t)
    if m3:
        return ("%d-%02d-%02d" % (year, MONTHS[m3.group(2)], int(m3.group(1))),
                "%d-%02d-%02d" % (year, MONTHS[m3.group(4)], int(m3.group(3))))
    # single day
    m4 = re.search(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", t)
    if m4:
        d = "%d-%02d-%02d" % (year, MONTHS[m4.group(2)], int(m4.group(1)))
        return d, d
    # month only
    m5 = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", t)
    if m5:
        d = "%d-%02d-01" % (year, MONTHS[m5.group(1)])
        return d, d
    return None, None

def extract_city(name):
    m = re.search(r"\(([^)]*)\)", name)
    if not m:
        return ""
    t = m.group(1)
    first = t.split(",")[0].strip()
    if re.match(r"^\d", first) or not first:
        return ""
    return first

def geocode(city):
    c = city.lower()
    for k, v in CITY_COORDS.items():
        if k in c or c in k:
            return v
    return None

rows = []
with open(CSV, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        iso = r["deadline_iso"].strip()
        days = None
        if iso:
            try:
                days = (datetime.date.fromisoformat(iso) - TODAY).days
            except ValueError:
                days = None
        name = clean(r["name"])
        s, e = parse_dates(name)
        city = extract_city(name)
        geo = geocode(city) if city else None
        low = (name + " " + r["url"]).lower()
        rows.append({
            "category": clean(r["category"]),
            "name": name,
            "desc": clean(r["description"]),
            "deadlineText": clean(r["deadline_text"]),
            "deadline": iso,
            "days": days,
            "members": [m.strip() for m in clean(r["members"]).split(",") if m.strip()],
            "url": r["url"].strip(),
            "start": s, "end": e,
            "city": city,
            "lat": geo[0] if geo else None,
            "lon": geo[1] if geo else None,
            "flag": "low" if any(p in low for p in PREDATORY) else "",
            "rolling": iso == "",
        })

CANON = ["Benard","Patience","Patrick","Ashalley","Ellen","Seth","Awuley","Abdul Rahman",
         "Jonathan","Joseph","Ashraf","Ahmed","Adonu","Kidibe","Justice","Collins","Mark",
         "David","Isaac","Eugene","Quarshie","Martin","Abavare","Donkor","Agyemang","Eghan","Addo","Menkah"]
for r in rows:
    joined = " ".join(r["members"]).lower()
    r["people"] = [p for p in CANON if p.lower() in joined]
    r["openAll"] = any(m.lower().startswith("all") for m in r["members"])
    r["rate"] = next((v for k, v in RATES.items() if k in r["name"]), "")

cats = sorted({r["category"] for r in rows})
members = [p for p in CANON if any(p in r["people"] for r in rows)]
cities = sorted({r["city"] for r in rows if r["city"]})
data = {"generated": TODAY.isoformat(), "rows": rows, "categories": cats,
        "members": members, "cities": cities, "elig": ELIG}

TEMPLATE = r"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MCP KNUST — Opportunities Dashboard</title>
<meta name="description" content="Interactive dashboard of workshops, conferences and grants for the Mathematical & Computational Physics unit, KNUST.">
<meta property="og:title" content="MCP KNUST — Opportunities Dashboard">
<meta property="og:description" content="Workshops, conferences and grants matched to MCP members.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%236ea8fe'/%3E%3Ctext x='16' y='22' font-size='16' font-family='sans-serif' font-weight='700' text-anchor='middle' fill='%230b1020'%3EM%3C/text%3E%3C/svg%3E">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#0b1020">
<style>
:root{
  --bg:#0b1020; --bg2:#111834; --card:#151d3b; --card2:#1b2547; --line:#26305a;
  --fg:#e8ecff; --mut:#9aa6d4; --acc:#6ea8fe; --acc2:#7ef0d0; --warn:#ffcf6e; --bad:#ff8a8a;
  --grad:linear-gradient(120deg,#6ea8fe,#7ef0d0 45%,#b39dff);
  --shadow:0 10px 30px rgba(0,0,0,.35);
  --c-quantum:#6ea8fe; --c-materials:#7ef0d0; --c-energy:#ffcf6e; --c-seismo:#8ab4ff;
  --c-astro:#b39dff; --c-africa:#ff9ecb; --c-grants:#8ef0a8;
}
html[data-theme="light"]{
  --bg:#f6f8ff; --bg2:#eef2ff; --card:#ffffff; --card2:#f2f5ff; --line:#dde3f5;
  --fg:#131a33; --mut:#5a6690; --acc:#2f6bff; --acc2:#0aa88a; --warn:#b7791f; --bad:#c0392b;
  --shadow:0 10px 30px rgba(30,50,120,.12);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Inter,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
a{color:var(--acc);text-decoration:none}
a:hover{text-decoration:underline}
mark{background:var(--acc2);color:#08122b;border-radius:3px;padding:0 2px}
.wrap{max-width:1200px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:60;backdrop-filter:blur(10px);
  background:color-mix(in srgb,var(--bg) 78%,transparent);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:12px;height:60px;min-width:0}
.brand{font-weight:800;letter-spacing:.2px;white-space:nowrap;flex:0 0 auto}
.brand span{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.pill{margin-left:auto;font-size:13px;border:1px solid var(--line);background:var(--card);
  padding:6px 12px;border-radius:999px;color:var(--mut);white-space:nowrap;
  min-width:0;overflow:hidden;text-overflow:ellipsis;flex-shrink:1}
.top .btn{flex:0 0 auto}
.pill b{color:var(--warn)}
.spacer{flex:1}
.btn{cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--fg);
  padding:8px 12px;border-radius:10px;font:inherit;transition:transform .15s ease,background .2s}
.btn:hover{transform:translateY(-1px);background:var(--card2)}
.btn:active{transform:translateY(0) scale(.98)}
.hero{position:relative;overflow:hidden;padding:64px 0 36px;border-bottom:1px solid var(--line)}
#stars{position:absolute;inset:0;width:100%;height:100%;z-index:0;opacity:.7}
.hero::before{content:"";position:absolute;inset:-40% -20%;background:
  radial-gradient(40% 40% at 20% 30%,rgba(110,168,254,.35),transparent 60%),
  radial-gradient(35% 35% at 80% 20%,rgba(126,240,208,.28),transparent 60%),
  radial-gradient(45% 45% at 60% 80%,rgba(179,157,255,.28),transparent 60%);
  filter:blur(20px);animation:drift 18s ease-in-out infinite alternate;z-index:0}
@keyframes drift{from{transform:translate3d(-3%,-2%,0) scale(1)}to{transform:translate3d(3%,2%,0) scale(1.08)}}
.hero .wrap{position:relative;z-index:1}
h1{font-size:clamp(28px,5vw,52px);line-height:1.05;margin:0 0 10px;font-weight:850}
h1 em{font-style:normal;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.lede{color:var(--mut);max-width:70ch;margin:0 0 22px}
.stats{display:flex;gap:26px;flex-wrap:wrap}
.stat b{display:block;font-size:30px;font-weight:850}
.stat span{color:var(--mut);font-size:13px;text-transform:uppercase;letter-spacing:.08em}
.controls{position:sticky;top:60px;z-index:50;background:color-mix(in srgb,var(--bg) 85%,transparent);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:12px 0}
.controls .wrap{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
input[type=search],select{background:var(--card);border:1px solid var(--line);color:var(--fg);
  padding:9px 12px;border-radius:10px;font:inherit;min-width:140px}
input[type=search]{flex:1;min-width:200px}
.seg{display:flex;border:1px solid var(--line);border-radius:10px;overflow:hidden}
.seg button{background:var(--card);border:0;color:var(--mut);padding:9px 14px;cursor:pointer;font:inherit}
.seg button[aria-pressed=true]{background:var(--card2);color:var(--fg)}
.count{color:var(--mut);font-size:13px;margin-left:auto}
section{padding:30px 0}
h2{font-size:22px;margin:0 0 16px}
.urgent{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(min(240px,100%),1fr);gap:14px;
  overflow-x:auto;padding-bottom:8px;scroll-snap-type:x mandatory}
.ucard{scroll-snap-align:start;background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:14px;min-width:240px;box-shadow:var(--shadow)}
.ucard .cd{font-variant-numeric:tabular-nums;font-weight:800;color:var(--warn)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:16px}
.ghead{grid-column:1/-1;position:sticky;top:118px;z-index:20;background:var(--bg);
  padding:8px 0;font-weight:800;font-size:15px;border-bottom:1px solid var(--line);margin-top:6px}
.card{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;
  box-shadow:var(--shadow);display:flex;flex-direction:column;gap:10px;
  opacity:0;transform:translateY(14px);transition:opacity .5s ease,transform .5s ease,box-shadow .2s}
.card.in{opacity:1;transform:none}
.card:hover{transform:translateY(-3px);box-shadow:0 16px 40px rgba(0,0,0,.4)}
.card.low{opacity:.72;border-style:dashed}
.badge{display:inline-block;font-size:11px;letter-spacing:.04em;text-transform:uppercase;
  padding:3px 9px;border-radius:999px;border:1px solid var(--line);color:var(--mut);background:var(--card2)}
.badge.cat{border-color:transparent;color:#08122b;font-weight:700}
.warnbadge{font-size:11px;padding:3px 9px;border-radius:999px;background:var(--bad);color:#2a0b0b;font-weight:700}
.card h3{margin:0;font-size:17px;line-height:1.25;overflow-wrap:anywhere}
.card p{margin:0;color:var(--mut);font-size:14px;overflow-wrap:anywhere}
.meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:13px;color:var(--mut)}
.dl{font-weight:700;color:var(--fg)}
.dl.soon{color:var(--warn)} .dl.past{color:var(--bad);text-decoration:line-through}
.ubar{height:4px;border-radius:2px;background:var(--card2);overflow:hidden}
.ubar i{display:block;height:100%;background:var(--grad)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font-size:12px;padding:2px 8px;border-radius:999px;background:var(--card2);border:1px solid var(--line);cursor:pointer}
.chip:hover{border-color:var(--acc)}
.acts{display:flex;gap:8px;flex-wrap:wrap;margin-top:2px}
.acts a,.acts button{font-size:12px;padding:4px 9px;border-radius:8px;border:1px solid var(--line);
  background:var(--card2);color:var(--fg);cursor:pointer}
.timeline{display:flex;flex-direction:column;gap:6px}
.trow{display:grid;grid-template-columns:170px 1fr;gap:10px;align-items:center;font-size:13px}
.track{background:var(--card2);border-radius:7px;position:relative;height:16px}
.tbar{position:absolute;top:2px;bottom:2px;border-radius:6px;background:var(--grad);opacity:.9}
.track .now{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--bad)}
.tgrid{position:absolute;top:0;bottom:0;width:1px;background:var(--line);opacity:.6}
.mapwrap{display:grid;grid-template-columns:1fr 260px;gap:20px}
@media(max-width:760px){.mapwrap{grid-template-columns:1fr}}
svg.world{width:100%;height:auto;background:var(--card);border:1px solid var(--line);border-radius:14px}
.citylist{display:flex;flex-direction:column;gap:6px;max-height:420px;overflow:auto}
.cityrow{display:flex;justify-content:space-between;gap:8px;font-size:13px;cursor:pointer;
  padding:5px 8px;border-radius:8px;border:1px solid transparent}
.cityrow:hover{border-color:var(--acc);background:var(--card2)}
.members{display:flex;gap:8px;flex-wrap:wrap}
.mchip{padding:6px 12px;border-radius:999px;border:1px solid var(--line);background:var(--card);cursor:pointer;font-size:13px}
.mchip:hover{border-color:var(--acc);transform:translateY(-1px)}
.mchip[aria-pressed=true]{background:var(--grad);color:#08122b;border-color:transparent;font-weight:700}
.elig{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:var(--shadow)}
.elig .row{display:flex;gap:12px;flex-wrap:wrap;align-items:end;margin-bottom:14px}
.elig label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--mut)}
.elig input,.elig select{background:var(--card2);border:1px solid var(--line);color:var(--fg);
  padding:8px 10px;border-radius:9px;font:inherit}
.eligout{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(260px,100%),1fr));gap:10px}
.erow{border:1px solid var(--line);border-radius:10px;padding:10px;font-size:13px;background:var(--card2)}
.erow.no{opacity:.5}
.erow .why{color:var(--bad);font-size:12px}
.empty{color:var(--mut);padding:30px 0}
.mpanel{background:var(--card);border:1px solid var(--acc);border-radius:16px;padding:18px;box-shadow:var(--shadow)}
.mphead{display:flex;align-items:center;gap:12px}
.mphead h2{margin:0}
.mphead .btn{margin-left:auto}
#mpGrid{margin-top:14px}
footer{border-top:1px solid var(--line);color:var(--mut);padding:26px 0;font-size:13px}
.reveal{opacity:0;transform:translateY(16px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}
.skel{height:120px;border-radius:16px;background:linear-gradient(90deg,var(--card),var(--card2),var(--card));
  background-size:200% 100%;animation:sh 1.2s linear infinite}
@keyframes sh{from{background-position:200% 0}to{background-position:-200% 0}}
@media (max-width:640px){
  .wrap{padding:0 14px}
  .pill{display:none}
  .controls{position:static}
  .controls .wrap{gap:8px}
  input[type=search],select{min-width:0;flex:1 1 44%}
  .seg{flex:1 1 100%}
  .seg button{flex:1}
  .count{flex:1 1 100%;margin-left:0}
  .trow{grid-template-columns:96px 1fr;font-size:12px}
  .hero{padding:44px 0 28px}
  .stats{gap:16px}
  .stat b{font-size:24px}
  .urgent{grid-auto-columns:minmax(210px,1fr)}
  .grid{grid-template-columns:1fr}
  .eligout{grid-template-columns:1fr}
  .ghead{top:auto;position:static}
}
@media print{
  header.top,.controls,.urgent,.elig,.members,#stars{display:none!important}
  body{background:#fff;color:#000}.card{break-inside:avoid;box-shadow:none;border:1px solid #ccc}
}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important}
  .card,.reveal{opacity:1!important;transform:none!important}
  html{scroll-behavior:auto}
}
</style>
</head>
<body>
<header class="top"><div class="wrap">
  <div class="brand">MCP <span>KNUST</span></div>
  <div class="pill" id="nextPill">next deadline: —</div>
  <a class="btn" href="mcp-deadlines.ics" download title="Download all deadlines">.ics</a>
  <button class="btn" id="theme" title="Theme: dark / light / auto">◐</button>
</div></header>

<section class="hero"><canvas id="stars"></canvas><div class="wrap">
  <h1>Opportunities for <em>Mathematical &amp; Computational Physics</em></h1>
  <p class="lede">Workshops, conferences and grants matched to MCP members. Filter by person, theme, deadline or place. Companion to the 77-page report.</p>
  <div class="stats">
    <div class="stat"><b data-count="__NROWS__">0</b><span>opportunities</span></div>
    <div class="stat"><b data-count="__NDATED__">0</b><span>dated deadlines</span></div>
    <div class="stat"><b data-count="__NMEM__">0</b><span>members</span></div>
    <div class="stat"><b data-count="__N90__">0</b><span>next 90 days</span></div>
  </div>
</div></section>

<div class="controls"><div class="wrap">
  <input type="search" id="q" placeholder="Search (press /)…" aria-label="Search">
  <input type="search" id="msearch" list="mlist" placeholder="Member…" aria-label="Search by member" autocomplete="off">
  <datalist id="mlist"></datalist>
  <select id="cat" aria-label="Theme"><option value="">All themes</option></select>
  <select id="win" aria-label="Deadline window">
    <option value="">Any deadline</option>
    <option value="90">Next 90 days</option>
    <option value="180">Next 6 months</option>
    <option value="365">Next 12 months</option>
    <option value="dated">Dated only</option>
    <option value="rolling">Rolling / watch</option>
  </select>
  <select id="sort" aria-label="Sort">
    <option value="deadline">Sort: deadline</option>
    <option value="name">Sort: name</option>
    <option value="category">Sort: theme</option>
  </select>
  <div class="seg" role="group" aria-label="View">
    <button id="vCards" aria-pressed="true">Cards</button>
    <button id="vTime" aria-pressed="false">Timeline</button>
    <button id="vMap" aria-pressed="false">Map</button>
  </div>
  <button class="btn" id="group" aria-pressed="false" title="Group by theme">Group</button>
  <button class="btn" id="reset">Reset</button>
  <span class="count" id="count" aria-live="polite"></span>
</div></div>

<section class="wrap reveal"><h2>Next 90 days</h2><div class="urgent" id="urgent"></div></section>

<section class="wrap" id="memberPanel" hidden><div class="mpanel">
  <div class="mphead"><h2 id="mpTitle">Action list</h2>
    <button class="btn" id="mpClear">clear</button></div>
  <p class="lede" id="mpSub"></p>
  <div class="grid" id="mpGrid"></div>
</div></section>

<main class="wrap"><section>
  <h2 id="listTitle">All opportunities</h2>
  <div class="grid" id="grid"></div>
  <div class="timeline" id="timeline" hidden></div>
  <div class="mapwrap" id="mapwrap" hidden>
    <svg class="world" id="world" viewBox="0 0 720 360" role="img" aria-label="World map of venues"></svg>
    <div class="citylist" id="citylist"></div>
  </div>
  <div class="empty" id="empty" hidden>No matches. Try clearing filters.</div>
</section></main>

<section class="wrap reveal"><h2>Grant eligibility checker</h2>
  <div class="elig">
    <div class="row">
      <label>Career stage
        <select id="eStage"><option value="">any</option><option>Student</option><option>Postdoc</option><option>Staff</option></select>
      </label>
      <label>Years since PhD
        <input id="eYears" type="number" min="0" max="40" placeholder="e.g. 3">
      </label>
      <label>Age
        <input id="eAge" type="number" min="16" max="80" placeholder="e.g. 32">
      </label>
      <label>Region
        <select id="eRegion"><option value="">any</option><option>Africa</option><option>Europe</option><option>Other</option></select>
      </label>
      <button class="btn" id="eRun">Check</button>
    </div>
    <div class="eligout" id="eligout"></div>
  </div>
</section>

<section class="wrap reveal"><h2>Members</h2><div class="members" id="members"></div></section>

<footer><div class="wrap">
  <p>Data as of <b id="asof">__GEN__</b> · <a href="mcp-knust-workshops-report.pdf">Full report (PDF)</a> · <a href="mcp-deadlines.ics">Calendar (.ics)</a> · <a href="mcp-opportunities.csv">CSV</a></p>
  <p>Deadlines decay — verify on the linked page before applying. Compiled by the opencode online-research pipeline.</p>
</div></footer>

<script>
const DATA = __DATA__;
const $ = s => document.querySelector(s);
const state = {q:"", cat:"", win:"", member:"", city:"", sort:"deadline", view:"cards", group:false};

/* ---------- theme (dark/light/auto) ---------- */
const root = document.documentElement;
const modes = ["dark","light","auto"];
let mode = localStorage.getItem("mcp-theme") || "dark";
function applyTheme(){
  const sys = matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  root.dataset.theme = mode === "auto" ? sys : mode;
  $("#theme").textContent = mode === "dark" ? "◐" : mode === "light" ? "◑" : "◓";
}
applyTheme();
$("#theme").onclick = () => { mode = modes[(modes.indexOf(mode)+1)%3]; localStorage.setItem("mcp-theme", mode); applyTheme(); };

/* ---------- hero constellation ---------- */
(function(){
  const c = $("#stars"); if(!c) return;
  const reduce = matchMedia("(prefers-reduced-motion:reduce)").matches;
  const ctx = c.getContext("2d"); let W,H,pts;
  function size(){ W=c.width=c.offsetWidth; H=c.height=c.offsetHeight;
    pts = Array.from({length: Math.min(70, Math.round(W/18))}, () => ({
      x:Math.random()*W, y:Math.random()*H, vx:(Math.random()-.5)*.25, vy:(Math.random()-.5)*.25 })); }
  function draw(){
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle = getComputedStyle(root).getPropertyValue("--acc").trim() || "#6ea8fe";
    for(const p of pts){ ctx.globalAlpha=.5; ctx.beginPath(); ctx.arc(p.x,p.y,1.4,0,7); ctx.fill(); }
    ctx.globalAlpha=.12; ctx.strokeStyle = ctx.fillStyle;
    for(let i=0;i<pts.length;i++) for(let j=i+1;j<pts.length;j++){
      const a=pts[i],b=pts[j],d=Math.hypot(a.x-b.x,a.y-b.y);
      if(d<110){ ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke(); } }
    ctx.globalAlpha=1;
    if(!reduce) for(const p of pts){ p.x+=p.vx; p.y+=p.vy;
      if(p.x<0||p.x>W)p.vx*=-1; if(p.y<0||p.y>H)p.vy*=-1; }
  }
  size(); draw(); addEventListener("resize", ()=>{size();draw();});
  if(!reduce) setInterval(draw, 60);
})();

/* ---------- helpers ---------- */
const CATCOLOR = {
  "QUANTUM SCIENCE & TECHNOLOGY":"--c-quantum","MATERIALS MODELLING & MOF/DFT":"--c-materials",
  "ENERGY, WATER & DIGITAL TWINS":"--c-energy","SEISMOLOGY, GEOSCIENCE & OCEAN":"--c-seismo",
  "ASTROPHYSICS":"--c-astro","AFRICAN PHYSICS, MATH & GENERAL":"--c-africa","GRANTS & FELLOWSHIPS":"--c-grants"};
function catColor(c){ return "var("+(CATCOLOR[c]||"--acc")+")"; }
function esc(s){ return (s||"").replace(/[&<>"]/g, m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m])); }
function hl(text, q){
  if(!q) return esc(text);
  const i = text.toLowerCase().indexOf(q.toLowerCase());
  if(i<0) return esc(text);
  return esc(text.slice(0,i))+"<mark>"+esc(text.slice(i,i+q.length))+"</mark>"+esc(text.slice(i+q.length));
}
function fmtDate(iso){ return iso ? new Date(iso+"T00:00:00").toLocaleDateString("en-GB",{day:"2-digit",month:"short",year:"numeric"}) : "rolling / watch"; }
function dlClass(r){ if(r.days===null) return ""; if(r.days<0) return "past"; if(r.days<=45) return "soon"; return ""; }
function gcalURL(r){
  const d = (r.deadline||"").replace(/-/g,"");
  const dates = d ? d+"/"+d : "";
  const p = new URLSearchParams({action:"TEMPLATE", text:r.name, details:r.desc, location:r.city||""});
  if(dates) p.set("dates", dates);
  return "https://calendar.google.com/calendar/render?"+p.toString();
}
function icsURL(r){
  const d = (r.deadline||"").replace(/-/g,"");
  const body = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//MCP KNUST//EN","BEGIN:VEVENT",
    "UID:"+encodeURIComponent(r.name).slice(0,40)+"@knust","DTSTAMP:20261016T000000Z",
    d?("DTSTART;VALUE=DATE:"+d):"", "SUMMARY:"+r.name.replace(/[,;]/g," "),
    "DESCRIPTION:"+r.desc.replace(/[,;]/g," "), r.url?("URL:"+r.url):"","END:VEVENT","END:VCALENDAR"]
    .filter(Boolean).join("\r\n");
  return "data:text/calendar;charset=utf-8,"+encodeURIComponent(body);
}

/* ---------- filtering ---------- */
function matches(r){
  if (state.cat && r.category !== state.cat) return false;
  if (state.member && !r.people.includes(state.member) && !r.openAll) return false;
  if (state.city && r.city !== state.city) return false;
  if (state.q){
    const hay = (r.name+" "+r.desc+" "+r.category+" "+r.people.join(" ")+" "+r.city+" "+(r.deadline?fmtDate(r.deadline):"rolling watch")).toLowerCase();
    if (!hay.includes(state.q.toLowerCase())) return false;
  }
  if (state.win === "dated" && r.days === null) return false;
  if (state.win === "rolling" && r.days !== null) return false;
  if (["90","180","365"].includes(state.win)){
    if (r.days === null || r.days < 0 || r.days > +state.win) return false;
  }
  return true;
}
function sortRows(rows){
  const s = state.sort;
  return rows.slice().sort((a,b)=>{
    if(s==="name") return a.name.localeCompare(b.name);
    if(s==="category") return a.category.localeCompare(b.category) || (a.deadline||"z").localeCompare(b.deadline||"z");
    const ad = a.deadline||"9999", bd = b.deadline||"9999";
    return ad.localeCompare(bd);
  });
}

/* ---------- card ---------- */
function card(r){
  const el = document.createElement("article");
  el.className = "card" + (r.flag==="low" ? " low" : "");
  const dl = r.days===null ? "rolling / watch" : fmtDate(r.deadline) + (r.days>=0 ? " · in "+r.days+"d" : " · passed");
  const pct = r.days===null ? 0 : Math.max(2, Math.min(100, 100 - (r.days/365)*100));
  el.innerHTML = `
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
      <span class="badge cat" style="background:${catColor(r.category)}">${esc(r.category)}</span>
      ${r.flag==="low"?'<span class="warnbadge" title="Aggregator/predatory indicators — verify before paying">low confidence</span>':""}
      ${r.city?`<span class="badge">${esc(r.city)}</span>`:""}
      ${r.rate?`<span class="badge" title="Acceptance rate">${esc(r.rate)}</span>`:""}
    </div>
    <h3>${r.url?`<a href="${r.url}" target="_blank" rel="noopener">${hl(r.name,state.q)}</a>`:hl(r.name,state.q)}</h3>
    <p>${hl(r.desc,state.q)}</p>
    <div class="meta"><span class="dl ${dlClass(r)}">${dl}</span></div>
    <div class="ubar"><i style="width:${pct}%"></i></div>
    <div class="chips">${(r.people.length?r.people:["All"]).map(m=>`<span class="chip" data-m="${esc(m)}">${esc(m)}</span>`).join("")}</div>
    <div class="acts">
      ${r.deadline?`<a href="${gcalURL(r)}" target="_blank" rel="noopener">+ Google Cal</a>`:""}
      ${r.deadline?`<a href="${icsURL(r)}" download="event.ics">+ .ics</a>`:""}
      ${r.url?`<a href="${r.url}" target="_blank" rel="noopener">open ↗</a>`:""}
    </div>`;
  el.querySelectorAll(".chip").forEach(c => c.onclick = () => { setMember(c.dataset.m); window.scrollTo({top:0,behavior:"smooth"}); });
  return el;
}

/* ---------- render ---------- */
function render(){
  const rows = sortRows(DATA.rows.filter(matches));
  const grid = $("#grid"), tl = $("#timeline"), mw = $("#mapwrap");
  $("#count").textContent = rows.length + " shown";
  $("#listTitle").textContent = state.view==="cards" ? "Opportunities" : state.view==="timeline" ? "Timeline" : "Venues";
  $("#empty").hidden = rows.length>0;
  grid.hidden = state.view!=="cards"; tl.hidden = state.view!=="timeline"; mw.hidden = state.view!=="map";

  if (state.view==="cards"){
    grid.innerHTML = "";
    if (state.group){
      const byCat = {};
      rows.forEach(r => (byCat[r.category] = byCat[r.category]||[]).push(r));
      Object.keys(byCat).sort().forEach(cat => {
        const h = document.createElement("div"); h.className="ghead"; h.textContent = cat+" ("+byCat[cat].length+")";
        h.style.color = catColor(cat); grid.appendChild(h);
        byCat[cat].forEach((r,i)=>{ const c=card(r); c.style.transitionDelay=Math.min(i*18,300)+"ms"; grid.appendChild(c); });
      });
    } else {
      rows.forEach((r,i)=>{ const c=card(r); c.style.transitionDelay=Math.min(i*18,400)+"ms"; grid.appendChild(c); });
    }
    requestAnimationFrame(()=>grid.querySelectorAll(".card").forEach(c=>c.classList.add("in")));
  } else if (state.view==="timeline"){
    const dated = rows.filter(r=>r.start||r.deadline);
    const pts = dated.map(r=>({r, s:r.start||r.deadline, e:r.end||r.deadline||r.start}));
    if(!pts.length){ tl.innerHTML = '<div class="empty">No dated items in this filter.</div>'; return; }
    const min = Math.min(...pts.map(p=>new Date(p.s).getTime()));
    const max = Math.max(...pts.map(p=>new Date(p.e).getTime()));
    const span = Math.max(1, max-min);
    const nowPct = Math.min(100, Math.max(0, ((Date.now()-min)/span)*100));
    const months = [];
    let d = new Date(min); d.setDate(1);
    while(d.getTime() <= max){ months.push(new Date(d)); d.setMonth(d.getMonth()+1); }
    const gridlines = months.map(m=>`<div class="tgrid" style="left:${((m.getTime()-min)/span)*100}%"></div>`).join("");
    tl.innerHTML = pts.sort((a,b)=>a.s.localeCompare(b.s)).map(p=>{
      const l = ((new Date(p.s).getTime()-min)/span)*100;
      const w = Math.max(1.5, ((new Date(p.e).getTime()-new Date(p.s).getTime())/span)*100);
      return `<div class="trow"><div title="${esc(p.r.name)}">${esc(p.r.name.slice(0,30))}</div>
        <div class="track">${gridlines}<div class="tbar" style="left:${l}%;width:${w}%"></div>
        <div class="now" style="left:${nowPct}%"></div></div></div>`;
    }).join("");
  } else {
    renderMap(rows);
  }
}

/* ---------- map ---------- */
function renderMap(rows){
  const svg = $("#world");
  const W=720,H=360;
  const proj = (lat,lon)=>[ (lon+180)/360*W, (90-lat)/180*H ];
  let g = "";
  for(let lon=-180; lon<=180; lon+=30){ const x=proj(0,lon)[0]; g+=`<line x1="${x}" y1="0" x2="${x}" y2="${H}" stroke="var(--line)" stroke-width=".5" opacity=".5"/>`; }
  for(let lat=-60; lat<=60; lat+=30){ const y=proj(lat,0)[1]; g+=`<line x1="0" y1="${y}" x2="${W}" y2="${y}" stroke="var(--line)" stroke-width=".5" opacity=".5"/>`; }
  const byCity = {};
  rows.filter(r=>r.lat!=null).forEach(r=>{ (byCity[r.city]=byCity[r.city]||[]).push(r); });
  let dots = "";
  Object.entries(byCity).forEach(([city, rs])=>{
    const [x,y] = proj(rs[0].lat, rs[0].lon);
    const rad = 3 + Math.min(9, rs.length*1.6);
    dots += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${rad}" fill="${catColor(rs[0].category)}" opacity=".8"><title>${esc(city)} — ${rs.length} event(s)</title></circle>`;
    dots += `<text x="${(x+rad+3).toFixed(1)}" y="${(y+3).toFixed(1)}" font-size="9" fill="var(--mut)">${esc(city)}</text>`;
  });
  svg.innerHTML = g + dots;
  const counts = Object.entries(byCity).sort((a,b)=>b[1].length-a[1].length);
  $("#citylist").innerHTML = counts.map(([city,rs])=>
    `<div class="cityrow" data-city="${esc(city)}"><span>${esc(city)}</span><b>${rs.length}</b></div>`).join("")
    || '<div class="empty">No geocoded venues in this filter.</div>';
  $("#citylist").querySelectorAll(".cityrow").forEach(el => el.onclick = () => {
    state.city = state.city===el.dataset.city ? "" : el.dataset.city; render();
  });
}

/* ---------- urgent strip ---------- */
function renderUrgent(){
  const soon = DATA.rows.filter(r=>r.days!==null && r.days>=0 && r.days<=90).sort((a,b)=>a.days-b.days).slice(0,12);
  $("#urgent").innerHTML = soon.map(r=>`
    <div class="ucard"><span class="badge cat" style="background:${catColor(r.category)}">${esc(r.category)}</span>
      <h3 style="margin:8px 0 4px;font-size:15px">${r.url?`<a href="${r.url}" target="_blank" rel="noopener">${esc(r.name)}</a>`:esc(r.name)}</h3>
      <div class="cd">${r.days===0?"today":"in "+r.days+" days"}</div>
      <div class="meta">${fmtDate(r.deadline)}</div></div>`).join("");
  const nxt = soon[0];
  if(nxt) $("#nextPill").innerHTML = `next: <b>${esc(nxt.name.slice(0,34))}</b> · ${nxt.days}d`;
}

/* ---------- members ---------- */
function syncMember(){ document.querySelectorAll(".mchip").forEach(c=>c.setAttribute("aria-pressed", c.dataset.m===state.member)); }
function renderMembers(){
  $("#members").innerHTML = DATA.members.map(m=>`<button class="mchip" data-m="${esc(m)}" aria-pressed="false">${esc(m)}</button>`).join("");
  document.querySelectorAll(".mchip").forEach(c=>c.onclick=()=>{
    setMember(state.member===c.dataset.m ? "" : c.dataset.m);
  });
}

/* ---------- eligibility ---------- */
function renderElig(){
  const stage=$("#eStage").value, years=parseFloat($("#eYears").value), age=parseFloat($("#eAge").value), region=$("#eRegion").value;
  const grants = DATA.rows.filter(r=>r.category==="GRANTS & FELLOWSHIPS");
  $("#eligout").innerHTML = grants.map(r=>{
    let rule=null; for(const k in DATA.elig){ if(r.name.includes(k)){ rule=DATA.elig[k]; break; } }
    let ok=true, why=[];
    if(rule){
      if(rule.stages && stage && !rule.stages.includes(stage)){ ok=false; why.push("stage: "+rule.stages.join("/")); }
      if(rule.maxAge && !isNaN(age) && age>rule.maxAge){ ok=false; why.push("age > "+rule.maxAge); }
      if(rule.maxYearsPhD && !isNaN(years) && years>rule.maxYearsPhD){ ok=false; why.push("> "+rule.maxYearsPhD+" yr since PhD"); }
      if(rule.region && region && rule.region!==region){ ok=false; why.push("region: "+rule.region); }
    }
    return `<div class="erow ${ok?"":"no"}"><b>${esc(r.name)}</b>
      <div class="why">${ok?(rule?("ok — "+esc(rule.note)):"no specific rule — check criteria"):("excluded — "+esc(why.join("; ")))}</div></div>`;
  }).join("");
}

/* ---------- URL state ---------- */
function readURL(){
  const p = new URLSearchParams(location.search);
  state.q=p.get("q")||""; state.cat=p.get("cat")||""; state.win=p.get("win")||"";
  state.member=p.get("member")||""; state.city=p.get("city")||""; state.sort=p.get("sort")||"deadline";
  state.view=p.get("view")||"cards"; state.group=p.get("group")==="1";
  $("#q").value=state.q; $("#cat").value=state.cat; $("#win").value=state.win; $("#sort").value=state.sort;
  $("#group").setAttribute("aria-pressed", state.group);
  $("#vCards").setAttribute("aria-pressed", state.view==="cards");
  $("#vTime").setAttribute("aria-pressed", state.view==="timeline");
  $("#vMap").setAttribute("aria-pressed", state.view==="map");
}
function writeURL(){
  const p = new URLSearchParams();
  if(state.q)p.set("q",state.q); if(state.cat)p.set("cat",state.cat); if(state.win)p.set("win",state.win);
  if(state.member)p.set("member",state.member); if(state.city)p.set("city",state.city);
  if(state.sort!=="deadline")p.set("sort",state.sort); if(state.view!=="cards")p.set("view",state.view);
  if(state.group)p.set("group","1");
  history.replaceState(null,"", location.pathname + (p.toString()?"?"+p:""));
}

/* ---------- events ---------- */
function update(){ writeURL(); render(); }
$("#q").oninput = e => { state.q = e.target.value; update(); };
$("#cat").onchange = e => { state.cat = e.target.value; update(); };
$("#win").onchange = e => { state.win = e.target.value; update(); };
$("#sort").onchange = e => { state.sort = e.target.value; update(); };
$("#group").onclick = () => { state.group=!state.group; $("#group").setAttribute("aria-pressed",state.group); update(); };
$("#reset").onclick = () => { Object.assign(state,{q:"",cat:"",win:"",member:"",city:"",sort:"deadline",view:"cards",group:false});
  $("#q").value="";$("#cat").value="";$("#win").value="";$("#sort").value="deadline";$("#group").setAttribute("aria-pressed","false");
  $("#msearch").value=""; $("#memberPanel").hidden=true;
  $("#vCards").setAttribute("aria-pressed","true");$("#vTime").setAttribute("aria-pressed","false");$("#vMap").setAttribute("aria-pressed","false");
  syncMember(); update(); };
function setView(v){ state.view=v;
  $("#vCards").setAttribute("aria-pressed",v==="cards"); $("#vTime").setAttribute("aria-pressed",v==="timeline"); $("#vMap").setAttribute("aria-pressed",v==="map");
  update(); }
$("#vCards").onclick=()=>setView("cards"); $("#vTime").onclick=()=>setView("timeline"); $("#vMap").onclick=()=>setView("map");
$("#eRun").onclick = renderElig;
["eStage","eYears","eAge","eRegion"].forEach(id=>$("#"+id).oninput = renderElig);
addEventListener("keydown", e=>{
  if(e.key==="/" && document.activeElement!==$("#q")){ e.preventDefault(); $("#q").focus(); }
  if(e.key==="Escape"){ $("#q").value=""; state.q=""; update(); }
});

/* ---------- member search + personalized action list ---------- */
function memberRows(name){
  return DATA.rows.filter(r => r.people.includes(name) || r.openAll)
    .sort((a,b)=> (a.deadline||"9999").localeCompare(b.deadline||"9999"));
}
function renderMemberPanel(){
  const name = state.member;
  const panel = $("#memberPanel");
  if(!name){ panel.hidden = true; return; }
  panel.hidden = false;
  const rows = memberRows(name);
  const dated = rows.filter(r=>r.days!==null && r.days>=0);
  const urgent = dated.filter(r=>r.days<=45);
  $("#mpTitle").textContent = name + " — action list";
  $("#mpSub").innerHTML = `${rows.length} opportunities · <b>${urgent.length}</b> urgent (≤45 days) · ${dated.length} dated. Sorted by deadline; urgent items first.`;
  const ordered = rows.slice().sort((a,b)=>{
    const au = (a.days!==null && a.days>=0 && a.days<=45)?0:1, bu = (b.days!==null && b.days>=0 && b.days<=45)?0:1;
    if(au!==bu) return au-bu;
    return (a.deadline||"9999").localeCompare(b.deadline||"9999");
  });
  const g = $("#mpGrid"); g.innerHTML = "";
  ordered.forEach((r,i)=>{
    const c=card(r);
    if(r.openAll && !r.people.includes(name)){
      const b=document.createElement("span"); b.className="badge"; b.textContent="open to all";
      c.querySelector("div").appendChild(b);
    }
    c.style.transitionDelay=Math.min(i*18,300)+"ms"; g.appendChild(c);
  });
  requestAnimationFrame(()=>g.querySelectorAll(".card").forEach(c=>c.classList.add("in")));
}
function setMember(name){
  state.member = name || "";
  $("#msearch").value = state.member;
  syncMember(); renderMemberPanel(); update();
}
$("#msearch").oninput = e => {
  const v = e.target.value.trim();
  const hit = DATA.members.find(m => m.toLowerCase() === v.toLowerCase())
           || DATA.members.find(m => m.toLowerCase().startsWith(v.toLowerCase()));
  if (v === "") { setMember(""); }
  else if (hit) { setMember(hit); }
};
$("#mpClear").onclick = () => setMember("");

/* ---------- init ---------- */
DATA.categories.forEach(c => { const o=document.createElement("option"); o.value=c; o.textContent=c; $("#cat").appendChild(o); });
$("#mlist").innerHTML = DATA.members.map(m=>`<option value="${esc(m)}">`).join("");
function countUp(el){ const t=+el.dataset.count, d=900, t0=performance.now();
  if(matchMedia("(prefers-reduced-motion:reduce)").matches){ el.textContent=t; return; }
  (function s(n){ const p=Math.min(1,(n-t0)/d), e=1-Math.pow(1-p,3); el.textContent=Math.round(t*e); if(p<1)requestAnimationFrame(s); })(t0); }
document.querySelectorAll("[data-count]").forEach(countUp);
const io = new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add("in"); io.unobserve(e.target);} }),{threshold:.12});
document.querySelectorAll(".reveal").forEach(el=>io.observe(el));
readURL(); syncMember(); renderUrgent(); renderMembers(); renderElig(); render(); renderMemberPanel();
$("#msearch").value = state.member;
if("serviceWorker" in navigator && location.protocol.startsWith("http")) navigator.serviceWorker.register("sw.js").catch(()=>{});
</script>
</body>
</html>
"""

n90 = sum(1 for r in rows if r["days"] is not None and 0 <= r["days"] <= 90)
ndated = sum(1 for r in rows if r["deadline"])
out = (TEMPLATE
       .replace("__DATA__", json.dumps(data, ensure_ascii=False))
       .replace("__NROWS__", str(len(rows)))
       .replace("__NDATED__", str(ndated))
       .replace("__NMEM__", str(len(members)))
       .replace("__N90__", str(n90))
       .replace("__GEN__", TODAY.isoformat()))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(out)

# PWA manifest + service worker
with open(os.path.join(DIR, "manifest.webmanifest"), "w", encoding="utf-8") as f:
    json.dump({"name":"MCP KNUST Opportunities","short_name":"MCP Opps","start_url":"./index.html",
               "display":"standalone","background_color":"#0b1020","theme_color":"#0b1020",
               "icons":[{"src":"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%236ea8fe'/%3E%3Ctext x='16' y='22' font-size='16' font-family='sans-serif' font-weight='700' text-anchor='middle' fill='%230b1020'%3EM%3C/text%3E%3C/svg%3E","sizes":"any","type":"image/svg+xml"}]}, f)
with open(os.path.join(DIR, "sw.js"), "w", encoding="utf-8") as f:
    f.write("""const C='mcp-v2';
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys()
    .then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k))))
    .then(()=>self.clients.claim()));
});
self.addEventListener('fetch',e=>{
  const req=e.request;
  if(req.method!=='GET' || new URL(req.url).origin!==location.origin) return;
  e.respondWith(
    fetch(req).then(res=>{ const cl=res.clone(); caches.open(C).then(c=>c.put(req,cl)); return res; })
      .catch(()=>caches.match(req).then(r=>r||caches.match('index.html')))
  );
});
""")

# CI workflow
gh = os.path.join(DIR, ".github", "workflows")
os.makedirs(gh, exist_ok=True)
with open(os.path.join(gh, "rebuild.yml"), "w", encoding="utf-8") as f:
    f.write("""name: rebuild-dashboard
on:
  push: {paths: ['mcp-opportunities.csv','build_assets.py','build_site.py']}
  schedule: [{cron: '0 6 1 * *'}]
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: python3 build_assets.py
      - run: python3 build_site.py
      - run: bash check-links.sh || true
      - uses: actions/upload-pages-artifact@v3
        with: {path: '.'}
  deploy:
    needs: build
    permissions: {pages: write, id-token: write}
    environment: {name: github-pages}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
""")

print("wrote index.html | rows:", len(rows), "| dated:", ndated, "| members:", len(members),
      "| next90:", n90, "| cities:", len(cities), "| flagged:", sum(1 for r in rows if r["flag"]))
