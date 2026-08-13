---
layout: default
permalink: /paper-atlas/fragoza2019-ppi-snv-a95bdfbd/
title: "Fragoza2019_PPI_SNV"
nav: false
wide: true
description: "这项工作不是训练一个变异致病性预测器，而是构建并验证一个实验 atlas：从 ExAC、HGMD 和 COSMIC 选择 2,009 个错义 SNV，逐个制备经过测序确认的突变克隆，再用酵母双杂交测试它们对 2,185 条蛋白互作的影响。最终得到 4,797 个“SNV—互作”测量，并用人细胞中的 PCA、蛋白稳定性实验、酶活实验和 CRISPR 小鼠把“互作边被破坏”逐步连接到分子和个体表型。"
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
      <span>Nature Communications · 2019</span>
    </div>
    <h1>Fragoza2019_PPI_SNV</h1>
    <p>Extensive disruption of protein interactions by genetic variants across the allele frequency spectrum in human populations</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-019-11959-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Fragoza2019_PPI_SNV">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Fragoza 2019 方法解读：从变异到被破坏的蛋白互作边

### 一句话理解

这项工作不是训练一个变异致病性预测器，而是构建并验证一个实验 atlas：从 ExAC、HGMD 和 COSMIC 选择 2,009 个错义 SNV，逐个制备经过测序确认的突变克隆，再用酵母双杂交测试它们对 2,185 条蛋白互作的影响。最终得到 4,797 个“SNV—互作”测量，并用人细胞中的 PCA、蛋白稳定性实验、酶活实验和 CRISPR 小鼠把“互作边被破坏”逐步连接到分子和个体表型。

### 1. 研究单位不是“一个变异”，而是“变异—互作对”

同一个蛋白可能与多个伙伴结合。一个错义变异可以只破坏其中一条边，而不让整个蛋白失效。因此作者没有只给每个 SNV 一个有害/无害标签，而是测试

$$
(v, P_i\leftrightarrow P_j),
$$

即变异 $v$ 对某一条具体蛋白互作边的影响。若一个变异至少破坏一条被测互作，它被记为 disruptive；对至少两个伙伴有测量的变异，还可分为：所有边保留的 non-disruptive、只丢失部分边的 partially disruptive、所有被测边都丢失的 null-like。

这里的 null-like 只表示“在已测试的互作集合中全部中断”，不等于该蛋白在细胞内彻底失活。平均每个变异只测试约 2.5 个伙伴，而且 Y2H 参考互作组本身不完整。

### 2. 为什么先按频率分层抽样

ExAC 0.3.1 含 60,706 个外显子组，其中超过一半独特变异是 singleton。若直接随机抽样，实验集会几乎被极罕见变异占据，无法比较常见与罕见变异。作者因此按 allele count 的六个区间各抽取约 200–400 个变异，并限制每个基因平均约两个变异，得到 1,676 个 ExAC SNV；另加入 204 个 HGMD 疾病突变和 162 个 COSMIC 体细胞突变。

候选还必须满足三个实验前提：所在基因有 hORFeome 克隆、有可由 Y2H 测试的已知互作、ExAC 变异通过 PASS。RefSeq 转录本与 ORF 先经 BLASTX 和 EMBOSS Stretcher 对齐，突变周围 31 aa 必须完全一致，整体同一性通常须超过 95%。所以 atlas 不是全外显子组的均匀样本，而是“可克隆且已有可测互作”的子集。

### 3. Clone-seq：先证明手里的突变克隆是对的

作者在 96 孔板中进行定点突变，每个反应挑最多四个单克隆，把多个克隆混池后做 Illumina NextSeq 1×75 测序。对目标位置，突变调用分数为

$$
\operatorname{Score}(WT,pos,Mut)=
\frac{\operatorname{Observed}_{Mut,pos}}
{\operatorname{Expected}_{Mut,pos}}.
$$

如果一个基因池中有 $N$ 个克隆且只有一个携带目标碱基，理想突变读段比例约为 $1/N$；期望值再用邻近 10 个非目标位置估计的测序错误率修正。与 Sanger 结果比较后，作者用 Score $\ge 0.5$ 调用真突变，并扫描 ORF 其余位置排除 PCR 引入的旁路突变。

