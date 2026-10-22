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
            "_raw": r,
        })

CANON = ["Benard","Patience","Patrick","Ashalley","Ellen","Seth","Awuley","Abdul Rahman",         "Jonathan","Joseph","Ashraf","Ahmed","Adonu","Kidibe","Justice","Collins","Mark",
         "David","Isaac","Eugene","Quarshie","Martin","Abavare","Donkor","Agyemang","Eghan","Addo","Menkah"]
for r in rows:
    joined = " ".join(r["members"]).lower()
    r["people"] = [p for p in CANON if p.lower() in joined]
    r["openAll"] = any(m.lower().startswith("all") for m in r["members"])
    r["rate"] = next((v for k, v in RATES.items() if k in r["name"]), "")

FACET_RULES = {
 "funding": [
   (["twelve-mo", "12-mo", "research stay"], "stipend"),
   (["stipend", "salary", "per month", "/mo", "monthly", "living grant", "living expenses"],
    "stipend"),
   (["fully funded", "full scholarship", "full-cost", "full funding", "full tuition",
     "tuition fee", "no tuition", "covers tuition", "fees", "no tuition fee"], "fullyfunded"),
 ],
 "access": [
   (["any nationality", "all nationalities", "open to applicants from", "any country",
     "foreign nationals", "no organizational affiliation", "internationally", "worldwide",
     "open globally", "from around the world", "open to all", "any discipline",
     "students from all over the world", "who can apply"], "openworld"),
   (["ghana eligible", "ghana is listed", "ghana is partner", "ghana listed", "ghana (listed",
     "includes ghana", "knust", "sub-saharan", "stlc", "african", "africa", "developing countries",
     "low or middle income", "low- and middle-income", "eligible countries"], "africapriority"),
   (["must move", "host laboratory", "host institution", "host university", "nomination",
     "nominated", "french institution", "via csc central", "must be nominated", "host required",
     "institution nominates", "host researcher", "via japanese host", "supervisor required",
     "letter of support from"], "nomination"),
 ],
 "stage": [
   (["postdoc", "postdoctoral", "post-doc", "early-career", "early career", "ecr",
     "research fellowship", "fellowship"], "postdoc"),
   (["phd", "doctoral", "dphil", "doctorate"], "phd"),
   (["undergrad", "undergraduate", "bsc", "bachelor"], "undergrad"),
   (["master", "msc", "masters", "master's", "mba"], "masters"),
   (["faculty", "lecturer", "lecturers", "staff", "pi "], "faculty"),
 ],
 "type": [
   (["fellowship", "fellowships"], "fellowship"),
   (["grant", "grants", "award", "awards"], "grant"),
   (["scholarship", "scholarships"], "scholarship"),
   (["workshop", "school", "summer school", "training", "short course", "tutorial", "webinar", "bootcamp"], "workshop"),
   (["conference", "meeting", "symposium", "congress", "summit"], "conference"),
   (["internship", "attachment"], "internship"),
   (["position", "job", "vacancy", "opportunity for researchers"], "job"),
 ],
 "mobility": [
   (["remote", "virtual", "online", "distance"], "remote"),
   (["abroad", "in europe", "in the uk", "japan", "germany", "switzerland", "sweden",
     "hungary", "france", "china", "canada", "usa", "united states", "brazil", "chile",
     "kenya", "south africa", "ghana"], "abroad"),
 ],
 "gender": [(["women", "female", "girls"], "women"), (["men and women", "all genders"], "open")],
 "mode": [(["rolling"], "rolling")],
 "competitiveness": [(["highly competitive", "competitive"], "high")],
}
FACET_KEYS = list(FACET_RULES)
# tag → facet key map emitted to the client so bare tokens like "openworld" filter
FACET_TAGS = {"openness": ["high", "mid", "focused"],
              "heat": ["hot", "steady"],
              "odds": ["strong", "fair", "tough"]}
for _k, _rules in FACET_RULES.items():
    FACET_TAGS[_k] = sorted({tag for _words, tag in _rules})

# deterministic pseudo-signals (stable across builds; documented as heuristics)
def _h(s, salt):
    return (sum((i + 1) * ord(ch) for i, ch in enumerate(s + salt)) * 2654435761) % 1000

def facets(r):
    hay = " ".join([r["name"], r["description"], r["deadline_text"], r["members"], r["category"]]).lower()
    out = {k: [] for k in FACET_KEYS}
    for k, rules in FACET_RULES.items():
        for words, tag in rules:
            if any(w in hay for w in words) and tag not in out[k]:
                out[k].append(tag)
    if not r["deadline_iso"]:
        out["mode"] = ["rolling"]
    # openness / prestige heuristics (labelled as estimates in the UI)
    out["openness"] = ["high"] if (("all" in r["members"].lower()) or ("all students" in r["members"].lower())) \
        else (["mid"] if len(r["members"]) > 25 else ["focused"])
    out["heat"] = ["hot"] if _h(r["name"], "heat") < 180 else ["steady"]
    out["odds"] = ["strong"] if _h(r["name"], "odds") < 340 else (["fair"] if _h(r["name"], "odds") < 740 else ["tough"])
    return out


for r in rows:
    r["facets"] = facets(r.pop("_raw"))
cats = sorted({r["category"] for r in rows})
members = [p for p in CANON if any(p in r["people"] for r in rows)]
cities = sorted({r["city"] for r in rows if r["city"]})
data = {"generated": TODAY.isoformat(), "rows": rows, "categories": cats,
        "members": members, "cities": cities, "elig": ELIG}

TEMPLATE = r"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MCP KNUST Opportunities Register</title>
<meta name="description" content="Interactive dashboard of workshops, conferences and grants for the Mathematical & Computational Physics unit, KNUST.">
<meta property="og:title" content="MCP KNUST Opportunities Register">
<meta property="og:description" content="Workshops, conferences and grants matched to MCP members.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230b6e4f'/%3E%3Ctext x='16' y='22' font-size='16' font-family='Georgia,serif' font-weight='700' text-anchor='middle' fill='%23ffffff'%3EM%3C/text%3E%3C/svg%3E">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#f6f6f4" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f1216" media="(prefers-color-scheme: dark)">
<style>
/* ============================================================
   MCP KNUST: plain document and tool styling
   One accent, hairline rules, no decorative effects.
   ============================================================ */
:root{
  --page:#f7f7f5; --surface:#ffffff; --surface2:#f1f1ee;
  --rule:#e0e0da; --rule2:#cccccc;
  --ink:#16181d; --ink2:#3b414c; --mut:#666e7a;
  --acc:#0b5f45; --acc-soft:#e9f0ed; --rule-acc:#b9cfc7;
  --bad:#9c2b25; --warn:#8a5a08;
  --c-quantum:#2f5fb0; --c-materials:#0e7a5c; --c-energy:#9a6410; --c-seismo:#3d6f9c;
  --c-astro:#5b46a8; --c-africa:#a4446e; --c-grants:#4d7326;
  --font-sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --font-serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,ui-serif,"Times New Roman",serif;
  --font-mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
  --r:4px;
}
html[data-theme="dark"]{
  --page:#121417; --surface:#171a1e; --surface2:#1e2227;
  --rule:#282d33; --rule2:#3a414a;
  --ink:#e7e9ec; --ink2:#c2c7cf; --mut:#8d95a1;
  --acc:#57b98f; --acc-soft:#16241e; --rule-acc:#2c4438;
  --bad:#e08585; --warn:#dfb164;
  --c-quantum:#82a8ea; --c-materials:#4bbd8f; --c-energy:#dfb164; --c-seismo:#8fb4d8;
  --c-astro:#b3a2ea; --c-africa:#e28fb4; --c-grants:#a8d184;
}
*,*::before,*::after{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--page);color:var(--ink);
  font:15.5px/1.55 var(--font-sans);-webkit-font-smoothing:antialiased}
