---
layout: default
permalink: /paper-atlas/tphp-humanproteomeatlas-11c625b7/
title: "TPHP_HumanProteomeAtlas"
nav: false
description: "> 先用 DDA 建立项目特异性光谱库，再用带诱捕序列的 DIA-NN 严格控制错误发现，得到统一蛋白丰度矩阵；随后分别做发育/病理轨迹、组织特异性、配对肿瘤混合模型和外部药物/依赖性数据整合，最后输出组织功能图谱、癌症差异蛋白和候选治疗靶点。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature · 2026</span>
    </div>
    <h1>TPHP_HumanProteomeAtlas</h1>
    <p>Spatial distribution of the proteome in the human body and in cancers</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/guomics-lab/TPHP" target="_blank" rel="noopener noreferrer" aria-label="Open code for TPHP_HumanProteomeAtlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TPHP 人体蛋白质组图谱：从 DIA 质谱到肿瘤靶点优先级

### 1. 这篇论文到底解决什么问题？

TPHP（本文工作空间对该人体蛋白质组资源的简称）要解决的不是“训练一个预测模型”，而是构建一个能够在**同一实验与计算框架下比较人体不同组织、发育状态和癌症状态**的定量蛋白质组图谱。

已有资源各有边界：

- HPA 最早以抗体免疫组化为核心，能提供空间定位，但抗体法是半定量的，而且缺少高质量抗体时难以可靠测量大量蛋白；论文引用的代表性 HPA 组织图谱发表于 *Science* 2015（`paper.md:15-25`）。
- 2014 年两篇 *Nature* 人体蛋白质组草图以及 Wang 等发表于 *Molecular Systems Biology* 2019 的图谱推进了质谱覆盖，但主要集中在约 30 种组织；TSomics 的定量人体蛋白质组发表于 *Cell* 2020，同样没有覆盖本文这样广泛的健康—胎儿—肿瘤—癌旁状态比较（`paper.md:26-33`）。
- TCGA（*Nature Genetics*, 2013）、ICGC 和 CPTAC 对特定癌种很深，但跨癌种平台、队列和批次差异会妨碍直接比较（`paper.md:34-40`）。
- mRNA 与蛋白丰度只有中等相关；真正承担多数功能、也是药物直接作用对象的往往是蛋白，而不是转录本（`paper.md:15-25`）。

因此，TPHP 的核心贡献是一个统一的 DIA-MS 资源：论文报告在 2,856 个生物样本中定量 13,609 个蛋白，覆盖 58 个主要组织、251 个组织亚型和 25 种癌（`paper.md:1-13,34-48`）。样本横跨胎儿（F）、健康成人（N）、肿瘤（T）和配对癌旁非肿瘤组织（NT）。

### 2. 一句话理解整个方法

> 先用 DDA 建立项目特异性光谱库，再用带诱捕序列的 DIA-NN 严格控制错误发现，得到统一蛋白丰度矩阵；随后分别做发育/病理轨迹、组织特异性、配对肿瘤混合模型和外部药物/依赖性数据整合，最后输出组织功能图谱、癌症差异蛋白和候选治疗靶点。

```text
人体组织与临床信息
      │
      ├─ DDA 光谱 ──> FragPipe/MSFragger/Philosopher/EasyPQP
      │                 └─> 项目光谱库
      │
      └─ DIA 光谱 + 人源/诱捕光谱库 ──> DIA-NN
                       ├─> q 值与诱捕 FDP 控制
                       └─> 蛋白 × 样本丰度矩阵
                                  │
                  归一化、log2、缺失值处理、批次校正
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
     F/T/NT/N 状态轴         健康组织特异性          配对 T–NT 癌症分析
     t-SNE/Monocle3          HPA 分类/药物靶点        每癌种每蛋白 LMM
          │                       │                        │
     ANOVA + 模块/通路        组织毒性线索            Hedges' g + B-H
          └───────────────────────┼────────────────────────┘
                                  │
            TCGA/CPTAC/HPA/DrugBank/临床试验/DepMapSanger
                                  │
                       验证、药物再利用与靶点排序
```

### 3. 第一层：怎样把质谱信号变成可信的蛋白矩阵？

