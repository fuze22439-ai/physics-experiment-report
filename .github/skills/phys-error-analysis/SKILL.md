---
name: phys-error-analysis
description: 'Use when: performing uncertainty analysis for physics experiments, calculating Type A and Type B uncertainties, combined standard uncertainty, error propagation, significant figures formatting, measurement uncertainty evaluation. Keywords: 误差分析, 不确定度, A类不确定度, B类不确定度, 合成不确定度, 标准偏差, 误差传递, 有效数字'
argument-hint: '数据或文件路径'
---

# 物理实验误差分析

## When to Use
- 计算实验测量值的不确定度
- A类不确定度（统计方法）和 B类不确定度（非统计方法）评定
- 合成标准不确定度计算
- 间接测量量的误差传递
- 科学计数法和有效数字格式化

## Uncertainty Types

### A类不确定度（统计方法）

$$u_A = s(\bar{x}) = \sqrt{\frac{\sum_{i=1}^{n}(x_i - \bar{x})^2}{n(n-1)}} = \frac{s(x)}{\sqrt{n}}$$

其中 $s(x)$ 为实验标准差：
$$s(x) = \sqrt{\frac{\sum_{i=1}^{n}(x_i - \bar{x})^2}{n-1}}$$

### B类不确定度（非统计方法）

仪器误差引起的不确定度（均匀分布）：
$$u_B = \frac{\Delta_{仪}}{\sqrt{3}}$$

其中 $\Delta_{仪}$ 为仪器允差。

### 合成标准不确定度

$$u_c = \sqrt{u_A^2 + u_B^2}$$

### 间接测量误差传递

对于 $y = f(x_1, x_2, ..., x_n)$：
$$u_c(y) = \sqrt{\sum_{i=1}^{n} \left(\frac{\partial f}{\partial x_i}\right)^2 u^2(x_i)}$$

常用公式：
- 加减：$y = ax_1 \pm bx_2$ → $u_c = \sqrt{a^2 u_1^2 + b^2 u_2^2}$
- 乘除：$y = k x_1^a x_2^b$ → $\frac{u_c}{y} = \sqrt{a^2\left(\frac{u_1}{x_1}\right)^2 + b^2\left(\frac{u_2}{x_2}\right)^2}$

## Procedure

1. **识别直接测量量**及其仪器允差
2. **A类评定**：多次测量计算 $u_A = s/\sqrt{n}$
3. **B类评定**：根据仪器参数计算 $u_B$
4. **合成**：$u_c = \sqrt{u_A^2 + u_B^2}$
5. **误差传递**（间接测量）：用偏导数公式
6. **结果表达**：$x = \bar{x} \pm u_c$（单位），保持有效数字一致

## Result Formatting

不确定度一般保留 1-2 位有效数字，测量值末位与不确定度末位对齐：
- ✅ $L = 667 \pm 12$ μm
- ✅ $I = 0.0511 \pm 0.0005$ μA
- ❌ $L = 667.05 \pm 12.3$ μm（位数不对齐）

## Reference Script
See [uncertainty.py](./scripts/uncertainty.py) for automated calculation.