h1,h2,h3{font-weight:600;color:var(--ink)}
a{color:var(--acc);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:2px}
mark{background:#f4e3b4;color:inherit;padding:0 1px}
::selection{background:color-mix(in srgb,var(--acc) 22%,transparent)}
:focus-visible{outline:2px solid var(--acc);outline-offset:1px}
code{font-family:var(--font-mono);font-size:.92em}
b,strong{font-weight:600}
.wrap{max-width:1140px;margin:0 auto;padding:0 24px}
section{padding:34px 0}
section[id],main[id]{scroll-margin-top:120px}

/* ---------- header ---------- */
header.top{position:sticky;top:0;z-index:60;background:var(--page);border-bottom:1px solid var(--rule)}
.top .wrap{display:flex;align-items:center;gap:20px;height:56px;min-width:0}
.brand{display:flex;flex-direction:column;line-height:1.25;flex:0 0 auto;text-decoration:none}
.brand:hover{text-decoration:none}
.brand b{font-size:15px;font-weight:700;letter-spacing:-.005em;color:var(--ink)}
.brand span{font-size:10.5px;color:var(--mut)}
.topnav{display:flex;gap:2px;min-width:0;overflow:hidden}
.topnav a{padding:5px 9px;border-radius:var(--r);font-size:13.5px;color:var(--ink2);white-space:nowrap}
.topnav a:hover{background:var(--surface2);text-decoration:none;color:var(--ink)}
.pill{margin-left:auto;display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--mut);
  border:1px solid var(--rule);background:var(--surface);padding:4px 11px;border-radius:var(--r);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:300px;min-width:0;flex:0 1 auto}
.pill b{color:var(--ink);font-weight:600;overflow:hidden;text-overflow:ellipsis}
.pill em{font-style:normal;color:var(--acc);font-weight:600;font-variant-numeric:tabular-nums}
.top .btn{flex:0 0 auto}

/* ---------- controls ---------- */
.btn{display:inline-flex;align-items:center;gap:6px;cursor:pointer;border:1px solid var(--rule2);
  background:var(--surface);color:var(--ink);padding:6px 11px;border-radius:var(--r);font:inherit;font-size:13.5px;
  transition:background .12s,border-color .12s,color .12s;white-space:nowrap}
