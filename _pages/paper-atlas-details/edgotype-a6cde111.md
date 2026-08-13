---
layout: default
permalink: /paper-atlas/edgotype-a6cde111/
title: "edgotype"
nav: false
description: "Edgotyping 的核心是把“mutation 是否破坏蛋白”拆成“是否引起 folding-quality-control signal、丢失哪些 protein partners、丢失哪些 DNA targets”。它证明 interaction-specific disease mechanisms 很常见，但每个 QW/E/QN 标签都受当时 interaction map 和 assay context 限制，必须作为可测…"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Cell · 2015</span>
    </div>
    <h1>edgotype</h1>
    <p>Widespread Macromolecular Interaction Perturbations in Human Genetic Disorders</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2015.04.013" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for edgotype">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Edgotyping：疾病错义突变不是只会“弄坏整颗蛋白”，也可能只切断特定分子连接

### 1. 这篇论文改变的是突变机制的观察单位

传统的准零模型（quasi-null）把疾病错义突变理解为：蛋白折叠或稳定性被破坏，表达量下降，于是全部功能一起丢失。Sahni 等人的 edgotyping 框架把观察单位从“一个基因/蛋白是否坏掉”细化为“这个等位基因改变了哪些网络边”。同一个蛋白往往连接多个 partner；一个表面突变可能只破坏某个界面，而保留折叠、表达量和其他相互作用。

论文定义三类可观察 PPI profile：

- quasi-WT（QW）：在已测试的 partner 集合中没有检测到改变；
- edgetic（E）：只丢失部分 WT interaction，其他 interaction 保留；
- quasi-null（QN）：检测到的 WT interaction 几乎或全部丢失。

这些名称是 assay-conditional。QW 不是“突变无功能后果”，QN 也不是直接测得蛋白完全失活；分类取决于当时可测的 interaction set、assay sensitivity 和表达背景。论文随后把 chaperone、PPI 和 PDI 三个层次整合，才把折叠失败与特异 edge loss 区分开。

### 2. 从 HGMD 到可测的 mutant ORFeome

作者从 HGMD 中约 16,400 个突变、1,200 多个有 WT ORF clone 的基因出发，每个基因最多选四个 mutation，并按蛋白序列四分位取样，以避免只集中在某一区域。通过 mutation primer、fragment PCR、fusion PCR、Gateway cloning 和测序验证，得到 hmORFeome1.1：2,890 个 single-amino-acid mutant ORF，覆盖 1,140 个基因。

这个资源决定了后续结论的分母。它不是所有疾病变异的随机样本：必须有可用 WT ORF、能够克隆、能够在 assay 中表达，并通过质量控制。作者用 RNA abundance、GO、Pfam、disorder 等比较降低明显 selection-bias 疑虑，但仍不能把比例无条件外推到所有基因、所有 isoform 或 truncating/splicing variants。

图 1 从左到右给出完整策略：先问 mutant 是否增强 chaperone binding；再比较 mutant/WT 的 PPI；对 TF 再测 PDI。实线和虚线分别表示保留和受扰动的 network edge。图 S1 记录 ORFeome 生成和代表性检查。

### 3. 第一层：用 chaperone binding 做“折叠分诊”

作者在 HEK293T 中用 LUMIER 测 7 个 quality-control factors（HSP90、HSC70、BAG2、CHIP/STUB1、PSMD2、GRP78/BIP、GRP94）与 WT/mutant bait 的结合。FLAG capture 后的 luciferase signal 表示 interaction，ELISA 估计 bait steady-state abundance。

扩展方法用 mixture model 同时处理 plate spatial bias 与 prey-specific background。可概括为：一个 well 的 log-luminescence 来自 background Gaussian 或 interaction Gaussian；plate/well bias 与 interaction effect 分开估计。mutant 和 WT 的 differential score 再用于判断 mutant-specific increased binding。未表达 pair 构成 noise control，threshold 调到使 background 中少于 2.5% 被误叫 positive。

