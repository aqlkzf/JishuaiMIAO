---
layout: default
permalink: /paper-atlas/auto-cell-52866b4b/
title: "auto-cell"
nav: false
description: "传统 H&E 单细胞分类需要病理医师逐个标注细胞，成本高且对巨噬细胞、中性粒细胞等形态相近类型的一致性有限。auto-cell 的关键思想是把“人工看 H&E 定义标签”替换成“同一组织切片上的多重免疫荧光（mIF）谱系标志物定义标签”。作者先在同一张 FFPE 切片上依次获取 mIF 与 H&E 图像，把两者精确配准，再把 mIF 上的细胞类型转移给 H&E 中对应细胞，从而建立大规模训练集。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>auto-cell</h1>
    <p>Automated cell annotation and classification on histopathology for spatial biomarker discovery</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-61349-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for auto-cell">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/lilab-stanford/auto-cell" target="_blank" rel="noopener noreferrer" aria-label="Open code for auto-cell">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## auto-cell 方法解读：用 mIF 自动生成 H&E 单细胞标签并发现空间标志物

### 1. 核心问题与方法定位

传统 H&E 单细胞分类需要病理医师逐个标注细胞，成本高且对巨噬细胞、中性粒细胞等形态相近类型的一致性有限。auto-cell 的关键思想是把“人工看 H&E 定义标签”替换成“同一组织切片上的多重免疫荧光（mIF）谱系标志物定义标签”。作者先在同一张 FFPE 切片上依次获取 mIF 与 H&E 图像，把两者精确配准，再把 mIF 上的细胞类型转移给 H&E 中对应细胞，从而建立大规模训练集。

训练完成后，部署阶段只需要普通 H&E：StarDist 检测细胞核，分类网络把每个核周围的 $75\times75$ 像素图像分为肿瘤细胞、淋巴细胞、中性粒细胞或巨噬细胞；低置信度细胞归为 Others。随后计算细胞组成和成对空间邻近特征，用于生存和免疫治疗响应分析。

因此 mIF 是训练标签来源，不是部署输入；auto-cell 也不是一个端到端同时分割、配准、分类和预后的单一网络，而是由外部 StarDist、DeeperHistReg、自监督预训练、域适应分类器和统计分析组成的多阶段工作流。

### 2. mIF 如何定义细胞类型

作者在两个 mIF panel 中测量 pan-CK、CD3、CD20、CD66b、CD68 等谱系标志物。代码 `cell_annotation/cell_cluster.py:15-64` 读取细胞面积和标志物平均强度，按样本做标准化，用 Scanpy 邻居图和 Leiden 聚类得到细胞群，再根据群的 marker profile 解释为：

- pan-CK 高：肿瘤细胞；
- CD3/CD20 高：淋巴细胞；
- CD66b 高：中性粒细胞；
- CD68 高：巨噬细胞。

这个过程是“无监督聚类 + 生物标志物命名”，并非完全无人工判断：Leiden 给出簇，但从 marker 模式到细胞类型仍需要知识映射。论文最终通过这一流程获得 1,127,252 个高质量 H&E 对应标签；第一张 TMA 中有 969,387 个细胞属于四个目标类型。

本地脚本只显式列出 CD3、pan-CK、CD20 三个 marker，适合 panel 1；panel 2 的 CD66b/CD68 与跨 panel 汇总并没有在同一个可执行脚本里完整呈现。因此论文级四类标签生成是 Partial，而不是单文件完全复现。

### 3. 同一细胞怎样从 mIF 匹配到 H&E

#### 3.1 图像配准

论文先做通道归一化、灰度化和 CLAHE，再用 SIFT 检测描述子、SuperGlue 匹配关键点得到刚性粗配准，随后用 DeeperHistReg 的多尺度梯度优化做非刚性配准。配准结果由病理医师目视检查。论文报告平均细胞匹配误差约 3.1 微米。

本地包含完整外部 DeeperHistReg 源码快照，但 auto-cell 仓库没有一个把论文所述 SIFT—SuperGlue—DeeperHistReg 参数完整串联的顶层脚本。因此它验证依赖和可用组件，而不是精确复现论文每次配准的配置。

#### 3.2 H&E 核分割与标签转移

