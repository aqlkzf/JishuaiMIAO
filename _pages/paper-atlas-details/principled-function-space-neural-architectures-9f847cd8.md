---
layout: default
permalink: /paper-atlas/principled-function-space-neural-architectures-9f847cd8/
title: "Principled_Function_Space_Neural_Architectures"
nav: false
wide: true
description: "普通神经网络通常学习有限维映射 而许多科学问题天然要求学习“函数到函数”的映射，例如从偏微分方程的外力场预测之后时刻的涡度场： 实际计算时，我们看不到完整连续函数，只能看到采样 并希望在任意查询点 Y=(yj){j=1}^{m} 上得到 g(yj)。困难在于：一个网络能接收不同大小的数组，并不等于它在不同网格上做的是同一个连续运算。固定卷积核覆盖的像素数不变时，它在物理空间中的感受野会随分辨率改变；"
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{ '/paper-atlas/' | relative_url }}" data-atlas-back>
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>Principled_Function_Space_Neural_Architectures</h1>
    <p>Principled approaches for extending neural architectures to function spaces for operator learning</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/neuraloperator/neuraloperator" target="_blank" rel="noopener noreferrer" aria-label="Open code for Principled_Function_Space_Neural_Architectures">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 从神经网络到函数空间：神经算子的原则化构造方法

### 1. 这篇论文究竟解决什么问题？

普通神经网络通常学习有限维映射

$$
x\longmapsto f(x),
$$

而许多科学问题天然要求学习“函数到函数”的映射，例如从偏微分方程的外力场预测之后时刻的涡度场：

$$
f\longmapsto g.
$$

实际计算时，我们看不到完整连续函数，只能看到采样

$$
f|_X=\big((x_i,f(x_i))\big)_{i=1}^{n},
$$

并希望在任意查询点 $Y=(y_j)_{j=1}^{m}$ 上得到 $g(y_j)$。困难在于：一个网络能接收不同大小的数组，并不等于它在不同网格上做的是同一个连续运算。固定卷积核覆盖的像素数不变时，它在物理空间中的感受野会随分辨率改变；固定 patch 的 ViT 也有类似问题（`paper.md:76-96,179-190`）。

论文希望构造满足三个原则的神经算子：

1. **离散化无关（discretization agnostic）**：同一组参数可用于不同网格或点云，并给出相互一致的结果；
2. **参数量固定**：参数量不随采样点数 $n,m$ 改变；
3. **通用逼近**：模型族原则上能逼近足够正则的函数空间算子（`paper.md:85-96`）。

这里的“一致”不是要求有限分辨率下结果完全相同，而是差异属于离散化误差，并应随网格加密而消失。

### 2. 为什么已有方法不够？

- **固定网格 CNN**：卷积核按索引定义。分辨率提高后，相同 $3\times3$ 或 $9\times9$ 核覆盖的物理区域缩小，网络实际执行的算子变了。
- **固定 patch 的 ViT**：token 化与训练网格绑定，跨分辨率时每个 token 的物理含义变化。
- **多分辨率数据增强**：可以让网络适配训练时出现过的若干网格，但不保证它能外推到未见分辨率（`paper.md:228-237`）。
- **输入/输出插值**：先把任意输入插值到固定训练网格，经过网络后再插值回来。这确实给出了一个参数量固定的“朴素算子”，但高分辨率信息可能在进入可学习部分之前就丢失（`paper.md:205-208,231`）。
- **神经场/隐式表示**：PINN（*Journal of Computational Physics*, 2019）或 NeRF（ECCV, 2020）通常用网络表示一个特定函数；神经算子学习的是对每个输入函数都输出一个函数的映射（`paper.md:42,511-518`）。

### 3. 核心创新：先连续化，再离散化

论文并没有提出一个包打天下的新层，而是总结了一套可复用的设计流程：