这个方向很重要：作者观察到 increased chaperone association enrichment，而 decreased score 与 background 难区分。因此“约 28% allele 增强至少一个 QCF binding”支持一部分 mutant 更不稳定/更难折叠；其余约 72% 没有增强，并不证明结构绝对不变，只表示在这 7 个 QCF 和该 assay 条件下未检测到明显 folding-quality-control signal。

图 2 显示 2,332 个 disease alleles 对 7 个 QCF 的 mutant/WT scatter、cytoplasmic 与 ER factor clustering，并用 co-IP 验证部分案例。图 3 进一步把增强 chaperone binding 与较低 expression、buried residue、较少 disorder、FoldX destabilization 连接；图 S3 的 cellular thermal shift assay 中 6 个案例有 5 个显示 decreased stability。这是多证据链，而不是把 LUMIER signal 直接等同于 unfolding free energy。

### 4. 第二层：PPI edgotyping 的实际判定

作者先将 2,449 个 mutant bait 和 1,072 个对应 WT bait 对约 7,200 个 human ORFeome v1.1 prey 做 yeast two-hybrid screen，移除 autoactivator；随后对 screen 找到的 partner 以及 HI-II-14 已知 partner 做 targeted pairwise retest。每对做四次独立测试，至少 3/4 positive 才判为 detected interaction。

对一个 mutation，定义 WT profile $A_{WT}(j)\in\{0,1\}$、mutant profile $A_{mut}(j)\in\{0,1\}$。核心比较是 WT-positive edges 是否在 mutant 中保留：

$$
r=\frac{\sum_j A_{WT}(j)A_{mut}(j)}
{\sum_j A_{WT}(j)}.
$$

$r\approx1$ 对应 QW，中间值对应 edgetic，$r\approx0$ 对应 QN。论文实际分类还依赖可用 partner 数与实验判定；只有 WT 至少有两个 partner 的 mutation 才适合区分“部分丢失”与“全部丢失”。因此单 partner protein 无法可靠获得 edgetic 标签。

最终获得 460 mutant、220 WT 的 interaction profiles，在 1,316 个 PPI 中发现 521 个 perturbations。对具有至少两个 partner 的 197 个 mutations（89 WT proteins），分布为 QN 26%、E 31%、QW 43%。论文摘要把 QN+E 合并为 interaction-perturbing，并指出 edgetic 占 perturbing alleles 的约一半。

作者用人细胞 GPCA 做 orthogonal validation：unperturbed pairs 的 recovery 类似 positive reference set，perturbed pairs 类似 random reference set。图 4B支持 Y2H edge calls 的方向，但 GPCA validation 仍是抽样/汇总验证，不代表每条 edge 都在原生组织、内源表达下成立。

### 5. 为什么 edgetic 与 quasi-null 在结构上不同

如果 QN 主要来自整体不稳定，它应当更像 core mutation；如果 E 只打断 interface，它应当更像 surface/interface mutation。图 4D–F显示 QN 对 cytoplasmic chaperone binding 增强、表达下降，而 E/QW 更接近 WT。图 5再比较：

- PolyPhen-2 能区分 interaction-perturbing 与 non-perturbing，但不能可靠区分 E 与 QN；
- edgetic mutations 更常位于 exposed residues 与 PPI interfaces；
- QN 更符合 buried/destabilizing picture；
- 对一个具体 perturbed interaction，mutation 位于该 partner interface 的比例高于 unperturbed interaction。

界面判定使用 co-crystal mapping 和多个宽松距离条件，例如 Cα–Cα ≤11 Å、atomic-center ≤10 Å 或 van-der-Waals surface distance ≤5.5 Å，并以 solvent accessibility change 辅助检查。由于可用 complex structures 只覆盖子集，界面分析的样本数远小于全部 mutant，不能把缺少结构映射当作非界面。

### 6. QW 为什么仍可能致病：PDI 补上另一类边

PPI profile 不变的 transcription factor mutation 可能破坏 DNA binding。作者用 enhanced yeast one-hybrid（eY1H）筛 152 个 human developmental enhancers：先找 WT TF 能绑定哪些 enhancer，再逐对比较 mutant/WT。只有 WT 至少绑定两个 enhancer，才可像 PPI 一样分成 QW/E/QN。