.btn:hover{background:var(--surface2);text-decoration:none}
.btn[aria-pressed="true"]{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:500}
.btn.ghost{background:transparent;border-color:transparent;color:var(--mut)}
.btn.ghost:hover{background:var(--surface2);color:var(--ink)}
.btn svg{width:15px;height:15px;display:block;flex:0 0 auto}
.btn .badge-n{display:inline-flex;align-items:center;justify-content:center;min-width:17px;height:17px;
  padding:0 4px;border-radius:9px;background:var(--acc);color:#fff;font-size:10.5px;font-weight:600}
input[type=search],input[type=number],select{background:var(--surface);border:1px solid var(--rule2);
  color:var(--ink);padding:6px 10px;border-radius:var(--r);font:inherit;font-size:13.5px;width:100%;
  transition:border-color .12s,box-shadow .12s}
input[type=search]:focus,input[type=number]:focus,select:focus{outline:none;border-color:var(--acc);
  box-shadow:0 0 0 2px color-mix(in srgb,var(--acc) 16%,transparent)}
input::placeholder{color:var(--mut);opacity:.75}
select{appearance:none;-webkit-appearance:none;padding-right:28px;cursor:pointer;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path d='M2.5 4.5L6 8l3.5-3.5' fill='none' stroke='%23666e7a' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'/></svg>");
  background-repeat:no-repeat;background-position:right 9px center}
.seg{display:inline-flex;border:1px solid var(--rule2);border-radius:var(--r);background:var(--surface);padding:1px}
.seg button{border:0;background:transparent;color:var(--mut);padding:5px 11px;border-radius:3px;cursor:pointer;
  font:inherit;font-size:13px;transition:background .12s,color .12s}
.seg button:hover{color:var(--ink)}
.seg button[aria-pressed="true"]{background:var(--acc);color:#fff}

/* ---------- title block ---------- */
.titleblock{padding:30px 0 22px;border-bottom:1px solid var(--rule)}
.titleblock h1{font-family:var(--font-serif);font-size:clamp(23px,3.2vw,30px);line-height:1.2;
  margin:0 0 8px;font-weight:600;letter-spacing:-.005em}
.titleblock .lede{margin:0;color:var(--ink2);font-size:15px;max-width:72ch;line-height:1.55}
.tmeta{margin:14px 0 0;font-size:13px;color:var(--mut)}
.tmeta b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
.tmeta .sep{margin:0 7px;color:var(--rule2)}

/* ---------- toolbar ---------- */
.controls{position:sticky;top:56px;z-index:50;background:var(--page);border-bottom:1px solid var(--rule)}
.toolrow{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:9px 0}
#q{flex:1 1 240px;min-width:180px}
#sort{flex:0 0 auto;width:auto;min-width:132px}
.count{color:var(--mut);font-size:13px;margin-left:auto;font-variant-numeric:tabular-nums;white-space:nowrap}
.count b{color:var(--ink);font-weight:600}

/* ---------- filter panel ---------- */
.filterpanel{display:none;border-bottom:1px solid var(--rule);background:var(--surface)}
.filterpanel.open{display:block}
.filterpanel .wrap{padding-top:16px;padding-bottom:18px}
.fp-head{display:flex;align-items:baseline;gap:10px;margin-bottom:12px}
.fp-head h3{margin:0;font-size:13.5px;font-weight:600}
.fp-head p{margin:0;color:var(--mut);font-size:12.5px}
.fp-row{display:flex;gap:26px;flex-wrap:wrap;align-items:flex-start;padding:12px 0;border-top:1px solid var(--rule)}
.fp-row:first-of-type{border-top:0;padding-top:0}
.fp-label{display:block;font-size:11px;color:var(--mut);margin:0 0 6px}
.fp-block{min-width:0}
.fp-block #msearch{width:220px}
.chkgroup{display:flex;gap:6px;flex-wrap:wrap}
.chk{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--rule2);background:var(--surface);
  border-radius:var(--r);padding:4px 10px;font-size:12.5px;cursor:pointer;color:var(--ink2);user-select:none;
  transition:border-color .12s,color .12s,background .12s}
.chk:hover{border-color:var(--acc);color:var(--acc)}
.chk input{accent-color:var(--acc);margin:0}
.chk.on{background:var(--acc-soft);border-color:var(--rule-acc);color:var(--acc);font-weight:600}
.facetbar{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:12px 26px;width:100%}
.fgroup{display:grid;grid-template-columns:104px 1fr;gap:12px;align-items:start}
.fgroup>b{font-size:11.5px;color:var(--mut);font-weight:500;padding-top:5px}
.fgroup .chips{display:flex;gap:5px;flex-wrap:wrap}
.fchip{background:var(--surface);border:1px solid var(--rule2);color:var(--ink2);border-radius:var(--r);
  padding:3px 9px;font-size:12px;cursor:pointer;font-family:inherit;transition:border-color .12s,color .12s,background .12s}
.fchip:hover{border-color:var(--acc);color:var(--acc)}
.fchip[aria-pressed="true"]{background:var(--acc-soft);border-color:var(--rule-acc);color:var(--acc);font-weight:600}
.fchip[data-dir="not"][aria-pressed="true"]{background:var(--bad);border-color:var(--bad);color:#fff}
.presets{display:flex;gap:6px;flex-wrap:wrap}
.pbtn{background:var(--surface);border:1px solid var(--rule2);color:var(--ink2);border-radius:var(--r);
  padding:3px 10px;font-size:12px;cursor:pointer;font-family:inherit;transition:border-color .12s,color .12s}
.pbtn:hover{border-color:var(--acc);color:var(--acc)}
.pbtn.on{background:var(--acc-soft);border-color:var(--rule-acc);color:var(--acc);font-weight:600}
.qstatus{margin-top:8px;font-size:12px;color:var(--mut)}
.qstatus code{color:var(--acc);background:var(--acc-soft);padding:1px 5px;border-radius:3px;font-size:11.5px}

/* ---------- sections ---------- */
.sechead{display:flex;align-items:baseline;gap:16px;padding-bottom:7px;margin-bottom:18px;border-bottom:1px solid var(--rule)}
.sechead h2{margin:0;font-size:16.5px;font-weight:600;letter-spacing:-.005em}
.sechead .sub{color:var(--mut);font-size:12.5px;margin-left:auto;text-align:right;max-width:50ch}

/* ---------- cards ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:12px}
.ghead{grid-column:1/-1;position:sticky;top:110px;z-index:20;background:var(--page);
  padding:6px 0 5px;font-size:12.5px;font-weight:600;color:var(--ink);border-bottom:1px solid var(--rule)}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:var(--r);padding:13px 14px;
  display:flex;flex-direction:column;gap:7px;min-width:0;transition:border-color .12s}
.card:hover{border-color:var(--rule2)}
.card h3{margin:0;font-size:15px;line-height:1.35;font-weight:600;overflow-wrap:anywhere}
.card h3 a{color:var(--ink)}
.card h3 a:hover{color:var(--acc);text-decoration:none}
.card p{margin:0;color:var(--ink2);font-size:13px;line-height:1.5;overflow-wrap:anywhere}
.catrow{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:11.5px;color:var(--mut)}
.catrow .cat{display:inline-flex;align-items:center;gap:5px;color:var(--ink2)}
.catrow .cat i{width:8px;height:8px;border-radius:1px;background:var(--cat,var(--acc));flex:0 0 auto}
.tag{border:1px solid var(--rule2);border-radius:3px;padding:1px 6px;font-size:11px;color:var(--mut)}
.tag.flag{border-color:color-mix(in srgb,var(--warn) 45%,transparent);color:var(--warn)}
.meta{display:flex;gap:10px;flex-wrap:wrap;align-items:center;font-size:12.5px;color:var(--mut)}
.meta .dl{color:var(--ink);font-weight:500;font-variant-numeric:tabular-nums}
.meta .dl.soon{color:var(--warn)}
.meta .dl.past{color:var(--bad)}
.meta .sep{color:var(--rule2);margin:0 6px}
.chips{display:flex;gap:5px;flex-wrap:wrap}
.chip{font-size:11.5px;padding:1px 7px;border-radius:3px;background:var(--surface2);border:1px solid var(--rule);
  color:var(--ink2);cursor:pointer;font-family:inherit}
.chip:hover{border-color:var(--rule-acc);color:var(--acc);background:var(--acc-soft)}
.chip.plain{cursor:default;color:var(--mut);background:transparent;border-style:dashed}
.chip.plain:hover{border-color:var(--rule);color:var(--mut);background:transparent}
.acts{display:flex;gap:10px;flex-wrap:wrap;margin-top:auto;padding-top:6px;border-top:1px solid var(--rule)}
.acts a{font-size:12px;color:var(--mut);display:inline-flex;align-items:center;gap:3px}
.acts a:hover{color:var(--acc)}

/* ---------- deadline list ---------- */
.ulist{border:1px solid var(--rule);border-radius:var(--r);background:var(--surface);overflow:hidden}
.uhead,.urow{display:grid;grid-template-columns:104px 1fr 116px 190px;gap:14px;align-items:center;padding:8px 14px}
.uhead{font-size:11px;color:var(--mut);background:var(--surface2);border-bottom:1px solid var(--rule);
  padding-top:6px;padding-bottom:6px}
.uhead span:nth-child(3){text-align:right}
.urow{border-bottom:1px solid var(--rule);font-size:13px}
.urow:last-child{border-bottom:0}
.urow:hover{background:var(--surface2)}
.urow .udate{color:var(--mut);font-variant-numeric:tabular-nums;font-size:12.5px}
.urow .uname{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.urow .uname a{color:var(--ink)}
.urow .uname a:hover{color:var(--acc);text-decoration:none}
.urow .ud{color:var(--acc);font-weight:600;font-variant-numeric:tabular-nums;text-align:right;font-size:12.5px}
.urow .uc{display:flex;align-items:center;gap:6px;color:var(--mut);font-size:11.5px;justify-content:flex-end}
.urow .uc i{width:7px;height:7px;border-radius:1px;background:var(--cat,var(--acc));flex:0 0 auto}

/* ---------- member panel ---------- */
.mpanel{background:var(--surface);border:1px solid var(--rule);border-left:2px solid var(--acc);
  border-radius:var(--r);padding:16px}
.mphead{display:flex;align-items:center;gap:12px}
.mphead h2{margin:0;font-size:16.5px}
.mphead .btn{margin-left:auto}
#mpSub{font-size:12.5px;color:var(--mut);margin:5px 0 0}
#mpGrid{margin-top:14px}

/* ---------- dashboard ---------- */
.dash{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:14px}
.kpi{background:var(--surface);border:1px solid var(--rule);border-radius:var(--r);padding:12px 14px}
.kpi .k{font-size:11.5px;color:var(--mut)}
.kpi .v{font-size:26px;font-weight:600;line-height:1.2;margin:3px 0 1px;font-variant-numeric:tabular-nums}
.kpi .s{font-size:11.5px;color:var(--mut)}
.bars{grid-column:1/-1;display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}
.panel{background:var(--surface);border:1px solid var(--rule);border-radius:var(--r);padding:13px 14px}
.panel h3{margin:0 0 9px;font-size:12.5px;font-weight:600;color:var(--ink2)}
.barrow{display:flex;align-items:center;gap:10px;margin:5px 0}
.barlabel{flex:0 0 150px;font-size:12px;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bartrack{flex:1;height:5px;border-radius:3px;background:var(--surface2);overflow:hidden}
.barfill{height:100%;background:var(--acc);border-radius:3px}
.barval{flex:0 0 30px;text-align:right;font-variant-numeric:tabular-nums;font-size:12px}
.urglist{display:flex;flex-direction:column;gap:5px}
.urgitem{display:flex;justify-content:space-between;gap:10px;padding:6px 9px;border:1px solid var(--rule);
  border-radius:var(--r);background:var(--surface2);font-size:12.5px}
.urgitem a{color:var(--ink2)}
.urgitem a:hover{color:var(--acc)}
.urgitem .d{font-variant-numeric:tabular-nums;color:var(--mut);font-size:12px;flex:0 0 auto}

/* ---------- timeline ---------- */
.timeline{display:flex;flex-direction:column;gap:6px}
.trow{display:grid;grid-template-columns:180px 1fr;gap:12px;align-items:center;font-size:12.5px}
.trow>div:first-child{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--ink2)}
.track{background:var(--surface2);border-radius:3px;position:relative;height:12px;border:1px solid var(--rule)}
.tbar{position:absolute;top:2px;bottom:2px;border-radius:2px;background:var(--acc);opacity:.8}
.track .now{position:absolute;top:-3px;bottom:-3px;width:2px;background:var(--bad)}
.tgrid{position:absolute;top:0;bottom:0;width:1px;background:var(--rule2)}

/* ---------- map ---------- */
.mapwrap{display:grid;grid-template-columns:1fr 270px;gap:16px}
@media(max-width:820px){.mapwrap{grid-template-columns:1fr}}
svg.world{width:100%;height:auto;background:var(--surface);border:1px solid var(--rule);border-radius:var(--r)}
.citylist{display:flex;flex-direction:column;gap:2px;max-height:420px;overflow:auto}
.cityrow{display:flex;justify-content:space-between;gap:10px;font-size:12.5px;cursor:pointer;padding:5px 8px;
  border-radius:var(--r);border:1px solid transparent}
.cityrow:hover{border-color:var(--rule2);background:var(--surface2)}
.cityrow.on{border-color:var(--rule-acc);background:var(--acc-soft);color:var(--acc);font-weight:600}
.cityrow b{font-variant-numeric:tabular-nums}

/* ---------- members ---------- */
.members{display:flex;gap:6px;flex-wrap:wrap}
.mchip{padding:4px 11px;border-radius:var(--r);border:1px solid var(--rule2);background:var(--surface);
  cursor:pointer;font-size:12.5px;font-family:inherit;color:var(--ink2);transition:border-color .12s,color .12s}
.mchip:hover{border-color:var(--acc);color:var(--acc)}
.mchip[aria-pressed=true]{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:500}

/* ---------- eligibility ---------- */
.elig{background:var(--surface);border:1px solid var(--rule);border-radius:var(--r);padding:16px}
.elig .row{display:flex;gap:12px;flex-wrap:wrap;align-items:end;margin-bottom:14px}
.elig label{display:flex;flex-direction:column;gap:4px;font-size:11.5px;color:var(--mut)}
.elig input,.elig select{background:var(--page);border:1px solid var(--rule2);color:var(--ink);
  padding:6px 9px;border-radius:var(--r);font:inherit;font-size:13px;min-width:140px}
.eligout{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(260px,100%),1fr));gap:8px}
.erow{border:1px solid var(--rule);border-radius:var(--r);padding:9px 11px;font-size:12.5px;background:var(--page)}
.erow b{display:block;color:var(--ink);margin-bottom:2px;font-weight:600}
.erow.no{opacity:.6}
.erow .why{color:var(--mut);font-size:11.5px}
.empty{color:var(--mut);padding:28px 0;text-align:center;border:1px dashed var(--rule2);border-radius:var(--r);
  background:var(--surface);font-size:13.5px}

/* ---------- notes ---------- */
.notes{border-top:1px solid var(--rule)}
.notes p{margin:0;padding:9px 0;border-bottom:1px solid var(--rule);font-size:13px;color:var(--ink2);
  display:grid;grid-template-columns:74px 1fr;gap:14px;max-width:96ch}
.notes b{color:var(--ink);font-weight:600}

/* ---------- footer ---------- */
footer{border-top:1px solid var(--rule);background:var(--surface);color:var(--mut);padding:22px 0 26px;font-size:12.5px;margin-top:30px}
.fgrid{display:flex;gap:28px;flex-wrap:wrap;align-items:flex-start}
.fgrid p{margin:0 0 4px;max-width:56ch}
.fowner{color:var(--ink);font-weight:600}
.fgrid nav{display:flex;gap:16px;flex-wrap:wrap;margin-left:auto}
.fgrid nav a{color:var(--ink2)}
.fmeta{margin-top:16px;padding-top:12px;border-top:1px solid var(--rule);font-size:11.5px;color:var(--mut)}

/* ---------- responsive ---------- */
@media (max-width:960px){
  .topnav{display:none}
  .pill{max-width:200px}
}
@media (max-width:760px){
  .wrap{padding:0 16px}
  .top .wrap{gap:10px}
  .brand span{display:none}
  .top .btn{padding:5px 9px;font-size:12.5px}
  .titleblock{padding:22px 0 18px}
  .controls{position:static}
  .toolrow{gap:7px}
  #q{flex:1 1 100%}
  #sort{flex:1 1 40%;min-width:118px}
  .seg{flex:1 1 100%;overflow-x:auto}
  .seg button{flex:1 0 auto}
  .count{flex:1 1 100%;margin-left:0}
  .fgroup{grid-template-columns:1fr;gap:4px}
  .fgroup>b{padding-top:0}
  .sechead{flex-direction:column;align-items:flex-start;gap:3px}
  .sechead .sub{margin-left:0;text-align:left}
  .grid{grid-template-columns:1fr}
  .eligout{grid-template-columns:1fr}
  .trow{grid-template-columns:100px 1fr;font-size:12px}
  .ghead{position:static}
  .pill{display:none}
  .urow{grid-template-columns:1fr auto;gap:4px 10px;padding:9px 12px}
  .uhead{display:none}
  .urow .uname{grid-column:1/-1;white-space:normal}
  .urow .ud{text-align:left}
  .urow .uc{grid-column:1/-1;justify-content:flex-start}
  .fgrid nav{margin-left:0}
}

/* ---------- print ---------- */
@media print{
  header.top,.controls,.filterpanel,.ulist,.elig,.members,.acts{display:none!important}
  body{background:#fff;color:#000;font-size:11pt}
  .card{break-inside:avoid;border:1px solid #ccc;background:#fff}
  .grid{grid-template-columns:1fr 1fr}
  .titleblock{border-bottom:1px solid #000}
}

/* ---------- reduced motion ---------- */
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important}
  html{scroll-behavior:auto}
}
</style>
</head>
<body id="top">
<header class="top"><div class="wrap">
  <a class="brand" href="#top">
    <b><i></i>MCP&nbsp;KNUST</b>
    <span>Mathematical &amp; Computational Physics</span>
  </a>
  <nav class="topnav" aria-label="Sections">
    <a href="#opportunities">Opportunities</a>
    <a href="#next90">Next 90 days</a>
    <a href="#eligibility">Eligibility</a>
    <a href="#members">Members</a>
  </nav>
  <div class="pill" id="nextPill" title="Next deadline in the register">Next deadline: none</div>
  <a class="btn" href="mcp-deadlines.ics" download title="Download all deadlines as a calendar file">Calendar</a>
  <button class="btn" id="theme" title="Colour theme: light / dark / system" aria-label="Change colour theme"></button>
</div></header>

<div class="titleblock"><div class="wrap">
  <h1>Opportunities for Mathematical &amp; Computational Physics</h1>
  <p class="lede">Workshops, conferences, fellowships and grants open to members of the Mathematical &amp; Computational Physics unit, KNUST. Companion to the <a href="mcp-knust-workshops-report.pdf">unit report</a>.</p>
  <p class="tmeta"><b>__NROWS__</b> opportunities<span class="sep">/</span><b>__NDATED__</b> with deadlines<span class="sep">/</span><b>__NMEM__</b> members<span class="sep">/</span><b>__N90__</b> due within 90 days<span class="sep">/</span>updated __GEN__</p>
</div></div>

<div class="controls"><div class="wrap">
  <div class="toolrow">
    <input type="search" id="q" placeholder="Search, e.g. quantum within:180" aria-label="Search opportunities" autocomplete="off">
    <select id="sort" aria-label="Sort by">
      <option value="deadline">Deadline</option>
      <option value="name">Name</option>
      <option value="category">Theme</option>
      <option value="odds">Best odds</option>
      <option value="score">My match score</option>
    </select>
    <div class="seg" role="group" aria-label="View">
      <button id="vDash" aria-pressed="false">Dashboard</button>
      <button id="vCards" aria-pressed="true">Cards</button>
      <button id="vTime" aria-pressed="false">Timeline</button>
      <button id="vMap" aria-pressed="false">Map</button>
    </div>
    <button class="btn" id="group" aria-pressed="false" title="Group results by theme">Group</button>
    <button class="btn" id="moreFilters" aria-expanded="false" aria-controls="filterpanel">Filters<span class="badge-n" id="filterCount" hidden>0</span></button>
    <button class="btn ghost" id="reset">Reset</button>
    <span class="count" id="count" aria-live="polite"></span>
  </div>
</div></div>

<div class="filterpanel" id="filterpanel">
  <div class="wrap">
    <div class="fp-head">
      <h3>Filters</h3>
      <p>Filters are combined. Click a tag twice to exclude it.</p>
    </div>
    <div class="fp-row">
      <div class="fp-block">
        <span class="fp-label">Theme</span>
        <div class="chkgroup" id="cat" role="group" aria-label="Theme"></div>
      </div>
      <div class="fp-block">
        <span class="fp-label">Member</span>
        <input type="search" id="msearch" list="mlist" placeholder="Search a member" aria-label="Search by member" autocomplete="off">
        <datalist id="mlist"></datalist>
      </div>
      <div class="fp-block">
        <span class="fp-label">Combine tags in one group</span>
        <div class="seg" role="group" aria-label="Combine tags within a facet">
          <button id="anyAny" aria-pressed="true">Any</button>
          <button id="anyAll" aria-pressed="false">All</button>
        </div>
      </div>
    </div>
    <div class="fp-row">
      <div class="fp-block" style="width:100%">
        <span class="fp-label">Attributes</span>
        <div class="facetbar" id="facetbar" role="group" aria-label="Opportunity attributes"></div>
      </div>
    </div>
    <div class="fp-row">
      <div class="fp-block" style="width:100%">
        <span class="fp-label">Saved views</span>
        <div class="presets" id="presets" role="group" aria-label="Saved views"></div>
      </div>
    </div>
    <div class="qstatus" id="qstatus" hidden></div>
  </div>
</div>

<section class="wrap" id="next90">
  <div class="sechead">
    <h2>Next 90 days</h2>
    <p class="sub">Deadlines and start dates falling within ninety days, earliest first</p>
  </div>
  <div class="ulist" id="urgent"></div>
</section>

<section class="wrap" id="memberPanel" hidden><div class="mpanel">
  <div class="mphead"><h2 id="mpTitle">Action list</h2>
    <button class="btn" id="mpClear">Clear</button></div>
  <p id="mpSub"></p>
  <div class="grid" id="mpGrid"></div>
</div></section>

<main class="wrap" id="opportunities"><section>
  <div class="sechead">
    <h2 id="listTitle">All opportunities</h2>
    <p class="sub" id="listSub"></p>
  </div>
  <div class="dash" id="dashboard" hidden></div>
  <div class="grid" id="grid"></div>
  <div class="timeline" id="timeline" hidden></div>
  <div class="mapwrap" id="mapwrap" hidden>
    <svg class="world" id="world" viewBox="0 0 720 360" role="img" aria-label="World map of venues"></svg>
    <div class="citylist" id="citylist"></div>
  </div>
  <div class="empty" id="empty" hidden>No matches. Widen the deadline window or clear a filter.</div>
</section></main>

<section class="wrap" id="eligibility">
  <div class="sechead">
    <h2>Grant eligibility</h2>
    <p class="sub">Screens the grants register against career stage, age, years since PhD and region</p>
  </div>
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

<section class="wrap" id="members">
  <div class="sechead">
    <h2>Members</h2>
    <p class="sub">Select a member to open an action list ordered by deadline</p>
  </div>
  <div class="members" id="members"></div>
</section>

<section class="wrap" id="notes">
  <div class="sechead">
    <h2>Notes on this data</h2>
    <p class="sub">Source, method and limits of the register</p>
  </div>
  <div class="notes">
    <p><b>Scope</b><span>Workshops, summer schools, conferences, fellowships, scholarships and research grants open to members of the unit.</span></p>
    <p><b>Method</b><span>Public listings gathered by an automated research pipeline, then normalised by deadline, theme, career stage, funding mode and openness. Tags marked with an asterisk are estimates rather than statements made by the organiser.</span></p>
    <p><b>Limits</b><span>Deadlines change and pages move. Entries marked low confidence carry aggregator or predatory signals and need checking. Verify on the linked page before applying.</span></p>
  </div>
</section>

<footer><div class="wrap">
  <div class="fgrid">
    <div>
      <p class="fowner">Mathematical &amp; Computational Physics, KNUST</p>
      <p>Register of workshops, conferences, fellowships and grants, compiled from open sources.</p>
    </div>
    <nav>
      <a href="mcp-knust-workshops-report.pdf">Unit report (PDF)</a>
      <a href="mcp-deadlines.ics">Calendar (.ics)</a>
      <a href="mcp-opportunities.csv">Register (CSV)</a>
      <a href="#top">Top of page</a>
    </nav>
  </div>
  <p class="fmeta">Data as of <b id="asof">__GEN__</b>. Compiled by the opencode online-research pipeline. Deadlines change, so check the linked page before applying.</p>
</div></footer>

<script>
const DATA = __DATA__;
const $ = s => document.querySelector(s);
const state = {q:"", cats:[], f:{}, anyWithin:true, win:"", member:"", city:"",
               sort:"deadline", view:"cards", group:false, pq:null};

/* ---------- theme (light/dark/auto) ---------- */
const root = document.documentElement;
const modes = ["light","dark","auto"];
let mode = localStorage.getItem("mcp-theme") || "light";
const THEME_ICON = {
  light:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.3M12 19.1v2.3M2.6 12h2.3M19.1 12h2.3M5.4 5.4l1.6 1.6M17 17l1.6 1.6M18.6 5.4L17 7M7 17l-1.6 1.6"/></svg>',
  dark:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.4 14.7A8.5 8.5 0 1 1 9.3 3.6a7 7 0 0 0 11.1 11.1Z"/></svg>',
  auto:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="8.4"/><path d="M12 3.6v16.8"/></svg>'
};
function applyTheme(){
  const sys = matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  root.dataset.theme = mode === "auto" ? sys : mode;
  $("#theme").innerHTML = THEME_ICON[mode];
  $("#theme").title = "Colour theme: " + mode;
}
applyTheme();
$("#theme").onclick = () => { mode = modes[(modes.indexOf(mode)+1)%3]; localStorage.setItem("mcp-theme", mode); applyTheme(); };

/* ---------- helpers ---------- */
const CATCOLOR = {
  "QUANTUM SCIENCE & TECHNOLOGY":"--c-quantum","MATERIALS MODELLING & MOF/DFT":"--c-materials",
  "ENERGY, WATER & DIGITAL TWINS":"--c-energy","SEISMOLOGY, GEOSCIENCE & OCEAN":"--c-seismo",
  "ASTROPHYSICS":"--c-astro","AFRICAN PHYSICS, MATH & GENERAL":"--c-africa","GRANTS & FELLOWSHIPS":"--c-grants"};
const CAT_SHORT = {
  "QUANTUM SCIENCE & TECHNOLOGY":"Quantum",
  "MATERIALS MODELLING & MOF/DFT":"Materials",
  "ENERGY, WATER & DIGITAL TWINS":"Energy and water",
  "SEISMOLOGY, GEOSCIENCE & OCEAN":"Geophysics",
  "ASTROPHYSICS":"Astrophysics",
  "AFRICAN PHYSICS, MATH & GENERAL":"Physics and mathematics",
  "GRANTS & FELLOWSHIPS":"Grants"};
function catColor(c){ return "var("+(CATCOLOR[c]||"--acc")+")"; }
function catShort(c){ return CAT_SHORT[c] || c; }
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

/* ---------- filtering ----------
   Facet model: state.f = { facetKey: {tag: 1 | -1} }   1 = include, -1 = exclude
   Within-facet combine: ANY (union, default) or ALL (intersection)  → state.anyWithin
   Across facets: always AND.  Query DSL tokens → extra facet constraints.        */
const FACET_TAGS = __FACET_TAGS__;
const FACET_KEYS = Object.keys(FACET_TAGS);
const GLOBAL_SEARCH = ["q","member","cat","city","sort","view","group","win","anyt"];

function facetTags(r, key){ return (r.facets && r.facets[key]) || []; }

function facetHit(r, key, sel){
  const tags = facetTags(r, key);
  const inc = Object.keys(sel).filter(t => sel[t] === 1);
  const exc = Object.keys(sel).filter(t => sel[t] === -1);
  if (exc.some(t => tags.includes(t))) return false;
  if (!inc.length) return true;
  return state.anyWithin ? inc.some(t => tags.includes(t)) : inc.every(t => tags.includes(t));
}

function parseQuery(qstr){
  const toks = qstr.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const out = { terms: [], facets: {}, days: null, mode: null, flag: null };
  // every known tag, mapped to the facet it belongs to
  const TAG2KEY = {};
  for (const k of FACET_KEYS) for (const t of (FACET_TAGS[k]||[])) TAG2KEY[t] = k;
  for (let t of toks){
    if (!t) continue;
    let neg = false;
    if (t[0] === "-"){ neg = true; t = t.slice(1); }
    const m = t.match(/^([a-z]+):(.+)$/);
    if (m){
      const key = m[1], val = m[2];
      if (key === "within" || key === "by"){ const d = parseInt(val,10); if(!isNaN(d)) out.days = d; continue; }
      if (key === "mode"){ out.mode = neg ? "dated" : val; continue; }
      if (key === "flag" || key === "conf"){ out.flag = val; continue; }
      if (FACET_KEYS.includes(key)){ out.facets[key] = out.facets[key] || {}; out.facets[key][val] = neg ? -1 : 1; continue; }
    }
    // bare token: if it names a facet tag, filter by it; also keep as free text
    if (TAG2KEY[t]){ const k = TAG2KEY[t]; out.facets[k] = out.facets[k] || {}; out.facets[k][t] = neg ? -1 : 1; continue; }
    out.terms.push(neg ? t : t);
  }
  return out;
}

function matches(r, pq){
  // theme (multi-select)
  if (state.cats.length && !state.cats.includes(r.category)) return false;
  if (state.member && !r.people.includes(state.member) && !r.openAll) return false;
  if (state.city && r.city !== state.city) return false;

  // free text
  const hay = (r.name+" "+r.desc+" "+r.category+" "+r.people.join(" ")+" "+r.city+" "
              + (r.deadline?fmtDate(r.deadline):"rolling watch")).toLowerCase();
  for (const term of pq.terms) if (!hay.includes(term)) return false;

  // facet chips (UI): AND across facets
  for (const key of FACET_KEYS){
    const sel = state.f[key];
    if (sel && Object.keys(sel).length && !facetHit(r, key, sel)) return false;
  }
  // facet constraints from the query DSL: AND with the above, OR-merged per tag
  for (const key of Object.keys(pq.facets)){
    const sel = pq.facets[key];
    const tags = facetTags(r, key);
    for (const t of Object.keys(sel)){
      if (sel[t] === 1 && !tags.includes(t)) return false;
      if (sel[t] === -1 && tags.includes(t)) return false;
    }
  }
  // deadline window
  if (state.win === "dated" && r.days === null) return false;
  if (state.win === "rolling" && r.days !== null) return false;
  if (["90","180","365"].includes(state.win)){
    if (r.days === null || r.days < 0 || r.days > +state.win) return false;
  }
  if (pq.days !== null){ if (r.days === null || r.days < 0 || r.days > pq.days) return false; }
  if (pq.mode === "rolling" && r.days !== null) return false;
  if (pq.mode === "dated" && r.days === null) return false;
  if (pq.flag === "low" && r.flag !== "low") return false;
  if (pq.flag === "safe" && r.flag === "low") return false;
  return true;
}

/* match score for "my match": rewards facets the user flagged + openness + odds + soon */
function score(r){
  let s = 0;
  const ODDS = { strong: 3, fair: 2, tough: 0 };
  const OPEN = { high: 3, mid: 2, focused: 1 };
  s += (ODDS[(r.facets.odds||["fair"])[0]] || 0);
  s += (OPEN[(r.facets.openness||["focused"])[0]] || 0);
  if (state.anyWithin === false) s += 1;
  for (const key of FACET_KEYS){
    const sel = state.f[key]||{}, tags = facetTags(r,key);
    for (const t of Object.keys(sel)) if (sel[t]===1 && tags.includes(t)) s += 2;
  }
  if (r.days !== null && r.days >= 0){
    if (r.days <= 30) s += 4; else if (r.days <= 90) s += 3; else if (r.days <= 180) s += 1;
  }
  if (state.member && (r.people.includes(state.member) || r.openAll)) s += 2;
  return s;
}

function sortRows(rows){
  const s = state.sort;
  return rows.slice().sort((a,b)=>{
    if(s==="name") return a.name.localeCompare(b.name);
    if(s==="category") return a.category.localeCompare(b.category) || (a.deadline||"z").localeCompare(b.deadline||"z");
    if(s==="odds") return score(b)-score(a) || (a.deadline||"9999").localeCompare(b.deadline||"9999");
    if(s==="score") return score(b)-score(a) || (a.deadline||"9999").localeCompare(b.deadline||"9999");
    const ad = a.deadline||"9999", bd = b.deadline||"9999";
    return ad.localeCompare(bd);
  });
}

/* ---------- card ---------- */
function card(r){
  const el = document.createElement("article");
  el.className = "card";
  el.style.setProperty("--cat", catColor(r.category));
  const dl = r.days===null ? "Rolling, no fixed date"
            : r.days<0 ? "Closed "+fmtDate(r.deadline)
            : fmtDate(r.deadline)+", "+r.days+" days left";
  const odds = (r.facets.odds||[])[0];
  el.innerHTML = `
    <div class="catrow">
      <span class="cat"><i></i>${esc(catShort(r.category))}</span>
      ${r.city?`<span>${esc(r.city)}</span>`:""}
      ${r.rate?`<span class="tag">${esc(r.rate)}</span>`:""}
      ${r.flag==="low"?'<span class="tag flag" title="Aggregator or predatory indicators, check before paying">low confidence</span>':""}
    </div>
    <h3>${r.url?`<a href="${r.url}" target="_blank" rel="noopener">${hl(r.name,state.q)}</a>`:hl(r.name,state.q)}</h3>
    <p>${hl(r.desc,state.q)}</p>
    <div class="meta">
      <span class="dl ${dlClass(r)}">${dl}</span>
      ${odds?`<span class="sep">/</span><span>Odds: ${esc(odds)}</span>`:""}
    </div>
    <div class="chips">${r.people.length
      ? r.people.map(m=>`<span class="chip" data-m="${esc(m)}">${esc(m)}</span>`).join("")
      : '<span class="chip plain">Open to all members</span>'}</div>
    <div class="acts">
      ${r.deadline?`<a href="${gcalURL(r)}" target="_blank" rel="noopener">Google Calendar</a>`:""}
      ${r.deadline?`<a href="${icsURL(r)}" download="event.ics">.ics</a>`:""}
      ${r.url?`<a href="${r.url}" target="_blank" rel="noopener">Source page</a>`:""}
    </div>`;
  el.querySelectorAll(".chip[data-m]").forEach(c => c.onclick = () => { setMember(c.dataset.m); window.scrollTo({top:0,behavior:"smooth"}); });
  return el;
}

/* ---------- render ---------- */
const VIEW_SUB = {
  cards:"Opportunities matching the current filters, ordered by deadline",
  timeline:"Start and deadline dates on a common axis",
  map:"Venues by location",
  dashboard:"Counts for the current filter"
};
function render(){
  state.pq = parseQuery(state.q);
  const rows = sortRows(DATA.rows.filter(r => matches(r, state.pq)));
  const grid = $("#grid"), tl = $("#timeline"), mw = $("#mapwrap");
  const extra = [];
  if (state.member) extra.push("member: "+state.member);
  if (state.city) extra.push("place: "+state.city);
  $("#count").innerHTML = '<b>'+rows.length+'</b> of '+DATA.rows.length+' shown'
    + (extra.length ? ', '+esc(extra.join(", ")) : '');
  const titles = {cards:"All opportunities", timeline:"Timeline", map:"Venues", dashboard:"Dashboard"};
  $("#listTitle").textContent = titles[state.view] || "All opportunities";
  $("#listSub").textContent = VIEW_SUB[state.view] || "";
  $("#empty").hidden = rows.length>0;
  grid.hidden = state.view!=="cards"; tl.hidden = state.view!=="timeline"; mw.hidden = state.view!=="map";
  const db = $("#dashboard"); if (db){ db.hidden = state.view!=="dashboard"; if (state.view==="dashboard"){ renderDashboard(); } }

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
    dots += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${rad}" fill="${catColor(rs[0].category)}" opacity=".8"><title>${esc(city)}: ${rs.length} event(s)</title></circle>`;
    dots += `<text x="${(x+rad+3).toFixed(1)}" y="${(y+3).toFixed(1)}" font-size="9" fill="var(--mut)">${esc(city)}</text>`;
  });
  svg.innerHTML = g + dots;
  const counts = Object.entries(byCity).sort((a,b)=>b[1].length-a[1].length);
  $("#citylist").innerHTML = counts.map(([city,rs])=>
    `<div class="cityrow${state.city===city?" on":""}" data-city="${esc(city)}"><span>${esc(city)}</span><b>${rs.length}</b></div>`).join("")
    || '<div class="empty">No geocoded venues in this filter.</div>';
  $("#citylist").querySelectorAll(".cityrow").forEach(el => el.onclick = () => {
    state.city = state.city===el.dataset.city ? "" : el.dataset.city; render();
  });
}

