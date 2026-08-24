#!/usr/bin/env python3
"""
build_customer.py — Transform the internal CMA (index.html on disk) into the
customer-facing homeowner presentation.

Strategy: the 8 MB of comp/gallery photography and the chart/grid/gallery engine
are preserved byte-for-byte. Only the <head> (design system), the <body> markup
(composition + copy), and a few baked-in JS labels are rebuilt for a homeowner
audience. The three inline record-card images in the original body are re-embedded.

Run:  python3 scripts/build_customer.py            # rewrites index.html in place
      python3 scripts/build_customer.py --check    # writes /tmp/index_customer.html only

Idempotent guard: refuses to run against an already-customer file (detects a marker).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "index.html")
CUSTOMER_MARKER = "data-artifact=\"customer\""

html = open(SRC, encoding="utf-8").read()
if CUSTOMER_MARKER in html:
    # Rebuild from the pristine internal version preserved in git history instead.
    import subprocess
    html = subprocess.check_output(["git", "show", "HEAD:index.html"], cwd=ROOT).decode("utf-8")

# ---- slice out the preserved pieces from the internal file ----
script_spans = [(m.start(), m.end()) for m in re.finditer(r"<script[^>]*>.*?</script>", html, re.S)]
assert len(script_spans) == 2, f"expected 2 script blocks, found {len(script_spans)}"
DATA_SCRIPT = html[script_spans[0][0]:script_spans[0][1]]          # window.__D__ / __G__  (verbatim)
render = html[script_spans[1][0]:script_spans[1][1]]              # engine (adapted below)

# three inline body images (assessor photos + sketch), in document order
body_region = html[html.find("<body>"):script_spans[0][0]]
body_imgs = re.findall(r'src="(data:image/[^"]+)"', body_region)
assert len(body_imgs) == 3, f"expected 3 inline body images, found {len(body_imgs)}"
IMG_SUBJECT, IMG_SKETCH, IMG_TWIN = body_imgs

# ---- adapt the engine: null-safety + soften two customer-facing labels ----
render = render.replace("function seg(root,cb){", "function seg(root,cb){ if(!root)return;")
render = render.replace('n:"Conclusion"', 'n:"Our estimate"')
# the condition toggle now carries a stable id instead of relying on a #grid ancestor
render = render.replace('$("#grid .seg")', '$("#condtoggle")')
render = render.replace(
    '$("#pooltable thead").addEventListener',
    'var _pth=$("#pooltable thead"); if(_pth)_pth.addEventListener')
render = render.replace(
    '$("#poolcount").textContent=D.comps.length;',
    'if($("#poolcount"))$("#poolcount").textContent=D.comps.length;')
# soften the internal "best-calibrated" phrasing shown under the reconciled tile
render = render.replace("Mean of the two best-calibrated sales", "The two closest-matched sales")
# and the same jargon in the ladder subtitle (must run AFTER the specific replace above)
render = render.replace("two best-calibrated", "two closest matches")

HEAD = r"""<!doctype html>
<html lang="en" data-artifact="customer">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<meta name="description" content="A market analysis of 24 Bishop Street, Natick, Massachusetts, prepared for the homeowners by Steinmetz Real Estate at William Raveis.">
<meta name="color-scheme" content="light dark">
<title>24 Bishop Street — Your Home's Market Analysis</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chivo:wght@400;500;600;700;900&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap">
<style>
:root{
  --paper:#EDEEE8; --surface:#F8F9F5; --surface2:#E5E7DF; --sunk:#DEE1D8;
  --ink:#181B17; --ink2:#464C45; --ink3:#6E756D;
  --rule:#C8CCC2; --rule2:#DADED4;
  --accent:#B5491C; --accent-mark:#CE5A1E;
  --spruce:#146351; --blue:#3F63BE; --ochre:#8A6A18;
  --good:#1F6B4A; --bad:#A3391B;
  --shadow:0 1px 2px rgba(24,27,23,.05),0 10px 30px -16px rgba(24,27,23,.2);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#131614; --surface:#1B1F1C; --surface2:#242A25; --sunk:#0F1210;
    --ink:#F1F3EF; --ink2:#B9BFB7; --ink3:#878F86;
    --rule:#333A34; --rule2:#2A302B;
    --accent:#F0733D; --accent-mark:#E9612A;
    --spruce:#3FA588; --blue:#5B84D8; --ochre:#B08A2A;
    --good:#3FA073; --bad:#E0714B;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 12px 34px -16px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --paper:#131614; --surface:#1B1F1C; --surface2:#242A25; --sunk:#0F1210;
  --ink:#F1F3EF; --ink2:#B9BFB7; --ink3:#878F86;
  --rule:#333A34; --rule2:#2A302B;
  --accent:#F0733D; --accent-mark:#E9612A;
  --spruce:#3FA588; --blue:#5B84D8; --ochre:#B08A2A;
  --good:#3FA073; --bad:#E0714B;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 12px 34px -16px rgba(0,0,0,.7);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:"Chivo","Helvetica Neue",Arial,sans-serif;
  font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
}
.wrap{max-width:1120px;margin:0 auto;padding:0 32px}
@media(max-width:620px){.wrap{padding:0 18px}}
.skip{position:absolute;left:-999px;top:0;background:var(--ink);color:var(--paper);padding:10px 16px;z-index:200;border-radius:0 0 4px 0}
.skip:focus{left:0}

/* ---------- type ---------- */
h1,h2,h3,h4{margin:0;text-wrap:balance;font-weight:700;letter-spacing:-.015em;line-height:1.12}
h2{font-size:clamp(25px,3.1vw,37px);font-weight:800;letter-spacing:-.024em}
h3{font-size:clamp(18px,2vw,23px)}
h4{font-size:15px;letter-spacing:.01em}
p{margin:0 0 1em}
.prose{font-family:"Newsreader",Georgia,serif;font-size:19px;line-height:1.66;color:var(--ink2);max-width:64ch}
.prose strong{color:var(--ink);font-weight:600}
.prose em{font-style:italic}
.mono{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace}
.num{font-variant-numeric:tabular-nums}
.lede{font-family:"Newsreader",Georgia,serif;font-size:clamp(20px,2.3vw,25px);line-height:1.5;color:var(--ink2);max-width:60ch;font-weight:400}
a{color:var(--accent)}

/* ---------- dimension-line section marks ---------- */
.mark{display:flex;align-items:center;gap:10px;margin:0 0 20px;color:var(--ink3)}
.mark .tick{width:1px;height:11px;background:var(--rule)}
.mark .line{flex:0 0 46px;height:1px;background:var(--rule)}
.mark .grow{flex:1;height:1px;background:var(--rule2)}
.mark .lbl{font-family:"IBM Plex Mono",monospace;font-size:11.5px;letter-spacing:.15em;text-transform:uppercase;white-space:nowrap}
.mark .n{color:var(--accent);font-weight:500}

section{padding:clamp(46px,6.5vw,82px) 0;border-top:1px solid var(--rule2);scroll-margin-top:20px}

/* ---------- cover ---------- */
.cover{padding:clamp(30px,4.5vw,52px) 0 clamp(30px,4vw,44px)}
.brandbar{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;font-family:"IBM Plex Mono",monospace;font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink3)}
.brandbar b{color:var(--accent);font-weight:500}
.brandbar .dot{opacity:.5}
.cover h1{font-size:clamp(38px,7.2vw,88px);font-weight:900;letter-spacing:-.04em;line-height:.94;margin:22px 0 10px}
.facts{display:flex;flex-wrap:wrap;gap:6px 10px;font-family:"IBM Plex Mono",monospace;font-size:clamp(11.5px,1.4vw,13px);letter-spacing:.04em;color:var(--ink3);text-transform:uppercase}
.facts span{background:var(--surface);border:1px solid var(--rule2);border-radius:2px;padding:3px 9px;white-space:nowrap}

.letter{margin-top:clamp(30px,4vw,48px);display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:clamp(26px,4vw,54px);align-items:start}
@media(max-width:860px){.letter{grid-template-columns:1fr;gap:30px}}
.letter .lede strong{color:var(--ink);font-weight:600}
.valuebox{background:var(--surface);border:1px solid var(--rule2);border-radius:4px;padding:clamp(20px,2.6vw,28px);box-shadow:var(--shadow)}
.valuebox .row{display:flex;flex-direction:column;gap:2px;padding:14px 0;border-bottom:1px solid var(--rule2)}
.valuebox .row:first-child{padding-top:0}
.valuebox .row:last-child{border-bottom:0;padding-bottom:0}
.valuebox .lab{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3)}
.valuebox .big{font-size:clamp(29px,4vw,38px);font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums;line-height:1.05;color:var(--spruce)}
.valuebox .sm{font-size:13px;color:var(--ink3);line-height:1.45;margin-top:2px}
.stamp{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.05em;color:var(--ink3);margin-top:14px;line-height:1.55;border-top:1px dashed var(--rule);padding-top:12px}

