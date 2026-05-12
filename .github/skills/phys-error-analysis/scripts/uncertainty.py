"""
不确定度计算工具

用法:
    from uncertainty import type_a, type_b_u, combined, format_result
"""
import numpy as np
from math import sqrt


def type_a(data):
    """
    A类不确定度（统计方法）
    u_A = s / sqrt(n)  其中 s 是实验标准差
    """
    n = len(data)
    if n < 2:
        return 0.0
    s = np.std(data, ddof=1)
    return s / sqrt(n)


def type_b_u(delta_instrument, distribution='uniform'):
    """
    B类不确定度（仪器允差）
    默认均匀分布: u_B = Delta / sqrt(3)
    """
    if distribution == 'uniform':
        return delta_instrument / sqrt(3)
    elif distribution == 'normal':
        return delta_instrument / 3  # 正态分布 k=3
    else:
        raise ValueError(f"Unknown distribution: {distribution}")


def combined(ua, ub):
    """合成标准不确定度"""
    return sqrt(ua**2 + ub**2)


def format_result(value, uncertainty, unit='', decimal_places=1):
    """
    格式化结果为 值 ± 不确定度 (单位)
    自动对齐有效数字
    """
    # 不确定度保留 1-2 位有效数字
    if uncertainty == 0:
        return f"{value:.{decimal_places}f} {unit}".strip()

    # 获取不确定度的数量级
    import math
    if uncertainty >= 1:
        u_digits = max(1, int(-math.floor(math.log10(uncertainty))) + 1)
    else:
        u_digits = int(-math.floor(math.log10(uncertainty))) + 1

    u_digits = max(1, min(u_digits, 6))  # 1-6位小数

    u_formatted = f"{uncertainty:.{u_digits}f}"
    v_formatted = f"{value:.{u_digits}f}"

    if unit:
        return f"{v_formatted} ± {u_formatted} {unit}"
    return f"{v_formatted} ± {u_formatted}"


def propagation_multiply(values, uncertainties, exponents=None):
    """
    乘除型误差传递: y = k * ∏ x_i^{a_i}
    u_c / y = sqrt(∑ a_i² (u_i/x_i)²)
    """
    if exponents is None:
        exponents = [1] * len(values)

    sum_sq = 0
    for x, u, a in zip(values, uncertainties, exponents):
        if x != 0:
            sum_sq += (a * u / x) ** 2

    return sqrt(sum_sq)


def propagation_add(uncertainties, coeffs=None):
    """
    加减型误差传递: y = ∑ c_i x_i
    u_c = sqrt(∑ c_i² u_i²)
    """
    if coeffs is None:
        coeffs = [1] * len(uncertainties)

    sum_sq = sum((c * u) ** 2 for c, u in zip(coeffs, uncertainties))
    return sqrt(sum_sq)


# 常用仪器允差参考 (Δ_仪)
INSTRUMENT_TOLERANCE = {
    '游标卡尺': 0.02,      # mm
    '螺旋测微器': 0.004,   # mm
    '数字万用表': 0.001,   # 取决于量程
    '钢直尺': 0.5,         # mm
    '电子天平': 0.001,     # g (视型号)
    '秒表': 0.01,          # s
    '温度计': 0.5,         # °C
}


if __name__ == '__main__':
    # 示例
    data = [2.51, 2.49, 2.53, 2.50, 2.48]
    ua = type_a(data)
    ub = type_b_u(0.02)
    uc = combined(ua, ub)
    mean = np.mean(data)
    print(f"测量值: {data}")
    print(f"平均值: {mean:.4f}")
    print(f"A类不确定度: {ua:.4f}")
    print(f"B类不确定度: {ub:.4f}")
    print(f"合成不确定度: {uc:.4f}")
    print(f"结果: {format_result(mean, uc, 'mm')}")