这个步骤很关键：后续 Y2H 的“互作丢失”只有在突变克隆不含其他改变时才能归因于目标 SNV。

### 4. Y2H：把生长差异转成互作是否被破坏

野生型与突变 ORF 分别进入 AD/DB 载体，在两种选择培养基上比较酵母生长。一个互作被判定为 disrupted，必须同时满足：

1. 突变型相对野生型的生长至少下降 50%，该阈值由两倍连续稀释实验标定；
2. 野生型和突变型 DB-ORF 都不是自激活子；
3. 生长下降在三轮筛选中复现。

2,009 个 SNV 共形成 4,797 个 SNV—互作对，作者识别出 442 个互作破坏型 SNV。这个数字包括不同来源；ExAC 中有 298 个 disruptive 变异。实验读数是二元的边保留/边中断，不能给出结合自由能或亲和力变化，也不能捕捉细胞类型、定位和翻译后修饰依赖的互作。

### 5. PCA：换一个体系验证 Y2H 的判断

为了避免把酵母体系的特异性当成普遍结论，作者在人 HEK293T 细胞中用 Venus 分体荧光 PCA 重测 192 个 Y2H-disrupted 与 205 个 non-disrupted 变异互作对，并同时使用文献阳性参考集 PRS 和随机参考集 RRS。

逻辑不是要求每一对都复现，而是比较各集合在相同阈值下的恢复比例。图 2a 显示 non-disrupted 对的恢复率接近 PRS，而 disrupted 对接近 RRS，支持 Y2H 网络在独立实验体系中的总体可重复性。它并不等价于所有 4,797 个测量都获得了人细胞验证。

### 6. DUAL-FLUO：区分“丢边”和“蛋白没了”

互作消失可能有两种机制：突变局部改变结合界面，或蛋白整体不稳定。作者把 WT/突变蛋白与 GFP 融合，同时由独立启动子表达 mCherry，以 mCherry 校正转染效率和细胞状态。对 278 个 ExAC 变异计算突变/WT 稳定性分数比：

- 比值 $\ge 0.5$：stable；
- $0\le$ 比值 $<0.5$：moderately stable；
- 突变稳定性分数 $<0$：unstable。

图 3 配合 western blot 表明，大多数互作破坏并非由蛋白表达完全丢失造成。论文将此解释为 edgetic 扰动：变异更常删除网络中的特定边，而不是删除整个蛋白节点。但 GFP 稳态荧光也可能受降解和表达动力学影响，不能直接等同于正确折叠。

### 7. 10.5% 是怎样算出的

ExAC 实验样本中的粗 disruptive 比例为 $298/1676=17.8\%$，但这是人为按频率分层后的样本，不能直接代表一个人的基因组。作者先在四个 MAF 区间测量破坏率 $r_i$，再用典型个体的 missense site-frequency spectrum 权重 $f_i$ 计算：

$$
R_{individual}=\sum_i f_i r_i.
$$

常见变异在单个人携带的 missense 变异中占绝大多数，而其测得破坏率较低；加权后得到 $10.5\%\pm1.8\%$。乘以每人平均 13,595 个 missense 变异，约为 1,434 个可能影响 PPI 的变异。

这个数是从分层实验率到人均负担的估计，不是对某个个体逐一实测的结果。它还受可测互作覆盖、ExAC 人群结构、Y2H 灵敏度和频率分箱假设影响。论文也明确指出，互作被扰动是否产生细胞或临床表型仍未确定。

### 8. 图 4–5：从互作图谱到疾病候选

作者发现，位于已知界面/界面结构域的变异更常破坏互作，disruptive 变异也位于更保守的残基。这些独立信号支持 atlas 测到的不是随机实验噪声。

进一步地，同一基因上的疾病突变若共享至少一条被破坏的互作，更常对应相同疾病。作者据此把未知表型的 ExAC 变异与已知疾病突变做“disruption profile matching”：