`cell_segment_he.py:12-92` 使用预训练 `StarDist2D.from_pretrained('2D_versatile_he')` 分割 H&E，先做染色归一化，再以 2048 像素 block 推理。每个核裁成 $75\times75$ RGB 小图，核轮廓外像素置白，避免分类器利用相邻细胞。

`cell_transfer.py:9-53` 在微米坐标中计算 H&E 与 mIF 细胞中心的欧氏距离，把每个 H&E 核匹配到最近 mIF 核；仅当距离不超过 5 微米时转移标签：

$$
d(i,j)=\sqrt{(x_i-x_j)^2+(y_i-y_j)^2},\qquad
y_i^{H\&E}=y_{\arg\min_j d(i,j)}^{mIF},\;d\le5\ \mu m.
$$

例如最近 mIF 核距 H&E 核 3.2 微米则接受；若最近也有 6.1 微米则不生成训练标签。该阈值大约是一个核半径，用精确率换覆盖率。代码使用全量距离矩阵，核心较大时内存随 $N_HN_M$ 增长。

### 4. 自监督预训练与域适应分类

#### 4.1 BYOL 预训练

作者从 CPTAC-COAD 的 372 张 WSI 中采样肿瘤区域，经 StarDist 获得 1,127,563 个无标签细胞，用 BYOL 预训练 ResNet18。对同一细胞图像做两种增强，在线网络预测目标网络表征；目标网络参数以指数移动平均更新。BYOL 让骨干在没有细胞类型标签时先学习细胞形态表征。

本地提供 `byol.yaml` 和后续加载 `byol-custom-dataset.ckpt` 的代码，但没有把论文整套 BYOL 训练器纳入 auto-cell 自有 Python 模块；它依赖 solo-learn/外部训练流程。因此 BYOL 机制有论文与配置证据，完整训练实现属于 External/Partial。

#### 4.2 监督分类器

`small_CNN.py:7-33` 的 `Customresnet` 包含三个部分：

1. ResNet18 特征提取器 $M_r$，输出 512 维向量；
2. 四类线性分类头 $M_c$；
3. 两类域分类器 $M_d$，区分 mIF 标注源域与 CPTAC 无标签目标域。

梯度反转层在前向时为恒等映射，在反向时把域损失梯度乘以 $-\alpha$：

$$
R_\alpha(z)=z,\qquad
\frac{\partial R_\alpha}{\partial z}=-\alpha I.
$$

总目标可概括为

$$
L=L_{cell}(M_c(M_r(x_s)),y_s)
+L_{domain}(M_d(R_\alpha(M_r(x_s))),0)
+L_{domain}(M_d(R_\alpha(M_r(x_t))),1).
$$

分类头希望保留细胞类型信息；域头希望辨认数据来源；反向梯度让骨干反过来学习“域头难以区分”的表征，从而缓解机构、扫描仪和染色差异。

`train_test_cell.py:13-84` 加载 BYOL 权重，支持 ResNet18/50、VGG16、ConvNeXt 和 EfficientNet，训练源域分类与源/目标域损失。`dataloaders.py:32-63` 在训练时加入 H&E 染色扰动、翻转旋转、弹性形变、模糊、噪声和亮度变化。论文部署时若四类概率全部低于 0.5，则把细胞标为 Others；本地训练循环输出四类 logits，但未在所读推理路径中找到该 Others 阈值的完整实现，因此这是 Partial。

### 5. 从细胞预测到 66 个空间特征

每个病人得到带类型和坐标的细胞地图后，`spatial_cell_analysis/core.py` 计算三组信息：

- composition：四类细胞的 fraction、density、mean area；
- spatial distribution：某类细胞周围 50 微米内各类细胞的平均数量；
- neighborhoods：以某类细胞为中心，其 50 个最近邻中各类型的比例；
- spatial proximity：不同类型之间的最近距离统计。

四类细胞的有序成对组合为 $4\times4=16$，空间邻近类特征逐对计算；连同组成和面积等合计 66 个特征。代码 `calculate_neighbourhoods_` 把中心细胞自身加入 $k+1$ 分母，因此“50 最近邻组成”实际是 50 个邻居加中心细胞的 51 个对象比例。这一实现细节应在复现中保留。

TMA 对整个 core 分析；WSI 则从肿瘤区域随机抽取八个 $2048\times2048$ patch，分别计算后再按患者平均。随机抽样意味着空间特征只代表抽到的肿瘤区域，并非完整 WSI 全景；严格复现需要固定随机种子和抽样坐标。

