"""Usage: finite_bounds.py A Q SIGMA T C N0 N1

Finite-size consistency check of every local lower bound of Sections 3-5 against the exact
Gauss valuations of T (h = T n, K = C n, n = N0..N1).  For each prime p the exact v_p^G(T)
is compared with the finite-h form of the bound:

  p = 2, a odd      : entrywise forward-difference bounds in the anchored bases (checked
                      entry by entry) and v_2 / h^2 against the leading constant;
  p = 2, a = 2^e a0 : parity-minor bound (finite form with exact pole and site costs);
  odd p | a         : -f h (2K - h) - 2 h floor(log_p 4h);
  p | q             : reported as v / (f h^2), to compare with 1/3;
  odd p | q^2-sa^2  : -f sum_i (2i + 1 - K)_+ - 2 h floor(log_p 4h);
  ordinary p        : jet / raw slot bounds (p^2 > 2K), 0 (p > 2K), -2h floor(log_p 4h).

A finite check supports the estimates; it does not prove them.  Exit status 1 on a failure.
"""
import math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
from flint import fmpq, fmpq_poly
from pencil import Pencil, gauss_valuation, vp


def primes_upto(n):
    sieve = bytearray([1]) * (n + 1); sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i, f in enumerate(sieve) if f]


def vpi(n, p):
    n = abs(n); k = 0
    while n % p == 0:
        n //= p; k += 1
    return k


def vfact(n, p):
    s, q = 0, p
    while q <= n:
        s += n // q; q *= p
    return s


def flog(p, x):
    L = 0
    while p ** (L + 1) <= x:
        L += 1
    return L


def vS(h, K, p):
    return h * vfact(K, p) - 2 * sum(vfact(i, p) for i in range(h))


def two_adic_even(h, K, e):
    """Finite parity-minor bound for a = 2^e a0."""
    L = flog(2, max(1, h - 1))
    Aof = [0]
    for j in range(h + 1):
        Aof.append(Aof[-1] + j + vfact(j, 2))
    poles = sorted(-e * (2 * k + 1) - (K - 1) - vfact(k, 2) - vfact(K - 1 - k, 2) for k in range(K))

    def vq(x):
        return vpi(x.numerator, 2) - vpi(x.denominator, 2)
    evens = []
    m = 1
    while len(evens) < 2 * h + 4:
        z = 2 * m
        Pk = 1
        for k in range(K):
            Pk *= (z + 2 * k + 1)
        Fv = Fr(z, Pk)
        dF = Fv * (Fr(1, z) - sum(Fr(1, z + 2 * k + 1) for k in range(K)))
        cst = 2 * e * m + min(vq(Fv), vq(dF) if dF != 0 else 10 ** 9)
        evens += [cst, cst]
        m += 1
    evens.sort()
    pc = [0]
    for x in poles:
        pc.append(pc[-1] + x)
    ec = [0]
    for x in evens:
        ec.append(ec[-1] + x)
    best = min(2 * Aof[P] + 2 * Aof[h - P] - (h - P) * (1 + L) + pc[P] + ec[h - P] for P in range(0, min(h, K) + 1))
    return vS(h, K, 2) + K * h - h * (h - 1) + best


def anchored_entries_ok(P, n):
    """Entrywise 2-adic bounds (odd a) in the bases a_i = prod_{k<i}(u - x_k),
    b_j = prod_{K-j<=k<K}(u - x_k).  Returns (number checked, list of failures, v_2 lower
    bound for the raw determinant obtained from the entry bounds by the assignment
    inequality, i.e. sum of the bound over the identity-type worst permutation is not
    computed here)."""
    env = P.setup(n)
    h, K, xs = env[0], env[1], env[2]
    u = fmpq_poly([0, 1])
    nu = vp(P.sigma * P.y ** 2 - 1, 2)
    A = [fmpq_poly([1])]
    for i in range(h):
        A.append(A[-1] * (u - xs[i]))
    Bq = [fmpq_poly([1])]
    for j in range(h):
        Bq.append(Bq[-1] * (u - xs[K - 1 - j]))
    fails, cnt = [], 0
    for i in range(h):
        for j in range(h):
            v0, v1 = P.mu(u * A[i] * Bq[j], env)
            v = min(vp(x, 2) for x in (v0, v1) if x != 0) if (v0 != 0 or v1 != 0) else 10 ** 9
            pi = i + j + 1 - K
            if pi <= 0:
                N = -pi
                if P.sigma == 1:
                    b = N - 1 - flog(2, N) if N >= 2 else 0
                else:
                    b = N - vfact(N, 2) if N >= 2 else 0
            else:
                b = min(1 - pi + bb + vfact(bb, 2) - nu * (bb + 1) for bb in range(pi))
            cnt += 1
            if v < b:
                fails.append((i, j, v, b))
    return cnt, fails, nu


