---
layout: default
permalink: /paper-atlas/scatlasvae-414a727c/
title: "scAtlasVAE"
nav: false
wide: true
description: "单细胞图谱越来越大，但“大”并不等于“可以直接合并”。不同研究往往来自不同实验室、测序批次、组织、疾病条件和样本处理流程，因此原始表达矩阵同时混合了两类变化： 希望保留的生物学变化，例如初始、记忆、效应、耗竭等 CD8^+ T 细胞状态； 希望消除的技术或队列变化，例如 atlas、study、sample 等多层批次效应。 跨图谱分析还有第二个困难：不同图谱的细胞亚型命名和注释粒度并不一致。"
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
      <span>Representation Models</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>scAtlasVAE</h1>
    <p>Integrative mapping of human CD8+ T cells in inflammation and cancer</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/WanluLiuLab/scAtlasVAE" target="_blank" rel="noopener noreferrer" aria-label="Open code for scAtlasVAE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scAtlasVAE 方法详解：从跨批次整合到参考图谱迁移

### 一、这篇论文真正要解决什么问题？

单细胞图谱越来越大，但“大”并不等于“可以直接合并”。不同研究往往来自不同实验室、测序批次、组织、疾病条件和样本处理流程，因此原始表达矩阵同时混合了两类变化：

- 希望保留的生物学变化，例如初始、记忆、效应、耗竭等 CD8$^+$ T 细胞状态；
- 希望消除的技术或队列变化，例如 atlas、study、sample 等多层批次效应。

跨图谱分析还有第二个困难：不同图谱的细胞亚型命名和注释粒度并不一致。即使两个图谱描述的是相似细胞群，也不能简单地按标签名称一一对应。最后，研究者还希望把已经建立好的参考图谱用于新数据：新数据进入后，不重新联合训练整个参考模型，就能得到参考空间中的潜变量和亚型标签。

已有方法只解决了其中一部分：

- scVI（*Nature Methods*, 2018）和 scANVI（*Molecular Systems Biology*, 2021）是概率生成模型，但编码器也使用批次信息；
- SCALEX（*Nature Communications*, 2022）采用 batch-invariant encoder，适合在线投影，但重建目标与本文不同；
- scPoli（*Nature Methods*, 2023）可以进行群体级整合，但不支持为多个图谱的独立注释体系同时设置多套预测头。

scAtlasVAE 的核心目标因此可以概括为：

> 学习一个尽量不含批次信息的细胞状态表示，同时让解码器利用批次信息完成计数重建；再用多个独立分类头对齐不同图谱的注释体系，并把训练好的参考模型直接迁移到查询数据。

### 二、输入、输出与整体框架

#### 输入

- 原始基因计数矩阵 ${\mathbf X}\in\mathbb{R}^{n\times G}$；$n$ 是细胞数，$G$ 是选定的 HVG 数。
- 多层批次信息 ${\mathbf B}$，例如 atlas、study、sample。
- 可选的一个或多个细胞亚型注释类别 ${\mathbf C}$；没有标签的细胞使用 `undefined`/ignore 类别。
- 零样本迁移时还需要：参考模型 checkpoint、参考潜空间与参考 UMAP、查询 `AnnData`。
- 论文的后续生物学分析还使用配对的完整 TCR$\alpha$/TCR$\beta$ 信息。

#### 输出

- 默认 10 维的细胞潜变量 $z$；代码在推理时默认输出后验均值 `q_mu`。
- ZINB 重建分布的表达比例、离散度和 dropout logits。
- 每套注释体系各自的细胞亚型预测。
- 查询数据在参考空间中的 `X_gex`、KNN 对齐的 `X_umap` 和预测标签。
- 论文下游得到的聚类、18 个 CD8$^+$ T 细胞亚型、TCR 多样性/不均衡性、克隆型共享、DEG、GO 和 GRN 等结果。

#### 一眼看懂的计算流程

