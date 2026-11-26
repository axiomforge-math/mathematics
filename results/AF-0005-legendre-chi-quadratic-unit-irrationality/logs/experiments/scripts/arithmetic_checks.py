#!/usr/bin/env python3
"""Independent exact checks of the pencil and of the two local estimates.

Written from the definitions with python-flint exact rationals.  Differences from the
original verifier: the polynomial part of the functional is computed from the rational
generating functions S_a(q) = (q d/dq)^a [q/(1 - sigma q^2)] (not from the Newton/Mahler
formula); the determinant polynomial is computed from a rational matrix obtained through
the reflection structure (checked exactly) with FLINT determinants; larger sizes are
covered; the parity-minor lemma and the finite 2-adic regularisation are tested directly.
Exit status is non-zero on any failure.
"""
import random
import sys
from math import comb, factorial

from flint import fmpq, fmpq_mat, fmpq_poly, fmpz, fmpz_mat

INF = 10 ** 9


def fail(msg):
    print("FAIL:", msg, flush=True)
    sys.exit(1)


def vp(x, p):
    x = fmpq(x)
    if x == 0:
        return INF
    a, b, v = abs(int(x.p)), int(x.q), 0
    while a % p == 0:
        a //= p
        v += 1
    while b % p == 0:
        b //= p
        v -= 1
    return v


class Field:
    """Q(z), z^2 + sigma n z - sigma = 0; elements a + b z."""

    def __init__(self, n, sigma):
        self.n, self.s = n, sigma

    def mul(self, x, y):
        a, b = x
        c, d = y
        # z^2 = sigma - sigma n z
        return (a * c + self.s * b * d, a * d + b * c - self.s * self.n * b * d)

    def inv(self, x):
        a, b = x
        nrm = a * a - self.s * self.n * a * b - self.s * b * b
        return ((a - self.s * self.n * b) / nrm, -b / nrm)

    def pw(self, x, k):
        if k < 0:
            return self.pw(self.inv(x), -k)
        r = (fmpq(1), fmpq(0))
        for _ in range(k):
            r = self.mul(r, x)
        return r


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def scal(c, x):
    return (c * x[0], c * x[1])


ZERO = (fmpq(0), fmpq(0))


def val(x, p):
    return min(vp(x[0], p), vp(x[1], p))


