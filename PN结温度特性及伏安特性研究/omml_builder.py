"""
OMML (Office Math Markup Language) 公式构建器
用于在 .docx 中插入专业排版数学公式
"""
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree

M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def _m(tag):
    """创建 m: 命名空间元素"""
    return OxmlElement(qn('m:' + tag))

def _mt(text):
    """创建 m:t 文本元素"""
    el = _m('t')
    el.text = str(text)
    el.set(qn('xml:space'), 'preserve')
    return el

def _mr(text, italic=True):
    """创建 m:r (math run) + m:t"""
    r = _m('r')
    if not italic:
        # 添加 rPr 取消斜体（用于单位、数字、运算符等）
        rPr = _m('rPr')
        nor = _m('nor')  # normal text
        rPr.append(nor)
        r.insert(0, rPr)
    r.append(_mt(text))
    return r

def _e(*children):
    """创建 m:e (表达式基)"""
    e = _m('e')
    for c in children:
        e.append(c)
    return e

# ---- 基本结构 ----
def sub(base, sub):
    """下标: base_sub"""
    s = _m('sSub')
    s.append(_e(_mr(base)))
    sb = _m('sub')
    sb.append(_mr(sub))
    s.append(sb)
    return s

def sup(base, sup_text):
    """上标: base^sup"""
    s = _m('sSup')
    s.append(_e(_mr(base)))
    sp = _m('sup')
    sp.append(_mr(sup_text))
    s.append(sp)
    return s

def subsup(base, sub_text, sup_text):
    """上下标: base_sub^sup"""
    s = _m('sSubSup')
    s.append(_e(_mr(base)))
    sb = _m('sub')
    sb.append(_mr(sub_text))
    s.append(sb)
    sp = _m('sup')
    sp.append(_mr(sup_text))
    s.append(sp)
    return s

def frac(num_children, den_children):
    """分数: 分子/分母
    num_children, den_children 可以是单个元素或元素列表
    """
    f = _m('f')
    num = _m('num')
    if isinstance(num_children, list):
        for c in num_children:
            num.append(c)
    else:
        num.append(num_children)
    f.append(num)
    den = _m('den')
    if isinstance(den_children, list):
        for c in den_children:
            den.append(c)
    else:
        den.append(den_children)
    f.append(den)
    return f

def paren(*children):
    """圆括号"""
    d = _m('d')
    dPr = _m('dPr')
    beg = _m('begChr')
    beg.set(qn('m:val'), '(')
    dPr.append(beg)
    end = _m('endChr')
    end.set(qn('m:val'), ')')
    dPr.append(end)
    d.append(dPr)
    e = _m('e')
    for c in children:
        e.append(c)
    d.append(e)
    return d

def bracket(*children):
    """方括号"""
    d = _m('d')
    dPr = _m('dPr')
    beg = _m('begChr')
    beg.set(qn('m:val'), '[')
    dPr.append(beg)
    end = _m('endChr')
    end.set(qn('m:val'), ']')
    dPr.append(end)
    d.append(dPr)
    e = _m('e')
    for c in children:
        e.append(c)
    d.append(e)
    return d

def operator(ch):
    """运算符"""
    return _mr(ch, italic=False)

def num(n):
    """数字（非斜体）"""
    return _mr(str(n), italic=False)

def text(s):
    """普通文本"""
    return _mr(s)

def greek(letter):
    """希腊字母 (Unicode)"""
    return _mr(letter)

# ---- 复合结构 ----
def exp_of(expr_children):
    """exp(expr) = e^expr"""
    s = _m('sSup')
    s.append(_e(_mr('e', italic=True)))
    sp = _m('sup')
    for c in expr_children if isinstance(expr_children, list) else [expr_children]:
        sp.append(c)
    s.append(sp)
    return s

def group(*children):
    """{ ... } 分组的表达式序列"""
    if len(children) == 1:
        return children[0]
    # 用于需要组合多个元素的情况
    return list(children)

# ---- 构建完整公式段落 ----
def make_omath(*children):
    """创建 m:oMath 元素（行内公式）"""
    om = _m('oMath')
    for c in children:
        if isinstance(c, list):
            for cc in c:
                om.append(cc)
        else:
            om.append(c)
    return om

def make_omath_para(*children):
    """创建 m:oMathPara 元素（显示公式，居中）"""
    op = _m('oMathPara')
    om = _m('oMath')
    for c in children:
        if isinstance(c, list):
            for cc in c:
                om.append(cc)
        else:
            om.append(c)
    op.append(om)
    return op

def insert_equation(paragraph, equation_elem):
    """在段落中插入公式（替换段落内容）"""
    # 清空段落
    for r in paragraph.runs:
        r.text = ""
    for r in paragraph.runs:
        r._element.getparent().remove(r._element)
    # 插入公式
    paragraph._element.append(equation_elem)


# ============================================================
# 预定义公式（针对本实验报告）
# ============================================================

# Greek letters Unicode
alpha = greek('\u03b1')
beta = greek('\u03b2')
delta = greek('\u0394')
minus = operator('\u2212')
dot = operator('\u00b7')
eq = operator('=')
approx = operator('\u2248')

# 常用物理量
V_F = lambda: sub('V', 'F')
I_F = lambda: sub('I', 'F')
I_S = lambda: sub('I', 'S')
V_g = lambda: sub('V', 'g')
E_g = lambda: sub('E', 'g')
V_F1 = lambda: sub('V', 'F1')
V_F2 = lambda: sub('V', 'F2')
I_F1 = lambda: sub('I', 'F1')
I_F2 = lambda: sub('I', 'F2')
V_1 = lambda: sub('V', '1')
V_n1 = lambda: sub('V', 'n1')

# 完整公式
def formula_1():
    """I_F = I_S [exp(qV_F/kT) - 1]"""
    return [
        I_F(), operator('='), I_S(),
        bracket(
            exp_of([_mr('q'), V_F(), operator('/'), _mr('kT')]),
            operator('\u2212'), num(1)
        )
    ]

def formula_2():
    """I_F = I_S exp(qV_F/kT)"""
    return [
        I_F(), operator('='), I_S(),
        exp_of([_mr('q'), V_F(), operator('/'), _mr('kT')])
    ]

def formula_3():
    """I_S = CT^r exp[qV_g(0)/kT]"""
    return [
        I_S(), operator('='), _mr('C'), _mr('T'),
        sup('', 'r'),
        exp_of([_mr('q'), V_g(), paren(operator('\u2212'), num(0)), operator('/'), _mr('kT')])
    ]

def formula_4():
    """V_F = V_g(0) - (k/q·ln(C/I_F))T - (kT/q)ln(T^r) = V_1 + V_n1"""
    return [
        V_F(), operator('='), V_g(), paren(num(0)),
        operator('\u2212'),
        paren(
            frac([_mr('k'), operator('/'), _mr('q')], []),  # simplified
        )
    ]