- PSPH T152I 与磷酸丝氨酸磷酸酶缺陷突变 D32N 都破坏 PSPH 自互作；纯化蛋白实验显示两者活性都降至 WT 的约 60%。
- SEPT12 G169E 与男性不育突变 D197N 破坏相似的 septin 互作；co-IP 支持 SEPT12–SEPT1 中断，纯合 G169E 雄鼠出现精子运动下降与亚育。

这两个案例证明共享互作表型可用于优先排序候选，并不证明所有 profile 匹配都致病。SEPT12 的人类纯合携带者在 ExAC 中未被观察到，鼠表型到人类疾病仍是推断。

### 9. 论文—代码与复现边界

论文没有 Code availability 段落或代码仓库链接，本地也没有分析代码，因此无法做源码级 paper-code 匹配。Methods 给出了 BWA、BLASTX、EMBOSS、PSI-BLAST、Clustal Omega 等工具和实验步骤，但未提供固定环境、完整命令流水线或版本锁定；Clone-seq 调用、SFS 加权、JSD/phyloP、Fay and Wu's $H$、LD 和统计图表都需自行重实现。

可用材料包括主文、补充说明/表格/数据附件的 PDF，以及详细实验协议。突变克隆仅说明可向作者申请；原始 Clone-seq 读段和板级荧光数据没有公共 accession。因而可复核论文给出的汇总数据和方法逻辑，但不能仅靠此工作区从原始数据端到端重现 atlas。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — Fragoza et al. 2019: Extensive disruption of protein interactions by genetic variants across the allele frequency spectrum in human populations

### Motivation & Novelty

Each human genome carries ~13,500 missense coding variants, yet the fraction that meaningfully alters protein function has been notoriously difficult to pin down. Prior estimates ranged from 1.7% (1000 Genomes Phase I, SFS-deleterious; *Nature*, 2012) to 12.3% (GoNL, PPH2+GERP; *Nat Genet*, 2014), relying on computational predictions rather than direct functional measurements. Experimental datasets were equally limited: the SKEMPI database (*Bioinformatics*, 2012) cataloged 3047 mutation effects on protein binding, but only 7 were human population variants — the rest came from scanning mutagenesis. Disease-focused screens (Sahni et al., *Cell*, 2015; Wei et al., *PLoS Genet*, 2014) examined known pathogenic mutations, which are very rare and do not capture the broader variant landscape.

Fragoza et al. address this gap with the first large-scale, unbiased experimental survey of how human population variants affect protein–protein interactions (PPIs). Three key innovations distinguish this work:

1. **Population-representative sampling**: Instead of oversampling rare variants (>50% of ExAC variants are singletons), the authors stratified selection across allele frequency bins, testing 1676 ExAC variants plus 204 HGMD disease mutations and 162 COSMIC somatic mutations — 2009 total.
2. **Direct experimental measurement at scale**: 4797 SNV-interaction pairs screened by yeast two-hybrid (Y2H) with orthogonal validation by protein complementation assay (PCA) in human 293T cells.
3. **Disruption profile matching**: A new concept for identifying candidate disease variants by matching their interaction perturbation patterns to those of known disease mutations, validated in two case studies with in vitro enzymology and CRISPR mouse models.

### Method Overview

The pipeline combines high-throughput mutagenesis, interaction screening, and protein stability profiling:

1. **Variant selection**: 2009 missense SNVs selected from ExAC (stratified across MAF bins), HGMD, and COSMIC, restricted to genes in hORFeome with Y2H-testable interactions in a ~14,000-interaction reference interactome.
2. **Clone-seq mutagenesis**: Site-directed mutagenesis + Illumina NextSeq sequencing of pooled clones. A scoring function identifies clones carrying only the desired mutation (Score ≥ 0.5 threshold, validated by Sanger).
3. **Y2H disruption screening**: Each variant tested against ~2.5 interaction partners on average. Disruption called when ≥50% growth reduction reproduced across three independent screens.
4. **PCA validation**: Representative subset retested in human 293T cells using Venus split-fluorescent protein complementation. Disrupted pairs recover at random-reference rates; intact pairs at positive-reference rates.
5. **DUAL-FLUO stability assay**: 278 ExAC variants tested for protein expression stability using GFP-tagged constructs with mCherry normalization in 293T cells. Classifies variants as stable, moderately stable, or unstable.
6. **Disruption profile matching**: Pairs of mutations on the same gene with overlapping disrupted interactions are identified; ExAC variants matching known disease mutation profiles are prioritized for validation.