def ordinary_bound(h, K, p):
    c = [0] * p; imp = [False] * p
    inv2 = pow(2, -1, p)
    for k in range(K):
        r = (-k - inv2) % p
        c[r] += 1
        if 2 * k + 1 < p:
            imp[r] = True
    w = [-c[r] - 1 for r in range(p)]
    jet = sum(sorted(w[r] + 2 * j for r in range(p) for j in range(h))[:h])
    raws = [w[r] + 2 * j + (2 if (imp[r] and j == c[r] - 1) else 0) for r in range(p) for j in range(c[r])]
    raw = sum(sorted(x for x in raws if x < 0)[:h])
    return max(jet, raw)


def main():
    a, q, sigma, t, c, n0, n1 = (int(x) for x in sys.argv[1:8])
    P = Pencil(a, q, sigma, t, c)
    kap = Fr(c, t); D = (2 - kap) ** 2 / 4
    Y = q * q - sigma * a * a
    e = vpi(a, 2)
    ok = True
    for n in range(n0, n1 + 1):
        t0 = time.time()
        h, K = t * n, c * n
        T = P.T_poly(n)
        assert T != 0
        fails, rep = [], []
        for p in primes_upto(max(4 * h, 2 * K + 2) + q):
            v = gauss_valuation(T, p)
            if p == 2 and e == 0:
                cnt, efails, nu = anchored_entries_ok(P, n)
                lead = (2 * (kap - 1) - (nu - 2) * D) if sigma == 1 else (kap - 1 - D)
                rep.append(f"p=2 (a odd, nu={nu}): {cnt} entry bounds, {len(efails)} failures; v_2={v}, v_2/h^2={v/h/h:.4f} (leading constant {float(lead):.4f})")
                if efails:
                    fails.append((2, 'entries', efails[:3]))
                continue
            if p == 2:
                b = two_adic_even(h, K, e); kind = f'2,e={e}'
            elif a % p == 0:
                f = vpi(a, p)
                b = -f * h * (2 * K - h) - 2 * h * flog(p, 4 * h); kind = 'num'
                rep.append(f"p={p}|a: v/(f h^2)={v/(f*h*h):.4f} (leading constant {-float(2*kap-1):.4f})")
            elif q % p == 0:
                f = vpi(q, p)
                rep.append(f"p={p}|q: v={v}, v/(f h^2)={v/(f*h*h):.4f} (leading constant 0.3333)")
                continue
            elif Y % p == 0:
                f = vpi(Y, p)
                b = -f * sum(max(0, 2 * i + 1 - K) for i in range(h)) - 2 * h * flog(p, 4 * h); kind = 'near-one'
            elif p > 2 * K:
                b = 0; kind = 'large'
            elif p * p > 2 * K:
                b = max(vS(h, K, p) + ordinary_bound(h, K, p), -2 * h * flog(p, 4 * h)); kind = 'macro'
            else:
                b = -2 * h * flog(p, 4 * h); kind = 'small'
            if v < b:
                fails.append((p, kind, v, b))
            if kind not in ('large', 'small', 'macro'):
                rep.append(f"p={p}[{kind}] v={v} bound={b}")
        ok &= not fails
        print(f"a={a} q={q} sigma={sigma:+d} n={n} h={h} K={K}: failures={fails}; " + "; ".join(rep) + f" [{time.time()-t0:.0f}s]", flush=True)
    sys.exit(0 if ok else 1)


main()