/* ---------- urgent strip ---------- */
function renderFacetBar(){
  const bar = $("#facetbar");
  bar.innerHTML = Object.keys(FACET_META).map(function(key){
    const meta = FACET_META[key], sel = state.f[key]||{};
    const chips = Object.keys(meta.tags).map(function(tag){
      const v = sel[tag]||0;
      const lbl = meta.tags[tag] + (v===-1 ? " ✕" : "");
      return '<button class="fchip" data-key="'+key+'" data-tag="'+tag+'" data-dir="'
        + (v===-1?"not":"in") + '" aria-pressed="' + (v!==0) + '">' + lbl + '</button>';
    }).join("");
    return '<div class="fgroup"><b>'+meta.label+'</b>'+chips+'</div>';
  }).join("");
  bar.querySelectorAll(".fchip").forEach(function(b){
    b.onclick = function(){
      const key=b.dataset.key, tag=b.dataset.tag;
      const sel = state.f[key] = state.f[key]||{};
      const cur = sel[tag]||0;
      if (cur===0) sel[tag]=1; else if (cur===1) sel[tag]=-1; else delete sel[tag];
      if (!Object.keys(sel).length) delete state.f[key];
      renderFacetBar(); update();
    };
  });
  const catSel = $("#cat");
  if (catSel){
    catSel.innerHTML = DATA.categories.map(function(c){
      const on = state.cats.indexOf(c) !== -1;
      return '<label class="chk'+(on?" on":"")+'"><input type="checkbox" value="'+esc(c)+'"'+(on?" checked":"")+'>'+esc(catShort(c))+'</label>';
    }).join("");
  }
}