图 7在 22 个 TF 上展示 PDI edgotype，并把 PPI 与 PDI 四格整合。关键结论不是“PPI assay 漏了错误”，而是不同 interaction modalities 捕获不同分子功能：某 mutation 可保留 protein partners，却丢失一部分 enhancer binding。DNA-binding-domain mutation 往往造成更广泛 PDI loss，域外 mutation 也可能产生选择性改变。

这里的覆盖同样有限：152 个 developmental enhancers 不是全基因组 regulatory elements；yeast reporter 缺少 mammalian chromatin、cofactor 和 cell-type state。PDI-QW 只能读作“在所测 enhancer/assay 中未改变”。

### 7. 七幅主图串起的逻辑

- **图 1：设计。** mutation ORFeome → PCI/PPI/PDI profiling → genotype-to-phenotype network explanation。
- **图 2：多数 mutation 未显示 gross folding defect。** 七个 QCF screen、profile clustering 和 co-IP validation；约 28% increased QCF binding。
- **图 3：chaperone-positive mutant 更不稳定。** expression、solvent accessibility、disorder、FoldX 与 thermal validation共同支持 folding triage。
- **图 4：PPI edgotype 与 disease enrichment。** QN/E/QW 分布、GPCA、expression/chaperone association，以及 disease mutations 57% vs common variants 8% perturb interaction。
- **图 5：edgetic 的界面与组织相关性。** E enriched at surface/interface，perturbed partners 更常表达于 disease-relevant tissues。bulk tissue expression 是相关性支持，不是 causality proof。
- **图 6：同基因不同 mutation、不同 edgotype、不同 phenotype。** TPM3、EFHC1 等案例以及 fraction of PPI loss 与 earlier onset 的 mutation-pair analysis；age of onset 还受 penetrance、背景和临床记录影响。
- **图 7：整合 PPI/PDI。** TF 的 DNA-binding perturbation提升机制分辨率，并说明单一 interaction modality 不足。

七张补充图分别支撑 ORFeome representativeness、LUMIER threshold、thermal stability、GPCA/network topology、QN folding、classification/downsampling/age-of-onset controls，以及 PPI/PDI/chemical-interface integration。

### 8. “96% precision、61% sensitivity”不能读成临床诊断性能

作者把 E 或 QN 视为 interaction-perturbing positive，用 HGMD disease-causing mutations 作 positive set、1000 Genomes common variants 作 putative negative set，得到 105/109=96% precision、105/172=61% sensitivity，并用 100,000 permutations 评估随机期望。

这个结果说明在作者选定、可克隆、可表达、且有可测 interaction 的 allele 集合中，检测到 edge perturbation 对 disease annotation 很特异。它不是 prospective clinical cohort：HGMD 与 common variants 的 ascertainment、allele frequency、gene selection和 assay coverage 不同；2015 年数据库 annotation 也不是当前临床 gold standard。61% sensitivity 还明确受未测 partner 和其他功能类型限制。

同理，论文发现 disease mutation perturbation 57%、common variant 8%，是这个实验 panel 的对照，而非任意 rare variant 的通用 posterior probability。

### 9. 从 edgotype 到 phenotype 的推理边界

图 6A显示同一 gene 中 edgotype 不同的 mutation pairs 更常对应不同 disease；TPM3/EFHC1 案例把特定 lost partners 与 tissue/disease knowledge连接。对同一 disease 的 allele pairs，lost-PPI fraction 更大者更常 earlier onset，并与 100,000 shuffled controls 比较。

这些分析提供 network-mechanism hypothesis：不同 edge loss 可能重定向受影响 pathway。但它们主要是 observational association。要证明某条 edge 导致临床 phenotype，需要 endogenous mutation、relevant cell type/animal model、edge-specific rescue 等实验。bulk RNA-seq 中 partner 在 disease tissue 表达也只说明机制可能发生，不证明该 edge 是致病中介。

### 10. Paper-code 与版本/复现边界

主证据是 `paper.md`、原始 `paper.xml`、7 张主图和 7 张补充图；没有作者 deposited source repository、analysis scripts、raw plate files、ORF clone sequences、Y2H/GPCA replicate matrix、permutation seeds 或 environment lockfile。因此下列实现只能从论文/Extended Experimental Procedures 重建，不能直接代码验证：