```text
原始计数 X
  │
  ├─> 不输入批次的编码器
  │      └─> q_mu, q_var ──重参数化──> z
  │                                  │
批次层级 B ──> batch embedding ─────┤
  │                                  v
  └────────────────────────────> 条件解码器
                                     │
                                     ├─> ZINB 参数并重建 X
                                     └─> 训练重建损失

z ──> 分类头 1 ──> 图谱 1 的细胞亚型
z ──> 分类头 2 ──> 图谱 2 的细胞亚型
...
```

最关键的设计不是“又用了一个 VAE”，而是批次信息进入模型的位置：**批次不进入编码器，只进入解码器**。

### 三、为什么 batch-unconditional encoder 能帮助批次校正？

论文把编码器写成

$$
{\mathcal F}_{\mathrm{encoder}}({\mathbf X})	o(\boldsymbol\mu,\boldsymbol\sigma^2),
\qquad q_\phi({\mathbf z}\mid{\mathbf X}),
$$

把解码器写成

$$
{\mathcal F}_{\mathrm{decoder}}({\mathbf z},{\mathbf B})
\to(r_{\mathrm{mean}},r_{\mathrm{var}},r_{\mathrm{gate}}).
$$

直觉上，编码器必须从表达矩阵中提取一个可以跨数据集复用的细胞状态 $z$；解码器在重建时再结合批次 ${\mathbf B}$，解释不同批次中特有的表达偏移。这样，模型不需要把“这是哪个 study/sample”硬编码进 $z$。

直接代码证据很清楚：`encode(X, batch_index)` 虽然保留了 `batch_index` 参数，但把批次拼接进输入的代码已经注释，实际只编码表达矩阵和可选 library size（`scAtlasVAE/scatlasvae/model/_gex_model.py:964-990`）。`decode` 才会把 $z$ 与主批次和附加批次编码拼接（`_gex_model.py:992-1046`）。

需要注意，“编码器不显式输入批次”不意味着 $z$ 数学上必然完全无批次信息。是否真正实现批次消除，还取决于数据覆盖、网络容量、重建约束和训练结果，因此论文仍用 scIB 指标评估 batch correction 与 biological conservation 的平衡。

### 四、输入归一化与潜变量

论文 Methods 给出方差稳定变换

$$
\log\left(\frac{x_{g,n}}{s_n}+x_0\right),\qquad x_0=1,
$$

但随后明确说明本研究实际只使用 Log1p，已经足以捕获表达方差（`paper.md:223`）。代码默认值与这句话一致：

- `log_variational=True`：编码前执行 $\log(1+X)$；
- `total_variational=False`：默认不先做总量归一化；
- 如果用户显式开启 `total_variational=True`，才会先归一化到 10,000 再 Log1p。

编码器输出 `q_mu` 和 `q_var`，然后采样

$$
{\mathbf z}=\boldsymbol\mu+\boldsymbol\sigma\odot\boldsymbol\epsilon,
\qquad \boldsymbol\epsilon\sim\mathcal N(0,I).
$$

训练时使用随机采样的 $z$，但下游构图和迁移默认使用 `q_mu`（`_gex_model.py:1578-1620`），这样不会因为一次随机采样而改变参考嵌入。

### 五、ZINB 解码和 VAE 损失

scAtlasVAE 假设给定潜变量和批次后，原始计数服从零膨胀负二项分布。论文的条件似然为

$$
{p}_{\theta }({\mathbf{X}}|{\mathbf{B}})={\int }_{z}{p}_{\theta }({\mathbf{X}}|{\mathbf{z}},{\mathbf{B}}){p}_{\theta }({\mathbf{z}}){\rm{d}}{\mathbf{z}}.
$$

由于无法直接积分所有 $z$，优化的是重建项加 KL 正则：

$$
&#123;&#123;\mathscr{L}}}_&#123;&#123;\rm{scAtlasVAE}}}=&#123;&#123;\mathbb{-}}{\mathbb{E}}}_{z \approx {q}_{\phi }\left(z,|,X\right)}\log {p}_{\theta }({\mathbf{X}}|{\mathbf{z}},{\mathbf{B}})+{\lambda }_&#123;&#123;{\mathrm{KL}}}}\times {D}_&#123;&#123;{\mathrm{KL}}}}({q}_{\phi }({\mathbf{z}}|{\mathbf{X}}){||}{p}_{\theta }({\mathbf{z}})).
$$