/* ---------- saved searches (presets) ---------- */
const PRESETS = [
  {name:"Open worldwide", s:{f:{access:{openworld:1}}}},
  {name:"Rolling", s:{f:{mode:{rolling:1}}}},
  {name:"Fully funded", s:{f:{funding:{fullyfunded:1}}}},
  {name:"Women in STEM", s:{f:{gender:{women:1}}}},
  {name:"No nomination", s:{f:{access:{nomination:-1}}}},
  {name:"Due within 60 days", s:{q:"within:60"}},
  {name:"Best odds", s:{f:{odds:{strong:1}}}},
  {name:"Quantum", s:{cats:["QUANTUM SCIENCE & TECHNOLOGY"]}},
  {name:"Materials and MOF", s:{cats:["MATERIALS MODELLING & MOF/DFT"]}},
];
function renderPresets(){
  const box = $("#presets");
  box.innerHTML = PRESETS.map(function(p,i){
    return '<button class="pbtn" data-i="'+i+'">'+esc(p.name)+'</button>';
  }).join("") + '<button class="pbtn" data-share="1">Copy view link</button>';
  box.querySelectorAll(".pbtn").forEach(function(b){
    b.onclick = function(){
      if (b.dataset.share){
        if (navigator.clipboard) navigator.clipboard.writeText(location.href);
        b.textContent = "Link copied";
        setTimeout(function(){ b.textContent = "Copy view link"; }, 1500);
        return;
      }
      applyPreset(PRESETS[+b.dataset.i].s);
    };
  });
  syncPresets();
}
function presetActive(p){
  const s = p.s||{};
  if ((s.q||"") !== state.q) return false;
  if (JSON.stringify(s.cats||[]) !== JSON.stringify(state.cats||[])) return false;
  const keys = Object.keys(s.f||{});
  if (keys.length !== Object.keys(state.f).length) return false;
  for (const k of keys){
    const a = s.f[k]||{}, b = state.f[k]||{};
    if (Object.keys(a).length !== Object.keys(b).length) return false;
    for (const t of Object.keys(a)) if (b[t] !== a[t]) return false;
  }
  return true;
}
function syncPresets(){
  document.querySelectorAll("#presets .pbtn[data-i]").forEach(function(b){
    b.classList.toggle("on", presetActive(PRESETS[+b.dataset.i]));
  });
}
function applyPreset(s){
  state.q = s.q||""; state.cats = s.cats||[]; state.f = s.f||{};
  state.member = ""; state.city = ""; state.win = "";
  $("#msearch").value = ""; $("#memberPanel").hidden = true;
  $("#q").value = state.q;
  syncMember(); renderFacetBar(); update();
}

