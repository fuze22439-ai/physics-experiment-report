"""
扩散长度拟合脚本
基于指数衰减公式 I = I0 * exp(±(x-D)/L) 拟合扩散长度

用法:
    python fit_diffusion.py <data_file> [--peak-pos D] [--peak-current I0]
"""
import numpy as np
from scipy.optimize import curve_fit
from scipy import stats
import sys
import os


def exp_decay(x, L):
    """单参数指数衰减: I/I0 = exp(-|x-D|/L)"""
    return np.exp(-np.abs(x) / L)


def fit_diffusion_length(filepath, peak_pos=None, peak_current=None, side='both'):
    """
    从线扫数据拟合扩散长度

    Parameters
    ----------
    filepath : str
        数据文件路径
    peak_pos : float, optional
        手动指定峰值位置 (μm)，不指定则自动查找
    peak_current : float, optional
        手动指定峰值电流 (A)，不指定则自动查找
    side : str
        'left' 仅拟合左侧, 'right' 仅拟合右侧, 'both' 分别拟合取平均

    Returns
    -------
    dict : {
        'L_left': float (μm),
        'L_right': float (μm),
        'L_avg': float (μm),
        'R2_left': float,
        'R2_right': float,
        'peak_pos': float (μm),
        'peak_current': float (μA),
        'n_points_left': int,
        'n_points_right': int
    }
    """
    # 读取数据
    positions = []
    currents = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]  # skip header

    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            pos = float(parts[0])
            cur = float(parts[1])
            positions.append(pos)
            currents.append(cur)
        except ValueError:
            continue

    positions = np.array(positions)
    currents = np.array(currents)

    # 自动查找峰值
    if peak_pos is None or peak_current is None:
        idx_max = np.argmax(np.abs(currents))
        if peak_pos is None:
            peak_pos = positions[idx_max]
        if peak_current is None:
            peak_current = currents[idx_max]

    # 分离左右两侧数据
    left_mask = positions < peak_pos
    right_mask = positions > peak_pos

    pos_left = positions[left_mask]
    cur_left = np.abs(currents[left_mask])
    pos_right = positions[right_mask]
    cur_right = np.abs(currents[right_mask])

    # 归一化
    I0_abs = abs(peak_current)
    y_left_norm = cur_left / I0_abs
    y_right_norm = cur_right / I0_abs

    x_left_trans = peak_pos - pos_left   # 正值
    x_right_trans = pos_right - peak_pos  # 正值

    result = {
        'peak_pos': peak_pos,
        'peak_current': peak_current * 1e6,  # → μA
        'L_left': None,
        'L_right': None,
        'L_avg': None,
        'R2_left': None,
        'R2_right': None,
        'n_points_left': len(x_left_trans),
        'n_points_right': len(x_right_trans)
    }

    # 拟合左侧
    if side in ('left', 'both') and len(x_left_trans) > 3:
        try:
            popt_left, _ = curve_fit(exp_decay, x_left_trans, y_left_norm, p0=[500], maxfev=10000)
            L_left = popt_left[0]
            y_pred = exp_decay(x_left_trans, L_left)
            ss_res = np.sum((y_left_norm - y_pred) ** 2)
            ss_tot = np.sum((y_left_norm - np.mean(y_left_norm)) ** 2)
            R2_left = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            result['L_left'] = L_left
            result['R2_left'] = R2_left
        except Exception as e:
            print(f"  ⚠ 左侧拟合失败: {e}")

    # 拟合右侧
    if side in ('right', 'both') and len(x_right_trans) > 3:
        try:
            popt_right, _ = curve_fit(exp_decay, x_right_trans, y_right_norm, p0=[500], maxfev=10000)
            L_right = popt_right[0]
            y_pred = exp_decay(x_right_trans, L_right)
            ss_res = np.sum((y_right_norm - y_pred) ** 2)
            ss_tot = np.sum((y_right_norm - np.mean(y_right_norm)) ** 2)
            R2_right = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            result['L_right'] = L_right
            result['R2_right'] = R2_right
        except Exception as e:
            print(f"  ⚠ 右侧拟合失败: {e}")

    # 计算平均值
    if result['L_left'] is not None and result['L_right'] is not None:
        result['L_avg'] = (result['L_left'] + result['L_right']) / 2
    elif result['L_left'] is not None:
        result['L_avg'] = result['L_left']
    elif result['L_right'] is not None:
        result['L_avg'] = result['L_right']

    return result


def print_result(result, label=''):
    """格式化输出拟合结果"""
    print(f"\n{'='*50}")
    if label:
        print(f"  {label}")
    print(f"  峰值位置:     {result['peak_pos']:.2f} μm")
    print(f"  峰值电流:     {result['peak_current']:.4f} μA")
    print(f"  左侧数据点数: {result['n_points_left']}")
    print(f"  右侧数据点数: {result['n_points_right']}")
    if result['L_left'] is not None:
        print(f"  左侧 L_left:  {result['L_left']:.2f} μm  (R²={result['R2_left']:.4f})")
    if result['L_right'] is not None:
        print(f"  右侧 L_right: {result['L_right']:.2f} μm  (R²={result['R2_right']:.4f})")
    if result['L_avg'] is not None:
        print(f"  ★ 平均扩散长度 L = {result['L_avg']:.2f} μm")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python fit_diffusion.py <data_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    result = fit_diffusion_length(filepath)
    print_result(result, os.path.basename(filepath))