#### 3.1 项目特异性 DDA 光谱库

不同组织需要不同的提取和消化流程。论文使用压力循环技术处理多种组织，同时为血液、体液、毛发、指甲和骨等特殊材料设计相应流程；之后用 timsTOF Pro 采集 ddaPASEF 和 diaPASEF 数据（`paper.md:147-215`）。

DDA 文件经 FragPipe v18、MSFragger v3.5、Philosopher v4.2.2 和 EasyPQP v0.1.29 处理。搜索库是人工审阅的人蛋白序列加反向 decoy；肽段和蛋白层面均采用 1% FDR，且下游排除不可区分的蛋白组（`paper.md:216-222`）。最终项目光谱库包含 15,332 个蛋白组。

#### 3.2 DIA-NN 定量

DIA-NN v2.2.0 使用上述光谱库搜索 3,005 个 DIA 文件。论文给出的关键参数包括（`paper.md:223-243`）：

- MS1、MS2 质量误差均为 15 ppm；
- 高精度稳健定量和依赖保留时间的跨运行归一化；
- 关闭 match-between-runs，把不同运行视为不相关；
- 只保留唯一肽支持的蛋白与 proteotypic peptide；
- `Q.Value < 0.001`、`PG.Q.Value < 0.01`；
- `Global.Q.Value < 0.001`、`Global.PG.Q.Value < 0.001`。

DIA-NN 在论文描述中通过目标—decoy 训练的分类器为每个前体选择最佳洗脱峰，用最强的六个碎片离子强度求和进行前体定量，再汇总到蛋白组（`paper.md:227-230`）。论文没有展开该分类器架构；这里不应把它误解为 TPHP 自己提出的新深度学习模型。

#### 3.3 为什么还要加入“诱捕”序列？

作者把非人物种光谱加入搜索库作为 entrapment（诱捕）项。若

- $N_T$：人源 target 发现数；
- $N_E$：非人诱捕发现数；
- $r$：光谱库中诱捕项与 target 项之比；

则论文使用

$$
\widehat{\mathrm{FDP}}_{T\cup E_T}
=\frac{N_E(1+1/r)}{N_T+N_E}
$$

估计 target 加 target-like entrapment 发现集合中的错误比例（`paper.md:231-243`）。作者扫描 $10^{-4}$ 到 $10^{-2}$ 的候选 $q$ 阈值，再选择前述严格阈值。直观上，非人物种本不应在人体样本中大量出现；若它们被“发现”，就为实际错误提供了一个独立探针。论文据此报告 13,609 个定量蛋白和全局蛋白层面 0.1% FDR（`paper.md:42-48`）。

### 4. 第二层：矩阵如何预处理？

论文对全图谱矩阵给出如下流程（`paper.md:244-261`）：

1. 去掉在所有组织类型中缺失比例不低于 50% 的蛋白；
2. 用 `preprocessCore::normalize.quantiles` 做样本间分位数归一化；
3. 做 log$_2$ 变换；
4. 用全矩阵最小值的 $0.5$ 倍填补剩余缺失值；
5. 用主方差成分分析评估批次贡献；
6. 用 `limma::removeBatchEffect` 两步校正批次，后续分析默认使用校正矩阵。

作者还同时使用项目混合 QC、通用小鼠肝标准、技术重复和生物重复，比较变异系数与 Pearson 相关。Extended Data Fig. 1 的图像中可直接看到技术/生物重复相关系数分布较高，但这些 QC 不能替代每个组织和癌种的独立验证。

**容易混淆的一点：**下面的癌症差异分析又定义了一个“每癌种”的缺失值规则，和这里的全矩阵规则并不完全相同。

### 5. 第三层：怎样把四种状态组织成“发育—肿瘤”轴？

#### 5.1 t-SNE 只负责可视化

作者对排除 pool 的矩阵标准化后，用 Rtsne v0.16、perplexity 10 降到二维，并画多元 $t$ 分布置信椭圆（`paper.md:262-267`）。Fig. 2 的图像显示总体上存在 F–T–NT–N 的排列，但四类点云有明显重叠，脑和肝又形成组织主导的例外。