两部分分别承担不同作用：

- **重建损失**要求 $z+B$ 能解释原始计数；默认使用 ZINB 负对数似然（`scAtlasVAE/scatlasvae/utils/_loss.py:113-142`）。
- **KL 损失**把后验限制在标准正态先验附近，使潜空间连续、可采样并避免无约束记忆训练数据（`_gex_model.py:1061-1068`）。

解码器先用 softmax 得到基因表达比例，再乘以每个细胞的 library size，随后与离散度和 dropout logits 一起进入 ZINB（`_gex_model.py:1021-1036,1070-1077`）。

### 六、多个独立标签头如何实现跨图谱半监督训练？

如果只设置一个统一分类器，就必须先把不同图谱的标签强行合并；这正是跨图谱分析想避免的问题。scAtlasVAE 为主标签和每个附加标签分别建立线性预测头：

```text
共同潜变量 z
  ├─> predictor_atlas_A ─> A 图谱标签
  ├─> predictor_atlas_B ─> B 图谱标签
  └─> predictor_atlas_C ─> C 图谱标签
```

论文使用带类别权重和 ignore mask 的交叉熵：

$$
\begin{array}{l}&#123;&#123;\mathcal{L}}}_&#123;&#123;\rm{celltype}}}=\mathop{\sum}\limits_{n}^{N}\mathop{\sum}\limits_{a}^{A}-&#123;&#123;w}_{\hat{y}}}_{a,n}\log \frac{\exp \left(&#123;&#123;f}_&#123;&#123;{\rm{celltype}}}_{a}}({z}_{a,n})}_&#123;&#123;\hat{y}}_{a,n}}\right)}{\mathop{\sum }\nolimits_{c}^&#123;&#123;C}_{a}}\exp \left(&#123;&#123;f}_&#123;&#123;{\rm{celltype}}}_{a}}({z}_{a,n})}_{c}\right)}\\\qquad\qquad\times\,1\&#123;&#123;\hat{\mathbf{y}}}_{a,n}\ne &#123;&#123;\rm{ignore}}\_{\mathrm{index}}}_{a,n}\}.\end{array}
$$

代码会根据每类实际细胞数建立反频率权重，并排除 `undefined` 类别（`_gex_model.py:650-758,1104-1128`）。因此，一个细胞可以只有 atlas A 的标签、没有 atlas B 的标签；模型只对可用标签计算对应损失。

#### 一个重要的论文—代码差异

论文把半监督目标写成 VAE 损失与分类损失的直接相加，但代码默认只在最后 `pred_last_n_epoch=10` 个 epoch 把分类损失加入总损失（`_gex_model.py:1243-1268,1424-1430`）。也就是说，默认训练更像：

1. 前期先主要学习表达重建和潜空间；
2. 最后十轮再用标签头强化亚型预测。

这个调度可能减少分类目标过早主导表示学习，但论文没有明确讨论，因此代码匹配状态应记为 `Partial`，不能写成完全一致。

### 七、训练过程与默认超参数

每个 mini-batch 的主要步骤是：

```text
1. 读取 raw count、batch、label 和 library size
2. 编码器内对 X 做 Log1p
3. 得到 q_mu、q_var 并采样 z
4. 把 z 与层级 batch embedding 输入解码器
5. 计算 ZINB 重建损失和 KL 损失
6. 可选计算 MMD 或外部潜空间约束
7. 最后若干 epoch 加入标签预测损失
8. AdamW 反向传播更新
```

论文和代码一致的主要默认值包括：

- AdamW；
- 学习率 $5\times10^{-5}$；
- weight decay $10^{-6}$；
- KL deterministic warmup；
- mini-batch 默认 128；
- 潜变量维度默认 10。

论文渲染出的 epoch 公式是

$$
\min\left[\operatorname{round}\left(\frac{20{,}000}{N}\right)\times400,400\right],
$$

