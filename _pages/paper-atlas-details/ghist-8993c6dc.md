---
layout: default
permalink: /paper-atlas/ghist-8993c6dc/
title: "GHIST"
nav: false
description: "GHIST 学习一条“组织形态 → 细胞类型与邻域 → 单细胞基因表达”的映射：训练时需要空间配准的 H&E 与亚细胞空间转录组（SST），训练完成后只输入 H&E、细胞核实例分割结果，以及可选的单细胞参考表达谱，就能为每个细胞预测 280–382 个基因的表达。 论文发表于 Nature Methods（2025），DOI 为 10.1038/s41592-025-02795-z。"
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{ '/paper-atlas/' | relative_url }}">
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>Deconvolution</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>GHIST</h1>
    <p>Spatial gene expression at single-cell resolution from histology using deep learning with GHIST</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GHIST 方法详解：从 H&E 图像预测单细胞空间基因表达

### 一句话理解

GHIST 学习一条“组织形态 → 细胞类型与邻域 → 单细胞基因表达”的映射：训练时需要空间配准的 H&E 与亚细胞空间转录组（SST），训练完成后只输入 H&E、细胞核实例分割结果，以及可选的单细胞参考表达谱，就能为每个细胞预测 280–382 个基因的表达。

论文发表于 *Nature Methods*（2025），DOI 为 `10.1038/s41592-025-02795-z`。

### 1. 它要解决什么问题？

空间转录组能够回答“一个基因在组织中的什么位置、什么细胞里表达”，但实验成本和流程复杂度都很高。H&E 病理切片则几乎是临床和病理研究的常规数据。如果能从 H&E 推断空间表达，就可以为大量历史切片增加一个“计算生成的空间组学模态”。

已有方法多在 spot 层面工作。例如：

- ST-Net（*Nature Biomedical Engineering*, 2020）用 CNN 从图像 patch 预测 spot 表达；
- HisToGene（bioRxiv, 2021）和 Hist2ST（*Briefings in Bioinformatics*, 2022）引入 Transformer/图网络；
- DeepPT（*Nature Cancer*, 2024）预测组织学对应的转录组信号；
- iStar（*Nature Biotechnology*, 2024）把 spot 数据超分辨到更细的像素。

这些方法的核心限制是：一个 spot 往往混合多个细胞，超分辨像素也可能同时包含细胞和背景；部分高分辨方法在推断时仍需要实测空间表达。它们不能直接完成“仅从 H&E 得到真实细胞单位的表达向量”这一任务。

GHIST 的难点也很明确：

1. 一张切片中细胞数量可达数万甚至数千万，输出规模远大于 spot 预测；
2. 许多细胞类型形态相似，例如 B 细胞和 T 细胞，单靠细胞核外观很难区分；
3. 基因表达不仅由单个细胞的形态决定，还受细胞类型和局部邻域影响；
4. H&E 染色、扫描和细胞核分割存在明显域偏移与质量差异。

### 2. GHIST 的核心想法

GHIST 不把基因表达当作一个孤立的回归目标，而是同时学习四层相互关联的信息：

```text
细胞核形态与局部组织结构
          │
          ├────────────┐
          ▼            ▼
       细胞类型     邻域细胞组成
          │            │
          └──────┬─────┘
                 ▼
          单细胞基因表达
```

这里的关键不是简单地增加几个输出头，而是让这些任务彼此约束：

- 形态特征要能支持细胞类型分类；
- 预测的基因表达还要能够反推出合理的细胞类型；
- patch 内的细胞类型分布要与邻域组成一致；
- 邻域组成再通过 cross-attention 修正每个细胞的表达；
- 对容易混淆的细胞类型，推断时可用邻域组成恢复缺失的少数类型，并切换到相应的表达分支。

这种多任务设计的作用，是缩小“数值上接近但生物学不合理”的解空间。

### 3. 输入、输出与前置条件

#### 训练输入