因此，正确表述是“出现总体状态结构”，而不是“t-SNE 完美分开四种状态”。t-SNE 坐标轴也没有可直接解释的生物单位。

#### 5.2 Monocle3 给出胎儿起点的伪时间

去除毛发、指甲和体液样本后，作者先 PCA，再 UMAP，再由 Monocle3 学习轨迹图；关闭 partition 和 loop closing，并把胎儿样本设为起点（`paper.md:268-276`）。这样得到的 pseudotime 是“从胎儿根节点沿蛋白相似性流形前进”的坐标。

它不是：

- 实际发育所需时间；
- 细胞谱系追踪；
- 肿瘤必然从某个癌旁样本演化而来的因果证据。

随后，作者对四种状态做单因素 ANOVA，经 FDR 校正筛出显著蛋白，计算其 F/T/NT/N 中位数，再以 $k=4$–8 的候选范围做 $k$-means，并用 GOBP 注释模块（`paper.md:273-276`）。Fig. 2 显示八个模块，例如 RNA 剪接程序沿 F–T–NT–N 下降，体液免疫相关模块上升（`paper.md:64-68`）。但最终 $k$ 的具体选择规则和随机种子在本地论文 Markdown 中 **Not found**。

### 6. 第四层：怎样定义组织特异性？

作者先用健康成人样本的两两 Pearson 相关和欧氏距离评估组织内部与组织之间的相似度，将异质性较大的大类细分，得到 74 个 refined tissue types（`paper.md:70-78,277-283`）。

随后采用修改版 HPA 分类，仅使用健康成人尸检样本，排除癌症、胎儿、体液、毛发、指甲和脐带。每个组织取蛋白丰度中位数，并把 HPA 的“五倍富集”阈值改为“三倍”，以适应更丰富的组织类型（`paper.md:301-309`）。类别包括：

- tissue-enriched；
- group-enriched；
- tissue-enhanced；
- expressed in all tissues；
- mixed；
- not detected。

组织富集蛋白再进入 GOBP 分析，并与 DrugBank 靶点相连。这样做的价值是：如果某药物靶点在肝、甲状腺或其他器官高度富集，就能为器官特异性毒性提出分子解释。但“靶点在某器官表达”不是药物一定在该器官产生毒性的因果证明。

论文报告 1,717 个组织富集蛋白，其中 480 个来自既往覆盖不足的 24 种组织；合成肽的镜像碎片谱支持 PANX3 在耳蜗中的检测（`paper.md:70-81`；Extended Data Fig. 4 已直接查看）。

### 7. 第五层：配对肿瘤分析是如何做的？

这是公开仓库唯一有直接实现代码的分析分支。

#### 7.1 论文规定的癌种内预处理

每个癌种只保留配对 T–NT 患者；去掉该癌种内缺失超过 50% 的蛋白。剩余缺失值按左删失/检测下限假设填补：

$$
I_{\mathrm{imp}}
=I_{\mathrm{global,min}}\times0.5\times\epsilon,
\qquad
\epsilon\sim\mathcal N(1,0.001^2),
$$

其中 $I_{\mathrm{global,min}}$ 是该癌症数据集内的全局最小强度。之后做 log$_2$ 变换（`paper.md:310-318`）。

这个假设意味着“没测到的蛋白大多在检测下限附近”。若缺失由批次、样本质量或其他非删失机制造成，填补可能产生偏差。

#### 7.2 线性混合模型

对癌种 $c$、蛋白 $j$，可把论文模型写成

$$
y_i
=\beta_0+\beta_1\mathbf 1(\mathrm{T}_i)
+\boldsymbol\gamma^\top\mathbf z_i
+b_{p(i)}+\varepsilon_i,
$$

$$
b_p\sim\mathcal N(0,\tau^2),
\qquad
\varepsilon_i\sim\mathcal N(0,\sigma^2).
$$

- $y_i$：样本 $i$ 的 log 蛋白强度；
- $\beta_1$：T 相对 NT 的主效应；
- $\mathbf z_i$：数据支持时加入的癌症亚型、性别、中心化年龄和 dataset；
- $b_{p(i)}$：患者随机截距，用来表示同一患者 T 与 NT 的配对相关；
- 拟合方式：REML（`paper.md:318-325,337-357`）。