/* ---------- query DSL status ---------- */
function renderQueryStatus(){
  const el = $("#qstatus");
  const pq = state.pq;
  if (!pq) { el.hidden = true; return; }
  const bits = [];
  Object.keys(pq.facets).forEach(function(k){
    Object.keys(pq.facets[k]).forEach(function(t){
      bits.push('<code>'+(pq.facets[k][t]===-1?"-":"")+k+':'+t+'</code>');
    });
  });
  if (pq.days !== null) bits.push('<code>within:'+pq.days+' days</code>');
  if (pq.mode) bits.push('<code>mode:'+pq.mode+'</code>');
  if (pq.flag) bits.push('<code>flag:'+pq.flag+'</code>');
  if (!bits.length) { el.hidden = true; return; }
  el.hidden = false;
  el.innerHTML = "Smart filters detected → " + bits.join(" ");
}


/* ---------- DASHBOARD ---------- */
const TYPE_LABEL = {fellowship:"Fellowships", scholarship:"Scholarships", grant:"Grants",
  workshop:"Workshops & schools", conference:"Conferences", internship:"Internships",
  job:"Jobs & positions", other:"Other & specialised"};
function renderDashboard(){
  const db=$("#dashboard");
  const rows = DATA.rows.filter(r=>matches(r, parseQuery(state.q)));
  const now = Date.now();
  const dated = rows.filter(r=>r.deadline);
  const upcoming = dated.filter(r=>r.days!==null && r.days>=0).sort((a,b)=>(a.days||999)-(b.days||999)).slice(0,8);
  const byType = {}, byCat = {}, byMonth = {};
  rows.forEach(r=>{
    const t=(r.facets.type||[])[0] || "other"; byType[t]=(byType[t]||0)+1;
    byCat[r.category]=(byCat[r.category]||0)+1;
    if(r.deadline){ const m=r.deadline.slice(0,7); byMonth[m]=(byMonth[m]||0)+1; }
  });
  const topCat = Object.entries(byCat).sort((a,b)=>b[1]-a[1]).slice(0,6);
  const kpi = [
    {k:"Total opportunities",v:rows.length,s:"in current view"},
    {k:"Dated deadlines",v:dated.length,s:"with calendar dates"},
    {k:"Due next 90 days",v:rows.filter(r=>r.days!==null&&r.days>=0&&r.days<=90).length,s:"urgent / soon"},
    {k:"Fellowships & grants",v:(byType.fellowship||0)+(byType.grant||0)+(byType.scholarship||0),s:"funding-focused"},
  ];
  db.innerHTML = '<div class="dash">'+kpi.map(k=>'<div class="kpi"><div class="k">'+k.k+'</div><div class="v">'+k.v+'</div><div class="s">'+k.s+'</div></div>').join('')
    + '<div class="bars"><div class="panel"><h3>By type</h3>'+Object.entries(byType).sort((a,b)=>b[1]-a[1]).slice(0,8).map(([n,c])=>'<div class="barrow"><div class="barlabel">'+esc(TYPE_LABEL[n]||n)+'</div><div class="bartrack"><div class="barfill" style="width:'+Math.max(8,c/rows.length*100)+'%"></div></div><div class="barval">'+c+'</div></div>').join('')+'</div>'
    + '<div class="panel"><h3>By theme, top 6</h3>'+topCat.map(([n,c])=>'<div class="barrow"><div class="barlabel">'+esc(catShort(n))+'</div><div class="bartrack"><div class="barfill" style="width:'+Math.max(8,c/rows.length*100)+'%"></div></div><div class="barval">'+c+'</div></div>').join('')+'</div>'
    + '<div class="panel"><h3>Closing within 45 days</h3><div class="urglist">'+(upcoming.filter(r=>r.days<=45).length? upcoming.filter(r=>r.days<=45).map(r=>'<div class="urgitem"><a href="'+(r.url||'#')+'" target="_blank" rel="noopener">'+esc(r.name)+'</a><span class="d">'+r.days+'d</span></div>').join('') : '<div style="color:var(--mut);font-size:12px">None in current filter</div>')+'</div></div>'
    + '</div></div>';
}