代码实际计算 `round((20000/N)*400)` 并上限设为 400（`_gex_model.py:1296-1304`）。如果严格按论文排版把乘 400 放在 `round` 外面，大数据集可能得到不合理的 0 epoch，因此代码表达应视为可运行的解释，但两者不能标为逐字完全一致。

### 八、三种使用任务

#### 任务 1：无监督建立参考图谱

没有标签时，只训练重建和 KL 项；训练后提取 `q_mu`，建立邻居图，进行 Leiden 聚类，再用 marker gene 人工注释。论文对 CD8$^+$ 图谱使用 4,000 HVGs、10 维潜空间、`n_neighbors=40`、Leiden resolution 1.2，先得到 24 个聚类，再经人工拆分/合并形成 18 个亚型（`paper.md:327-336`）。

因此，18 个亚型并不是模型端到端“自动发现并命名”的结果，而是模型整合、无监督聚类和专家注释共同产生的。

#### 任务 2：监督/半监督跨图谱整合

多个图谱共同训练，同一 $z$ 接多个标签头。训练后对每个细胞预测不同图谱体系的标签，再统计标签之间的重叠。论文定义

$$
{P}_{i,j}=\frac{\sum_{1}^{n}\mathbb{I}((m_{n,a}=i)\wedge(m_{n,b}=j))}{\sum_{1}^{n}\mathbb{I}(m_{n,a}=i)},
$$

并使用 $\tau=10\%$ 保留关系（`paper.md:321-324`）。代码 `cell_type_alignment` 默认同样使用 0.1，但要求交集同时占标签 $i$ 和标签 $j$ 各自细胞数的 10% 以上（`scAtlasVAE/scatlasvae/tools/_alignments.py:59-74`）。代码因此比论文的单向定义更严格，也是 `Partial` 匹配。

#### 任务 3：零样本 query-to-reference 迁移

```text
参考 checkpoint + 查询计数矩阵
  -> 按 checkpoint 的基因顺序重排，缺失基因补 0
  -> 恢复参考模型的 batch/label 类别字典
  -> 直接加载权重，不调用 fit
  -> 编码查询细胞得到 q_mu
  -> 用训练好的标签头预测亚型
  -> 查询细胞寻找参考潜空间近邻
  -> 取近邻参考 UMAP 坐标的均值作为查询 UMAP
```

`run_transfer` 直接实现上述流程，并返回写入 `X_gex`、`X_umap` 和预测标签的查询 `AnnData`（`scAtlasVAE/scatlasvae/pipeline/_transfer.py:8-52`）。其中快捷函数固定使用 3 个近邻；通用 `umap_alignment` 默认使用 5 个近邻。

这里的 UMAP 是**参考坐标插值**，不是把参考和查询重新联合优化得到的新 UMAP。因此它适合展示查询细胞落在参考图谱的什么位置，但不应把细小距离解释为精确的生物学轨迹。

### 九、从模型到论文 CD8$^+$ T 细胞图谱

论文的完整研究链条比 VAE 本身更长：

```text
68 项研究的数据收集与 QC
  -> 整合 1,151,678 个 CD8+ T 细胞
  -> Leiden + marker 人工注释为 18 个亚型
  -> 配对 TCR clonotype 定义
  -> D50、Gini、克隆扩增与共享分析
  -> DEG / GO / GRN
  -> 用参考模型迁移 8 个外部查询数据集
```

研究最终覆盖 961 个样本、42 种疾病条件，并报告 498,663 个 unique clonotypes。论文的主要生物学观察包括：

- $GZMK^+$、$ITGAE^+$ 和 $XBP1^+$ 三类 T$_{ex}$ 具有不同的表达程序和克隆共享模式；
- 自身免疫炎症与免疫检查点抑制剂相关不良事件（irAE）中的扩增亚型构成不同；
- 外周血中存在表达 *FCER1G*、*TYROBP* 的 ILTCK-like cells，并观察到其与 MAIT 细胞的克隆共享；
- 参考模型把 8 个外部数据集中的 574,911 个细胞投影和注释到参考空间。