- LUMIER Gaussian mixture/plate spatial correction 与 differential Z-score；
- ELISA normalization 与 threshold application；
- Y2H pairwise 3/4 calling 和 edgotype assignment tables；
- FoldX batch preprocessing/rotamer restarts；
- PDB interface mapping、DSSP/Pfam/PSI-BLAST joins；
- tissue-expression mapping；
- 100,000 permutations 与 downsampling；
- Figures 1–7/S1–S7 的 plotting pipeline。

这里可以严谨解释实验流程、图和报告数字，不能声称一键复现或重新计算结果。未来若找到 code/data release，必须记录 URL、release/commit、数据库版本（HGMD 2009、ClinVar/1000 Genomes、HI-II-14、PDB/FoldX 等）并重新做 paper-code map。

工作区放在 `protein_sequence_models` 是仓库分类历史，不应把 edgotyping 误写成 protein language model 或 sequence predictor。它是高通量 experimental interaction-profiling framework，辅以统计模型和结构/网络分析。

### 11. 一句话抓住 edgotyping

Edgotyping 的核心是把“mutation 是否破坏蛋白”拆成“是否引起 folding-quality-control signal、丢失哪些 protein partners、丢失哪些 DNA targets”。它证明 interaction-specific disease mechanisms 很常见，但每个 QW/E/QN 标签都受当时 interaction map 和 assay context 限制，必须作为可测网络上的 profile，而非等位基因全部功能的最终判决。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — Edgotyping: Widespread Macromolecular Interaction Perturbations in Human Genetic Disorders

**Paper**: Sahni N, Yi S, Taipale M, et al. "Widespread Macromolecular Interaction Perturbations in Human Genetic Disorders." *Cell* 161:647–660 (2015).
**DOI**: 10.1016/j.cell.2015.04.013
**Reproducibility**: 3/5

---

### Motivation & Novelty

#### Biological Problem

Over 100,000 genetic variants have been linked to Mendelian disorders, yet for the vast majority the molecular mechanism — why the variant causes disease — remains unknown. The critical gap is between genotype (a missense mutation in gene X) and phenotype (a specific disease), mediated by molecular interactions that are largely unmapped.

#### Why Existing Methods Fall Short

The dominant prior framework treated disease-causing missense mutations as primarily acting through **protein destabilization / misfolding** — causing quasi-null loss of function. This view was reinforced by computational tools:

- **PolyPhen-2** (*Nat. Methods*, 2010): predicts deleteriousness based on evolutionary conservation and structural features. Effective at identifying interaction-perturbing mutations as "probably damaging" (Figure 5A), but cannot distinguish edgetic from quasi-null mutations (E vs QN p = 0.33, non-significant). Misclassifies many disease-causing mutations as "benign" (Figure S7D); among these, ~50% can be explained by molecular interaction perturbations detected by edgotyping.
- **Zhong et al. computational edgetic model** (*Mol. Syst. Biol.*, 2009): first computational prediction that disease mutations could be "edgetic." But was small-scale and purely computational — no experimental validation at proteome scale.
- **Human interactome HI-II-14** (*Cell*, 2014): provides the binary PPI reference network. Currently incomplete (~35% of human proteome covered), which limits edgotyping sensitivity.
- **LUMIER assay** (*Cell*, 2012): previously used for chaperone client profiling but not applied at the scale of a genome-wide disease mutation survey.

A key overlooked possibility: many disease mutations are structurally intact but specifically perturb only a subset of a protein's molecular interactions — disrupting individual "edges" of the interaction network — while leaving all other interactions intact. These **edgetic mutations** would be invisible to structural stability predictors and would require direct interaction profiling to detect.

#### What's New

1. **hmORFeome1.1**: the first large-scale human disease mutation ORF collection — 2,890 sequence-verified mutant ORFs across 1,140 genes with single amino acid changes, drawn from HGMD with spatial sampling along gene sequences.