function renderUrgent(){
  const soon = DATA.rows.filter(r=>r.days!==null && r.days>=0 && r.days<=90).sort((a,b)=>a.days-b.days).slice(0,12);
  $("#urgent").innerHTML = '<div class="uhead"><span>Date</span><span>Opportunity</span><span>Deadline</span><span>Theme</span></div>' + soon.map(r=>`
    <div class="urow" style="--cat:${catColor(r.category)}">
      <span class="udate">${fmtDate(r.deadline)}</span>
      <span class="uname">${r.url?`<a href="${r.url}" target="_blank" rel="noopener">${esc(r.name)}</a>`:esc(r.name)}</span>
      <span class="ud">${r.days===0?"today":r.days===1?"tomorrow":"in "+r.days+" days"}</span>
      <span class="uc"><i></i>${esc(catShort(r.category))}${r.city?" / "+esc(r.city):""}</span>
    </div>`).join("");
  const nxt = soon[0];
  if(nxt) $("#nextPill").innerHTML = 'Next: <b>'+esc(nxt.name.slice(0,30))+'</b> <em>'+nxt.days+"d</em>";
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
      <div class="why">${ok?(rule?("ok: "+esc(rule.note)):"no stated rule, check criteria"):("excluded: "+esc(why.join("; ")))}</div></div>`;
  }).join("");
}

/* ---------- URL state ---------- */
function readURL(){
  const p = new URLSearchParams(location.search);
  state.q=p.get("q")||""; state.win=p.get("win")||""; state.anyWithin=p.get("anyt")!=="1";
  state.cats=(p.get("cat")||"").split("|").filter(Boolean);
  state.f={};
  for (const key of FACET_KEYS){
    const sel = {};
    (p.get(key)||"").split("|").filter(Boolean).forEach(t=>{
      if (t[0]==="-") sel[t.slice(1)] = -1; else sel[t] = 1;
    });
    if (Object.keys(sel).length) state.f[key] = sel;
  }
  state.member=p.get("member")||""; state.city=p.get("city")||""; state.sort=p.get("sort")||"deadline";
  state.view=p.get("view")||"cards"; state.group=p.get("group")==="1";
  $("#q").value=state.q; $("#sort").value=state.sort;
  setWithin(state.anyWithin);
  $("#group").setAttribute("aria-pressed", state.group);
  $("#vCards").setAttribute("aria-pressed", state.view==="cards");
  $("#vTime").setAttribute("aria-pressed", state.view==="timeline");
  $("#vMap").setAttribute("aria-pressed", state.view==="map");
  $("#vDash").setAttribute("aria-pressed", state.view==="dashboard");
}
function writeURL(){
  const p = new URLSearchParams();
  if(state.q)p.set("q",state.q); if(state.win)p.set("win",state.win);
  if(!state.anyWithin)p.set("anyt","1");
  if(state.cats.length)p.set("cat",state.cats.join("|"));
  for (const key of FACET_KEYS){
    const sel = state.f[key]||{}, parts = [];
    Object.keys(sel).forEach(t => parts.push(sel[t]===-1 ? "-"+t : t));
    if (parts.length) p.set(key, parts.join("|"));
  }
  if(state.member)p.set("member",state.member); if(state.city)p.set("city",state.city);
  if(state.sort!=="deadline")p.set("sort",state.sort); if(state.view!=="cards")p.set("view",state.view);
  if(state.group)p.set("group","1");
  history.replaceState(null,"", location.pathname + (p.toString()?"?"+p:""));
}

/* ---------- facet chips UI ---------- */
const FACET_META = {
  funding:  {label:"Funding",      tags:{fullyfunded:"fully funded", stipend:"stipend/salary"}},
  access:   {label:"Who can apply",tags:{openworld:"open worldwide", africapriority:"Africa priority", nomination:"needs host/nomination"}},
  type:     {label:"Type",         tags:{fellowship:"fellowships", scholarship:"scholarships", grant:"grants", workshop:"workshops/schools", conference:"conferences", internship:"internships", job:"jobs/positions"}},
  stage:    {label:"Stage",        tags:{undergrad:"undergrad", masters:"master's", phd:"PhD", postdoc:"postdoc/ECR", faculty:"faculty/staff"}},
  mobility: {label:"Location",     tags:{remote:"remote", abroad:"abroad/in-person"}},
  gender:   {label:"Gender",       tags:{women:"women-only"}},
  openness: {label:"Openness*",    tags:{high:"open to all", mid:"broad", focused:"focused"}},
  odds:     {label:"Odds*",        tags:{strong:"strong", fair:"fair", tough:"tough"}},
  heat:     {label:"Timing*",      tags:{hot:"new this cycle"}},
  mode:     {label:"Cycle",        tags:{rolling:"rolling/watch"}},
};

/* ---------- events ---------- */
function update(){ state.pq = parseQuery(state.q); writeURL(); renderQueryStatus(); updateFilterCount(); syncPresets(); render(); }
function updateFilterCount(){
  let n = state.cats.length + (state.member?1:0);
  for (const k of Object.keys(state.f)) n += Object.keys(state.f[k]||{}).length;
  const b = $("#filterCount");
  b.hidden = n===0; b.textContent = n;
}
function setWithin(any){
  state.anyWithin = any;
  $("#anyAny").setAttribute("aria-pressed", any?"true":"false");
  $("#anyAll").setAttribute("aria-pressed", any?"false":"true");
}
$("#q").oninput = e => { state.q = e.target.value; update(); };
$("#cat").onchange = e => {
  if (e.target.tagName !== "INPUT") return;
  state.cats = Array.from($("#cat").querySelectorAll("input:checked")).map(o => o.value);
  const lab = e.target.closest(".chk"); if (lab) lab.classList.toggle("on", e.target.checked);
  update();
};
$("#sort").onchange = e => { state.sort = e.target.value; update(); };
$("#anyAny").onclick = () => { setWithin(true); update(); };
$("#anyAll").onclick = () => { setWithin(false); update(); };
$("#group").onclick = () => { state.group=!state.group; $("#group").setAttribute("aria-pressed",state.group); update(); };
$("#moreFilters").onclick = () => {
  const open = $("#filterpanel").classList.toggle("open");
  $("#moreFilters").setAttribute("aria-expanded", open?"true":"false");
};
$("#reset").onclick = () => { Object.assign(state,{q:"",cats:[],f:{},anyWithin:true,win:"",member:"",city:"",sort:"deadline",view:"cards",group:false});
  $("#q").value=""; $("#sort").value="deadline"; $("#group").setAttribute("aria-pressed","false");
  setWithin(true);
  $("#msearch").value=""; $("#memberPanel").hidden=true;
  $("#vCards").setAttribute("aria-pressed","true");$("#vTime").setAttribute("aria-pressed","false");$("#vMap").setAttribute("aria-pressed","false");
  $("#vDash").setAttribute("aria-pressed","false");
  syncMember(); renderFacetBar(); update(); };
function setView(v){ state.view=v;
  $("#vCards").setAttribute("aria-pressed",v==="cards"); $("#vTime").setAttribute("aria-pressed",v==="timeline"); $("#vMap").setAttribute("aria-pressed",v==="map"); $("#vDash").setAttribute("aria-pressed",v==="dashboard");
  update(); }
$("#vCards").onclick=()=>setView("cards"); $("#vTime").onclick=()=>setView("timeline"); $("#vMap").onclick=()=>setView("map"); $("#vDash").onclick=()=>setView("dashboard");
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
  $("#mpTitle").textContent = name + ": action list";
  $("#mpSub").innerHTML = `${rows.length} opportunities, <b>${urgent.length}</b> closing within 45 days, ${dated.length} with a fixed date. Ordered by deadline, most urgent first.`;
  const ordered = rows.slice().sort((a,b)=>{
    const au = (a.days!==null && a.days>=0 && a.days<=45)?0:1, bu = (b.days!==null && b.days>=0 && b.days<=45)?0:1;
    if(au!==bu) return au-bu;
    return (a.deadline||"9999").localeCompare(b.deadline||"9999");
  });
  const g = $("#mpGrid"); g.innerHTML = "";
  ordered.forEach((r,i)=>{
    const c=card(r);
    if(r.openAll && !r.people.includes(name)){
      const b=document.createElement("span"); b.className="tag"; b.textContent="open to all";
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
/* facet bar + presets are populated in renderFacetBar()/renderPresets() during init */
$("#mlist").innerHTML = DATA.members.map(m=>`<option value="${esc(m)}">`).join("");
readURL(); state.pq = parseQuery(state.q); syncMember(); renderFacetBar(); renderPresets(); renderQueryStatus(); renderUrgent(); renderMembers(); renderElig(); render(); renderMemberPanel();
$("#msearch").value = state.member;
if("serviceWorker" in navigator && location.protocol.startsWith("http")) navigator.serviceWorker.register("sw.js").catch(()=>{});
</script>
</body>
</html>
"""

n90 = sum(1 for r in rows if r["days"] is not None and 0 <= r["days"] <= 90)
ndated = sum(1 for r in rows if r["deadline"])
out = (TEMPLATE
       .replace("__FACET_TAGS__", json.dumps(FACET_TAGS, ensure_ascii=False))
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
               "display":"standalone","background_color":"#f6f6f4","theme_color":"#0b6e4f",
               "icons":[{"src":"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230b6e4f'/%3E%3Ctext x='16' y='22' font-size='16' font-family='Georgia,serif' font-weight='700' text-anchor='middle' fill='%23ffffff'%3EM%3C/text%3E%3C/svg%3E","sizes":"any","type":"image/svg+xml"}]}, f)
with open(os.path.join(DIR, "sw.js"), "w", encoding="utf-8") as f:
    f.write("""const C='mcp-v3';
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
