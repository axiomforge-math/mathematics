"""Shared definitions of the checkers ``verify_*.py`` (separately written recomputation).

Everything here is written from the mathematical definitions in the manuscript
(``paper/``); the original certificate programs (``certify_*.py``) were read only to obtain
the comparison-measure mass vectors, which are data of the proof (manuscript, Table 8).

Rigour conventions
------------------
* Exact rationals: ``fractions.Fraction``.
* Transcendental quantities: Arb balls (python-flint ``arb``/``acb``) at ``ctx.prec``
  bits.  An inequality ``a < b`` between balls is accepted only if Arb certifies it
  (python-flint returns True for ``a < b`` only when it holds for every point of the
  balls).
* ``Checks`` collects named checks; every checker exits with status 1 if a checked
  inequality fails or cannot be certified.

Units: the certificate for 2/11 is computed in the scale u = n (h = 4n, mass m = 4); the
other three in the scale u = h (mass m = 1). See Remark 7.8 of the manuscript.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from fractions import Fraction as Fr
from pathlib import Path

from flint import acb, arb, ctx

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "outputs"  # logs/experiments/outputs
OUT.mkdir(exist_ok=True)

ctx.prec = 256


# ---------------------------------------------------------------------------
# Case parameters (from the manuscripts)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Case:
    name: str
    slug: str
    lam: Fr
    H: int  # h = H n
    C: int  # K = C n
    B: int  # A = B n
    unit: str  # "n" (2/11 manuscript) or "h" (the other two manuscripts)
    delta: Fr  # cut for the profile integral
    # exceptional primes: loss prime P with exponent f (Newton loss), gain prime G with
    # e = v_G(1/lambda)
    P: int
    fP: int
    G: int
    eG: int
    source: str
    claims: dict = field(default_factory=dict)

    @property
    def scale(self) -> int:
        """unit as a multiple of n (1 for n-units, H for h-units)."""
        return 1 if self.unit == "n" else self.H

    @property
    def m(self) -> Fr:  # h / unit
        return Fr(self.H, self.scale)

    @property
    def alpha(self) -> Fr:  # A / unit
        return Fr(self.B, self.scale)

    @property
    def kappa(self) -> Fr:  # K / unit
        return Fr(self.C, self.scale)


CASES: dict[str, Case] = {
    "2/11": Case(
        "2/11", "two-elevenths", Fr(2, 11), 4, 6, 1, "n", Fr(1, 40), 3, 2, 11, 1,
        "original program certify_two_elevenths.py",
        claims={
            "profile_minus_cut_lower": Fr(9, 2),  # int B - 1/5 > 9/2 (n-scale; Table 5)
            "profile_minus_cut_reported": "4.505934466249617",  # printed by certify_two_elevenths.py
            "content_rate_lower": Fr(-2169, 500),  # > -4.338 (n-scale), i.e. -2169/8000 per h^2
            "content_rate_reported": "-4.3370400120",
            "E_reported": "4.4615788049",
            "posint_upper": Fr(602835, 1000000),  # int (W-theta)_+ < 0.602835 (Appendix A.4)
            "analytic_upper": Fr(-49, 10),  # analytic bound < -4.900 (n-scale), i.e. -49/160 per h^2
            "analytic_reported": "-4.9143918336",
        },
    ),
    "2/9": Case(
        "2/9", "two-ninths", Fr(2, 9), 8, 9, 0, "h", Fr(1, 500), 7, 1, 3, 2,
        "original programs certify_two_ninths.py, certify_minus_two_ninths.py",
        claims={
            "profile_minus_cut_reported": "-0.885055234371268",
            "content_rate_lower": Fr(-133, 100),
            "content_rate_reported": "-1.32452749",
            "analytic_upper": Fr(-134, 100),
            "analytic_reported": "-1.3436316775354369",
            "margin_reported": "0.01910",
        },
    ),
    "-2/9": Case(
        "-2/9", "minus-two-ninths", Fr(-2, 9), 4, 7, 1, "h", Fr(1, 500), 11, 1, 3, 2,
        "original programs certify_two_ninths.py, certify_minus_two_ninths.py",
        claims={
            "profile_minus_cut_reported": "0.16730938092710554",
            "content_rate_lower": Fr(-2, 5),
            "content_rate_reported": "-0.38308817",
            "E_reported": "(-1.353843411037, -1.353843411035)",
            "theta_reported": "-4.368300751840826",
            "analytic_upper": Fr(-49, 100),
            "analytic_reported": "-0.4954089410772183",
            "margin_reported": "0.11232",
        },
    ),
    "-2/7": Case(
        "-2/7", "minus-two-sevenths", Fr(-2, 7), 5, 8, 1, "h", Fr(1, 500), 3, 2, 7, 1,
        "original program certify_minus_two_sevenths.py",
        claims={
            "profile_minus_cut_reported": "0.07694503668343355",
            "content_rate_lower": Fr(-521323, 1000000),
            "content_rate_reported": "-0.5213226182796139",
            "E_reported": "(-1.353423362440, -1.353423362439)",
            "theta_reported": "-4.09717011379389",
            "analytic_upper": Fr(-526078, 1000000),
            "analytic_reported": "-0.5260781971006337",
            "margin_reported": "0.004755578821019797",
        },
    ),
}


def vp_frac(x: Fr, p: int) -> int:
    x = Fr(x)
    if x == 0:
        raise ValueError
    v = 0
    a, b = abs(x.numerator), x.denominator
    while a % p == 0:
        a //= p
        v += 1
    while b % p == 0:
        b //= p
        v -= 1
    return v


def check_exceptional_data(case: Case) -> list[str]:
    """Re-derive the exceptional-prime data from lambda (consistency of the table)."""
    lam = case.lam
    msgs = []
    one = Fr(1)
    # loss prime: f = max(0, -v(lam/(1-lam)), -v(1/(1-lam)))
    f = max(0, -vp_frac(lam / (one - lam), case.P), -vp_frac(one / (one - lam), case.P))
    if f != case.fP:
        msgs.append(f"loss prime {case.P}: f={f} != table {case.fP}")
    e = vp_frac(one / lam, case.G)
    if e != case.eG:
        msgs.append(f"gain prime {case.G}: e={e} != table {case.eG}")
    # the gain prime must have no Newton loss, and lambda^{-1} a unit at P
    if min(vp_frac(lam / (one - lam), case.G), vp_frac(one / (one - lam), case.G)) < 0:
        msgs.append(f"gain prime {case.G} also has a Newton loss")
    if vp_frac(one / lam, case.P) != 0:
        msgs.append(f"lambda not a unit at loss prime {case.P}")
    # primes outside {2,P,G} dividing num/den of lam, 1-lam must not exist
    bad = set()
    for q in (lam, one - lam):
        for z in (abs(q.numerator), q.denominator):
            d = 2
            while z > 1:
                while z % d == 0:
                    bad.add(d)
                    z //= d
                d += 1
    extra = bad - {2, case.P, case.G}
    if extra:
        msgs.append(f"unexpected exceptional primes {extra}")
    return msgs


# ---------------------------------------------------------------------------
# Arb helpers
# ---------------------------------------------------------------------------
def A(x) -> arb:
    """Exact rational (Fraction/int) -> arb (exact if dyadic, else 1-ulp ball)."""
    x = Fr(x)
    return arb(x.numerator) / x.denominator


def arb_to_interval(x: arb) -> tuple[Fr, Fr]:
    """Exact rational endpoints [lo, hi] of an Arb ball."""
    lo, hi = x.lower(), x.upper()
    m1, e1 = lo.man_exp()
    m2, e2 = hi.man_exp()
    return Fr(int(m1)) * Fr(2) ** int(e1), Fr(int(m2)) * Fr(2) ** int(e2)


def fmt(x: arb, digits: int = 16) -> str:
    return x.str(digits, radius=True)


def upper_str(x: arb, digits: int = 15) -> str:
    return arb(x.upper()).str(digits, radius=False)


class Checks:
    """Collects named checks; ``finish`` exits non-zero if any failed."""

    def __init__(self, title: str):
        self.title = title
        self.items: list[tuple[str, bool, str]] = []

    def check(self, name: str, ok: bool, detail: str = "") -> bool:
        self.items.append((name, bool(ok), detail))
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}" + (f" :: {detail}" if detail else ""), flush=True)
        return bool(ok)

    @property
    def ok(self) -> bool:
        return all(x[1] for x in self.items)

    def finish(self, outfile: Path | None = None, payload: dict | None = None) -> None:
        nfail = sum(1 for x in self.items if not x[1])
        print(f"== {self.title}: {len(self.items) - nfail} passed, {nfail} failed ==")
        if outfile is not None:
            data = dict(payload or {})
            data["checks"] = [{"name": n, "ok": o, "detail": d} for n, o, d in self.items]
            data["all_passed"] = nfail == 0
            outfile.write_text(json.dumps(data, indent=2, default=str))
        sys.exit(0 if nfail == 0 else 1)


def frac_str(x: Fr, digits: int = 18) -> str:
    """Decimal rendering of an exact rational (orientation only)."""
    x = Fr(x)
    sign = "-" if x < 0 else ""
    x = abs(x)
    ip = x.numerator // x.denominator
    rem = x - ip
    s = str(ip) + "."
    for _ in range(digits):
        rem *= 10
        d = rem.numerator // rem.denominator
        s += str(d)
        rem -= d
    return sign + s