### 6. 论文结果怎样读

论文在同一切片 mIF-H&E 数据上训练，并在 9 个外部验证数据集评估，包括 136-core TMA 和 3263 张 WSI。四类细胞外部准确率为 86%–89%，外部平均 AUC 约 0.964。以相同模型技术比较标签来源时，完整自动标注训练集在外部集达到约 89.1% 准确率，而人工标注训练集约 56.2%。这说明大规模、蛋白标志物定义的标签有优势，但比较同时改变了标签质量、样本量和类别分布，不能把差异完全归因于“自动”二字。

消融显示去掉 BYOL 或域适应会降低泛化；StarDist 与 Hover-Net 分割得到的分类性能相近（约 86.4% vs 86.3%）。作者还比较 VOLTA、DINO、UNI 和 Virchow。模型只定义四个主要类型，其他细胞通过低置信度策略处理；这不是全组织细胞谱系图谱。

在 12 个队列、3605 名患者、8 种癌症中，作者筛选与生存相关的空间特征。一个反复出现的信号是淋巴细胞邻域中的中性粒细胞比例，高值关联较差生存（不同队列 HR 约 1.91–5.75）。在两个免疫治疗队列中，组合空间标志物预测客观缓解的验证 AUC 为 0.817，高于 PD-L1 CPS 的 0.650；验证集 PFS HR 为 2.32。

这些是回顾性关联与预测验证，不代表操纵中性粒细胞即可改变疗效，也不等同于前瞻性临床可用性。空间标志物受到肿瘤区域选择、细胞分类误差和队列差异影响。

### 7. 主图的证据链

- 图 1：同片 mIF/H&E、marker 定义、配准标签转移、BYOL+域适应、空间标志物全流程。
- 图 2：两个 mIF panel 的 Leiden 聚类、marker 雷达图和核面积分布。
- 图 3：配准 H&E、核分割、mIF identity、H&E 标签转移，以及细胞中心误差与直径比较。
- 图 4：训练/内外验证混淆矩阵和 ROC，以及细胞潜在空间/形态示例。
- 图 5：八种癌症队列中空间特征与总生存的 Kaplan–Meier 结果。
- 图 6：免疫治疗响应 ROC、90% specificity 灵敏度、PFS 分层及多变量 forest plot。

本地 15 页主论文 PDF 和六张提取主图均已检查。因此补图 S1–S16 和补表的细节只能依据主文引用，不能冒充已直接读取。

### 8. 代码—论文对应边界

| 论文环节 | 本地代码 | 状态 |
|---|---|---|
| mIF marker 聚类 | `cell_annotation/cell_cluster.py` | Partial：panel 1 明确，四类整合不完整 |
| DeeperHistReg | `DeeperHistReg/` | External snapshot；顶层论文配置未固定 |
| StarDist 核分割/75 px crop | `cell_segment_he.py:12-92` | Exact |
| 5 微米最近邻标签转移 | `cell_transfer.py:9-53` | Exact |
| BYOL | `byol.yaml` + checkpoint load | Partial/External |
| ResNet18 + GRL 域适应 | `small_CNN.py`, `train_test_cell.py` | Exact core |
| 66 空间特征 | `spatial_cell_analysis/core.py` | Exact/Verified |
| 生存与 ICI 模型 | `prognosis_analysis.py` | Script-level，依赖缺失数据文件 |

源码快照没有独立 Git 元数据；README 与论文指向 `https://github.com/lilab-stanford/auto-cell`，论文另给 Zenodo DOI `10.5281/zenodo.15660609`。

### 9. 最重要的复现与解释限制

1. mIF 标签依赖 marker panel、聚类分辨率和簇命名，并非绝对真值。
2. 5 微米匹配阈值和配准质量直接决定训练标签噪声。
3. 核外背景被置白，模型主要学习核内/核周形态，可能丢失胞质上下文。
4. 域适应降低已见域差异，不保证任意新医院或扫描仪上的不变性。
5. Others 是低置信度拒识，不是经过完整类别监督的所有其他细胞。
6. WSI 只抽八个肿瘤 patch，空间特征存在抽样方差。
7. 预后和疗效结果是多阶段模型后的回顾性关联，需前瞻验证。
8. 当前仓库包含外部 StarDist 和 DeeperHistReg 快照，不能把它们的全部代码视为 auto-cell 原创贡献。