class Pencil:
    """A_d + X B_d = Lambda_X(t^d), 0 <= d <= 2h-2, for poles x_j = 2j - h."""

    def __init__(self, n, sigma, h):
        self.n, self.s, self.h = n, sigma, h
        K = self.K = h + 1
        F = self.F = Field(n, sigma)
        z = (fmpq(0), fmpq(1))
        y = scal(fmpq(sigma), F.mul(z, z))
        if add(y, scal(fmpq(n), z)) != (fmpq(1), fmpq(0)):
            fail("1 - y = n z")
        self.z, self.y = z, y
        xs = self.xs = [2 * j - h for j in range(K)]
        D = fmpq_poly([1])
        for x in xs:
            D = D * fmpq_poly([-x, 1])
        self.D = D
        # S_a(z) = sum_{t odd >= 1} sigma^((t-1)/2) z^t t^a through the generating function
        q = fmpq_poly([0, 1])
        Dq = fmpq_poly([1, 0, -sigma])
        mpoly = fmpq_poly([-sigma, sigma * n, 1])
        Na = q
        inv_nz = F.inv(scal(fmpq(n), z))
        S = []
        pw = inv_nz
        for a in range(2 * h):
            r = Na % mpoly
            S.append(F.mul((r[0], r[1]), pw))
            pw = F.mul(pw, inv_nz)
            Na = q * (Na.derivative() * Dq + 2 * sigma * (a + 1) * q * Na)
        self.S = S
        # pole data
        self.pole = []
        for j, x in enumerate(xs):
            dp = fmpq(2) ** h * (-1) ** (h - j) * factorial(j) * factorial(h - j)
            if dp != D.derivative()(x):
                fail("D'(x_j)")
            P = ZERO
            if x < 0:
                rs = range(1, -x, 2)
                sign = 1
            else:
                rs = range(1 - x, 0, 2)
                sign = -1
            for r in rs:
                w = scal(fmpq(sigma) ** (((r - 1) // 2) % 2), F.pw(z, r))
                P = add(P, scal(fmpq(sign, r * r), w))
            yx = F.pw(y, x // 2)
            self.pole.append((x, dp, P, yx))
        self.A, self.B = [], []
        for d in range(2 * h - 1):
            a, b = self.functional(fmpq_poly([0] * d + [1]))
            self.A.append(a)
            self.B.append(b)

    def poly_part(self, R):
        """M(R) = sum_a [t^a]R' S_a(z)."""
        out = ZERO
        Rp = R.derivative()
        for a in range(Rp.degree() + 1):
            out = add(out, scal(Rp[a], self.S[a]))
        return out

    def functional(self, g):
        """Lambda_X(g) = A + X B for a polynomial g."""
        R = g // self.D
        a = self.poly_part(R)
        b = ZERO
        for x, dp, P, yx in self.pole:
            c = g(x) / dp
            # L_X(1/(t-x)) = -y^(x/2) (X - P(x))
            a = add(a, scal(c, self.F.mul(yx, P)))
            b = add(b, scal(-c, yx))
        return a, b

    def rational_matrices(self):
        """Rational A~, B~ with det(A~ + X B~) = Delta_h(X) (reflection structure, checked)."""
        h, n, s = self.h, self.n, self.s
        disc = n * n + 4 * s
        MA, MB = fmpq_mat(h, h), fmpq_mat(h, h)
        for i in range(h):
            for j in range(h):
                d = i + j
                out = []
                for u in (self.A[d], self.B[d]):
                    if d % 2 == 0:
                        if u[1] != 0:
                            fail(f"E_{d} not rational")
                        out.append(u[0])
                    else:
                        # a + b z = (a - s n b/2) + (b/2) * (+-sqrt(disc))
                        if u[0] - fmpq(s * n, 2) * u[1] != 0:
                            fail(f"E_{d} not a rational multiple of sqrt(disc)")
                        c = u[1] / 2
                        out.append(c * disc if i % 2 else c)
                MA[i, j], MB[i, j] = out
        return MA, MB

    def delta(self):
        MA, MB = self.rational_matrices()
        h = self.h
        pts = list(range(h + 1))
        vals = [(MA + x * MB).det() for x in pts]
        # Newton interpolation
        coeffs = list(vals)
        for k in range(1, h + 1):
            for i in range(h, k - 1, -1):
                coeffs[i] = (coeffs[i] - coeffs[i - 1]) / k
        pol = fmpq_poly([0])
        for i in range(h, -1, -1):
            pol = pol * fmpq_poly([-i, 1]) + coeffs[i]
        for x in pts:
            if pol(x) != vals[x]:
                fail("interpolation")
        return pol


def content_exponent(pol, p):
    return -min(vp(pol[i], p) for i in range(pol.degree() + 1) if pol[i] != 0)


def A2(k):
    return sum(r + vp(factorial(r), 2) for r in range(k))


def bound_two(h):
    Lh = max(1, h - 1).bit_length() - 1
    return -min(-2 * h * k + 2 * A2(k) + 2 * A2(h - k) - 2 * (h - k) * (1 + Lh) for k in range(h + 1))


def bound_odd(n, h, p):
    e = vp(n, p)
    L = 0
    while p ** (L + 1) <= 2 * h:
        L += 1
    S = h * vp(factorial(h + 1), p) - 2 * sum(vp(factorial(i), p) for i in range(h))
    return 2 * h * L + e * (h - 2) ** 2 // 4 + S


def check_contents(cases, hs):
    print("exact content exponents n_p(h) against the finite bounds (7) and (12):")
    count = 0
    for n, p in cases:
        for s in (1, -1):
            row = []
            for h in hs:
                pol = Pencil(n, s, h).delta()
                if pol == 0:
                    fail("Delta_h == 0")
                if pol.degree() > h:
                    fail("degree")
                npv = content_exponent(pol, p)
                b = bound_two(h) if p == 2 else bound_odd(n, h, p)
                if npv > b:
                    fail(f"content bound n={n} s={s} h={h} p={p}: {npv} > {b}")
                row.append(f"h={h}:{npv}<={b}")
                count += 1
            print(f"  n={n:3d} sigma={s:+d} p={p}: " + "  ".join(row), flush=True)
    return count


def check_odd_entries(cases, hs):
    """v(K! Lambda_X(b_i b_j)) >= -2L - e (i+j-K)_+ with b_i = binom((t+h)/2, i)."""
    count, tight = 0, 0
    for n, p in cases:
        e = vp(n, p)
        for s in (1, -1):
            for h in hs:
                pen = Pencil(n, s, h)
                K = h + 1
                L = 0
                while p ** (L + 1) <= 2 * h:
                    L += 1
                basis = [fmpq_poly([1])]
                for i in range(1, h):
                    basis.append(basis[-1] * fmpq_poly([h - 2 * (i - 1), 1]) / (2 * i))
                for i in range(h):
                    for j in range(i, h):
                        a, b = pen.functional(basis[i] * basis[j])
                        v = min(val(a, p), val(b, p)) + vp(factorial(K), p)
                        bd = -2 * L - e * max(0, i + j - K)
                        if v < bd:
                            fail(f"entry bound n={n} s={s} h={h} p={p} i={i} j={j}: {v} < {bd}")
                        tight += v == bd
                        count += 1
    print(f"odd-prime entry bounds: {count} entries checked, {tight} attain the bound")
    return count


def check_parity_minors(trials, seed=20261126):
    rng = random.Random(seed)
    count, tight = 0, 0
    for _ in range(trials):
        h = rng.randrange(2, 13)
        k = rng.randrange(1, h + 1)
        rows = sorted(rng.sample(range(h), k))
        eps = rng.randrange(2)
        Lh = max(1, h - 1).bit_length() - 1
        cols = [(2 * rng.randrange(-12, 13) + eps, rng.random() < 0.4) for _ in range(k)]
        d = sum(1 for _, der in cols if der)
        M = fmpz_mat(k, k)
        for i, a in enumerate(rows):
            for j, (t, der) in enumerate(cols):
                M[i, j] = (a * t ** (a - 1) if a else 0) if der else t ** a
        det = M.det()
        v = vp(det, 2)
        bd = A2(k) - d * (1 + Lh)
        if v < bd:
            fail(f"parity minor h={h} rows={rows} cols={cols}: {v} < {bd}")
        tight += v == bd
        count += 1
    print(f"parity-minor lemma: {count} random minors checked, {tight} attain the bound")
    return count


def kdet(F, M):
    """Determinant over the quadratic field (Gaussian elimination)."""
    M = [list(r) for r in M]
    out = (fmpq(1), fmpq(0))
    m = len(M)
    for i in range(m):
        piv = next((r for r in range(i, m) if M[r][i] != ZERO), None)
        if piv is None:
            return ZERO
        if piv != i:
            M[i], M[piv] = M[piv], M[i]
            out = scal(fmpq(-1), out)
        out = F.mul(out, M[i][i])
        iv = F.inv(M[i][i])
        for r in range(i + 1, m):
            c = F.mul(M[r][i], iv)
            if c == ZERO:
                continue
            for k in range(i + 1, m):
                M[r][k] = add(M[r][k], scal(fmpq(-1), F.mul(c, M[i][k])))
    return out


def check_regularisation(cases, hs, Ls):
    """Finite 2-adic regularisation (9): integrality, convergence, determinant bound (12)."""
    count = 0
    for n in cases:
        for s in (1, -1):
            for h in hs:
                pen = Pencil(n, s, h)
                F, z, y = pen.F, pen.z, pen.y
                one = (fmpq(1), fmpq(0))
                for L in Ls:
                    M = 2 ** L
                    yM = F.pw(y, M)
                    iv = F.inv(add(one, scal(fmpq(-1), yM)))
                    if val(iv, 2) != 0:
                        fail("1 - y^M not a unit")
                    om = [F.mul(F.mul(z, F.pw(y, k)), iv) for k in range(M)]
                    if any(val(w, 2) < 0 for w in om):
                        fail("omega not integral")
                    Dp = pen.D.derivative()

                    def IM_deriv_of_rational(g):
                        # I_M((g/D)') = sum omega_s (g' D - g D')/D^2 at t = 2s+1
                        out = ZERO
                        gp = g.derivative()
                        for k in range(M):
                            t = 2 * k + 1
                            Dv = pen.D(t)
                            out = add(out, scal((gp(t) * Dv - g(t) * Dp(t)) / (Dv * Dv), om[k]))
                        return out

                    AM, BM = [], []
                    for d in range(2 * h - 1):
                        g = fmpq_poly([0] * d + [1])
                        a = IM_deriv_of_rational(g)
                        b = ZERO
                        for x, dp, P, yx in pen.pole:
                            c = g(x) / dp
                            # + c * (L_X(1/(t-x)) - I_M((1/(t-x))'))
                            a = add(a, scal(c, F.mul(yx, P)))
                            b = add(b, scal(-c, yx))
                            corr = ZERO
                            for k in range(M):
                                corr = add(corr, scal(fmpq(-1, (2 * k + 1 - x) ** 2), om[k]))
                            a = add(a, scal(-c, corr))
                        AM.append(a)
                        BM.append(b)
                        # convergence to the true functional: difference is I_M(R') - M(R)
                        diff = add(a, scal(fmpq(-1), pen.A[d]))
                        if b != pen.B[d]:
                            fail("X-part of the regularised functional")
                        if d >= pen.K and val(diff, 2) < L + 1:
                            # R monic integral of degree d-K: R'(2s+1) integral, period-M classes
                            fail(f"convergence n={n} s={s} h={h} L={L} d={d}: {val(diff, 2)}")
                        if d < pen.K and diff != ZERO:
                            fail("proper case must be exact")
                        count += 1
                    bd = -bound_two(h)
                    for X in range(h + 1):
                        mat = [[add(AM[i + j], scal(fmpq(X), BM[i + j])) for j in range(h)] for i in range(h)]
                        v = val(kdet(F, mat), 2)
                        if v < bd:
                            fail(f"regularised determinant n={n} s={s} h={h} L={L} X={X}: {v} < {bd}")
                        count += 1
    print(f"2-adic regularisation: {count} checks (integrality, convergence, determinant bound)")
    return count


def check_series(n, s, h, digits=60):
    """The algebraic functional equals the convergent series at X = T (Arb)."""
    from flint import arb, ctx
    ctx.prec = 4 * digits
    pen = Pencil(n, s, h)
    zr = 2 / (arb(n) + arb(n * n + 4 * s).sqrt())
    T = arb(0)
    k = 0
    while True:
        term = zr ** (2 * k + 1) / arb(2 * k + 1) ** 2
        T += term if (s == 1 or k % 2 == 0) else -term
        k += 1
        if term < arb(10) ** (-digits - 20):
            break
    worst = arb(0)
    Dp = pen.D.derivative()
    for d in range(2 * h - 1):
        a, b = pen.A[d], pen.B[d]
        alg = arb(a[0]) + arb(a[1]) * zr + T * (arb(b[0]) + arb(b[1]) * zr)
        ser = arb(0)
        j = 0
        while True:
            t = 2 * j + 1
            Dv = arb(pen.D(t))
            w = zr ** t * (1 if (s == 1 or j % 2 == 0) else -1)
            term = w * (d * arb(t) ** max(d - 1, 0) * (1 if d else 0) * Dv - arb(t) ** d * arb(Dp(t))) / (Dv * Dv)
            ser += term
            j += 1
            if j > 50 and abs(term) < arb(10) ** (-digits - 20):
                break
        err = abs(alg - ser)
        if not err < arb(10) ** (-digits):
            fail(f"series identity n={n} s={s} h={h} d={d}")
    print(f"series identity n={n} sigma={s:+d} h={h}: all {2*h-1} moments agree to 1e-{digits}")
    return 2 * h - 1


def main():
    quick = len(sys.argv) > 1 and sys.argv[1] == "quick"
    total = 0
    for n, s in [(14, 1), (27, -1), (7, 1), (5, -1)]:
        total += check_series(n, s, 6)
    total += check_parity_minors(300 if quick else 4000)
    total += check_odd_entries([(6, 3), (14, 7), (18, 3), (30, 3), (30, 5), (27, 3), (25, 5), (45, 3), (45, 5), (63, 3), (63, 7)],
                               [4, 8] if quick else [4, 8, 12, 16, 20])
    total += check_regularisation([5, 7, 27] if quick else [3, 5, 7, 25, 27, 33], [4] if quick else [4, 6],
                                  [1, 2, 3] if quick else [1, 2, 3, 4, 5])
    hs = [4, 6, 8] if quick else [4, 6, 8, 10, 12, 16, 20, 24, 32]
    total += check_contents([(7, 2), (25, 2), (27, 2), (33, 2), (165, 2), (14, 7), (18, 3), (30, 3), (30, 5),
                             (27, 3), (45, 3), (45, 5), (165, 11)], hs)
    print(f"PASS: {total} exact checks.")


if __name__ == "__main__":
    main()