2. **Systematic edgotyping strategy**: a three-layer interaction profiling pipeline — protein-chaperone interaction (PCI) as a folding triage layer, protein-protein interaction (PPI) profiling by Y2H, and protein-DNA interaction (PDI) profiling by eY1H — applied simultaneously at proteome scale to disease mutations.

3. **The edgotype concept experimentally validated at scale**: three functional classes (quasi-null / edgetic / quasi-WT) shown to be biologically real, structurally distinct, and clinically predictive across hundreds of genes and diseases.

4. **PPI+PDI integration**: first systematic demonstration that ~47% of disease mutations affecting transcription factors perturb DNA binding but not protein-protein interactions — these would be completely missed by PPI-only analysis.

---

### Method Overview

#### Algorithmic Framework

Edgotyping is fundamentally a **comparative interaction profiling** approach: for each disease mutation, measure all detectable molecular interactions and compare to the wild-type counterpart. The three assay layers provide orthogonal information:

**Layer 1 — PCI (folding triage)**: LUMIER assay in HEK293T cells with 7 quality control factors (HSP90β, HSC70, BAG2, CHIP/STUB1, PSMD2, GRP78, GRP94). A Gaussian mixture model corrects for plate spatial bias; differential Z-scores identify mutant proteins with enhanced chaperone binding (indicator of destabilized structure). ~28% of alleles show increased binding to ≥1 QCF; the majority (~72%) maintain normal folding.

**Layer 2 — PPI profiling**: Y2H first-pass screen of 2,449 mutant + 1,072 WT ORFs against ~7,200 human ORFs (ORFeome v1.1), followed by pairwise confirmation (4× replicates, ≥3/4 threshold) against all interaction partners found in the screen or in HI-II-14. GPCA in HEK293T cells provides orthogonal validation. 460 mutant / 220 WT proteins receive interaction profiles; 521 perturbed / 1,316 total PPIs.

**Layer 3 — PDI profiling (TFs only)**: eY1H pairwise assay of 70 mutant TF ORFs (173 mutations) against 152 human developmental enhancers from VISTA Enhancer Browser. Dual reporters (HIS3 + LacZ) with 5mM 3AT stringency.

**Classification**: Mutations assigned to quasi-null (QN), edgetic (E), or quasi-WT (QW) based on fraction of interactions perturbed. QN = global interaction loss (protein destabilization); E = selective interaction loss (interface mutation); QW = no detected interaction change.

#### Key Technical Components

- Gaussian process spatial bias correction in LUMIER (critical for 96-well plate artifact suppression)
- ELISA expression normalization (ELISA < 0.20 → protein excluded; prevents false inflation of interaction scores)
- Position-stratified mutation selection (up to 4 mutations per gene, one per protein quartile)
- FoldX ΔΔG with 5 random restarts for stability prediction
- PDB co-crystal interface analysis with three distance criteria (α-C ≤ 11Å, center ≤ 10Å, VdW ≤ 5.5Å)
- Upper quartile RNA-seq normalization for tissue expression analysis (minimizes highly expressed transcript inflation)

#### Biological Assumptions

- Chaperone binding faithfully reports on protein structural integrity
- Y2H in yeast detects biologically relevant binary interactions
- Interaction perturbation profiles are informative about disease mechanism
- Current interactome maps are incomplete but sufficient for trend detection

---

### Evaluation

#### Primary Findings

**PCI results**: ~28% of disease missense mutations increase chaperone binding (structural destabilization). Cytoplasmic and ER chaperone profiles are highly internally correlated (R² ≈ 0.6–0.85) but cluster separately — reflecting distinct chaperone client pathways. Structurally, QCF-binding mutants are enriched at buried core residues and deplete from disordered regions; FoldX ΔΔG significantly higher (p < 0.001). Critically, ~72% of disease mutations maintain normal chaperone binding, refuting the assumption that most Mendelian disease mutations act through misfolding.

**PPI edgotyping results** (Figure 4C): among 197 mutations in 89 WT proteins with ≥2 partners:
- Quasi-null (QN): 26% (n = 51)
- Edgetic (E): 31% (n = 62)
- Quasi-WT (QW): 43% (n = 84)
- Combined interaction-perturbing (E + QN): 57%