- 空间配准的 H&E 图像与 SST 数据；
- H&E 中的细胞核实例分割图；
- SST 分割后得到的每细胞基因表达；
- 可选的细胞类型标签；
- 可选的平均单细胞参考表达矩阵
  (R\in &#123;&#123;\mathfrak{R}}}^&#123;&#123;n}_{\rm AvgExp}\times n_{\rm genes}})。

参考表达不必来自同一个患者，也不要求参考中的细胞类型与目标标签一一对应；但训练和推断应使用同一个参考矩阵。

#### 推断输入

- H&E 图像；
- 预先得到的细胞核实例分割图；
- 已训练模型；
- 可选的平均参考表达矩阵 (R)。

推断不需要 SST，也不需要真实细胞类型标签。需要注意，“H&E only”是相对于空间组学输入而言；源码仍需要上游细胞核分割结果。

#### 输出

对每个细胞输出：

- 基因表达向量 (y'_i\in &#123;&#123;\mathfrak{R}}}^{n_{\rm genes}})；
- 辅助细胞类型预测；
- 细胞 ID 和核面积等用于重叠 patch 去重的信息。

模型还输出像素级分割/分类图和 patch 级邻域组成。

### 4. 从输入到输出的完整计算流程

```text
训练：H&E + SST + 核实例 mask + 可选细胞类型/参考表达
  │
  ├─ 切成 256×256 patch
  ├─ RGB 标准化，表达 log1p
  ├─ 随机翻转与 90°/180°/270° 旋转
  │
  ▼
UNet 3+ 主干网络
  ├─ 像素级核分割/细胞类型图
  ├─ 第一层高分辨率特征
  └─ 最后一层解码特征
  │
  ▼
对每个核做 masked mean pooling
+ 对整个 patch 做全局 mean pooling
  │
  ▼
768 维拼接特征 → 256 维 x_nucleus
  │
  ├─ 形态细胞类型头
  ├─ 邻域组成头
  └─ 表达头
       ├─ 参考表达加权，或直接 MLP 回归
       ├─ 邻域 cross-attention
       ├─ 主表达 y'
       ├─ 表达→细胞类型一致性约束
       └─ 特定细胞类型表达分支
  │
  ▼
多项损失求和，端到端反向传播

推断：H&E + 核 mask (+ R)
  │
  ▼
同一模型前向计算
  │
  ├─ 可选的邻域驱动细胞类型修正
  ├─ 修正细胞切换到相应表达分支
  ├─ 重叠 patch 中保留核可见面积最大的预测
  └─ 输出 cell × gene CSV
```

### 5. 视觉主干：怎样把 H&E 变成每细胞表示？

输入 patch 为

$$
x\in &#123;&#123;\mathfrak{R}}}^{h\times w\times 3}.
$$

UNet 3+ 输出每个像素属于细胞类型或背景的概率，并用像素交叉熵训练：

$$
{L}_{\rm Morph}=-\frac{1}{N}\sum_{i=1}^{N}\sum_{j=1}^{M} I_{ij}\log p_{ij}.
$$

源码 `model/backbone.py` 实现五尺度编码器、解码器和 full-scale skip connections。`model/model.py:93-133` 取主干第一层和最后解码层的特征：

1. 用每个核的实例 mask 对特征逐像素相乘；
2. 在核内求和并除以核面积，消除核大小差异；
3. 对同两层特征在整个 patch 上求平均，得到局部环境表示；
4. 将核级与 patch 级特征拼接；
5. 经 `Embed` 映射为 256 维 (x_{\rm nucleus})。

直观上，一个细胞的表示同时包含“这个核长什么样”和“它周围组织长什么样”。

### 6. 细胞类型为什么既从图像预测，又从表达预测？

#### 图像到细胞类型

形态分支以 (x_{\rm nucleus}) 为输入，经两层 MLP 输出细胞类型 logits，并使用交叉熵

$$
{L}_&#123;&#123;\rm CT},{\rm class}}=-\frac{1}{C}\sum_{i=1}^{C}\sum_{j=1}^{M}I_{ij}\log p_{ij}.
$$

这迫使视觉表示保留细胞类型相关信息。

#### 表达到细胞类型

另一个 MLP 同时读取预测表达和真实表达，并比较三件事：

- 预测表达能否正确分类细胞类型：(L_&#123;&#123;\rm CT},{\rm expr}})；
- 两种表达产生的中间 embedding 是否方向一致：

$$
{L}_&#123;&#123;\rm CT},{\rm embed}}=\frac{1}{C}\sum_{i=1}^{C}\left(1-\cos(x_&#123;&#123;\rm pr},i},x_&#123;&#123;\rm gt},i})\right);
$$

- 两种表达产生的 logits 是否一致：

$$
{L}_&#123;&#123;\rm CT},{\rm logits}}=\frac{1}{C}\sum_{i=1}^{C}(p_&#123;&#123;\rm pr},i}-p_&#123;&#123;\rm gt},i})^2.
$$

因此，主表达头不仅被要求接近真实数值，还要保留细胞类型的表达特征。代码把 embedding loss 放大 100 倍，与论文 Methods 一致。

### 7. 邻域组成如何进入模型？

模型先在每个 patch 内平均所有细胞的 256 维 embedding，再用 softmax MLP 预测邻域细胞类型比例 (P_{\rm est})。论文使用两项 KL 约束：

$$
L_&#123;&#123;\rm NC},{\rm est}}=D_{\rm KL}(P_{\rm est}\|Q),
$$

$$
L_&#123;&#123;\rm NC},{\rm pr}}=D_{\rm KL}(P_{\rm CT}\|Q),
$$

其中 (Q) 是真实组成，(P_{\rm CT}) 是把辅助细胞类型预测计数后得到的组成。

这项设计有两个用途：

1. 让单细胞特征的集合与整个局部区域一致；
2. 对形态近似的细胞类型提供先验。例如，若模型把大部分淋巴细胞都判成 T 细胞，但邻域头认为该 patch 应包含一定比例的 B 细胞，就可以在推断时恢复一部分 B 细胞。

补充图 S1/S2 显示，去掉细胞类型或邻域组成时，B 和 myeloid 等少数类型可能消失；组合这些信息可改善细胞类型比例。

### 8. 表达预测头：有参考和无参考两种路径

#### 路径 A：使用平均参考表达

模型先从核 embedding 预测对参考谱的 softmax 权重 (W)：

$$
W(x_{\rm nucleus})=\left({\rm ReLU}(x_{\rm nucleus}W_r^{(1)}+b_r^{(1)})\right)W_r^{(2)}+b_r^{(2)}.
$$

第 (j) 个基因的初始表达为

$$
S_j=\sum_{k=1}^{K}W_kR_{kj}.
$$

这不是先判定一个离散细胞类型再查表，而是学习多个参考谱的连续混合权重。补充图 S20 使用 7、15 和 27 类参考谱，性能总体稳定，说明参考标签体系具有一定灵活性。

#### 路径 B：不使用参考表达

模型直接从核 embedding 回归表达：

$$
S(x_{\rm nucleus})=\left({\rm ReLU}(x_{\rm nucleus}W_e^{(1)}+b_e^{(1)})\right)W_e^{(2)}+b_e^{(2)}.
$$

源码在这个 MLP 输出后额外应用一次 ReLU，再进入可选的 cross-attention；这是论文公式没有明确写出的实现细节。

### 9. 邻域 cross-attention 真正在做什么？

GHIST 把 patch 的邻域组成 (p_{\rm est}) 作为 query，把单细胞的初始表达 (S) 作为 key/value，使用 8 头 cross-attention，最后投影为基因维度的修正量 (b)。

有参考时：

$$
y'={\rm ReLU}(S+b).
$$

无参考时：

$$
y'={\rm ReLU}(b).
$$

源码 `model/modules.py:6-33` 使用 `nn.MultiheadAttention`。从张量形状看，它对每个细胞做“邻域组成与本细胞初始表达”的融合，而不是让一个 patch 内所有细胞互相做序列注意力。换句话说，邻域信息是 patch 级条件变量，不是显式的细胞—细胞图传播。

### 10. 推断时的细胞类型恢复与表达切换

论文对目标细胞类型 (t) 定义修正量：

$$
v_t=\alpha n_{\rm cells}(p_&#123;&#123;\rm est},t}-p_&#123;&#123;\rm CT},t})|\Phi_t|,
$$

并更新 logits：

$$
y'_&#123;&#123;\rm NC},t}=v_t+y'_&#123;&#123;\rm CT},t}.
$$

乳腺癌实验对 B、myeloid 和 T 细胞使用该机制，并保护概率高于 0.6 的 T 细胞。若最终类型发生改变，相应细胞的主表达会被替换成针对该类型训练的表达分支。TCGA invasive 场景还使用很大的疾病特异性修正系数。

源码 `model/adjustments.py` 的随机向量生成、最后一维噪声取法，以及 immune/invasive 分支划分，比论文公式更具体，也不是完全透明的一一对应。因此这部分论文—代码匹配应标记为 **Partial**。

### 11. 总损失与优化

论文把所有任务联合为：

$$
\min\sum_n\left[
L_{\rm Morph}+L_&#123;&#123;\rm CT},{\rm class}}+L_&#123;&#123;\rm CT},{\rm embed}}+L_&#123;&#123;\rm CT},{\rm logits}}+L_&#123;&#123;\rm CT},{\rm expr}}
+L_&#123;&#123;\rm NC},{\rm est}}+L_&#123;&#123;\rm NC},{\rm pr}}
+\frac{1}{N_{\rm CT}}L_&#123;&#123;\rm GE},{\rm adj}}+L_{\rm GE}
\right].
$$

主表达损失为每细胞 MSE：

$$
L_{\rm GE}=\frac{1}{C}\sum_{i=1}^{C}(y'_i-y_i)^2.
$$

论文还定义 spot 模式：先把 patch 中所有核的预测相加，再与 spot 表达做 MSE。但在本次检查的主训练入口中，没有找到清晰独立的 spot-mode 开关，因此该部分实现边界记为 `Not found/Partial`，不能只凭论文公式断言主源码完整支持。

论文训练设置为 batch size 8、50 epochs、AdamW、learning rate 0.001、betas (0.9, 0.999)、weight decay 0.0001。源码大部分参数一致，但 `train.py:217-219` 会随 epoch 线性衰减学习率，而论文写的是固定学习率。这是一个明确的论文—代码差异。

### 12. 数据切分与重叠 patch

Xenium 实验将整张 H&E 沿纵向分成 5 个不重叠区域做五折验证。训练 patch 不重叠；验证/推断使用 30 像素重叠，以减少边缘处细胞被截断的问题。

同一个细胞可能出现在多个重叠 patch 中。源码在推断结束后按 cell ID 合并，保留“该细胞核在 patch 中可见面积最大”的预测（`inference.py:431-453`）。这与论文 Practical implementation 完全对应，是一个容易忽略但很重要的后处理步骤。

### 13. 结果应该怎样解读？

#### 单细胞层面

- 两个乳腺 Xenium 样本的表达推导细胞类型准确率为 0.75 和 0.66；
- top 20 和 top 50 SVG 的中位 PCC 为 0.7 和 0.6；
- *SCD*、*FASN*、*FOXA1*、*EPCAM* 的相关性为 0.74–0.84；
- melanoma 与 lung adenocarcinoma 的预测/真实细胞类型比例相关性分别为 0.92 和 0.97。

图 2 是最直接的证据，因为有 SST-derived ground truth。它也显示非 SVG 的相关性接近 0，说明高相关性主要集中在有空间信号的基因，而不是所有基因都被模型“平滑”成相关。

#### spot 层面

HER2ST 上 GHIST 的 all-gene PCC 为 0.16、SSIM 为 0.10；SVG PCC 为 0.27、SVG SSIM 为 0.26，均优于比较方法。但 all-gene 的绝对相关性仍然不高，所以更准确的表述是“在低绝对信号下相对最好”，而不是“已经精确重建所有基因”。

#### 外部 TCGA 与下游分析

GHIST 在 92 张 HER2-positive TCGA WSI 上生成单细胞表达，并进一步构造生存、空间模式、细胞类型特异表达和 SCNA 关联分析。这证明输出具有分析潜力，但 TCGA 没有配对 SST，因此图 4/5 主要展示规模、内部合理性和假设生成，不能替代外部空间真值验证。图 5e 的 SCNA 关联使用未做多重校正的 (P) 值，也应视为探索性发现。

### 14. 代码里最值得注意的实现细节

| 事项 | 论文描述 | 源码行为 | 判断 |
|---|---|---|---|
| 核/patch 特征 | 第一层与最后层特征，核内和 patch 平均 | `model/model.py:93-133` 明确实现 | Exact |
| 表达参考混合 | softmax 权重加权参考谱 | `model/model.py:204-260` | Exact |
| 邻域 cross-attention | 组成作 query，表达作 key/value | `model/modules.py:6-33` | Exact |
| 邻域 KL | 论文按 patch 写出 | 代码先在 batch 聚合并再次 softmax | Partial |
| 无参考表达 | 两层 MLP 后进入邻域模块 | 代码在中间额外 ReLU | Partial |
| 调整表达分支 | 通用目标类型分支 | 代码硬编码 immune/invasive 三套头 | Partial |
| 随机类型恢复 | Eqs. 7–8 | 噪声生成与取值更具体且不完全直观 | Partial |
| 学习率 | 固定 0.001 | 每个 epoch 线性衰减 | Partial |
| 重叠 patch 去重 | 保留核面积最大者 | `inference.py:431-453` | Exact |

整体代码忠实度为 **medium**：核心网络和主要损失不是概念性伪代码，而是有可定位的直接实现；但若要复现论文数值，必须处理上述差异和缺失资产。

### 15. 复现时的实际障碍

- 主仓库有核心模型、训练/推断脚本、固定版本依赖、demo 数据、三个 notebook 和外部 demo checkpoint 下载命令。
- 预处理 notebook 不提供 H&E–Xenium 配准流程，需要用户准备已对齐图像或使用外部/手工配准。
- 核分割依赖外部 Hover-Net 仓库和 checkpoint；补充图 S18 显示分割方法会显著影响结果。
- 仓库中只有 `config_demo.json`，没有论文各数据集完整配置和所有 fold checkpoint。
- 没有自动化测试；本次分析也没有执行安装、训练或推断。
- 论文图 2–5 的生存、多组学、SCNA 和绘图流程不在主 GHIST snapshot 中，README 指向另一个 `GHIST_figure` 仓库。
- 内部 DCIS 队列需要向作者申请；公共 Xenium、HER2ST、TCGA 和参考数据提供了链接。

### 16. 最后怎样把 GHIST 记住？

可以把 GHIST 看成三层约束：

1. **视觉层：** UNet 3+ 从 H&E 提取核与局部组织特征；
2. **生物结构层：** 细胞类型和邻域组成约束表示与表达；
3. **表达层：** 参考谱混合或直接回归，再用邻域 cross-attention 得到每细胞表达。

它真正的新意不是“用 CNN 预测表达”本身，而是把形态、类型、邻域和表达连接成一个联合训练系统，并把输出推进到单细胞空间尺度。与此同时，模型仍然依赖高质量配准、核分割、染色域一致性和足够的训练数据；对外部队列的下游发现应作为计算假设，而不是实测空间组学的替代证据。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## GHIST

**Paper:** *Spatial gene expression at single-cell resolution from histology using deep learning with GHIST*
**Journal:** *Nature Methods* (2025)
**DOI:** `10.1038/s41592-025-02795-z`

### Problem

Spatial transcriptomics can reveal where genes are expressed in tissue, but subcellular platforms remain expensive and operationally complex. H&E slides are far more abundant, so the paper asks whether a model can learn from paired H&E and subcellular spatial transcriptomics (SST) and later infer gene expression for every segmented cell from H&E alone.

Earlier image-to-expression methods were mainly spot-level: ST-Net (*Nature Biomedical Engineering*, 2020), HisToGene (bioRxiv, 2021), Hist2ST (*Briefings in Bioinformatics*, 2022), DeepPT (*Nature Cancer*, 2024) and related approaches predict mixtures of multiple cells per spot. iStar (*Nature Biotechnology*, 2024) super-resolves spot data, but its pixels may mix cells and background and it still uses measured spatial expression at prediction time. These settings do not provide true cell-resolved expression from histology alone and have shown limited translational performance.

### Proposed Method

GHIST is a multitask deep-learning framework that links four layers of information:

- nucleus morphology and local H&E context;
- cell type;
- local cell-type composition;
- per-cell gene expression.

A UNet 3+ backbone jointly performs nucleus segmentation/classification and supplies early and late feature maps. Features are pooled within each nucleus and over its image patch, then embedded into a 256-dimensional vector. Auxiliary heads predict cell type and neighborhood composition. The expression head either learns a weighted mixture of optional average single-cell reference profiles or directly regresses expression, then conditions the result on neighborhood composition through eight-head cross-attention. Expression-derived cell-type losses encourage biologically plausible profiles. During inference, neighborhood composition can recover visually confusable minority cell types and switch affected cells to a cell-type-specific expression branch.

Training uses paired H&E/SST, nucleus masks and optional cell labels/reference profiles. Inference requires H&E, an upstream nucleus mask and the trained model; SST is not required. The study predicts panels of 280–382 genes.

### Evaluation and Main Results

The evaluation spans multiple levels:

- **Single-cell ground truth:** Xenium breast cancer samples, plus lung adenocarcinoma and melanoma datasets.
- **Spot-level benchmark:** HER2ST with patient-grouped fourfold cross-validation against ST-Net, HisToGene, GeneCodeR, DeepSpaCE, DeepPT, Hist2ST, THItoGene and iStar.
- **External scaling and downstream utility:** 92 TCGA HER2-positive slides, 461 TCGA luminal slides and an in-house cohort of 44 individuals.
- **Metrics:** cell-type accuracy/proportion, PCC, SSIM, RMSE, SVG/HVG performance, survival *C*-index, log-rank tests and spatial feature analyses.

On two breast Xenium samples, expression-derived cell-type accuracy was 0.75 and 0.66. The top 20 and top 50 SVGs had median PCC of 0.7 and 0.6, whereas non-SVG correlations stayed near 0–0.1. Individual SVGs such as *SCD*, *FASN*, *FOXA1* and *EPCAM* reached correlations of 0.74–0.84. Predicted versus measured cell-type proportions also agreed strongly in melanoma ((r=0.92)) and lung adenocarcinoma ((r=0.97)).

On HER2ST, GHIST obtained the best reported all-gene PCC (0.16) and SSIM (0.10), plus SVG PCC 0.27 and SVG SSIM 0.26. These are improvements over baselines, although the absolute all-gene correlations remain modest. GHIST-derived pseudobulk achieved average survival *C*-index 0.57 and separated risk groups with (P=0.017).

Applied to TCGA H&E slides, GHIST generated a new predicted single-cell spatial modality at large scale. The authors used it for cell-type-specific expression, spatial survival features, patient subgrouping and associations between copy-number alterations and differential spatial patterning. These analyses demonstrate possible utility, but most lack matched spatial ground truth and should be viewed as prediction-driven discovery rather than experimental validation.

### What the Figures Establish

- **Fig. 1:** architecture and training/inference data flow.
- **Fig. 2:** the strongest direct evidence—single-cell predictions compared with SST-derived ground truth.
- **Fig. 3:** spot-level benchmark and downstream survival comparison; superiority is relative to low absolute PCCs.
- **Fig. 4:** WSI-scale prediction and coherent cell/marker maps on TCGA, without matched SST truth.
- **Fig. 5:** downstream spatial and multi-omics hypotheses; SCNA association *P* values are unadjusted.

Supplementary ablations show complementary benefits from cell type, neighborhood composition and average reference expression. They also show sensitivity to nucleus segmentation, patch size and training-data quantity, while performance is broadly stable across several reference-cell taxonomies.

### Limitations

- The paired training set contains many cells but relatively few slides; more diverse training data should improve robustness.
- H&E stain quality and domain shift materially affect prediction. Two poor-quality TCGA slides produced implausibly low malignant fractions.
- Accuracy depends on upstream image registration and nucleus segmentation; the repository tutorial delegates these to external/manual registration and Hover-Net.
- A 300–500-gene spatial panel may omit markers needed to distinguish clinically relevant cell types.
- The neighborhood recovery rule includes empirical, disease-specific settings and a stochastic adjustment.
- TCGA downstream findings are based on predicted expression, not matched experimental SST.
- The code linearly decays learning rate although the Methods describe a fixed 0.001 rate; neighborhood KL and refinement also differ in detail from the displayed equations.

### Reproducibility

**Rating: 3/5.** The primary GitHub snapshot at commit `917456be305fc82e92293ea272812e79675e821c` contains the core PyTorch model, preprocessing scripts, training and inference entry points, pinned dependencies, demo data, three tutorials and a downloadable demo checkpoint. Core paper-code fidelity is **medium**: the main architecture and objectives are present, but several implementation details differ from the prose.

Full reproduction of reported results is not repository-local. The snapshot lacks the complete study-specific configs and fold checkpoints, automated tests, and the separate downstream/figure-analysis workflows. Runtime installation, training and inference were not executed in this analysis. Public data links are supplied, while the in-house DCIS cohort is available by request.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