公开 R 源码确实把 `sample_type` 顺序设为 NT、T，构造 `value ~ sample_type + ... + (1 | patient_ID)`，用 `lmerTest::lmer(..., REML=TRUE)` 拟合，并提取 `sample_typeT`（`TPHP/tumor_dysregulation_analysis.R:65-77,102-139`）。

#### 7.3 为什么用 Hedges’ g？

不同蛋白的强度尺度和残差波动不同，因此先用残差标准差标准化肿瘤系数，再用小样本校正：

$$
g=\frac{\hat\beta_1}{\hat\sigma}J(\nu),
$$

$$
J(\nu)=
\frac{\Gamma(\nu/2)}
{\sqrt{\nu/2}\,\Gamma((\nu-1)/2)}.
$$

源码用 log-Gamma 形式实现 $J(\nu)$，与论文数学形式等价且数值上更稳定（`TPHP/tumor_dysregulation_analysis.R:11-20,140-151`）。每个癌种内对 $P$ 值做 B-H 校正；满足

$$
P_{\mathrm{adj}}<0.05,
\qquad |g|\geq0.5
$$

才是 DEP。这个阈值在源码中完全对应（`TPHP/tumor_dysregulation_analysis.R:156-169`）。

#### 7.4 论文与源码并不完全一致

必须保留以下差异：

1. **缺失过滤、左删失填补和 log$_2$ 变换在脚本中 Not found。** 二进制 Parquet 输入可能已在上游处理，但源码无法证明其来源和变换状态。
2. **完整配对仅部分实现。** 脚本先把 T/NT pivot 成宽表并 `drop_na(T, NT)` 来确定蛋白列表，但真正模型数据又来自原始长表；若输入本身不全是完整配对，残缺观测仍可能进入拟合（`TPHP/tumor_dysregulation_analysis.R:51-71`）。
3. **协变量选择比论文多一层限制。** 代码按行数最多保留 1、2 或 3 个可选项，并按“亚型→性别→年龄→dataset”截断；论文没有写这个优先级（`:81-105`）。
4. **收敛处理只有 Partial。** 硬错误会跳过，奇异拟合会记录；但 warning 被抑制，没有显式检查收敛 warning，也没有剔除奇异拟合（`:109-125`）。
5. `direction` 在显著性过滤前按 $g$ 正负赋值，因此 `Up/Down` 标签本身不等于显著（`:164-169`）。

论文报告该模型在 25 个癌种中得到 8,940 个 DEP，其中 2,878 个为肿瘤特异 DEP（`paper.md:96-115`）。这些数字是论文结果，不是本次重新运行代码得到的结果。

### 8. 第六层：如何从差异蛋白走向候选药物？

#### 8.1 癌症分群

作者从批次校正的肿瘤矩阵中保留 CV 高于中位数的蛋白，用 `ConsensusClusterPlus` 在 $k=2$–20 上做欧氏距离 $k$-means；负 silhouette 样本被删除。每个 cluster 与其余样本做 Wilcoxon 比较，要求 $|\log_2\mathrm{FC}|\geq1.5$ 且调整后 $P<0.05$，再与 cluster-enriched 蛋白合并为 signature，并用 GSVA/ssGSEA 计算 Hallmark 通路分数（`paper.md:358-363`）。

Extended Data Fig. 6 可见五个分子 cluster，细胞周期、代谢、免疫/应激程序在不同 cluster 中不同，而且解剖癌种与分子 cluster 并非一一对应。

#### 8.2 三种衍生蛋白类别

- **肿瘤特异 DEP：**只在某一癌种显著上调或下调。
- **LEDEP：**肿瘤特异 DEP 与相应健康组织的组织富集蛋白取交集。
- **tumour-enriched protein：**不仅 T 高于配对 NT，也高于广泛健康组织；此外要求所有正常样本的最大强度低于肿瘤第 25 百分位，且正常组织中最高中位数小于肿瘤中位数的一半（`paper.md:364-375`）。