See doc_method.md for detailed mathematics and algorithm walkthrough.

### Evaluation

#### Scale and disruption rates
- **442 interaction-disruptive SNVs** identified across 669 disrupted interactions from 4797 tested SNV-interaction pairs.
- Disruption rates by source: HGMD disease mutations 52.9%; COSMIC cancer (known cancer genes) 34.8%; COSMIC (other) 22.1%; ExAC overall 17.8%.
- MAF-stratified disruption: <0.1% → 20.0%, 0.1–1% → 17.9%, 1–10% → 16.4%, >10% → 9.6% (P=0.0054, chi-square). See Figure 2b.

#### Per-individual estimate
- **10.5% ± 1.8%** of missense variants per individual expected to disrupt PPIs after site frequency spectrum weighting — notably higher than all prior estimates (Figure 2c table). Explicitly a lower bound, since Y2H cannot detect all interactions.

#### Validation and consistency
- PCA retest: disrupted pairs recover at RRS rates (P=5.4×10⁻⁴ vs. intact). Figure 2a.
- Most disruptions are edgetic: 68.8% affect only 1 partner; 93% of disruptive variants maintain stable protein expression. Figure 3d.
- Disruptive variants enriched at interaction interfaces (19.2% vs. 5.0%, P=3.1×10⁻⁵), conserved residues (JSD P=1.2×10⁻¹⁰), and genomic regions under positive selection (Fay & Wu's H, P=0.0099 overall). Figure 4.
- Shared disruption profiles predict same disease (0.76 for ≥2 shared disruptions vs. 0.63 for none, P=0.018). Figure 4e.

#### Case study validations
- **PSPH T152I** (MAF=0.10%): matches disruption profile of disease mutation D32N. In vitro phosphatase activity reduced to 59.2% of WT (P=0.0010), matching D32N at 60.0% (P=6.6×10⁻⁴). Figure 5b.
- **SEPT12 G169E** (MAF=0.02%): matches disruption profile of infertility mutation D197N. CRISPR-edited homozygous mice show subfertility (P=5.2×10⁻⁴) and poor sperm motility. Figure 5f-g.
- **AKR7A2 A142T** (MAF_Eur=9.3%): common null-like variant reduces kcat/KM by 44% (P=0.034). Figure 3f.

#### Negative result
- No enrichment for disruptive variants in LD with GWAS SNPs (Supplementary Figure 5), suggesting molecular-level interaction perturbations do not directly translate to GWAS-scale phenotypic effects — consistent with the "buffering" hypothesis and the complexity of genotype-phenotype mapping.

### Reproducibility

**Rating: 3/5** (paper-only assessment)

**Strengths**:
- All interaction disruption data provided as Supplementary Data 2–4; stability data as Supplementary Data 5; PCA data as Supplementary Data 6; drug-relevant variants as Supplementary Data 7.
- Clone-seq mutagenesis primers provided (Supplementary Data 1).
- Methods section is detailed and well-structured, covering all experimental protocols.
- Mutant clones available upon request from Haiyuan Yu.
- Key equations and statistical tests explicitly described.

**Limitations**:
- **No code repository**: No computational analysis code provided. Disruption rate calculations, site frequency spectrum weighting, conservation analyses (JSD, phyloP), Fay & Wu's H, and LD calculations would need to be reimplemented.
- **No raw sequencing data**: Clone-seq NGS data and PCA fluorescence raw data not deposited in public repositories (no GEO/SRA accession).
- **Custom resources required**: The ~14,000-interaction Y2H reference interactome is a prerequisite; hORFeome clone libraries are not publicly deposited for open distribution.
- **Experimental reproduction**: Reproducing the Y2H screen requires institutional access to yeast mating facilities, clone libraries, and 293T cells — feasible for well-equipped labs but not trivial.
- **CRISPR mouse model**: Sept12^G169E mice were generated at Cornell; breeding colonies would need to be re-established.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
