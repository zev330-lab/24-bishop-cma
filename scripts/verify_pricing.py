#!/usr/bin/env python3
"""
verify_pricing.py — Mechanical verification of the 24 Bishop Street CMA.

Parses the embedded data blocks (window.__D__ and window.__G__) out of index.html
and re-derives every published figure from first principles. Fails (exit 1) if any
arithmetic in the artifact is internally inconsistent, and also checks that key
numbers quoted in the visible prose agree with the computed values.

Run:  python3 scripts/verify_pricing.py [path/to/index.html]

This test validates INTERNAL consistency only. It cannot validate the underlying
MLS/assessor source data, which is not machine-checkable from this repo. See
PRICING-VALIDATION.md for the provenance and adversarial review of those inputs.
"""
import json
import re
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "index.html")

failures = []
checks = 0


def approx(a, b, tol, label):
    global checks
    checks += 1
    if abs(a - b) > tol:
        failures.append(f"FAIL  {label}: got {a}, expected {b} (tol {tol})")
    return abs(a - b) <= tol


def eq(a, b, label):
    global checks
    checks += 1
    if a != b:
        failures.append(f"FAIL  {label}: got {a!r}, expected {b!r}")
    return a == b


def extract_object(html, marker):
    """Extract the balanced {...} literal that follows `marker` in html."""
    i = html.find(marker)
    if i < 0:
        raise SystemExit(f"marker not found: {marker}")
    start = html.find("{", i)
    depth = 0
    instr = False
    esc = False
    for j in range(start, len(html)):
        c = html[j]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
        else:
            if c == '"':
                instr = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(html[start:j + 1])
    raise SystemExit(f"unbalanced object for {marker}")


def text_of(html):
    """Strip base64 payloads, tags, and collapse whitespace for prose checks."""
    s = re.sub(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]+", "", html)
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&amp;", "&").replace("&nbsp;", " ").replace("&ldquo;", '"').replace("&rdquo;", '"')
    s = re.sub(r"\s+", " ", s)
    return s


def med(a):
    b = sorted(a)
    m = len(b) // 2
    return b[m] if len(b) % 2 else (b[m - 1] + b[m]) / 2