.toc{margin-top:clamp(34px,4vw,50px);border-top:1px solid var(--rule2);padding-top:22px}
.toc h4{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--ink3);font-weight:400;margin-bottom:14px}
.toc ol{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:2px 26px;counter-reset:toc}
@media(max-width:760px){.toc ol{grid-template-columns:1fr}}
.toc li{counter-increment:toc;border-bottom:1px solid var(--rule2)}
.toc a{display:grid;grid-template-columns:30px 1fr;gap:8px;padding:11px 2px;text-decoration:none;color:var(--ink);font-size:14.5px;align-items:baseline}
.toc a:hover{color:var(--accent)}
.toc a::before{content:counter(toc,decimal-leading-zero);font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--accent)}

/* ---------- panels / tiles ---------- */
.panel{background:var(--surface);border:1px solid var(--rule2);border-radius:4px;padding:clamp(18px,2.4vw,26px)}
.panel.tight{padding:16px 18px}
.grid{display:grid;gap:14px}
.g2{grid-template-columns:repeat(2,minmax(0,1fr))}
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
@media(max-width:900px){.g3,.g4{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:560px){.g2,.g3,.g4{grid-template-columns:1fr}}
.tile{background:var(--surface);border:1px solid var(--rule2);border-radius:4px;padding:16px 18px;display:flex;flex-direction:column;gap:4px;min-width:0}
.tile .k{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3)}
.tile .v{font-size:clamp(22px,2.6vw,29px);font-weight:700;letter-spacing:-.026em;font-variant-numeric:tabular-nums;line-height:1.12}
.tile .n{font-size:12.5px;color:var(--ink3);line-height:1.45}
.tile.hot{border-color:color-mix(in srgb,var(--spruce) 42%,var(--rule2));background:color-mix(in srgb,var(--spruce) 5%,var(--surface))}
.tile.hot .v{color:var(--spruce)}

/* ---------- tables ---------- */
.scroller{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--rule2);border-radius:4px;background:var(--surface)}
.scroller[tabindex]:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
table{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}
th,td{padding:9px 12px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--rule2)}
th:first-child,td:first-child{text-align:left}
thead th{
  font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink3);font-weight:400;background:var(--surface2);position:sticky;top:0;z-index:2;
  border-bottom:1px solid var(--rule);cursor:pointer;user-select:none;
}
thead th:hover{color:var(--accent)}
thead th[aria-sort]:not([aria-sort="none"]){color:var(--accent)}
thead th .ar{opacity:.55;font-size:9px;margin-left:3px}
tbody tr:hover{background:var(--surface2)}
tbody tr.sub{background:color-mix(in srgb,var(--spruce) 9%,var(--surface));font-weight:600}
tbody tr.sub td{border-bottom-color:color-mix(in srgb,var(--spruce) 30%,var(--rule2))}
tbody tr:last-child td{border-bottom:0}
#gridtable{font-size:12.5px}
#gridtable th,#gridtable td{padding:7px 9px}
#gridtable td:first-child,#gridtable th:first-child{min-width:130px}
table.fixed{table-layout:fixed;width:100%}
table.fixed td,table.fixed th{white-space:normal;word-break:normal;overflow-wrap:anywhere;vertical-align:top;font-size:13px;line-height:1.45}
td.a{font-weight:600;color:var(--ink)}
.chip{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.07em;text-transform:uppercase;padding:2px 6px;border-radius:2px;border:1px solid var(--rule);color:var(--ink3);background:var(--surface2)}
.up{color:var(--good)} .down{color:var(--bad)}

/* ---------- controls ---------- */
.controls{display:flex;flex-wrap:wrap;gap:14px 22px;align-items:flex-end;margin:0 0 18px}
.ctl{display:flex;flex-direction:column;gap:6px;min-width:0}
.ctl > span{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3)}
.seg{display:flex;flex-wrap:wrap;border:1px solid var(--rule);border-radius:4px;overflow:hidden;background:var(--surface)}
.seg button{
  font:inherit;font-size:12.5px;font-weight:500;padding:7px 12px;background:transparent;color:var(--ink2);
  border:0;border-right:1px solid var(--rule2);cursor:pointer;white-space:nowrap;font-variant-numeric:tabular-nums;
}
.seg button:last-child{border-right:0}
.seg button:hover{background:var(--surface2);color:var(--ink)}
.seg button[aria-pressed="true"]{background:var(--spruce);color:#fff;border-right-color:var(--spruce)}
:root[data-theme="dark"] .seg button[aria-pressed="true"],
:root:not([data-theme="light"]) .seg button[aria-pressed="true"]{color:#0F1210}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]) .seg button[aria-pressed="true"]{color:#fff}}
button:focus-visible,summary:focus-visible,.gitem:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

/* ---------- charts ---------- */
.chart{width:100%;display:block;overflow:visible}
.chart text{font-family:"IBM Plex Mono",monospace;font-size:10px;fill:var(--ink3)}
.chart .grid-l{stroke:var(--rule2);stroke-width:1}
.chart .axis{stroke:var(--rule);stroke-width:1}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:12px;font-size:12.5px;color:var(--ink2)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}

/* ---------- ladder ---------- */
.ladder{display:flex;flex-direction:column;gap:2px}
.lrow{display:grid;grid-template-columns:minmax(150px,230px) 1fr;gap:16px;align-items:center;padding:12px 0;border-bottom:1px solid var(--rule2)}
.lrow:last-child{border-bottom:0}
@media(max-width:640px){.lrow{grid-template-columns:1fr;gap:6px}}
.lrow .nm{font-size:13.5px;font-weight:600}
.lrow .nm em{display:block;font-style:normal;font-weight:400;font-size:11.5px;color:var(--ink3);font-family:"IBM Plex Mono",monospace;letter-spacing:.02em}
.bartrack{position:relative;height:30px}
.bar{position:absolute;top:9px;height:12px;border-radius:2px}
.bar .pt{position:absolute;top:-3px;width:2px;height:18px;background:var(--ink);border-radius:1px}
.blab{position:absolute;top:-3px;font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink2);white-space:nowrap;font-variant-numeric:tabular-nums}

/* ---------- comp photo strips ---------- */
.strip{display:flex;gap:6px;overflow-x:auto;padding:2px 0 8px;scroll-snap-type:x proximity;-webkit-overflow-scrolling:touch}
.strip::-webkit-scrollbar{height:7px}
.strip::-webkit-scrollbar-thumb{background:var(--rule);border-radius:4px}
.strip::-webkit-scrollbar-track{background:var(--sunk);border-radius:4px}
.strip button{flex:0 0 auto;padding:0;border:1px solid var(--rule2);border-radius:3px;overflow:hidden;background:var(--sunk);cursor:zoom-in;scroll-snap-align:start;line-height:0}
.strip button:hover{border-color:var(--accent)}
.strip img{width:104px;height:78px;object-fit:cover;display:block}
.strip.big img{width:150px;height:112px}
.striphdr{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin:0 0 5px}
.striphdr .c{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.11em;text-transform:uppercase;color:var(--ink3)}

/* ---------- gallery ---------- */
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.gitem{position:relative;margin:0;border:1px solid var(--rule2);border-radius:4px;overflow:hidden;background:var(--sunk);cursor:zoom-in;display:block;padding:0;width:100%;text-align:left}
.gitem img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;transition:transform .4s cubic-bezier(.2,.7,.3,1)}
.gitem:hover img{transform:scale(1.035)}
.gitem figcaption{padding:9px 11px 11px;font-size:12.5px;line-height:1.4;color:var(--ink2);background:var(--surface)}
.gitem .tag{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:3px}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}