这些结果来自图谱级统计关联。UMAP 邻近、Sankey ribbon、共享 clonotype 和 pSTARTRAC-trans 可以提示共同来源或状态转换，但不能单独证明真实发育轨迹或因果关系。

### 十、评测设计与结果应该怎样理解？

#### 数据集

- 本文 huARdb CD8$^+$ 图谱：1,151,678 cells，18 个亚型；
- TCellLandscape：110,218 cells，17 个亚型；
- TCellMap：205,166 cells，13 个亚型；
- 三者统一选择 4,000 HVGs。

#### 对比方法

- 深度生成/自编码：scVI、scANVI、scPoli、SCALEX；
- 图与回归整合：Scanorama、Harmony、Seurat；
- 注释迁移：CellTypist 等。

#### 指标

- 生物学保留：ASW、isolated-label ASW、isolated-label F1；
- 批次校正：graph connectivity、batch ASW；
- 注释迁移：ROC AUC；
- 任务包括单图谱整合、跨图谱整合和 query 标签迁移。

论文文字和 Extended Data Figures 1–4 表明：无监督 scAtlasVAE 与 scVI 等方法具有竞争力；加入监督标签后，在 batch correction 与 biological conservation 的综合平衡上表现更强；零样本和 full-shot 迁移都有效。超参数图显示 latent dimension 为 10 或 20 时结果较稳定，时间和内存随细胞数近似线性增长。

由于栅格图中的精确分数较小，本文档只保留“竞争力/领先/稳定”等图文共同支持的结论，不从图片重新抄写不可可靠辨认的小数。

### 十一、论文—代码对应关系

| 方法部件 | 代码位置 | 匹配 | 说明 |
|---|---|---|---|
| batch-unconditional encoder | `model/_gex_model.py:964-990` | Exact | batch 参数未进入编码计算。 |
| batch-conditioned decoder | `model/_gex_model.py:992-1046` | Exact | $z$ 与主/附加 batch covariate 拼接。 |
| ZINB + KL | `model/_gex_model.py:1061-1102`; `utils/_loss.py:113-142` | Exact | 默认重建与先验正则有直接实现。 |
| AdamW、KL warmup、epoch 规则 | `model/_gex_model.py:1243-1310,1473-1475` | Partial | 主要默认值一致，epoch 括号解释与论文排版不同。 |
| 多标签头半监督训练 | `model/_gex_model.py:403-411,650-758,1104-1128,1424-1430` | Partial | 结构和加权交叉熵存在，但默认只在最后 10 epoch 加入预测损失。 |
| 零样本迁移 | `pipeline/_transfer.py:8-52` | Exact | 直接加载权重、编码、预测、映射 UMAP。 |
| 跨图谱标签对齐 | `tools/_alignments.py:6-113` | Partial | 代码使用双向 10% 阈值。 |
| 论文全流程与出图 | `docs/source/notebooks/_build/html/_sources/*.ipynb` | Notebook | 4 个 notebook 存在，但本次未执行或全面审计。 |
| D50 | 安装包中未找到 | Not found | 论文说明使用 `scirpy.tl.alpha_diversity(metric='D50')`。 |
| customized Gini | 安装包中未找到 | Not found | 论文明确称为 customized Python code。 |
| dominant/shared/ambiguous clonotype 公式 | 安装包中未找到 | Not found | 通用 scirpy clonotype 预处理存在，但下游 top-two 规则不存在。 |
| pSTARTRAC-trans | 安装包中未找到 | Not found | 论文使用 STARTRAC R 0.1.0，核心 Python 包未发现对应实现。 |

### 十二、下游 clonotype 公式与保留缺口

论文把扩增 clonotype 定义为至少 3 个细胞，并用 D50 衡量多样性、Gini 衡量不均衡性。对于共享亚型，定义

$$
{t}^{A \approx B}\Longleftrightarrow \left({p}_{A}^{t}=\mathop{\max }\limits_{j\in {\mathbf{C}}}{p}_{j}^{t}\right)\wedge \left({p}_{B}^{t}=\mathop{\max }\limits_{j\in {\mathbf{C}}\setminus \{A\}}{p}_{j}^{t}\right),
$$