auto-cell 的核心价值在于把蛋白标志物的可解释定义大规模转移到 H&E，解决单细胞训练标签瓶颈；其真正部署链则必须同时控制配准误差、分割误差、域偏移和空间抽样。读结果时应沿这四个误差来源逐层审计，而不是只看最终 AUC。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

Motivation/Novelty (动机和创新性)

1. 核心问题：传统病理图像单细胞分析依赖人工标注，存在严重缺陷：
    - 人工标注效率低且容易出错（inter-observer variability）
    - 对巨噬细胞等难识别细胞类型，病理学家间一致性仅约50%
    - 现有方法标注细胞数量有限，不足以训练可靠的深度学习模型
  2. 创新突破：
    - 首次使用多重免疫荧光(mIF)替代人工标注，基于细胞谱系蛋白标记物自动定义细胞类型
    - 创建了包含1,127,252个高质量标注细胞的大规模数据集
    - 将空间细胞互作特征与临床预后和免疫治疗响应关联

Method (方法)

1. 自动细胞标注流程：

# 从代码cell_cluster.py中的Leiden聚类实现
  # 基于mIF蛋白标记物表达进行无监督聚类
  clustering = Leiden(resolution=0.5)
  cell_types = clustering.fit_predict(marker_expression)

2. 图像配准技术 (DeeperHistReg/):

- 粗配准：使用SIFT + SuperGlue进行关键点检测和匹配
  - 精配准：基于梯度优化的非刚性配准，确保单细胞级别精度（平均误差3.1微米）

3. 深度学习模型架构 (small_CNN.py):

class Customresnet(nn.Module):
      def __init__(self, num_classes=4):
          # BYOL自监督预训练的ResNet18
          self.feature = timm.create_model('resnet18', pretrained=True)
          # 域适应分支（梯度反转层）
          self.domain_classifier = nn.Sequential(...)

关键技术组合：
  - 自监督学习(BYOL)：在1,127,563个未标注细胞上预训练
  - 域适应(Domain Adaptation)：使用梯度反转层(GRL)减少染色差异影响

数学公式：
  $$L(\theta_r, \theta_c, \theta_d) = \sum L_c(M_c(M_r(x)), y) + \sum L_d(M_d(R(M_r(x))), y)$$

4. 空间特征提取 (spatial_cell_analysis/core.py):

# 计算k近邻细胞类型分布
  def calculate_neighbourhoods_(self, k=50):
      nearest_neighbours_idx = np.argpartition(self.cell_distances, k, axis=1)
      # 计算每个细胞周围不同类型细胞的比例

提取66个空间特征，包括：
  - 细胞密度和组成
  - 细胞间空间邻近度（50微米内的细胞数量）
  - k近邻细胞类型分布（50个最近邻）

Evaluation (评估)

1. 细胞分类性能：

- 整体准确率：86%-89%（外部验证集）
  - 各类细胞AUC：平均0.964（外部验证）
  - 与人工标注对比：自动标注模型准确率89.1% vs 人工标注56.2%

2. 临床预后验证：

- 数据规模：3,605名患者，8种癌症类型，12个独立队列
  - 关键发现：淋巴细胞周围中性粒细胞比例与生存期显著相关（HR: 1.91-5.75，所有P<0.003）

从prognosis_analysis.py中的Cox回归实现：
  # Elastic Net正则化的Cox生存分析
  CoxnetSurvivalAnalysis(l1_ratio=0.5, alpha_min_ratio=0.01)

3. 免疫治疗响应预测：

- 客观缓解预测：AUC=0.817（验证集），显著优于PD-L1 CPS（AUC=0.650）
  - PFS预测：HR=2.32（验证集），独立于年龄、性别、PD-L1表达等临床因素
  - 空间标志物优势：90%特异性下，灵敏度提升2倍以上

4. 消融实验：

- 移除自监督学习或域适应后，分类准确率显著下降
  - 不同细胞分割算法（StarDist vs Hover-Net）对性能影响小（86.4% vs 86.3%）

核心贡献：提出了一个可扩展的自动化框架，通过mIF引导的细胞标注和深度学习，实现了标准H&E图像的高精度单细胞分析，并发现了与临床结果相关的新型空间生物标志物。

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