```text
熟悉的有限维网络层
        │
        ▼
它在连续物理域中想表达什么变换？
        │  把索引改写成坐标，把数组改写成函数
        ▼
写出连续算子（点态映射 / 积分 / 卷积 / 注意力 / 基展开）
        │
        ▼
设计与分辨率兼容的离散化
        │  物理感受野 + 求积权重 + 可查询解码器
        ▼
经验神经算子：(x_i, f(x_i)) → g(y_j)
        │
        ▼
用同一组参数测试未见分辨率
```

许多层可以写成统一模板：

$$
g(y)=\Psi\!\left(y,f(y),\int_{D_f}K(x,y,f(x),f(y))\,\mathrm dx\right),
\tag{6}
$$

实际计算用求积近似：

$$
\int_{D_f}K(x)\,\mathrm dx\approx\sum_{i=1}^{n}K(x_i)\Delta_i.
\tag{7}
$$

$K$ 表示核、注意力相互作用或其他聚合；$\Psi$ 把聚合结果与查询点特征组合；$\Delta_i$ 是采样点代表的面积/体积权重。真正关键的是：**模型参数描述连续域中的变换，而不是某个固定数组上的权重表。** 这正是论文在 `paper.md:117-158,264-289` 给出的两阶段方法。

### 4. 六类典型网络层如何变成算子层？

#### 4.1 全连接层 → 积分变换

全连接层把权重绑定在输入、输出索引上：

$$
\mathbf g_j=\sum_i\mathbf K_{ji}\mathbf f_i+\mathbf b_j.
$$

把权重和偏置改成坐标函数，并加入求积权重：

$$
g(y_j)=\sum_iK(x_i,y_j)f(x_i)\Delta_i+b(y_j)
\approx\int K(x,y_j)f(x)\,\mathrm dx+b(y_j).
\tag{9}
$$

这样 $K$ 的参数量不依赖输入点数，也能在新的 $y_j$ 上求值（`paper.md:298-317`）。

#### 4.2 逐点层 → 逐点算子

激活函数、lifting、projection、$1\times1$ 卷积本来就在每个位置应用同一个通道映射：

$$
g(x_i)=K(f(x_i)).
\tag{10}
$$

它们天然不依赖采样点数；但输出仍位于输入坐标上，要查询新坐标需再接一个算子层或插值（`paper.md:320-331`）。

#### 4.3 离散卷积 → 物理域卷积或谱卷积

不要用固定“邻居点个数”定义感受野，而要在物理坐标中固定半径 $r$：

$$
g(y_j)=\sum_{i:|x_i-y_j|\le r}K(y_j-x_i)f(x_i)\Delta_i.
\tag{12}
$$

分辨率提高时，半径内的点会增多，但覆盖的物理区域保持不变。对周期全局卷积，还可用卷积定理：

$$
K*f=F^{-1}(F(K)F(f)),
\tag{13}
$$

这导向 FNO 的谱卷积（`paper.md:334-361`）。图 3 直观展示了两者差别：固定邻居数会使物理感受野随加密而坍缩，固定物理范围则不会。

#### 4.4 GNN → 图神经算子（GNO）

普通 GNN 按图边或索引邻域聚合；GNO 则按坐标定义邻域，并使消息求和近似局部积分：

$$
g(y_j)=\sum_{i:x_i\in D(y_j)}K(x_i,y_j,f(x_i),f(y_j))\Delta_i.
\tag{15}
$$

坐标决定“从哪里收消息”，$\Delta_i$ 决定“每个点代表多少测度”，因此不同密度的点云可以逼近同一个连续运算（`paper.md:364-383`）。

#### 4.5 Transformer → 注意力算子

注意力本身就是全局聚合，但连续极限要求分子与归一化都包含求积权重：

$$
g(y_j)=\sum_i
\frac{K(f(x_i),\widetilde f(y_j))}
{\sum_\ell K(f(x_\ell),\widetilde f(y_j))\Delta_\ell}
v(f(x_i))\Delta_i.
\tag{17}
$$