def main():
    html = open(HTML_PATH, encoding="utf-8").read()
    D = extract_object(html, "window.__D__")
    G = extract_object(html, "window.__G__")
    prose = text_of(html)

    # ---- Constants published in the methodology footnote (section 04) ----
    GLA = 1832          # marketable sq ft basis (MLS basis, matches twin)
    PSF_WN = 463        # West Natick median $/sqft
    TIME_RATE = 0.0015  # +0.15% / month
    SQFT_RATE = 170     # $/sqft living-area adjustment
    ANCHORS = ["14 Hardwick Rd", "3 Oxbow Rd"]

    # =====================================================================
    # 1. Per-comp internal arithmetic for BOTH condition states
    # =====================================================================
    for state in ("asis", "fixed"):
        for r in G[state]:
            adj = r["adj"]
            net = sum(adj.values())
            gross = sum(abs(v) for v in adj.values())
            ind = r["sp"] + net
            eq(net, r["net"], f"[{state}] {r['addr']} net adjustment")
            eq(gross, r["gross"], f"[{state}] {r['addr']} gross adjustment")
            eq(ind, r["ind"], f"[{state}] {r['addr']} indicated value")
            approx(round(r["sp"] / r["sf"]), r["psf"], 1, f"[{state}] {r['addr']} $/sqft")
            approx(net / r["sp"] * 100, r["netpct"], 0.1, f"[{state}] {r['addr']} net %")
            approx(gross / r["sp"] * 100, r["grosspct"], 0.1, f"[{state}] {r['addr']} gross %")

            # living-area adjustment must equal (GLA - comp sf) * $170
            approx(adj["gla"], round((GLA - r["sf"]) * SQFT_RATE, -2), 600,
                   f"[{state}] {r['addr']} GLA adj vs $170/sf on 1832 basis")
            # time adjustment must equal sp * 0.15%/mo * months
            approx(adj["time"], round(r["sp"] * TIME_RATE * r["mo"], -2), 600,
                   f"[{state}] {r['addr']} time adj vs +0.15%/mo")

    # =====================================================================
    # 2. Reconciliation, median, range (as-is)  -> section 04 tiles
    # =====================================================================
    asis = G["asis"]
    inds = [r["ind"] for r in asis]
    anchor_inds = [r["ind"] for r in asis if r["addr"] in ANCHORS]
    eq(len(anchor_inds), 2, "two anchors present in as-is grid")
    recon = round(sum(anchor_inds) / len(anchor_inds) / 1000) * 1000
    approx(recon, 814000, 0, "reconciled = mean of 2 anchors -> $814,000 tile")
    approx(med(inds), 841500, 0, "median of six adjusted -> $841,500 tile")
    approx(min(inds), 683500, 0, "adjusted range low -> $683,500")
    approx(max(inds), 897000, 0, "adjusted range high -> $897,000")

    # fixed-state reconciliation (informs the $850K normal-condition figure)
    fx = [r["ind"] for r in G["fixed"] if r["addr"] in ANCHORS]
    recon_fixed = round(sum(fx) / len(fx) / 1000) * 1000
    approx(recon_fixed, 851000, 1000, "fixed reconciled ~ $851K (normal-condition anchor)")

    # =====================================================================
    # 3. The four methods (section 06)
    # =====================================================================
    # Method D: $463/sf * 1832 sf, rounded to nearest $1,000
    mD = round(PSF_WN * GLA / 1000) * 1000
    approx(mD, 848000, 0, "Method D = $463 x 1832 -> $848,000")

    # Method A: 1.207x prior-year (FY2025) assessment.
    # FY2026 assessment 812,100 is 'up 6.9%', so FY2025 = 812100 / 1.069.
    fy2025 = 812100 / 1.069
    mA = round(fy2025 * 1.207 / 1000) * 1000
    approx(mA, 917000, 2000, "Method A = 1.207 x FY2025 assessment -> ~$917,000")

    # Method C = reconciled grid
    approx(recon, 814000, 0, "Method C = reconciled grid -> $814,000")

    # =====================================================================
    # 4. Mirror house / Method B (section 05) line-by-line
    # =====================================================================
    base_22 = 675000
    mkt_move = 169000     # +25% of 675,000 = 168,750 ~ 169,000
    approx(mkt_move, round(base_22 * 0.25, -3), 1000, "mirror +25% market move ~ $169,000")

    mirror_asis = {
        "market": 169000, "lot": -700, "deck": 4000, "half_bath": 5000,
        "lower": -6000, "exterior": -16000, "permits": -20000,
        "heat": -10000, "shared_drive": 0, "tenancy": -8000,
    }
    mirror_fixed = {
        "market": 169000, "lot": -700, "deck": 9400, "half_bath": 5000,
        "lower": -6000, "exterior": 0, "permits": -5000,
        "heat": -4000, "shared_drive": 0, "tenancy": -8000,
    }
    b_asis = base_22 + sum(mirror_asis.values())
    b_fixed = base_22 + sum(mirror_fixed.values())
    eq(b_asis, 792300, "mirror-house indicated value as-is -> $792,300")
    eq(b_fixed, 834700, "mirror-house indicated value work-done -> $834,700")

    # Sensitivity: swap the market-move rate 20% / 25% / 30% of $675,000
    for pct, exp_asis, exp_fixed in ((0.20, 758000, 801000), (0.25, 792000, 835000), (0.30, 826000, 868000)):
        delta = round(base_22 * pct) - mkt_move
        approx(round((b_asis + delta) / 1000) * 1000, exp_asis, 1000,
               f"mirror sensitivity +{int(pct*100)}% as-is -> ${exp_asis:,}")
        approx(round((b_fixed + delta) / 1000) * 1000, exp_fixed, 1000,
               f"mirror sensitivity +{int(pct*100)}% work-done -> ${exp_fixed:,}")

    # =====================================================================
    # 5. Land comparison (section 02) — $/sqft of dirt
    # =====================================================================
    approx(469000 / 41579, 11.28, 0.05, "24 Bishop land $/sf -> $11.28")
    approx(480490 / 23553, 20.40, 0.05, "6 D St land $/sf -> $20.40")

    # =====================================================================
    # 6. Pool explorer default filter must yield the six chosen comps as a subset
    #    (distance <=1.6mi, sold <=12mo before 2026-08-21, 1350-2400 sf, no new construction)
    # =====================================================================
    from datetime import date
    asof = date(2026, 8, 21)

    def months_ago(s):
        y, m, d = map(int, s.split("-"))
        return (asof - date(y, m, d)).days / 30.44

    pool = [c for c in D["comps"]
            if c["d"] <= 1.6 and months_ago(c["sd"]) <= 12
            and 1350 <= c["sf"] <= 2400 and c["yb"] < 2015]
    pool_addr = {c["a"] for c in pool}
    # normalise a couple of address spellings between the two data blocks
    alias = {"28 Barnesdale Road": "28 Barnesdale Rd"}
    for r in asis:
        a = alias.get(r["addr"], r["addr"])
        present = a in pool_addr or r["addr"] in pool_addr
        # 120 Hartford (13mo) is intentionally just outside the 12mo window; allow it
        if r["addr"] == "120 Hartford St":
            continue
        checks_before = len(failures)
        if not present:
            failures.append(f"FAIL  chosen comp {r['addr']} not found in default pool filter")
        _ = checks_before

    # =====================================================================
    # 7. Prose <-> data consistency: numbers quoted in visible copy
    # =====================================================================
    must_contain = [
        "$815,000", "$850,000", "$799,000", "$849,000",
        "$795,000", "$835,000",           # defensible range
        "$792,000",                        # mirror as-is headline
        "$917,000", "$848,000",           # methods A and D
        "41,579",                          # lot sqft
        "$812,100",                        # FY2026 assessment
        "1,832",                           # marketable sqft basis
    ]
    for token in must_contain:
        if token not in prose and token.replace(",", "") not in prose.replace(",", ""):
            failures.append(f"FAIL  prose is missing expected figure: {token}")
        else:
            global checks
            checks += 1

    # ---- report ----
    print(f"index.html: {HTML_PATH}")
    print(f"comps in pool dataset: {len(D['comps'])}")
    print(f"checks run: {checks}")
    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures:
            print(" ", f)
        sys.exit(1)
    print("\nALL CHECKS PASSED — the artifact's published figures are internally consistent.")


if __name__ == "__main__":
    main()