最后一个定义更强调“肿瘤选择性”，因此适合寻找潜在低脱靶膜靶点。论文报告 41 个位于质膜的 tumour-enriched 候选蛋白（`paper.md:141-144`）。

#### 8.3 外部证据整合

作者把 DEP 与多类数据连接（`paper.md:122-144,376-394`）：

1. DrugBank：蛋白是否已有药物；
2. ClinicalTrials.gov：对应癌种和药物处在哪个临床阶段；
3. TCGA/CPTAC：转录或蛋白差异方向是否一致；
4. HPA pathology：是否关联预后；
5. ProCan-DepMapSanger：蛋白丰度是否与药敏或 CRISPR 依赖相关。

对 ProCan 关联，作者筛选 `nc_fdr < 0.01`、`nc_beta < -0.1` 且 target/perturbed gene 与蛋白一致的配对。重点候选同时满足：

- 患者肿瘤中 $g\geq0.5$、调整后 $P<0.05$；
- 细胞系中蛋白越高，药物 IC$_{50}$ 越低或基因依赖越强，即 $\beta<-0.1$、FDR $<0.01$。

这是一种“患者组织上调 + 细胞系功能关联”的三角验证。Fig. 5 中 MET、BCL2L1 等例子由此出现。但它仍是**候选排序**，不是随机临床试验证明。Trodelvy 或 olaparib 的跨癌种建议也是结合已有试验提出的再利用假设（`paper.md:122-132`）。

### 9. 论文如何验证图谱？

它没有用单一 accuracy 指标，而是用多层证据检查不同性质：

- pool、技术重复、生物重复的 CV 与相关；
- entrapment FDP 与严格 DIA-NN 全局阈值；
- 同一组织内距离更小、相关更高；
- 与 HPA、Wang 等和 TSomics 的组织富集结果比较；
- PANX3 合成肽碎片谱；
- 癌症特异蛋白的 PRM；
- 与 TCGA/CPTAC 差异方向的一致性；
- 与 HPA 预后、药敏和 CRISPR 依赖的交叉映射。

本地 13 张图像均已直接查看：Fig. 1–5 支持图谱范围、状态/组织结构、肿瘤差异和靶点排序；Extended Data Fig. 1–8 支持流程/QC、癌种覆盖、组织一致性、合成肽/PRM、外部验证和临床试验映射。图像证据的具体边界见 `figure_analysis.md`。

### 10. 复现性：能复现到什么程度？

#### 公开仓库中直接存在的内容

GitHub 快照 `guomics-lab/TPHP`，commit `1a53d859d1b3064804cbd2b321ffcea8302868dc`，包含：

- `tumor_dysregulation_analysis.R`：186 行肿瘤 T–NT 混合模型脚本；
- `data/tumor_compare_data.parquet`：模型输入；
- `output/compare_report_output.rds`：结果对象；
- `output/package_versions.txt`：Windows 10、R 4.4.0 与包版本记录。

因此，**肿瘤混合模型切片**有脚本、输入、输出和版本信息，复现条件相对完整；但本次作者分析没有执行该脚本，不能声称“已成功重跑”。而且 Parquet 的上游生成过程不在源码中。

#### 仓库中 Not found 的内容

完整文件清单中没有以下代码：DDA/DIA-NN 处理、FDP 阈值扫描、全局预处理、t-SNE/轨迹、组织特异性、共识聚类、外部数据库整合、PRM 和网站生成。仓库只覆盖论文的 tumour dysregulation 部分，不能被描述成“完整论文代码”。

#### 综合判断

- 已发布肿瘤分析切片：**3/5**；
- 仅靠该仓库重建整篇论文：**1/5**。

此外，没有本地 `SUPP_MD`；Supplementary Information 和表格只有外部链接。CodeGraph 数据库有效但索引到 0 个文件/节点/边，因此所有代码结论都来自直接读取 R 源码，而不是 CodeGraph 推断。

### 11. 怎样正确使用这个资源？

适合的问题：

- 某蛋白在哪些成人组织富集？
- 某癌种相对配对癌旁组织有哪些稳健差异蛋白？
- 某候选靶点是否同时具备肿瘤上调、组织选择性和外部药敏/依赖证据？
- 某组织在胎儿、肿瘤、癌旁和健康状态中的蛋白程序如何变化？

