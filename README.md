# 24 Bishop Street Seller Presentation

Static, customer-facing listing and pricing presentation for 24 Bishop Street, Natick.

## Local preview

```bash
python3 -m http.server 8788
```

Open `http://127.0.0.1:8788/`.

## Pricing verification

```bash
python3 scripts/verify_pricing.py
```

The validator checks the embedded comparable-sale data, adjustment arithmetic, valuation methods, ranges, and displayed recommendation for internal consistency.

## Evidence and limitations

- `PRICING-VALIDATION.md` records the adversarial pricing review, public corroboration, corrections, confidence and remaining MLS/assessor gates.
- `evidence/` contains before/after desktop and mobile screenshots.
- The seller presentation labels the 1,832-square-foot basis as unmeasured and distinguishes MLS-sourced claims from publicly corroborated facts.
- Confirm the named MLS records, assessor cards, permits and independent floor-area measurement before sending.

The site is GitHub Pages compatible. Publishing is a separate deliberate step.
