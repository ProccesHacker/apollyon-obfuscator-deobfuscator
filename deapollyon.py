import ast
import marshal
import os
import re
import zipfile
from types import CodeType


abc = "abcdefghijklmnopqrstuvwxyz0123456789"


def banner():
    print(f"""\033[31m
             %                                                    %
              %%                                                %%
               %%%                                            %%%
                 %%%%                                      %%%%
                   %%%%%                                %%%%%
                     %%%%%%%                        %%%%%%%
                       %%%%%%%%:                :%%%%%%%%
                         %%%%%%%%%%          %%%%%%%%%%
                           :%%%%%%%%        %%%%%%%%:
                              %%%%%%        %%%%%%
                               %%%%.         %%%%
                               %%%%          %%%%
                              :%%%%%        %%%%%:
                              %%%%%%%%%  %%%%%%%%%
                                %%%%%%%%%%%%%%%%
                                  %%%%%%%%%%%%
                                    #%%%%%%#
                                       %%

                        Деобфускатор создавал ProcHacker.""")
                        

class Err(ValueError):
    pass


def read(path):
    with open(path, "rb") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def txt(data):
    for e in ("utf-8", "utf-16", "cp1251", "latin1"):
        try:
            return data.decode(e)
        except Exception:
            pass
    return data.decode("utf-8", "ignore")


def pick(path):
    if os.path.isdir(path):
        for x in ("src/_run.py", "_run.py", "launch.py"):
            p = os.path.join(path, x)
            if os.path.isfile(p):
                return read(p), p
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith((".py", ".pyc")):
                    p = os.path.join(root, file)
                    return read(p), p
        raise Err("python файлы не найдены")
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            use = None
            for x in ("src/_run.py", "_run.py", "launch.py"):
                if x in names:
                    use = x
                    break
            if use is None:
                for x in names:
                    if x.endswith((".py", ".pyc")):
                        use = x
                        break
            if use is None:
                raise Err("python файлы не найдены")
            return z.read(use), use
    return read(path), path


def bins_ast(src):
    try:
        tree = ast.parse(src)
    except Exception:
        return []
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call) or not n.args:
            continue
        ok = False
        if isinstance(n.func, ast.Name) and n.func.id == "loads":
            ok = True
        if isinstance(n.func, ast.Attribute) and n.func.attr == "loads":
            ok = True
        if not ok:
            continue
        try:
            v = ast.literal_eval(n.args[0])
        except Exception:
            continue
        if isinstance(v, bytes):
            out.append(v)
    return out


def bins_re(src):
    out = []
    for m in re.finditer(r"loads\s*\(\s*(b(['\"]).*?\2)\s*\)", src, re.S):
        try:
            v = ast.literal_eval(m.group(1))
        except Exception:
            continue
        if isinstance(v, bytes):
            out.append(v)
    return out


def loadcode(data, name=""):
    if name.endswith(".pyc") or data[:4] in (b"\xa7\r\r\n", b"\x42\x0d\x0d\x0a"):
        for i in (16, 12, 8, 0):
            try:
                return marshal.loads(data[i:])
            except Exception:
                pass
    src = txt(data)
    for b in bins_ast(src) + bins_re(src):
        try:
            return marshal.loads(b)
        except Exception:
            pass
    return None


def strings(code, out=None):
    if out is None:
        out = []
    if not isinstance(code, CodeType):
        return out
    for c in code.co_consts:
        if isinstance(c, CodeType):
            strings(c, out)
        elif isinstance(c, str) and len(c) > 3:
            out.append(c)
    return out


def keys(items):
    out = {49348}
    for s in items:
        for n in re.findall(r"key\s*=\s*(-?\d+)", s):
            try:
                out.add(int(n))
            except Exception:
                pass
    return list(out)


def dec(s, key):
    tmp = []
    for ch in s:
        if ch == "ζ":
            tmp.append("\n")
        else:
            o = ord(ch) - key
            if o < 0 or o > 0x10ffff:
                return ""
            tmp.append(chr(o))
    res = []
    for ch in "".join(tmp):
        if ch in abc:
            res.append(abc[(abc.index(ch) + 1) % len(abc)])
        else:
            res.append(ch)
    return "".join(res)


def rate(s):
    if not s:
        return -999
    z = s[:5000]
    n = 0
    for w in ("import ", "from ", "def ", "class ", "print(", "if ", "for ", "while ", "=", "\n"):
        n += z.count(w)
    bad = sum(1 for c in z if ord(c) < 9 or 13 < ord(c) < 32)
    hi = sum(1 for c in z if ord(c) > 127 and c not in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
    return n - bad * 5 - hi


def best(items):
    got = None
    num = -999
    for s in items:
        for k in keys(items):
            d = dec(s, k)
            r = rate(d)
            if r > num:
                got = d
                num = r
    if got is not None and num > 1:
        return got
    return None


def bytext(src):
    q = re.findall(r"script\s*=\s*r?(['\"]{3})(.*?)\1", src, re.S)
    if not q:
        q = re.findall(r"script\s*=\s*r?(['\"])(.*?)\1", src, re.S)
    arr = [x[1] for x in q]
    arr.append(src)
    return best(arr + [src])


def clean(src):
    src = src.replace("\r\n", "\n").replace("\r", "\n")
    try:
        return ast.unparse(ast.parse(src)) + "\n"
    except Exception:
        return src.rstrip() + "\n"


def deobf(path):
    data, name = pick(path)
    code = loadcode(data, name)
    if code is not None:
        d = best(strings(code))
        if d is not None:
            return clean(d)
    d = bytext(txt(data))
    if d is not None:
        return clean(d)
    raise Err("не удалось деобфусцировать файл")


def proc(p, o=None):
    d = deobf(p)
    if o is None:
        if p.endswith(".py"):
            o = re.sub(r"\.py$", "", p) + "_deobf.py"
        else:
            o = p.rstrip("/\\") + "_deobf.py"
    write(o, d)
    return o


def main():
    banner()
    p = ""
    while not p:
        p = input("Введите путь к файлу: ").strip().strip('"')
    r = proc(p)
    print(f"Deobfuscated file written to: {r}")


if __name__ == "__main__":
    main()