不应直接得出的结论：

- t-SNE 或 pseudotime 证明了肿瘤演化路线；
- 蛋白与药敏相关就证明它是致病驱动或临床有效靶点；
- 组织富集就证明某药一定导致该器官毒性；
- GitHub 仓库能够复现所有论文图表。

### 12. 最值得记住的结论

TPHP 的真正创新是**统一平台下的广泛人体蛋白质组资源和可比较的多状态设计**。它把解剖位置、发育/病理状态、配对癌症差异和治疗线索连成一条证据链。最强证据是广覆盖 DIA 图谱、严格错误控制、配对混合模型以及多层外部验证；最明显短板是公开代码只覆盖肿瘤差异模型，而且该脚本与论文预处理/配对/收敛规范仍有若干 Partial 或 Not found 项。研究者可以把它用作高价值候选生成与比较资源，但任何药物或靶点结论仍需要独立机制实验和前瞻性临床验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TPHP Human Proteome Atlas

### Problem

Protein abundance is only moderately reflected by mRNA, while antibody atlases are semi-quantitative and depend on reagent availability. Representative predecessors include the HPA tissue map (*Science*, 2015), two MS-based human proteome drafts (*Nature*, 2014), Wang et al.’s 29-tissue atlas (*Molecular Systems Biology*, 2019), and TSomics (*Cell*, 2020); these MS resources covered roughly 30 major tissues and did not provide the present broad, uniformly processed comparison of healthy, fetal, tumour, and paired non-tumour states (`paper.md:15-40,431-495`). Cancer consortia are deep within selected tumours—the paper cites the TCGA Pan-Cancer project (*Nature Genetics*, 2013) and a CPTAC program overview (*Cancer Discovery*, 2013)—but are harder to compare across tumour types because platforms, cohorts, and batches differ (`paper.md:34-40,445-446`).

TPHP addresses this resource gap with one DIA-MS pipeline spanning 2,856 samples, 58 major tissues, 251 subtypes, and 25 carcinomas. The study reports 13,609 quantified proteins and provides a spatially resolved reference across fetal, healthy adult, tumour, and adjacent non-tumour states (`paper.md:1-13,34-48`).

### What the study contributes

TPHP is an **atlas plus a family of downstream analyses**, rather than a new standalone machine-learning algorithm:

1. A project-specific DDA spectral library is combined with non-human entrapment spectra and used for stringent DIA-NN quantification.
2. Quantile normalization, log$_2$ transformation, missing-value handling, QC, and batch correction yield a common protein matrix.
3. t-SNE, fetal-rooted Monocle3 pseudotime, and protein modules describe F–T–NT–N state transitions.
4. A modified HPA scheme maps tissue-enriched proteins and tissue-localized drug targets.
5. Per-cancer mixed models compare paired tumour and NT tissue, with patient random intercepts, supported covariates, Hedges’ small-sample correction, and within-cancer B-H control.
6. Consensus clustering and external links to DrugBank, clinical trials, TCGA, CPTAC, HPA, drug-response data, and CRISPR dependencies support biological interpretation and target prioritization (`paper.md:203-410`).

The entrapment false-discovery estimate is

$$
\widehat{\mathrm{FDP}}_{T\cup E_T}
=\frac{N_E(1+1/r)}{N_T+N_E},
$$

and a cancer protein is called differential at adjusted $P<0.05$ and $|g|\geq0.5$, where

$$
g=\frac{\hat\beta_1}{\hat\sigma}J(\nu).
$$

### Main evidence and results