即 $A$ 和 $B$ 分别是 clonotype $t$ 中占比第一和第二的细胞亚型；如果第二和第三名占比相同，则

$$
{t}^&#123;&#123;{\mathrm{Ambiguous}}}}\Longleftrightarrow {p}_{B}^{t}={p}_{C}^{t}.
$$

本地安装包中只找到通用的 `scirpy` clonotype 定义/聚类调用（`preprocessing/_preprocess.py:283-292`），没有找到上述 top-two/ambiguous 规则、D50 调用、customized Gini 或 pSTARTRAC-trans。4 个大型 notebook 虽然存在，但本次没有执行或全面审计，所以这些条目必须继续标为 **Not found**，不能根据图或 notebook 文件名推断成已实现。

### 十三、复现性与使用建议

#### 优点

- 核心模型、损失、checkpoint 和零样本迁移代码与论文高度对应；
- checkpoint 保存权重、基因顺序、模型配置和类别字典；
- 教程提供参考图谱、潜变量和监督模型的 Zenodo 链接；
- 本地保留论文全文、15 张图和 4 个论文相关 notebook source。

#### 风险与限制

- 未找到核心路径的自动化测试；
- 论文 notebook 未在本次分析中运行，不能声称端到端复现成功；
- 安装包的便捷下载函数指向旧 Zenodo accession `10472914`，而论文/CD8 教程使用 `12542577`，应优先使用论文和教程链接；
- 18 个亚型依赖专家 marker 注释，低频细胞群可能需要更细粒度的重新聚类；
- 新定义亚型的功能与疾病作用仍需要实验验证。

### 十四、最简理解

如果只记住三点：

1. **把批次放在解码器，不放在编码器**，是 scAtlasVAE 学习跨批次表示的核心。
2. **一个共享潜空间接多套独立分类头**，使不同图谱的注释可以同时训练和比较。
3. **保存的参考模型可直接编码和标注查询数据**，但论文中的 TCR/clonotype 生物学结论还依赖未在核心包中验证的下游分析代码。

因此，scAtlasVAE 的模型部分适合直接学习、复用和继续开发；若目标是完整重现论文全部克隆型与疾病结论，还必须进一步获取数据、运行并审计论文 notebook 与外部 R/Python 分析流程。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scAtlasVAE Summary

### What problem does the paper solve?

Large single-cell atlases are assembled from many studies, laboratories, tissues, and disease contexts. They therefore need strong batch correction without erasing biological state, and their independently developed subtype labels are often incompatible. The paper also needs a reference model that can annotate new datasets at atlas scale without repeatedly retraining on the reference.

Earlier VAE-based tools were effective but did not cover this combination cleanly: scVI (*Nature Methods*, 2018) and scANVI (*Molecular Systems Biology*, 2021) condition their probabilistic models on batch; SCALEX (*Nature Communications*, 2022) uses a batch-invariant encoder for online projection but a different reconstruction objective; scPoli (*Nature Methods*, 2023) performs population-level integration but does not provide independent predictors for several atlas-specific annotation systems. The authors argue that these limitations make cross-atlas subtype comparison and parallel semi-supervision difficult (`paper.md:27,273-287`).

### Proposed method

scAtlasVAE is a variational autoencoder with a deliberately asymmetric treatment of batch:

```text
raw counts X
  -> batch-unconditional encoder
  -> latent cell state z
  -> batch-conditioned ZINB decoder -> reconstructed counts
  -> one or more independent label heads -> atlas-specific subtype predictions
```

The encoder learns a Gaussian latent representation from expression alone. Hierarchical batch covariates are embedded and injected only into the decoder, which reconstructs counts with a zero-inflated negative-binomial likelihood. Optional independent classification heads make it possible to train on multiple atlases whose annotation vocabularies differ. A saved supervised model can then encode and label query cells without finetuning; query UMAP positions are aligned to the reference through nearest-neighbor coordinate averaging.

