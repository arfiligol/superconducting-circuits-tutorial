---
aliases:
- 為什麼磁通量子化
tags:
- diataxis/explanation
- audience/user
- topic/physics
status: draft
owner: docs-team
audience: user
scope: 解釋超導迴路中的磁通量子化來源
version: v0.1.0
last_updated: 2026-02-16
updated_by: team
---

# 為什麼磁通量會是量子化的？

## 本章回答的問題

為什麼在超導封閉迴路中，可允許的磁通不是連續值，而是接近磁通量子 `\Phi_0` 的整數倍？

## 先備知識對照

- 量子：波函數單值性與相位
- 電磁：向量位勢 `\mathbf{A}`、Stokes 定理
- 古典：封閉路徑積分與約束條件

## 物理核心

若超導序參量寫成

$$
\Psi(\mathbf{r}) = |\Psi(\mathbf{r})| e^{i\theta(\mathbf{r})},
$$

則規範不變相位梯度可寫為

$$
\nabla\theta - \frac{2\pi}{\Phi_0}\mathbf{A}.
$$

沿封閉路徑 `C` 積分，波函數單值性要求

$$
\oint_C \left(\nabla\theta - \frac{2\pi}{\Phi_0}\mathbf{A}\right)\cdot d\mathbf{l} = 2\pi n,
\quad n\in\mathbb{Z}.
$$

因此可得到磁通量子化條件（在常見近似下）

$$
\Phi \approx n\Phi_0.
$$

!!! note "歷史脈絡"
    磁通量子化把「超導是宏觀量子態」變成可直接量測的事實，成為 SQUID 與超導量測技術的重要基礎。

## 工程映射

- `\Phi/\Phi_0` 直接決定 SQUID 迴路的偏壓工作點。
- 量子化條件提供迴路相位約束，限制可行的動力學分支。

## 限制與近似

- 需在相干長度與溫度條件允許下才可觀察清楚量子化。
- 含多個 Josephson 接面的迴路，需一併納入接面相位跳躍。

## 跨文件導航

- 下一步：[為什麼非線性會讓能階間距不一致？](why-nonlinearity-makes-unequal-level-spacing.md)
- 任務導向：[Flux Analysis](../../tutorials/flux-analysis.md)