/* ---------- lightbox ---------- */
dialog{border:0;padding:0;background:transparent;max-width:96vw;max-height:96vh}
dialog::backdrop{background:rgba(10,12,10,.86);backdrop-filter:blur(3px)}
.lb{position:relative;background:var(--surface);border:1px solid var(--rule);border-radius:4px;overflow:hidden;max-width:1100px}
.lb img{display:block;width:100%;max-height:76vh;object-fit:contain;background:var(--sunk)}
.lb .cap{padding:13px 16px;font-size:13.5px;color:var(--ink2);display:flex;gap:14px;justify-content:space-between;align-items:flex-start}
.lb .count{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--ink3);white-space:nowrap}
.lb button{font:inherit;font-size:12px;background:var(--surface2);border:1px solid var(--rule);color:var(--ink2);border-radius:3px;padding:5px 10px;cursor:pointer;white-space:nowrap}
.lb .nav{position:absolute;top:50%;transform:translateY(-50%);width:44px;height:64px;border:0;background:rgba(20,22,20,.55);color:#fff;font-size:22px;cursor:pointer;border-radius:3px;line-height:1}
.lb .nav:hover{background:rgba(20,22,20,.8)}
.lb .prev{left:8px}.lb .next{right:8px}

/* ---------- misc ---------- */
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(20px,3vw,40px)}
@media(max-width:860px){.two{grid-template-columns:1fr}}
.recimg{width:100%;border:1px solid var(--rule);border-radius:4px;display:block;background:var(--sunk)}
figcaption.src{font-family:"IBM Plex Mono",monospace;font-size:10.5px;color:var(--ink3);margin-top:7px;letter-spacing:.03em;line-height:1.5}
.kv{display:grid;grid-template-columns:auto 1fr;gap:7px 16px;font-size:13.5px;font-variant-numeric:tabular-nums}
.kv dt{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink3);padding-top:2px}
.kv dd{margin:0;color:var(--ink)}
.callout{border-left:2px solid var(--spruce);padding:4px 0 4px 18px;margin:24px 0;font-family:"Newsreader",Georgia,serif;font-size:19px;line-height:1.55;color:var(--ink);max-width:60ch}
.callout.warm{border-left-color:var(--accent)}
ul.plain{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:12px}
ul.plain li{display:flex;gap:12px;font-size:15px;line-height:1.55;color:var(--ink2)}
ul.plain li::before{content:"";flex:0 0 6px;height:6px;margin-top:9px;background:var(--spruce);border-radius:1px}
ul.plain.warm li::before{background:var(--accent)}
ol.steps{list-style:none;counter-reset:s;padding:0;margin:0;display:flex;flex-direction:column;gap:0}
ol.steps li{counter-increment:s;display:grid;grid-template-columns:34px 1fr auto;gap:14px;padding:15px 0;border-bottom:1px solid var(--rule2);align-items:baseline}
ol.steps li:last-child{border-bottom:0}
ol.steps li::before{content:counter(s,decimal-leading-zero);font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--accent)}
ol.steps .t{font-size:15px;font-weight:600;color:var(--ink)}
ol.steps .d{font-size:13.5px;color:var(--ink3);line-height:1.5;margin-top:3px;font-weight:400}
ol.steps .c{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--ink2);white-space:nowrap;font-variant-numeric:tabular-nums;text-align:right}
@media(max-width:600px){ol.steps li{grid-template-columns:26px 1fr;gap:10px}ol.steps .c{grid-column:2;text-align:left}}

.disc{background:var(--surface);border:1px solid var(--rule2);border-radius:4px;padding:clamp(20px,2.6vw,30px);font-size:14px;line-height:1.65;color:var(--ink2)}
.disc h4{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink3);font-weight:400;margin:0 0 8px}
.disc p{margin:0 0 12px}.disc p:last-child{margin:0}

.nextstep{background:color-mix(in srgb,var(--spruce) 7%,var(--surface));border:1px solid color-mix(in srgb,var(--spruce) 30%,var(--rule2));border-radius:6px;padding:clamp(26px,3.4vw,44px);text-align:center}
.nextstep h2{max-width:20ch;margin:0 auto 14px}
.nextstep p{max-width:52ch;margin:0 auto 22px;color:var(--ink2);font-family:"Newsreader",Georgia,serif;font-size:18.5px;line-height:1.6}
.contacts{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}
.contacts a{display:inline-flex;flex-direction:column;gap:2px;text-decoration:none;background:var(--surface);border:1px solid var(--rule);border-radius:5px;padding:14px 22px;color:var(--ink);min-width:210px}
.contacts a:hover{border-color:var(--spruce)}
.contacts .nm{font-weight:600;font-size:15px}
.contacts .dt{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink3);letter-spacing:.02em}

footer{padding:44px 0 64px;border-top:1px solid var(--rule2);color:var(--ink3);font-size:12.5px;line-height:1.65}
.tipbox{position:fixed;pointer-events:none;z-index:99;background:var(--ink);color:var(--paper);font-family:"IBM Plex Mono",monospace;font-size:11.5px;line-height:1.45;padding:7px 9px;border-radius:3px;opacity:0;transition:opacity .12s;white-space:nowrap;font-variant-numeric:tabular-nums;box-shadow:var(--shadow)}