规则网格上各 $\Delta_i$ 相同，会约掉并退化为标准注意力。因为注意力核只看特征值，还必须加入坐标或位置编码。交叉注意力中的查询特征可以来自输出坐标、位置编码或另一函数（`paper.md:386-405`）。

#### 4.6 编码器–解码器 → 与采样无关的潜变量接口

编码器必须把函数映射到固定维潜变量，而不是绑定固定输入数组；解码器必须能在任意 $y$ 上查询。一种代表性构造是用学习到的基函数做内积：

$$
\mathbf v_j=\sum_i[b_j(x_i)]^*f(x_i)\Delta_i,
\qquad \mathbf w=K(\mathbf v),
\qquad g(y)=\mathrm{decoder}(\mathbf w).
\tag{19}
$$

潜变量维数固定，因此接口与采样点数无关；但固定瓶颈可能丢失高频信息（`paper.md:408-427`）。

### 5. 求积权重为何是隐藏的关键？

若离散求和想逼近积分，正确形式是

$$
\int_DH(x)\,\mathrm dx\approx\sum_iH(x_i)\Delta_i.
\tag{20}
$$

规则网格上可用相同权重；非均匀点云上，若仍给每个点同样权重，采样密集处会被过度计算。图 5 的上排表明：同一函数的两种不规则采样在统一权重下得到不同面积；下排使用自适应单元宽度后，两种离散化变得一致，并随加密逼近连续积分。

因此“加入 $\Delta_i$”不是公式装饰，而是把点的计数改成对物理域测度的近似。它贯穿积分层、卷积层、GNO、注意力、编码器和损失函数。

### 6. 论文如何验证这套原则？

主实验学习二维不可压缩 Navier–Stokes 系统中“外力场 → 之后时刻涡度场”的算子。主要模型在 $128^2$ 分辨率训练，再用同一组参数测试 64、128、256、512、1,024；混合分辨率训练使用 64、128、256。训练损失为绝对 $L^2$，评估指标为相对 $L^2$（`paper.md:214-237,470-487`）。

图 4 的视觉结论是：

- FNO 和 OFormer 在展示的跨分辨率范围内误差曲线较低且较平；
- U-Net 和 ViT 在训练分辨率 128 附近最好，离开它后明显恶化；
- 核插值 U-Net 比普通 U-Net 更稳，但高分辨率仍有离散化误差；
- 多分辨率 U-Net 改善了见过的分辨率，却没有自动获得对未见分辨率的稳定外推；
- FNO + LocalConv/DiffConv 表明全局谱算子可和局部算子结合，但组合中每个组件仍有自己的离散化误差范围。

这些结果支持“架构必须对应稳定的连续算子”这一主张，但并不能单凭一张图证明所有架构的通用逼近或收敛定理。

### 7. 代码实际验证了什么？

论文对应的 Zenodo 代码包 `20335280` 直接验证了以下实现行为：

- 单分辨率训练、64–1,024 跨分辨率测试与绝对/相对 $L^2$ 设置：`train_single_res.py:20-216`、`utilities.py:303-415`；
- 混合分辨率每轮把各分辨率 loader 的 batch 随机交错，直到全部耗尽：`utilities.py:122-131,241-300`；
- OFormer 编码器，以及可选的坐标查询解码器：`models/oformer.py:543-720`；
- U-Net 按输入/基础分辨率比例缩放卷积核、归一化核面积并调整 padding：`models/unet_kernel_interp.py:38-68,150-208`；
- 朴素输入/输出插值包装：`evaluate_input_output_interpolation.py:16-51`。

代码与论文的整体匹配度为**中等**。实验流程和部分关键机制是直接证据，但 FNO、LocalNO、普通 Trainer 和相对 `LpLoss` 由外部 Neural Operator 依赖提供；工作区中另一个 `neuraloperator/` clone 是不同提交，只能作为辅助上下文，不能替代论文归档版本。