Validated by GPCA: unperturbed interactions recovered at PRS rate, perturbed at RRS rate — complete statistical separation confirms quality.

**Disease vs. non-disease discrimination** (Figure 4G): only 8% of 1000 Genomes common variants perturb interactions — 7-fold fewer than disease mutations (57%; p = 1.7×10⁻⁹). Precision = 96% (105/109 interaction-perturbing alleles are disease-causing); Sensitivity = 61% (105/172 HGMD disease mutations detected).

**Structural basis** (Figure 5): edgetic mutations occupy intermediate solvent accessibility (~32% surface-exposed vs ~47% for QW and ~11% for QN) and are significantly enriched at PPI co-crystal interfaces (p = 8.9×10⁻⁵). Crucially, they are enriched specifically at interfaces with their PERTURBED partners vs unperturbed partners (p = 1.5×10⁻³) — demonstrating mechanistic specificity.

**Tissue relevance** (Figure 5F): perturbed interaction partners are significantly more likely to be expressed in the disease-relevant tissue (43%) than unperturbed partners (28%) or random genes (28%).

**Edgotype-phenotype connection** (Figure 6): mutations from different edgotype classes in the same pleiotropic gene cause different diseases in 53% of pairs vs 22% for same-class pairs (p = 0.03). TPM3 and EFHC1 case studies show specific perturbed partners (troponin TNNT1 for muscle contraction; ZBED1/TCF4 for epilepsy-relevant pathways) expressed in disease tissue. More PPIs lost → earlier age of disease onset (p = 6.0×10⁻³ vs 100,000 permutation controls).

**PDI results** (Figure 7A): for 22 TFs with ≥2 enhancer binding partners: QN 38%, edgetic 43%, QW 19%. Over 80% of TF mutations affect DNA binding. The integrated PPI+PDI analysis covers 88% of tested mutations — 47% are PPI-intact but PDI-perturbing (would be missed by PPI analysis alone).

#### Comparative Performance vs. PolyPhen-2

PolyPhen-2 can identify interaction-perturbing mutations as "probably damaging" (Figure 5A), but fails to distinguish edgetic from quasi-null mutations (the 0.33 non-significant p-value in Figure 5A). For disease severity prediction, PolyPhen-2 shows poor correlation with age of onset (Figure S6I), while the edgotyping approach achieves p = 6.0×10⁻³. Among PolyPhen-2 "benign" misclassified disease mutations, ~50% are explained by molecular interaction perturbations.

---

### Reproducibility Rating: 3/5

**Justification**:

**Strengths**:
- All 2,890 mutant ORF clones are publicly available via the ORFeome Collaboration (contact: david_hill@dfci.harvard.edu). This is exceptional resource availability for a 2015 Cell paper.
- Supplementary tables (S1–S7) provide complete mutation lists, interaction profiles, edgotype assignments, PDB interface data — full data transparency.
- Methods are extensively documented in Extended Experimental Procedures — enough detail to replicate the assay pipeline.
- Validation layers (GPCA for Y2H, co-IP for LUMIER, CeTSA for protein stability) support the primary findings.

**Limitations**:
- **No code repository**: all computational analyses (Gaussian mixture model for LUMIER, FoldX pipeline, conservation analysis, network centrality, permutation tests) are described in text but no code deposited. Exact implementation details (e.g., the Gaussian process covariance matrix K specification, the MeV clustering parameters) are partially documented but not fully reproducible without implementation effort.
- **Scale and cost**: regenerating the experimental data would require Y2H infrastructure, stable HEK293T chaperone cell lines, yeast strain collections, and PacBio sequencing — significant resource barriers.
- **Incomplete interactome**: results depend on HI-II-14 interactome coverage (~35% proteome). The ~61% sensitivity limit means reproducing the exact classification for any given mutation depends on the interaction partner set tested.
- **Manual elements**: disease-tissue assignments for RNA-seq analysis were done manually; PDI positives required manual curation after image analysis (MyBrid software + manual review).

A determined lab with the ORF clones and Y2H infrastructure could reproduce the core edgotyping workflow; however, the absence of analysis code makes full computational reproducibility estimated at 2–3 person-months of effort.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
