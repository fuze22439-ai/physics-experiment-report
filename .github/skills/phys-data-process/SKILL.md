---
name: phys-data-process
description: 'Use when: processing physics experiment data, scanning photocurrent data, line scan analysis, finding peak values, extracting max current and position from tab-separated data files, calculating diffusion length L from exponential decay I=I0*exp(±(x-D)/L), batch processing multiple voltage files, converting units (A to μA), curve fitting for physics experiments. Keywords: 数据处理, 扫描光电流, 线扫, 峰值, 扩散长度, 拟合, 物理实验数据'
argument-hint: '实验文件夹路径'
---

# 物理实验数据处理

## When to Use
- 处理扫描光电流线扫/面扫 `.txt` 数据文件
- 从多电压扫描数据中提取峰值电流和峰值位置
- 基于指数衰减公式 $I = I_0 e^{\pm(x-D)/L}$ 拟合计算扩散长度
- 批量处理多样品、多电压的实验数据
- 数据单位转换（A → μA, m → μm）

## Data File Format

原始数据文件为两列制表符分隔：
```
Position(μm)    Current(A)
0.00            1.23e-9
...
```

## Procedure

### 1. Peak Detection

对每个电压下的线扫数据：
1. 跳过标题行
2. 解析两列：`position` (μm) 和 `current` (A)
3. 找到最大绝对值电流及其对应位置
4. 记录：峰值电流 (μA) = `current_max_abs × 10⁶`，峰值位置 (μm)

### 2. Diffusion Length Calculation (扩散长度)

对 0V 数据：
1. 找到峰值位置 D 和峰值电流 I₀
2. 在峰值**左侧**取数据点，拟合 $I = I_0 e^{(x-D)/L_{left}}$
3. 在峰值**右侧**取数据点，拟合 $I = I_0 e^{-(x-D)/L_{right}}$
4. 扩散长度 $L = (L_{left} + L_{right}) / 2$

### 3. Batch Processing

```python
# 扫描样品文件夹，自动匹配文件
samples = ['样品1', '样品2', '样品3']
voltages = ['-0.5', '-0.3', '0', '0.3', '0.5']
```

### 4. Output Format

生成 Markdown 表格：
```markdown
| 项目/电压 (V)          |  -0.5  |  -0.3  |    0    |   0.3   |   0.5   |
| ---------------------- | :----: | :----: | :-----: | :-----: | :-----: |
| 最大峰值电流 (μA)     |  ...   |  ...   |   ...   |   ...   |   ...   |
| 最大峰值电流位置 (μm) |  ...   |  ...   |   ...   |   ...   |   ...   |
```

## Reference Scripts

- [calc.py](../../../扫描光电流/calc.py) — 参考：峰值提取脚本
- [fit_diffusion.py](./scripts/fit_diffusion.py) — 扩散长度拟合脚本

## Scientific Notes

- 暗电流通常在 nA 量级，光电流在 μA 量级
- 扩散长度 L 表征少数载流子在半导体中的扩散能力
- 正负电压对应不同的载流子输运方向