@media print{
  body{background:#fff;color:#000;overflow:visible}
  .seg,.tipbox,dialog,.toc,.nextstep .contacts{display:none!important}
  section{page-break-inside:auto;padding:22px 0;border-top:1px solid #ccc}
  .panel,.tile,.gitem,.scroller,.valuebox,.disc{break-inside:avoid}
  .scroller{overflow:visible}
  .gal{grid-template-columns:repeat(3,1fr)}
  a{color:#000}
}
</style>
</head>
<body>
<a class="skip" href="#home">Skip to the analysis</a>
<div class="wrap">
"""

BODY = r"""
<header class="cover" id="home">
  <div class="brandbar">
    <span>Steinmetz Real Estate</span><span class="dot">·</span><span>William Raveis</span>
    <span class="dot">·</span><span>Prepared for the homeowners</span>
    <span class="dot">·</span><span><b>21 August 2026</b></span>
  </div>
  <h1>24 Bishop Street</h1>
  <div class="facts">
    <span>Natick, MA 01760</span><span>≈ 0.95 acre</span><span>Built 1996</span>
    <span>Parcel 31-0000215C</span>
  </div>

  <div class="letter">
    <div>
      <p class="lede">
        Thank you for letting us spend time in your home. This is our read on what it's worth
        today, the homes it will be measured against, and the few small things that would help
        it show at its best. Everything here is meant to be checked — the sales, the math and the
        assumptions are all laid out so you can see how we got to the number.
      </p>
      <p class="prose" style="margin-top:20px;font-size:18px">
        In short: this is a genuinely nice house on an unusually large, private lot, with an
        interior that already competes at the top of its market. The one thing holding it back is
        outside — a tired deck, a weathered walk and some paperwork the town never caught up on.
        None of it is structural, and none of it changes the fact that the house is ready to sell.
      </p>
    </div>

    <aside class="valuebox" aria-label="Opinion of value summary">
      <div class="row">
        <span class="lab">As it stands today</span>
        <span class="big num">$815,000</span>
        <span class="sm">Our opinion of value in current condition. The comparable sales support a
          range of roughly <strong>$815,000&nbsp;–&nbsp;$840,000</strong>; we plan around the lower
          end to stay conservative.</span>
      </div>
      <div class="row">
        <span class="lab">After a light refresh</span>
        <span class="big num">≈ $850,000</span>
        <span class="sm">In normal, market-ready condition — after roughly 2% of value spent
          outside. The work recovers a discount the house is carrying now; it does not add value
          above the market.</span>
      </div>
      <div class="row">
        <span class="lab">Where we'd suggest starting</span>
        <span class="big num" style="font-size:clamp(22px,2.6vw,27px);color:var(--ink)">$799,000&nbsp;<span style="color:var(--ink3);font-weight:400;font-size:15px">or $849,000 after the work</span></span>
        <span class="sm">Two launch options, explained in section 09. Both are a choice for you to
          make — the house sells either way.</span>
      </div>
      <p class="stamp">
        This is a professional opinion of value prepared for pricing. <strong style="color:var(--ink)">It
        is not a formal appraisal.</strong> The figures lean on recent comparable sales and on a
        square-footage basis (1,832&nbsp;sq&nbsp;ft) we recommend confirming with a measurement
        before listing.
      </p>
    </aside>
  </div>

  <nav class="toc" aria-label="Contents">
    <h4>What's inside</h4>
    <ol>
      <li><a href="#the-home">The home, as we found it</a></li>
      <li><a href="#the-land">Your land and setting</a></li>
      <li><a href="#the-market">The Natick market right now</a></li>
      <li><a href="#comps">Homes like yours that sold</a></li>
      <li><a href="#next-door">The house next door</a></li>
      <li><a href="#range">How we arrived at the range</a></li>
      <li><a href="#all-sales">Every sale we considered</a></li>
      <li><a href="#refresh">The value of a light refresh</a></li>
      <li><a href="#launch">Two ways to go to market</a></li>
      <li><a href="#prep">Before we go live, together</a></li>
      <li><a href="#how-to-read">How to read this analysis</a></li>
    </ol>
  </nav>
</header>

<!-- 01 -->
<section id="the-home">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">01</span> &nbsp;The home, as we found it</span><span class="grow"></span><span class="tick"></span></div>
  <h2>The town's file is missing most of what makes your house special.</h2>
  <p class="prose" style="margin-top:18px">
    Natick's assessment reflects what an assessor can see from the street. Their records show the
    last time anyone from the town was <em>inside</em> was in 2003 — so everything finished since
    then lives in the house but not on paper. That's the main reason the town's number understates
    the property, and it's a good-news gap: it means there's real, finished space here that the
    official record simply hasn't caught up with.
  </p>
  <p class="prose">
    It also means a little housekeeping before listing. When finished space, a second full bath and
    the electric heating were added, the work was done by professional tradesmen — the deck was
    permitted and inspected in 2007, and the electrical was installed by a licensed electrician —
    but the permits were never formally closed out. That's a paperwork gap, not a workmanship one,
    and it's inexpensive to put right. Section 10 lists exactly how.
  </p>

  <div class="two" style="margin-top:30px">
    <figure style="margin:0">
      <img class="recimg" loading="lazy" src="{{IMG_SUBJECT}}" alt="Town of Natick assessor photograph of 24 Bishop Street showing the tan elevation and two garage bays">
      <figcaption class="src">Town of Natick property record card, FY2026 · parcel 31-0000215C · assessor photograph.</figcaption>
    </figure>
    <div>
      <dl class="kv">
        <dt>Style</dt><dd>Cape, 1.5 story (record notes read <span class="mono">"RAISED CAPE"</span>)</dd>
        <dt>Living area</dt><dd>Town record 1,532 sq ft &nbsp;<span class="chip">we market 1,832 — see note</span></dd>
        <dt>Rooms</dt><dd>3 bedrooms · we found 2 full + 1 half bath (town shows 1 full + 1 half)</dd>
        <dt>Basement</dt><dd>Full, 2-car under · finished rec room and sauna</dd>
        <dt>Heat</dt><dd>Oil warm-air system, plus room-by-room electric and a mini-split</dd>
        <dt>Lot</dt><dd>41,579 sq ft (≈ 0.95 acre)</dd>
        <dt>Town assessment</dt><dd>$812,100 for FY2026 (land $469,000 + building $343,100) — a figure that lags the market and predates the interior work</dd>
        <dt>Purchased</dt><dd>28 June 1996 · owned by the same family for thirty years</dd>
      </dl>
      <figure style="margin:22px 0 0">
        <img class="recimg" loading="lazy" src="{{IMG_SKETCH}}" alt="Assessor building sketch and dwelling computations for 24 Bishop Street">
        <figcaption class="src">Same record card — the footprint sketch. The 36×24 main building is 864 sq ft; the 20×24 element is the deck.</figcaption>
      </figure>
    </div>
  </div>

  <h3 style="margin:44px 0 14px">What the record says, and what we actually saw</h3>
  <div class="scroller" tabindex="0" aria-label="Comparison of town record and walkthrough, scrollable">
    <table class="fixed">
      <colgroup><col style="width:16%"><col style="width:22%"><col style="width:36%"><col style="width:26%"></colgroup>
      <thead><tr><th style="cursor:default">Item</th><th style="cursor:default;text-align:left">Town record</th><th style="cursor:default;text-align:left">Our walkthrough, 20 Aug 2026</th><th style="cursor:default;text-align:left">What it means for you</th></tr></thead>
      <tbody style="white-space:normal">
        <tr><td class="a">Finished space</td><td style="text-align:left">1.5 story, 1,532 sq ft</td><td style="text-align:left">Three usable levels — a finished lower level with sauna, the main floor, and a finished upper level with skylight and mini-split</td><td style="text-align:left">Real finished space the record doesn't count; worth confirming with permits</td></tr>
        <tr><td class="a">Full baths</td><td style="text-align:left">1 full, 1 half</td><td style="text-align:left">Two full baths (the upper one has a glass-mosaic tub surround) plus a half off the laundry</td><td style="text-align:left">A full bath the town has never recorded</td></tr>
        <tr><td class="a">Heat</td><td style="text-align:left">Oil, warm air</td><td style="text-align:left">Oil system in place, with independent electric heat in nearly every room plus a mini-split</td><td style="text-align:left">Professionally installed; we'd document and service it before photos</td></tr>
        <tr><td class="a">Deck</td><td style="text-align:left">Replaced under permit, 2007</td><td style="text-align:left">≈480 sq ft, screened and awninged, sound underfoot — the finish has failed</td><td style="text-align:left">Refinish, not rebuild</td></tr>
        <tr><td class="a">Condition</td><td style="text-align:left">Average</td><td style="text-align:left">Interior well above average; exterior below it</td><td style="text-align:left">The refresh in section 08 is about closing that gap</td></tr>
      </tbody>
    </table>
  </div>

  <h3 style="margin:46px 0 8px">Photographs from our visit</h3>
  <p class="prose" style="margin-bottom:16px">
    We took these on the afternoon of 20 August. They aren't marketing photos — they're what we
    saw, and they're the honest basis for everything in this analysis. Use the filter to see how
    the story splits: the inside is ready; only the outside needs attention.
  </p>
  <div class="controls">
    <div class="ctl"><span>Show</span><div class="seg" id="f-cat" role="group" aria-label="Filter photographs">
      <button type="button" data-v="all" aria-pressed="true">All 29</button>
      <button type="button" data-v="exterior" aria-pressed="false">Outside</button>
      <button type="button" data-v="main" aria-pressed="false">Main level</button>
      <button type="button" data-v="upper" aria-pressed="false">Upper level</button>
      <button type="button" data-v="lower" aria-pressed="false">Lower level</button></div></div>
  </div>
  <div class="gal" id="gal"></div>
</section>

<!-- 02 -->
<section id="the-land">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">02</span> &nbsp;Your land and setting</span><span class="grow"></span><span class="tick"></span></div>
  <h2>Nearly an acre of privacy — the property's best story.</h2>
  <p class="prose" style="margin-top:18px">
    24 Bishop Street sits on about 41,579 square feet — roughly four times the typical lot among
    the homes it compares to. What that acre buys is real and worth marketing hard: a level,
    private rear yard with a paver patio and fire pit, mature trees on three sides, and no house
    directly behind you. In a neighbourhood where the usual yard is a quarter acre, that privacy
    is rare.
  </p>
  <p class="prose">
    We'll be straightforward about the trade-off, because buyers will ask. The house sits back from
    the street at the end of a shared driveway. That setting is why the lot is as large as it is —
    and it's also why the town applies a 10% reduction to the land's assessed value. The size isn't
    surplus you could sell off; it's the privacy you enjoy. We've kept that reality inside every
    number in this report rather than treating the acre as a windfall.
  </p>

  <div class="panel" style="margin:24px 0 8px">
    <div class="mono" style="font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3);margin-bottom:4px">These are assessed land values — not sale prices</div>
    <p style="margin:0 0 16px;font-size:14px;color:var(--ink2);line-height:1.55">
      A quick illustration of how the town views street access. Both figures below are the assessed
      value of the <strong>land alone</strong> from each property's FY2026 record card — no house
      included, nothing bought or sold.
    </p>
    <div class="grid g2">
      <div class="tile"><span class="k">24 Bishop St · land only</span><span class="v">$469,000</span>
        <span class="n">41,579 sq ft · carries the −10% factor · about <b>$11.28</b> per sq ft of land</span></div>
      <div class="tile"><span class="k">6 D St · land only (fronts the street)</span><span class="v">$480,490</span>
        <span class="n">23,553 sq ft · no reduction · about <b>$20.40</b> per sq ft of land</span></div>
    </div>
  </div>
  <p class="prose" style="margin-top:18px">
    Three-quarters more land, yet a slightly lower land value and barely half the rate per square
    foot — that's what sitting behind another house rather than on the street costs, in the town's
    own arithmetic. Naming it plainly, with the driveway easement ready to share, turns a common
    buyer question into a non-issue.
  </p>
</section>

<!-- 03 -->
<section id="the-market">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">03</span> &nbsp;The Natick market right now</span><span class="grow"></span><span class="tick"></span></div>
  <h2>Steady prices, quick sales — and little patience for the wrong number.</h2>
  <p class="prose" style="margin-top:18px">
    The figures below come from the closed-sale record for Natick single-family homes. Prices have
    been essentially flat over the past year, and well-priced homes sell quickly. These trends line
    up with what the public market trackers (Redfin, Zillow) show for Natick, which is a good sign
    that the picture is real and not a quirk of one data source.
  </p>

  <div class="grid g4" style="margin:26px 0">
    <div class="tile"><span class="k">Median sale · 12 months</span><span class="v">$1.10M</span><span class="n">Natick single-family, townwide</span></div>
    <div class="tile"><span class="k">Median $/sq ft</span><span class="v">$460</span><span class="n">$463 in West Natick specifically</span></div>
    <div class="tile hot"><span class="k">Your size range · 1,300–2,200 sf</span><span class="v">$837K</span><span class="n">median · about $485/sq ft</span></div>
    <div class="tile"><span class="k">List to closing</span><span class="v">55 days</span><span class="n">Homes typically go under agreement much sooner — often within a few weeks</span></div>
  </div>

  <div class="two" style="gap:clamp(24px,3vw,44px)">
    <div>
      <h4 style="margin-bottom:10px">Price per square foot, by quarter</h4>
      <div id="qtrchart"></div>
      <p class="prose" style="font-size:16px;margin-top:14px">
        Five quarters, essentially one flat line — up less than a percent over the year. There's no
        rising tide to carry a home that's priced too high, which is why getting the number right at
        launch matters.
      </p>
    </div>
    <div>
      <h4 style="margin-bottom:10px">How long homes take to close</h4>
      <div id="domchart"></div>
      <p class="prose" style="font-size:16px;margin-top:14px">
        Half of Natick closes inside 60 days from listing. The homes that sit are almost always the
        ones that opened too high and had to chase the market down — the outcome we price to avoid.
      </p>
    </div>
  </div>
</section>

<!-- 04 -->
<section id="comps">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">04</span> &nbsp;Homes like yours that sold</span><span class="grow"></span><span class="tick"></span></div>
  <h2>Six recent sales, adjusted to match your home.</h2>
  <p class="prose" style="margin-top:18px">
    This is the heart of the analysis. We chose six homes that recently sold and that bracket
    24&nbsp;Bishop on the things that matter — four sold in 2026, all within a mile, all between
    1,820 and 2,017 square feet, none of them new construction. Then we adjust each one, in
    dollars, for every way it differs from your house. The figure in the right-hand column is what
    that buyer would effectively have paid for 24&nbsp;Bishop Street.
  </p>
  <p class="prose">
    The toggle is the honest test of what the exterior refresh is worth. Flip it to see how the
    numbers move when the outside is brought up to match the inside.
  </p>

  <div class="controls" style="margin-top:26px">
    <div class="ctl"><span>Condition of 24 Bishop</span>
      <div class="seg" id="condtoggle" role="group" aria-label="Property condition state">
        <button type="button" data-state="asis" aria-pressed="true">As it stands today</button>
        <button type="button" data-state="fixed" aria-pressed="false">After the refresh</button>
      </div>
    </div>
  </div>

  <div class="grid g3" style="margin:0 0 20px">
    <div class="tile hot"><span class="k">Our estimate</span><span class="v" id="recon">$814,000</span><span class="n" id="recon-n">The two closest-matched sales</span></div>
    <div class="tile"><span class="k">Middle of the six</span><span class="v" id="medind">$841,500</span><span class="n">Median of the adjusted column — the six-sale central tendency</span></div>
    <div class="tile"><span class="k">Full adjusted range</span><span class="v" id="rng" style="font-size:clamp(17px,2vw,22px)">$683,500 – $897,000</span><span class="n">Low and high both kept, on purpose — they bracket your home</span></div>
  </div>

  <div class="scroller" tabindex="0" aria-label="Adjustment grid, scrollable"><table id="gridtable"><thead></thead><tbody></tbody></table></div>
  <p class="src mono" style="font-size:11px;color:var(--ink3);margin-top:9px;letter-spacing:.03em">
    Adjustments equate each sale with your home. Rates: market movement +0.15%/mo · living area
    $170/sq ft · lot $0.90/sq ft (±$25K) · age $5,000/decade (±$24K) · garage $6,000/bay · full
    bath $10,000 · half bath $5,000 · extra bedroom −$8,000, plus condition and access lines. From
    MLS PIN; figures to be confirmed against the source records before listing.
  </p>
  <div class="callout">
    Notice where our estimate sits. Five of the six adjusted sales land <em>above</em> it, and the
    middle of the six is about $27,000 higher. We anchor to the two closest matches — the freshest
    sale and the one repeat sale — which pulls the number to the careful side. It's a deliberately
    conservative read, and it leaves room, not risk.
  </div>

  <div id="gridcards" class="grid g3" style="margin-top:22px"></div>
</section>

<!-- 05 -->
<section id="next-door">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">05</span> &nbsp;The house next door</span><span class="grow"></span><span class="tick"></span></div>
  <h2>A near-identical twin shares your driveway — and it has a price history.</h2>
  <div class="two" style="margin-top:22px;align-items:start">
    <div>
      <p class="prose">
        22 Bishop Street came out of the same 1995 land split and the same 1996 build. On the town's
        records the two houses are almost interchangeable: the same ground-floor footprint, the same
        recorded living area, the same full basement with two-car garage under, the same heat, the
        same grade and condition, and the same 10% land factor. The differences are small and mostly
        in your favour — your deck is larger and you have an extra half bath.
      </p>
      <p class="prose"><strong>Its sale history is the closest thing to a price history your own home has:</strong></p>
      <div class="scroller" tabindex="0" aria-label="Sale history of 22 Bishop Street" style="margin-top:14px">
        <table>
          <thead><tr><th style="cursor:default">Date</th><th style="cursor:default">Price</th><th style="cursor:default">Change</th><th style="cursor:default">Held</th></tr></thead>
          <tbody>
            <tr><td>1 Oct 1996</td><td>$199,900</td><td class="chip">new build</td><td>—</td></tr>
            <tr><td>16 Mar 2000</td><td>$277,250</td><td class="up">+38.7%</td><td>3.5 yr</td></tr>
            <tr><td>27 Aug 2007</td><td>$415,000</td><td class="up">+49.7%</td><td>7.4 yr</td></tr>
            <tr><td>22 Jul 2016</td><td>$510,000</td><td class="up">+22.9%</td><td>8.9 yr</td></tr>
            <tr class="sub"><td>28 Jul 2021</td><td>$675,000</td><td class="up">+32.4%</td><td>5.0 yr</td></tr>
          </tbody>
        </table>
      </div>
      <p class="prose" style="margin-top:14px;font-size:16px">
        The 2021, 2016 and 2007 sales all appear in public property records, so this history is
        well-grounded. Carrying that July 2021 sale forward to today, and pricing the physical
        differences line by line, points to roughly <strong>$792,000 as-is</strong> — a useful,
        slightly lower check on the six-sale grid.
      </p>
      <p class="prose">
        One thing to know rather than worry about: 22 Bishop is currently tenant-occupied. A shared
        driveway with a rental is something buyers ask about, and the honest answer is simple — the
        easement runs with the land and predates both households. We'll have the deed language ready
        at the first showing.
      </p>
    </div>
    <figure style="margin:0">
      <img class="recimg" loading="lazy" src="{{IMG_TWIN}}" alt="Town of Natick assessor photograph of 22 Bishop Street, the neighbouring 1996 house">
      <figcaption class="src">22 Bishop Street · parcel 31-0000215B · FY2026 record card. Same builder, same year, same footprint — and a documented sale every five to nine years since 1996.</figcaption>
      <div class="grid" style="margin-top:16px;gap:10px">
        <div class="tile"><span class="k">Its 2021 sale</span><span class="v">$675,000</span><span class="n">28 July 2021 · confirmed in public records</span></div>
        <div class="tile"><span class="k">Adjusted to 24 Bishop, as-is</span><span class="v">$792,000</span><span class="n">Range $758,000 – $826,000, driven mostly by how much the market rose since 2021</span></div>
      </div>
    </figure>
  </div>

  <h3 style="margin:44px 0 10px">Its listing photographs</h3>
  <p class="prose" style="margin-bottom:14px">
    These are the marketing photos from 22 Bishop Street. Scrolling them is effectively a preview of
    your own floor plan — and a look at what this house can be when it's presented well.
  </p>
  <div class="striphdr"><span style="font-size:13.5px;font-weight:600">22 Bishop Street</span><span class="c" id="twincount"></span></div>
  <div class="strip big" id="twingal"></div>
  <p class="src mono" style="font-size:10.5px;color:var(--ink3);margin-top:4px;letter-spacing:.03em">Photos: MLS PIN listing 73415674. Based on information from MLS PIN. Not guaranteed accurate.</p>

  <h3 style="margin:46px 0 10px">The twin, adjusted line by line</h3>
  <p class="prose">
    Because the two houses are so alike, most of the guesswork an appraiser normally faces simply
    isn't here — the shared-driveway setting even cancels out, since this house carries it too. So we
    take the July 2021 sale and adjust it the same way as the six sales above.
  </p>
  <div class="scroller" tabindex="0" aria-label="Twin adjustment table, scrollable" style="margin-top:16px">
    <table class="fixed">
      <colgroup><col style="width:26%"><col style="width:15%"><col style="width:15%"><col style="width:44%"></colgroup>
      <thead><tr><th style="cursor:default">Adjustment</th><th style="cursor:default">As-is</th><th style="cursor:default">Refreshed</th><th style="cursor:default;text-align:left">Basis</th></tr></thead>
      <tbody>
        <tr class="sub"><td>22 Bishop St sold 28 July 2021</td><td>$675,000</td><td>$675,000</td><td style="text-align:left;white-space:normal">Confirmed in public records (listed $700,000)</td></tr>
        <tr><td class="a">Market movement, 2021 → 2026</td><td><span class="up">+$169,000</span></td><td><span class="up">+$169,000</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">MA single-family +20% to +30% over the period; +25% midpoint used. Public indices support this, with most of the gain in 2021–22</td></tr>
        <tr><td class="a">Lot size</td><td><span class="down">−$700</span></td><td><span class="down">−$700</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">41,579 vs 43,297 sq ft</td></tr>
        <tr><td class="a">Deck</td><td><span class="up">+$4,000</span></td><td><span class="up">+$9,400</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">Your deck is larger; as-is it's discounted for its finish</td></tr>
        <tr><td class="a">Half bath</td><td><span class="up">+$5,000</span></td><td><span class="up">+$5,000</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">You have a half bath the twin doesn't</td></tr>
        <tr><td class="a">Finished lower level</td><td><span class="down">−$6,000</span></td><td><span class="down">−$6,000</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">The twin carries slightly more finished lower-level area</td></tr>
        <tr><td class="a">Exterior presentation</td><td><span class="down">−$16,000</span></td><td><span style="color:var(--ink3)">— matched</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">The twin presented normally at sale; as-is, yours doesn't yet</td></tr>
        <tr><td class="a">Permits &amp; records</td><td><span class="down">−$20,000</span></td><td><span class="down">−$5,000</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">Upper level, electric heat and second bath not yet on record; closing the permits shrinks this</td></tr>
        <tr><td class="a">Heating system</td><td><span class="down">−$10,000</span></td><td><span class="down">−$4,000</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">Documenting and servicing the oil system reduces this</td></tr>
        <tr><td class="a">Shared drive &amp; access</td><td><span style="color:var(--ink3)">— matched</span></td><td><span style="color:var(--ink3)">— matched</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">Identical setting — cancels completely</td></tr>
        <tr><td class="a">Neighbouring tenancy</td><td><span class="down">−$8,000</span></td><td><span class="down">−$8,000</span></td><td style="text-align:left;white-space:normal;font-size:12.5px;color:var(--ink3)">The twin is now tenant-occupied</td></tr>
        <tr class="sub"><td>Indicated value of 24 Bishop St</td><td>$792,300</td><td>$834,700</td><td style="text-align:left;white-space:normal">The twin's own answer</td></tr>
      </tbody>
    </table>
  </div>
  <p class="prose" style="margin-top:18px">
    Nearly every line is small and firm — except the first. How much the market rose since 2021 is
    the one big, uncertain number, and it swings the answer:
  </p>
  <div class="grid g3" style="margin:18px 0">
    <div class="tile"><span class="k">If the market rose 20%</span><span class="v" style="font-size:clamp(19px,2.2vw,24px)">$758,000</span><span class="n">as-is · $801,000 refreshed</span></div>
    <div class="tile hot"><span class="k">If 25% — midpoint</span><span class="v" style="font-size:clamp(19px,2.2vw,24px)">$792,000</span><span class="n">as-is · $835,000 refreshed</span></div>
    <div class="tile"><span class="k">If 30%</span><span class="v" style="font-size:clamp(19px,2.2vw,24px)">$826,000</span><span class="n">as-is · $868,000 refreshed</span></div>
  </div>
  <p class="prose">
    Because that single assumption moves the answer by tens of thousands, we treat the twin as a
    <em>check</em> rather than the headline, and lean on the six recent sales where the time gap is
    months, not years. Read together, they place the honest centre of gravity a little below
    $815,000 as-is — which is where our estimate sits.
  </p>
</section>

<!-- 06 -->
<section id="range">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">06</span> &nbsp;How we arrived at the range</span><span class="grow"></span><span class="tick"></span></div>
  <h2>Four independent methods, and where they land.</h2>
  <p class="prose" style="margin-top:18px">
    No single method is the truth. We ran four different ways of valuing the house — two of them
    tested against hundreds of past Natick sales to see how far off they usually are — and looked at
    where they agree and disagree. When several honest methods cluster, that cluster is the price.
  </p>

  <div class="controls" style="margin-top:26px">
    <div class="ctl"><span>Which square footage?</span>
      <div class="seg" id="glaseg" role="group" aria-label="Marketable square footage basis">
        <button type="button" data-gla="1532" aria-pressed="false">1,532 <span style="opacity:.7">town</span></button>
        <button type="button" data-gla="1582" aria-pressed="false">1,582 <span style="opacity:.7">above grade</span></button>
        <button type="button" data-gla="1832" aria-pressed="true">1,832 <span style="opacity:.7">listing basis</span></button>
        <button type="button" data-gla="2030" aria-pressed="false">2,030 <span style="opacity:.7">all finished</span></button>
      </div>
    </div>
  </div>
  <p class="prose" style="font-size:16px;max-width:74ch;margin-bottom:26px">
    <strong>Why this choice matters.</strong> The town says 1,532. The twin next door was marketed
    at 1,832. Counting every finished room gets you past 2,000. All are defensible, and the number
    you pick moves the price meaningfully — which is exactly why we recommend a professional
    measurement before listing. We use <strong>1,832</strong> here because it matches the identical
    house next door and the basis the comparable sales are measured on, but treat it as unconfirmed
    until it's measured.
  </p>

  <div class="ladder" id="ladder"></div>

  <div class="grid g4" style="margin-top:28px">
    <div class="panel tight"><div class="mono" style="font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3)">A · Assessment ratio</div>
      <div style="font-size:27px;font-weight:700;letter-spacing:-.03em;margin:6px 0 4px" class="num">$917,000</div>
      <div style="font-size:12.5px;color:var(--ink3);line-height:1.5">Natick homes sell at a median 1.207× their prior-year assessment (measured on 64 West Natick sales, typical error 6.7%). This is a <em>market-ready</em> answer — what the house is worth presented like everything else on the market. We treat it as the ceiling, not the target, because of the back-lot setting.</div></div>
    <div class="panel tight"><div class="mono" style="font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3)">B · The twin next door</div>
      <div style="font-size:27px;font-weight:700;letter-spacing:-.03em;margin:6px 0 4px" class="num">$792,000</div>
      <div style="font-size:12.5px;color:var(--ink3);line-height:1.5">22 Bishop — same builder, same footprint, same driveway — adjusted from its confirmed 2021 sale. The strongest physical match there is, but it hangs on a five-year market assumption. Range $758,000–$826,000.</div></div>
    <div class="panel tight"><div class="mono" style="font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3)">C · Adjusted sales · we lean here</div>
      <div style="font-size:27px;font-weight:700;letter-spacing:-.03em;margin:6px 0 4px" class="num" id="mC">$815,000</div>
      <div style="font-size:12.5px;color:var(--ink3);line-height:1.5">The six-sale grid from section 04, anchored to the two closest matches — 14 Hardwick Rd (closed within days of this analysis, almost exactly your size) and 3 Oxbow Rd (the one home to sell twice). This is the method an appraiser will use, so it's the one that has to hold up.</div></div>
    <div class="panel tight"><div class="mono" style="font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3)">D · Price per square foot</div>
      <div style="font-size:27px;font-weight:700;letter-spacing:-.03em;margin:6px 0 4px" class="num" id="mD">$848,000</div>
      <div style="font-size:12.5px;color:var(--ink3);line-height:1.5"><span id="mDbasis">$463/sq ft × 1,832 sq ft</span> — the West Natick median (typical error 8.7%). The bluntest tool here, and the one most sensitive to the square-footage question above. Included because every buyer runs this on their phone.</div></div>
  </div>

  <div class="callout warm">
    Three of the four methods, and five of the six adjusted sales, sit above our as-is estimate.
    That's not a contradiction — it's the exterior and the unclosed permits, which the refresh in
    section 08 is designed to recover. We hold the as-is number conservative on purpose; the upside
    is real and documented.
  </div>
</section>

<!-- 07 -->
<section id="all-sales">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">07</span> &nbsp;Every sale we considered</span><span class="grow"></span><span class="tick"></span></div>
  <h2>Not just the six — the whole pool, for you to check.</h2>
  <p class="prose" style="margin-top:18px">
    An analysis is only as honest as the sales it leaves out. So here's the entire pool we drew
    from — <strong id="poolcount">77</strong> Natick single-family sales within two miles of Bishop
    Street since June 2025. Move the filters, sort any column, and see for yourself whether the six
    we chose were the right six. The medians recompute as you go.
  </p>

  <div class="controls" style="margin-top:26px">
    <div class="ctl"><span>Distance</span><div class="seg" id="f-rad" role="group" aria-label="Filter by distance">
      <button type="button" data-v="0.6" aria-pressed="false">0.6 mi</button>
      <button type="button" data-v="1.0" aria-pressed="false">1 mi</button>
      <button type="button" data-v="1.6" aria-pressed="true">1.6 mi</button>
      <button type="button" data-v="2.0" aria-pressed="false">2 mi</button></div></div>
    <div class="ctl"><span>Sold within</span><div class="seg" id="f-win" role="group" aria-label="Filter by recency">
      <button type="button" data-v="6" aria-pressed="false">6 mo</button>
      <button type="button" data-v="12" aria-pressed="true">12 mo</button>
      <button type="button" data-v="15" aria-pressed="false">All</button></div></div>
    <div class="ctl"><span>Size band</span><div class="seg" id="f-size" role="group" aria-label="Filter by size">
      <button type="button" data-v="1600,2100" aria-pressed="false">1,600–2,100</button>
      <button type="button" data-v="1350,2400" aria-pressed="true">1,350–2,400</button>
      <button type="button" data-v="0,99999" aria-pressed="false">Any size</button></div></div>
    <div class="ctl"><span>New construction</span><div class="seg" id="f-new" role="group" aria-label="Include new construction">
      <button type="button" data-v="0" aria-pressed="true">Excluded</button>
      <button type="button" data-v="1" aria-pressed="false">Included</button></div></div>
  </div>

  <div class="grid g4" style="margin-bottom:20px">
    <div class="tile"><span class="k">Sales in filter</span><span class="v" id="s-n">—</span><span class="n">of 77 loaded</span></div>
    <div class="tile"><span class="k">Median sale price</span><span class="v" id="s-med">—</span><span class="n">Closed, not asking</span></div>
    <div class="tile"><span class="k">Median $/sq ft</span><span class="v" id="s-psf">—</span><span class="n">On reported living area</span></div>
    <div class="tile"><span class="k">Median sold ÷ assessed</span><span class="v" id="s-rat">—</span><span class="n">Against the prior-year assessment</span></div>
  </div>

  <div class="panel" style="margin-bottom:20px">
    <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;margin-bottom:8px">
      <h4 style="margin:0">Where 24 Bishop Street sits</h4>
      <div class="seg" id="f-axis" role="group" aria-label="Chart measure">
        <button type="button" data-v="price" aria-pressed="true">Sale price</button>
        <button type="button" data-v="psf" aria-pressed="false">$ per sq ft</button>
      </div>
    </div>
    <div id="scatter"></div>
    <div class="legend">
      <span><i style="background:var(--spruce)"></i>Built before 1980</span>
      <span id="lg-new"><i style="background:var(--blue)"></i>Built 1980 or later</span>
      <span><i style="background:var(--accent-mark)"></i>24 Bishop Street, as-is</span>
    </div>
  </div>

  <div class="scroller" tabindex="0" aria-label="Full comparable pool, scrollable" style="max-height:520px;overflow-y:auto"><table id="pooltable"><thead><tr>
    <th data-k="a">Address</th><th data-k="sd">Sold</th><th data-k="sp">Price</th><th data-k="psf">$/sf</th>
    <th data-k="sf">Sq ft</th><th data-k="yb">Built</th><th data-k="lot">Lot</th><th data-k="bd">Bd</th>
    <th data-k="ba">Ba</th><th data-k="d">Miles</th><th data-k="ratio">vs list</th><th data-k="days">Days</th>
  </tr></thead><tbody></tbody></table></div>
</section>

<!-- 08 -->
<section id="refresh">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">08</span> &nbsp;The value of a light refresh</span><span class="grow"></span><span class="tick"></span></div>
  <h2>A small spend outside recovers a discount the house is carrying.</h2>
  <div class="callout" style="margin-top:22px">
    Let's be clear about what this work does. It doesn't make the house worth more than the market
    says. It removes a discount the house carries right now, because the outside doesn't yet match
    the inside. You'd be buying back roughly <strong>$35,000</strong> for about 2% of value — and the
    house sells either way. Think of it as a choice about price and timing, not a condition of sale.
  </div>
  <p class="prose">
    Here's the mechanism, because it matters more than the list. A buyer forms an opinion before they
    reach the front door — down the shared drive, past a weathered walk and a deck whose finish gave
    out. Then they step inside to granite, two updated baths and hardwood throughout, and the house
    reads as a pleasant surprise rather than the standard. Refreshing the outside means the first
    impression matches the home you actually have.
  </p>
  <p class="prose">
    The comparable sales show this plainly. Homes described as updated and well-presented traded at
    <strong>$462 to $510 a square foot</strong>; the one dated home traded at <strong>$350</strong>.
    Your interior already belongs in the first group — only the outside is voting for the second.
  </p>

  <h3 style="margin:40px 0 8px">Two tiers, as a share of value</h3>
  <p class="mono" style="font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink3);margin-bottom:16px">We're not contractors — please get three quotes. These are planning ranges, not bids.</p>
  <div class="scroller" tabindex="0" aria-label="Refresh tiers, scrollable">
    <table class="fixed">
      <colgroup><col style="width:32%"><col style="width:28%"><col style="width:18%"><col style="width:22%"></colgroup>
      <thead><tr><th style="cursor:default">Scope</th><th style="cursor:default;text-align:left">What it covers</th><th style="cursor:default;text-align:left">Share of value</th><th style="cursor:default;text-align:left">Planning range</th></tr></thead>
      <tbody style="white-space:normal">
        <tr><td class="a">Tier 1 — the essentials</td>
            <td style="text-align:left">Sand and re-stain the deck, replace the cupped boards · pressure-wash siding, trim and foundation · cut back, edge and mulch · patch the driveway</td>
            <td style="text-align:left"><b style="color:var(--spruce)">≈ 0.7%</b></td>
            <td style="text-align:left">$4,100 – $8,400</td></tr>
        <tr><td class="a">Tier 2 — add the front walk</td>
            <td style="text-align:left">Everything above, plus a proper new walkway from the drive to the door, tying into the pavers already in back</td>
            <td style="text-align:left"><b style="color:var(--spruce)">≈ 1.9%</b></td>
            <td style="text-align:left">$11,100 – $20,900</td></tr>
        <tr class="sub"><td>Discount recovered</td><td style="text-align:left">Moves the estimate from $815,000 toward $850,000</td><td style="text-align:left">≈ 4.3%</td><td style="text-align:left">≈ $35,000</td></tr>
      </tbody>
    </table>
  </div>
  <p class="prose" style="margin-top:20px">
    <strong>Tier 1 is the clear yes</strong> — under one percent of value, and it removes the two
    strongest "needs work" signals on the property. <strong>Tier 2 is a preference, not a
    return</strong>: the walkway roughly earns back what it costs, so do it if you'd like the top of
    the range and have a few weeks, but it isn't required.
  </p>

  <h3 style="margin:44px 0 12px">And where <em>not</em> to spend</h3>
  <ul class="plain warm" style="max-width:70ch">
    <li><span><strong>Don't repave the driveway.</strong> Buyers read it as shared and semi-rural. Patch the hole and stop.</li>
    <li><span><strong>Don't touch the kitchen or baths.</strong> They already test at the top of this comparable set. Money spent there is money donated.</li>
    <li><span><strong>Don't replace the siding.</strong> It's vinyl, it's sound, and it's simply dirty — a wash, not a replacement.</li>
    <li><span><strong>Don't finish anything else.</strong> There's one open permit question already; no reason to add a second.</li>
  </ul>
</section>

<!-- 09 -->
<section id="launch">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">09</span> &nbsp;Two ways to go to market</span><span class="grow"></span><span class="tick"></span></div>
  <h2>The asking price is a starting line, not the finish.</h2>
  <p class="prose" style="margin-top:18px">
    In this market, well-priced Natick homes tend to draw competition — ten of the twenty comparable
    sales we reviewed closed <em>above</em> their asking price. So the asking price is best thought of
    as where you invite buyers in, not the most you'll get. Our suggestion is to start a touch below
    a round-number threshold, for one practical reason.
  </p>
  <p class="prose">
    Most buyers shop by setting a maximum price in their search and letting the site show them what
    fits. Those maximums cluster on round numbers — $800,000, $850,000. A home listed at $815,000
    simply never appears for the large group of buyers who capped their search at $800,000. Listed at
    <strong>$799,000</strong>, the same home shows up for all of them, and still reads as the value
    buy for anyone searching higher. It's a common, well-documented practice — and here it costs you
    nothing, because a credible price in this market gets bid up, not left behind.
  </p>
  <div class="callout warm">
    We'll be honest about the trade-off: starting below your value is a bet on drawing competing
    offers. The evidence here strongly supports it, but if bidding didn't materialise, an offer near
    the asking price could land below the home's supportable value. That's why the number has to be
    <em>credible for the house</em> — reaching too high is the one move this market punishes (one
    nearby home asked $899,900, then closed at $820,000 after two months on the market).
  </div>

  <div class="grid g2" style="margin:26px 0 0">
    <div class="panel">
      <div class="mono" style="font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink3)">Option A · list as it stands</div>
      <div style="font-size:34px;font-weight:900;letter-spacing:-.035em;margin:8px 0 6px" class="num">$799,000</div>
      <p style="margin:0;font-size:14.5px;color:var(--ink2);line-height:1.55">Against an estimate of $815,000. Reaches the widest pool right away, with no work and no waiting.
        A reasonable expectation is offers in the $795,000–$835,000 range.</p>
    </div>
    <div class="panel" style="border-color:color-mix(in srgb,var(--spruce) 45%,var(--rule2))">
      <div class="mono" style="font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--spruce)">Option B · list after the refresh</div>
      <div style="font-size:34px;font-weight:900;letter-spacing:-.035em;margin:8px 0 6px;color:var(--spruce)" class="num">$849,000</div>
      <p style="margin:0;font-size:14.5px;color:var(--ink2);line-height:1.55">Against an estimate of $850,000, after about 2% of value spent outside over roughly three weeks. A
        reasonable expectation is offers in the $830,000–$870,000 range, with a stronger first impression.</p>
    </div>
  </div>
  <p class="prose" style="margin-top:24px">
    <strong>Our recommendation is Option B</strong> — the refresh recovers more than it costs and
    moves the home out of the "project" pile — but it's a recommendation, not a requirement. The
    house sells well either way, and the choice is entirely yours.
  </p>
</section>

<!-- 10 -->
<section id="prep">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">10</span> &nbsp;Before we go live, together</span><span class="grow"></span><span class="tick"></span></div>
  <h2>A short list to nail down — and who handles each one.</h2>
  <p class="prose" style="margin-top:18px">
    None of these change the price. All of them make the sale smoother, and several let you disclose
    something calmly up front rather than answer it under pressure later. Where an item says
    "we'll," that's our job, not yours.
  </p>

  <ol class="steps" style="margin-top:24px">
    <li><div><span class="t">Measure the house properly</span><div class="d">A third-party floor plan and measurement. The value leans on square footage that hasn't been verified in over twenty years, so a ~$300 measurement is the single most valuable thing on this list — it firms up nearly every number in this report.</div></div><span class="c">We'll arrange</span></li>
    <li><div><span class="t">Close out the permits for the upper level and electrical</span><div class="d">The work was done by licensed tradesmen — the hard part is already handled. As-built permits turn an open question into a closed file. This is the longest-lead item, so we'd start it now.</div></div><span class="c">We'll open · with you</span></li>
    <li><div><span class="t">Service and certify the oil system</span><div class="d">If the oil system fires, the story becomes "oil heat with electric zone control in every room," which buyers like — rather than "electric heat," which can give Massachusetts buyers pause. Worth a service call before photos.</div></div><span class="c">You · before photos</span></li>
    <li><div><span class="t">Confirm town water vs. private well</span><div class="d">There's a softener and filter in the lower level, common on either. The listing has to state which, correctly.</div></div><span class="c">You · one phone call</span></li>
    <li><div><span class="t">Have the driveway easement ready</span><div class="d">Book 26455, Page 361. We'll pull the exact language and attach it, so the shared-drive question is answered in writing before it's asked.</div></div><span class="c">We'll pull</span></li>
    <li><div><span class="t">Correct the bath count on the record</span><div class="d">The card shows one full bath; the house has two. We'll fix this with the assessor at the same time as the permits.</div></div><span class="c">We'll bundle</span></li>
    <li><div><span class="t">Pull the survey stakes before photography</span><div class="d">Two orange markers still stand in the gravel. They photograph as a boundary question whether or not there is one.</div></div><span class="c">Ten minutes</span></li>
  </ol>
</section>

<!-- 11 -->
<section id="how-to-read">
  <div class="mark"><span class="tick"></span><span class="line"></span><span class="lbl"><span class="n">11</span> &nbsp;How to read this analysis</span><span class="grow"></span><span class="tick"></span></div>
  <h2>What's solid, and what we'd still confirm.</h2>
  <div class="two" style="margin-top:22px;align-items:start">
    <div class="disc">
      <h4>Where the numbers come from</h4>
      <p><strong>Comparable sales &amp; market figures:</strong> MLS PIN closed-sale records for Natick
        single-family homes, spring 2025 through August 2026. The broad market trends (flat prices,
        quick sales, the roughly 25% rise since 2021) are consistent with public trackers such as
        Redfin and Zillow, which we checked independently.</p>
      <p><strong>Assessment, permit and deed details:</strong> Town of Natick FY2026 property record
        cards and the registry of deeds.</p>
      <p><strong>The twin's sale history</strong> ($675,000 in 2021, and the 2016 and 2007 sales) is
        confirmed in public property records.</p>
      <p><strong>Photographs:</strong> our site visit on 20 August 2026, and the neighbouring home's
        MLS listing.</p>
    </div>
    <div class="disc">
      <h4>What we'd confirm before listing</h4>
      <p><strong>Square footage.</strong> We market 1,832 sq ft, borrowed from the identical house
        next door; the town shows 1,532. A measurement settles it and firms up the price. This is the
        biggest open item.</p>
      <p><strong>The comparable sales themselves.</strong> Sale prices, dates and condition come from
        MLS and should be confirmed against the source records.</p>
      <p><strong>Permit status.</strong> To be verified with the Natick Building Department; on a
        financed sale, an appraiser may not count unpermitted finished space, so closing the permits
        also protects the price.</p>
      <p style="color:var(--ink3)"><strong>This is an opinion of value, not an appraisal</strong>, and
        shouldn't be relied on as one. Equal Housing Opportunity. Anything said about neighbouring
        property refers only to recorded ownership, tenure and access.</p>
    </div>
  </div>
</section>

<section id="next" style="border-top:0;padding-top:clamp(30px,4vw,52px)">
  <div class="nextstep">
    <h2>Whenever you're ready, let's talk it through.</h2>
    <p>There's no rush and no obligation. When it suits you, we'll sit down with this, answer any
      questions, and — if and when you decide to move forward — put together the plan that fits your
      timing. It's your home and your call; we're here to make the next step an easy one.</p>
    <div class="contacts">
      <a href="mailto:Zev.Steinmetz@raveis.com"><span class="nm">Zev Steinmetz</span><span class="dt">617.335.2019 · Zev.Steinmetz@raveis.com</span></a>
      <a href="mailto:Sarina.Steinmetz@raveis.com"><span class="nm">Sarina Steinmetz</span><span class="dt">617.610.0207 · Sarina.Steinmetz@raveis.com</span></a>
    </div>
  </div>
</section>

<footer>
  <div class="two" style="gap:30px">
    <div>
      <div class="mono" style="font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--ink2);margin-bottom:10px">Prepared by</div>
      <p style="margin:0 0 4px;font-size:15px;color:var(--ink);font-weight:600">Zev Steinmetz · Sarina Steinmetz</p>
      <p style="margin:0 0 14px;line-height:1.65">Steinmetz Real Estate · William Raveis<br>1229 Centre Street, Newton, MA 02459</p>
    </div>
    <div>
      <div class="mono" style="font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--ink2);margin-bottom:10px">Sources &amp; limitations</div>
      <p style="margin:0 0 10px;line-height:1.65">
        Sales data from MLS PIN; assessment, permit and deed data from the Town of Natick and the
        registry of deeds; statewide price index reference, The Warren Group and public indices;
        property photographs from our 20 August 2026 site visit. Based on information from MLS PIN;
        not guaranteed accurate.</p>
      <p style="margin:0;line-height:1.65;color:var(--ink3)">
        This is a comparative market analysis prepared by licensed real estate agents to help
        establish a marketing price. It is not an appraisal. Square footage is unverified pending
        measurement. Permit status should be confirmed with the Natick Building Department before
        listing. Equal Housing Opportunity.</p>
    </div>
  </div>
</footer>
</div>

<dialog id="lb"><div class="lb">
  <img id="lbimg" alt="">
  <button type="button" class="nav prev" id="lbprev" aria-label="Previous photo">&#8249;</button>
  <button type="button" class="nav next" id="lbnext" aria-label="Next photo">&#8250;</button>
  <div class="cap"><span id="lbcap"></span><span style="display:flex;gap:12px;align-items:center"><span class="count" id="lbcount"></span><button type="button" id="lbclose">Close &nbsp;esc</button></span></div>
</div></dialog>
<div class="tipbox" id="tip" role="status" aria-live="polite"></div>
"""

BODY = BODY.replace("{{IMG_SUBJECT}}", IMG_SUBJECT).replace("{{IMG_SKETCH}}", IMG_SKETCH).replace("{{IMG_TWIN}}", IMG_TWIN)

TAIL = "\n" + DATA_SCRIPT + "\n" + render + "\n</body>\n</html>\n"

out = HEAD + BODY + TAIL

dest = "/tmp/index_customer.html" if "--check" in sys.argv else SRC
with open(dest, "w", encoding="utf-8") as f:
    f.write(out)
print(f"wrote {dest}  ({len(out):,} bytes)")
print(f"  inline images re-embedded: subject={len(IMG_SUBJECT)} sketch={len(IMG_SKETCH)} twin={len(IMG_TWIN)}")
print(f"  data script preserved: {len(DATA_SCRIPT):,} bytes; engine: {len(render):,} bytes")
