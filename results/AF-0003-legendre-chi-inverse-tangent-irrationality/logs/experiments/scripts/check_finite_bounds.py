"""Usage: check_finite_bounds.py Q SIGMA {general|band} N0 N1

Finite-size check of the local lower bounds against exact Gauss valuations of T.
For each prime p: compare v_p^G(T) with the finite-h form of the bound proved in the
manuscript (2-adic parity-minor bound, p | q^2-4sigma convexity bound, ordinary jet/raw
bounds for p^2 > 2K, uniform bound), and report v_p/h^2 for p | q (manuscript, Appendix B).
Exit status 1 if some bound fails."""
import sys, math, time
sys.set_int_max_str_digits(0)
import os
from define_half_integer_pencils import Pencil, T_poly


def primes_upto(n):
    sieve = bytearray([1]) * (n + 1); sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i, f in enumerate(sieve) if f]


def gauss_valuation(T, p):
    vals = []
    for k in range(T.degree() + 1):
        c = T[k]
        if c != 0:
            a, b = int(c.p), int(c.q); v = 0
            while a % p == 0: a //= p; v += 1
            while b % p == 0: b //= p; v -= 1
            vals.append(v)
    return min(vals)

def vpi(n, p):
    n = abs(n); k = 0
    if n == 0: return 10**9
    while n % p == 0: n //= p; k += 1
    return k

def vfact(n, p):
    s, q = 0, p
    while q <= n: s += n // q; q *= p
    return s

def flog(p, x):
    L = 0
    while p**(L+1) <= x: L += 1
    return L

def vS(h, K, A, p):
    return h*(vfact(K, p) - 2*vfact(A, p)) - 2*sum(vfact(i, p) for i in range(h))

def two_adic_bound(h, K, A):
    L = flog(2, max(1, h-1))
    Aof = [0]
    for j in range(h+1): Aof.append(Aof[-1] + j + vfact(j, 2))   # Aof[t] = A(t)
    # pole costs v_2(gamma_k): -(2k+1) - (K-1) - v2(k!) - v2((K-1-k)!)  (odd numerator factors)
    poles = sorted(-(2*k+1) - (K-1) - vfact(k, 2) - vfact(K-1-k, 2) for k in range(K))
    # even sites m > A: valuation of F(2m) and F'(2m); slot cost 2m + min(vF, vF')
    from fractions import Fraction as Fr
    def vq(x):
        return vpi(x.numerator, 2) - vpi(x.denominator, 2)
    evens = []
    m = A + 1
    while len(evens) < 2*h + 4:
        z = 2*m
        Pk = 1
        for k in range(K): Pk *= (z + 2*k + 1)
        Nn = 1
        for j in range(1, A+1): Nn *= (z - 2*j)**2
        Fv = Fr(z*Nn, Pk)
        logder = Fr(1, z) + sum(Fr(2, z-2*j) for j in range(1, A+1)) - sum(Fr(1, z+2*k+1) for k in range(K))
        dF = Fv*logder
        c = 2*m + min(vq(Fv), vq(dF) if dF != 0 else 10**9)
        evens += [c, c]
        m += 1
    evens.sort()
    pc = [0]
    for c in poles: pc.append(pc[-1] + c)
    ec = [0]
    for c in evens: ec.append(ec[-1] + c)
    best = min(2*Aof[P] + 2*Aof[h-P] - (h-P)*(1+L) + pc[P] + ec[h-P] for P in range(0, min(h, K)+1))
    return vS(h, K, A, 2) + (K-2*A)*h - h*(h-1) + best

def ordinary_bound(h, K, A, p):
    """jet / raw bounds for v_p(Delta) with actual class counts (requires p^2 > 2K)."""
    c = [0]*p; n = [0]*p; imp = [False]*p
    inv2 = pow(2, -1, p)
    for k in range(K):
        a = (-k - inv2) % p
        c[a] += 1
        if 2*k + 1 < p: imp[a] = True
    for j in range(1, A+1): n[j % p] += 1
    w = [2*n[a] - c[a] - 1 for a in range(p)]
    jets = sorted(w[a] + 2*j for a in range(p) for j in range(h))
    jet = sum(jets[:h])
    raws = []
    for a in range(p):
        for j in range(c[a]):
            raws.append(w[a] + 2*j + (2 if (imp[a] and j == c[a]-1) else 0))
    raws = sorted(x for x in raws if x < 0)[:h]
    raw = sum(raws)
    return max(jet, raw), jet, raw

def main():
    q, sigma, cons, n0, n1 = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    P = Pencil(q, sigma, cons)
    Y = q*q - 4*sigma
    total_fails = 0
    for nn in range(n0, n1+1):
        t0 = time.time()
        h, K, A = P.sizes(nn)
        T = T_poly(P, nn)
        if T == 0:
            print(f"n={nn}: T = 0"); sys.exit(1)
        fails = []; rep = []
        for p in primes_upto(max(4*h, 2*K + 2) + q):
            v = gauss_valuation(T, p)
            if p == 2:
                b = two_adic_bound(h, K, A); kind = '2'
            elif q % p == 0:
                f = vpi(q, p); rep.append(f"p={p}|q: v={v} v/(f h^2)={v/(f*h*h):.4f}"); continue
            elif Y % p == 0:
                f = vpi(Y, p)
                b = -f*sum(max(0, 2*i + 2*A + 1 - K) for i in range(h)) - 2*h*flog(p, 4*h); kind = 'Y'
            elif p > 2*K:
                b = 0; kind = 'large'
            elif p*p > 2*K:
                bb, jet, raw = ordinary_bound(h, K, A, p)
                b = max(vS(h, K, A, p) + bb, -2*h*flog(p, 4*h)); kind = 'macro'
            else:
                b = -2*h*flog(p, 4*h); kind = 'small'
            if v < b: fails.append((p, kind, v, b))
            if kind in ('2', 'Y') or (kind == 'macro' and p in (h//2+1, h-1, h+1)):
                rep.append(f"p={p}[{kind}] v={v} bound={b}")
        print(f"n={nn} h={h} K={K} A={A}: failures={fails} ; " + "; ".join(rep) + f" [{time.time()-t0:.0f}s]", flush=True)
        total_fails += len(fails)
    print(f"== failures: {total_fails}")
    sys.exit(1 if total_fails else 0)


if __name__ == '__main__':
    main()