还有一个值得注意的实现细节：输入/输出插值包装在非训练分辨率分支调用全局变量 `model(new_input)`，而不是 `self.model(new_input)`（`evaluate_input_output_interpolation.py:39-51`）。在脚本全局环境中它会递归到训练分辨率后运行，但作为独立导入的类并不稳健。这是代码行为，不是论文方法主张。

### 8. 如何把这套方法用于自己的模型？

面对一个新层，可以依次问：

1. 它的索引在物理域中代表什么？
2. 它对应点态映射、局部/全局积分、卷积、注意力还是基投影？
3. 参数是否绑定某个固定样本索引或网格？
4. 感受野能否用物理距离定义？
5. 哪些求和其实是在近似积分，是否需要 $\Delta_i$？
6. 编码器是否不依赖样本数，解码器是否能在新坐标查询？
7. 参数量是否与 $n,m$ 无关？
8. 同一组参数在网格加密和未见分辨率上是否趋于一致？

这套清单比“把输入 resize 一下”更严格，因为它要求先说明模型在连续域中究竟计算什么。

### 9. 证据边界与未解决问题

#### 论文明确给出的内容

三项原则、连续化再离散化的流程、各类架构对应关系、公式 (6)–(21) 以及图 4 的比较结论来自 `paper.md:85-96,117-237,258-487`。

#### 代码直接验证的内容

训练/测试分辨率、损失设置、混合分辨率 batch 交错、OFormer、核插值与输入/输出插值来自上述归档源代码行。

#### 本文的解释性归纳

“先连续化，再离散化”和“参数描述连续域变换”是对论文两阶段策略的教学性概括，不是论文原句。

#### Not found / 缺失证据

- 本地没有补充材料 Markdown，因此 Supplementary B、C、F、G 中的完整推导、实验细节与伪代码没有作为本次主证据重新核验；
- 主代码包不含精确固定版本的 Neural Operator 依赖源码，也不含数据张量或检查点；
- 没有重新运行实验，图 4 数值仍属于论文/图像证据；
- 论文讨论非均匀求积，但主 Navier–Stokes 代码使用规则网格，归档中未找到对应图 5 的不规则点云实验。

论文也指出仍需研究实际离散化误差控制、复杂与自适应几何、高分辨率高效注意力、局部–全局混合算子，以及能够预测跨分辨率迁移性的理论（`paper.md:240-252`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Principled Approaches for Extending Neural Architectures to Function Spaces for Operator Learning

Berner *et al.*, *Nature Machine Intelligence* 8, 1173–1181 (2026). DOI: `10.1038/s42256-026-01267-z`.

### Problem

Many scientific tasks map one field to another—for example, a PDE forcing function to a solution field—but standard neural networks operate on finite vectors and often bind their parameters, receptive fields or tokenization to one discretization. Merely accepting differently sized arrays does not guarantee that the same function-space operation is applied at each resolution. The paper seeks a systematic way to preserve modern architectural inductive biases while making the learned map discretization agnostic, fixed in parameter count and capable of approximating operators (`paper.md:25-31,76-96`).

### Limitations of Existing Approaches

- Fixed-grid CNNs and vision transformers can change their physical operation when grid spacing changes: a fixed index stencil or patch size covers a different domain region (`paper.md:179-190,214-231`).
- Multi-resolution augmentation promotes consistency only on resolutions seen during training; it does not impose a principled bias for unseen discretizations (`paper.md:228-237`).
- Input/output interpolation defines a naive operator interface but can discard high-resolution information before the learnable component acts (`paper.md:205-208,231`).
- Neural fields represent one function at a time. Examples include physics-informed neural networks (*Journal of Computational Physics*, 2019) and neural radiance fields (ECCV, 2020); neural operators instead learn a map that emits a function for each input function (`paper.md:42,511-518`).

### Proposed Framework

The paper contributes a general recipe, not a single new architecture:

1. Identify the continuous function-space operation that a finite-dimensional layer approximately discretizes.
2. Express parameters, interactions and receptive fields using domain coordinates and functions rather than array indices.
3. Replace sums intended as integrals with quadrature-weighted aggregations.
4. Discretize the continuous operator so the learned parameter set is independent of point count and can be evaluated at new input/output coordinates (`paper.md:117-158,264-289`).

