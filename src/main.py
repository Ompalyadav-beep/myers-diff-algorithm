import sys


def read_lines(path):
    with open(path, "rb") as f:
        lines = f.read().split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def middle_snake(a, b, alo, ahi, blo, bhi, vf, vb):
    n = ahi - alo
    m = bhi - blo
    delta = n - m
    odd = delta % 2 == 1
    vf[1] = 0
    vb[1] = 0
    for d in range((n + m + 1) // 2 + 1):
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and vf[k - 1] < vf[k + 1]):
                x = vf[k + 1]
            else:
                x = vf[k - 1] + 1
            y = x - k
            x0, y0 = x, y
            while x < n and y < m and a[alo + x] == b[blo + y]:
                x += 1
                y += 1
            vf[k] = x
            if odd and -d < delta - k < d and x + vb[delta - k] >= n:
                return alo + x0, blo + y0, alo + x, blo + y

        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and vb[k - 1] < vb[k + 1]):
                x = vb[k + 1]
            else:
                x = vb[k - 1] + 1
            y = x - k
            x0, y0 = x, y
            while x < n and y < m and a[ahi - 1 - x] == b[bhi - 1 - y]:
                x += 1
                y += 1
            vb[k] = x
            if not odd and -d <= delta - k <= d and x + vf[delta - k] >= n:
                return alo + n - x, blo + m - y, alo + n - x0, blo + m - y0


def diff(a, b):
    keep_a = bytearray(len(a))
    keep_b = bytearray(len(b))

    in_a = set(a)
    in_b = set(b)
    ra = [i for i in range(len(a)) if a[i] in in_b]
    rb = [j for j in range(len(b)) if b[j] in in_a]
    sa = [a[i] for i in ra]
    sb = [b[j] for j in rb]

    size = len(sa) + len(sb) + 5
    vf = [0] * size
    vb = [0] * size

    stack = [(0, len(sa), 0, len(sb))]
    while stack:
        alo, ahi, blo, bhi = stack.pop()

        while alo < ahi and blo < bhi and sa[alo] == sb[blo]:
            keep_a[ra[alo]] = keep_b[rb[blo]] = 1
            alo += 1
            blo += 1
        while alo < ahi and blo < bhi and sa[ahi - 1] == sb[bhi - 1]:
            ahi -= 1
            bhi -= 1
            keep_a[ra[ahi]] = keep_b[rb[bhi]] = 1

        if alo == ahi or blo == bhi:
            continue

        x0, y0, x1, y1 = middle_snake(sa, sb, alo, ahi, blo, bhi, vf, vb)
        for t in range(x1 - x0):
            keep_a[ra[x0 + t]] = keep_b[rb[y0 + t]] = 1
        stack.append((x1, ahi, y1, bhi))
        stack.append((alo, x0, blo, y0))

    return keep_a, keep_b


def diff_lines(a_lines, b_lines):
    ids = {}
    a_ids = [ids.setdefault(line, len(ids)) for line in a_lines]
    b_ids = [ids.setdefault(line, len(ids)) for line in b_lines]
    return diff(a_ids, b_ids)


def render(a, b, keep_a, keep_b):
    out = []
    i = j = 0
    while i < len(a) or j < len(b):
        while i < len(a) and not keep_a[i]:
            out.append(b"-" + a[i] + b"\n")
            i += 1
        while j < len(b) and not keep_b[j]:
            out.append(b"+" + b[j] + b"\n")
            j += 1
        if i < len(a) and j < len(b):
            out.append(b" " + a[i] + b"\n")
            i += 1
            j += 1
    return out


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    command, a_path, b_path = sys.argv[1:]

    try:
        a = read_lines(a_path)
        b = read_lines(b_path)
    except OSError as e:
        print(f"error: cannot read file: {e}", file=sys.stderr)
        return 2

    keep_a, keep_b = diff_lines(a, b)
    sys.stdout.buffer.write(b"".join(render(a, b, keep_a, keep_b)))
    return 0


raise SystemExit(main())