Direct code inspection confirms this core design. The model implementation omits batch from `encode`, injects batch into `decode`, implements ZINB and KL losses, uses AdamW with KL warmup, saves gene/category metadata with checkpoints, and exposes a zero-shot `run_transfer` pipeline. The implementation has two important details not stated clearly in the paper: prediction loss is included only in the final ten epochs by default, and the subtype-alignment helper requires a 10% overlap in both directions rather than only the one-directional $P_{i,j}$ definition.

### Evaluation

The authors benchmark three tasks on the paper's atlas and two prior pan-cancer T-cell atlases:

- **Datasets:** 1,151,678-cell huARdb CD8$^+$ atlas, 110,218-cell TCellLandscape, and 205,166-cell TCellMap, using the same 4,000 HVGs.
- **Integration baselines:** scVI, scANVI, scPoli, SCALEX, Scanorama, Harmony, Seurat, and PCA/uncorrected controls.
- **Transfer baselines:** scPoli, scANVI, and CellTypist.
- **Integration metrics:** biological-conservation ASW, isolated-label ASW/F1, graph connectivity, and batch ASW, summarized into biological, batch, and overall scores.
- **Annotation metric:** area under the ROC curve for randomly held-out 5% queries or study-held-out queries.

The text and extended-data figures show that unsupervised scAtlasVAE is competitive with scVI, supervised scAtlasVAE improves the balance of batch correction and biological conservation, and scAtlasVAE performs effectively in both zero-shot and full-shot transfer. Cross-atlas experiments visually show better simultaneous batch mixing and retention of multiple subtype systems. Hyperparameter panels indicate stability across latent dimensions 10–20 and several encoder settings, while time and memory scale approximately linearly with cell number.

### Main biological results

Using scAtlasVAE, the study integrates 1,151,678 CD8$^+$ T cells from 961 samples, 68 studies, and 42 disease conditions into 18 annotated subtypes with paired TCR information. The atlas reveals:

- distinct transcriptomic and clonotype-sharing patterns for $GZMK^+$, $ITGAE^+$, and $XBP1^+$ exhausted T-cell subtypes;
- different expanded-subtype compositions in autoimmune versus immune-related adverse-event inflammation;
- circulating ILTCK-like cells expressing *FCER1G* and *TYROBP*, including observed clonotype sharing with MAIT cells;
- transfer of reference annotations to 574,911 cells from eight external query datasets, with marker patterns and several clonal relationships qualitatively consistent with the reference.

These findings are atlas-scale associations. UMAP proximity, Sankey ribbons, and pSTARTRAC-trans scores do not by themselves prove developmental transitions or causal disease mechanisms, and the paper explicitly calls for further experimental validation.

### Reproducibility assessment: 3.5/5

#### Strengths

- Core VAE, loss, checkpoint, prediction, and zero-shot transfer paths match the paper closely and are documented with runnable examples.
- Paper data, reference atlas, latent coordinates, and supervised model checkpoints are linked through Zenodo/tutorial documentation.
- Four built notebook sources for paper-related GEX/TCR analyses are present.
- All 15 paper figures and the full publisher-derived paper Markdown are local.

#### Gaps

- No automated test suite was found for the core paths.
- The large paper notebooks were not executed or fully audited in this analysis.
- The D50 call, customized Gini implementation, dominant/shared/ambiguous clonotype formulas, and pSTARTRAC-trans workflow are **Not found** in the searched installable package; these gaps are preserved rather than inferred from figures.
- The core package's convenience downloader points to an older Zenodo accession than the paper/tutorial, so the paper/tutorial links should be preferred.
- The biological atlas construction still requires manual annotation choices and extensive external data processing beyond calling the VAE.

### Bottom line

scAtlasVAE's main computational contribution is a well-matched, batch-unconditional encoder plus batch-conditioned decoder that supports several independent annotation heads and fast zero-shot transfer. The public code is strong enough to understand and reuse the model, but not sufficient by itself to reproduce every TCR/clonotype-derived biological result without executing and validating the bundled notebooks and external data workflow.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