This converts dense layers into integral transforms, elementwise maps into pointwise operators, convolutions into physical-support or spectral operators, GNN message passing into graph neural operators, attention into a normalized integral operator and encoder–decoder models into discretization-independent latent interfaces (`paper.md:161-211,292-427`). The unifying insight is **continuum first, discretization second**: varying tensor size is useful only if all finite computations approximate the same underlying map.

### Evaluation and Main Findings

The main benchmark maps a Navier–Stokes forcing field to later-time vorticity. Models train at resolution 128 and are evaluated at 64, 128, 256, 512 and 1,024 with the same parameters; mixed-resolution models train at 64, 128 and 256. Training uses absolute $L^2$ error, evaluation uses relative $L^2$ error, and Adam is used with model-specific schedules (`paper.md:214-237,470-487`).

Figure 4 shows that FNO and OFormer remain in a low-error band across displayed resolutions, whereas fixed-grid U-Net and ViT deteriorate away from the training resolution. Kernel interpolation improves U-Net but remains less stable at high resolution; mixed-resolution U-Net performs better at seen resolutions without matching the unseen-resolution behavior of the operator architectures. FNO + LocalConv and FNO + DiffConv show that global spectral and local operator components can be combined, although each component retains its own discretization-error range (`paper.md:220-237`; direct visual read of `figure_04.png`). Exact curve values were not extracted from pixels.

### What the Code Verifies

The paper-linked Zenodo release (`20335280`, archive commit label `892ba1c…`) directly provides:

- single- and mixed-resolution runners and the 64–1,024 test protocol (`train_single_res.py:20-216`; `train_multi_res.py:54-240`; `utilities.py:303-415`);
- a uniform-grid absolute $L^2$ training loss and relative $L^2$ evaluation setup (`utilities.py:47-120`; `train_single_res.py:178-214`);
- randomized interleaving that consumes batches from every selected resolution once per epoch (`utilities.py:122-131,241-300`);
- archive-local OFormer, U-Net kernel interpolation and input/output interpolation mechanisms (`models/oformer.py:543-747`; `models/unet_kernel_interp.py:38-208`; `evaluate_input_output_interpolation.py:16-51`).

The code–paper fidelity is **medium**: the experiment protocol and several custom mechanisms are directly represented, but FNO/LocalNO and generic trainer internals resolve through an external pinned Neural Operator library. The separate `neuraloperator/` clone in this workspace is supporting context at a different commit and is not treated as primary release evidence.

### Reproducibility: 3/5

**Strengths:** the paper-specific archive, model/configuration branches, optimizer settings, resolution splits, data downloader and usage instructions are available. The release README identifies an Ubuntu/CUDA/GPU setup and pins the expected Neural Operator library commit (`README.md:7-33`).

**Limits:** dataset tensors and checkpoints are external; the exact pinned dependency source is not bundled; the local supplementary Markdown is absent; OFormer's supplied configuration disables its optional query decoder; generic FNO/LocalNO internals are outside the primary archive. No experiment was rerun, so reported curves remain paper/figure evidence rather than reproduced results. The release also contains a fragile global-variable call in the input/output interpolation wrapper (`evaluate_input_output_interpolation.py:39-51`).

### Scope and Open Questions

The empirical results support the design principle that physical receptive fields, principled quadrature and information-preserving interfaces improve cross-resolution behavior. They do not establish that every architecture in the framework has identical convergence, accuracy or cost. Important open directions named by the paper include practical discretization-error control, complex/adaptive geometries, efficient high-resolution attention, hybrid local–global operators and theory that predicts when an inductive bias transfers across resolutions (`paper.md:240-252`).

Detailed method derivations and evidence separation are in `doc_method.md`; direct archive mapping and all `Not found` scopes are in `doc_code.md`; image-grounded support is in `figure_analysis.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