- The DIA workflow quantified 13,609 proteins from 3,005 MS files at a reported global protein-level FDR of 0.1%. Replicate CV/correlation panels and variance decomposition support overall data quality (`paper.md:42-48`; visually inspected Extended Data Fig. 1).
- The state embedding shows a broad fetal→tumour→non-tumour→normal organization, with brain and liver deviations; eight protein modules connect this structure to RNA-splicing, immune, and tissue-specific programs (`paper.md:54-68`; Fig. 2 inspected).
- Across 74 refined healthy tissue types, 1,717 proteins are tissue-enriched; 480 occur in tissues underrepresented by earlier atlases. Synthetic-peptide spectra support the cochlea-associated PANX3 finding (`paper.md:70-81`; Fig. 3 and Extended Data Fig. 4 inspected).
- The paired model identifies 8,940 DEPs across 25 tumours, including 2,878 tumour-specific DEPs. Targeted PRM validates selected cancer-specific signals, while TCGA/CPTAC comparisons show substantial directional agreement (`paper.md:96-121`; Fig. 4 and Extended Data Figs. 5–7 inspected).
- The resource links 402 tissue-enriched proteins to 2,598 drugs and identifies 41 plasma-membrane tumour-enriched proteins as lower-off-target hypotheses. ProCan-DepMapSanger integration highlights target/drug associations such as MET inhibitors and BCL2-family inhibition (`paper.md:82-95,122-144`; Fig. 5 and Extended Data Fig. 8 inspected).

These are primarily **resource, association, and prioritization results**. The drug panels do not themselves demonstrate therapeutic efficacy.

### Strengths

- Broad anatomical and pathological coverage under a common DIA platform.
- Explicit entrapment-based error assessment plus stringent global $q$ thresholds.
- Paired tumour design and patient random effects reduce inter-patient confounding.
- Multiple validation modes: pooled/technical/biological QC, synthetic peptides, PRM, cross-cohort agreement, prognosis mapping, and functional screens.
- Public raw data (PXD077178/IPX0003578000 and PXD063370), source data, ProteinTalks portal, and a GitHub code snapshot (`paper.md:412-428`).

### Limitations

- Normal donors are predominantly older; tissue-specific protocols can introduce cross-tissue artifacts; and about 40 patients per tumour type limit inter-patient heterogeneity analysis (`paper.md:145-146`).
- Pseudotime is a fetal-rooted similarity coordinate, not measured developmental time or lineage evidence.
- Floor-based imputation assumes left-censored missingness; results may be sensitive if missingness has other causes.
- Cross-dataset drug response, CRISPR dependency, and prognosis links are associative and require experimental/clinical validation.
- Full stochastic/optimization details—seeds, embedding dimensions, consensus-resampling controls, and some selection rules—are not in the local paper Markdown. No supplementary Markdown is available.

### Code and reproducibility

**Code-paper fidelity: low overall, medium for the supplied tumour-model slice.** Repository `guomics-lab/TPHP` at commit `1a53d859d1b3064804cbd2b321ffcea8302868dc` contains one 186-line R analysis script, a 34 MB Parquet input, an 18 MB RDS output, and package-version capture. Direct source confirms the ordered NT→T REML mixed model, patient random intercept, Hedges’ correction, within-cancer B-H adjustment, and $|g|\geq0.5$/adjusted-$P<0.05$ filtering (`TPHP/tumor_dysregulation_analysis.R:65-169`).

Important differences are documented rather than smoothed over:

- **Not found in the script:** >50% missingness filtering, left-censored imputation, and log$_2$ transformation specified by the paper.
- **Partial:** a complete-pair wide table chooses protein names, but the model is fitted to the original long table (`TPHP/tumor_dysregulation_analysis.R:51-71`).
- **Partial:** optional covariates are capped by row count and fixed priority, an implementation rule absent from the paper (`:81-105`).
- **Partial:** hard errors are skipped and singularity recorded, but warnings are suppressed without an explicit convergence test (`:109-125`).
- **Not found in the repository:** code for DIA processing, global preprocessing, trajectory/tissue analyses, clustering, external integration, PRM, and the website.

The overall atlas is data-rich and openly deposited, yet reproducing every published analysis requires code and supplementary detail not present in the snapshot. CodeGraph indexed zero files, so direct source reads—not graph output—support all implementation claims.

### Bottom line

TPHP’s main value is a unified, unusually broad quantitative human proteome resource that connects anatomy, development, cancer dysregulation, and therapeutic hypotheses. Its experimental breadth and layered validation are strong; its major reproducibility weakness is that the public repository covers only the paired tumour mixed-model branch, and even that branch does not visibly perform every preprocessing step described in the paper.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
