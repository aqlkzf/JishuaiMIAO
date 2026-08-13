---
layout: default
permalink: /paper-atlas/hongkonggenomeproject-aa4c3bf9/
title: "HongKongGenomeProject"
nav: false
wide: true
description: "HKGP 把全基因组测序用于两个互补目标：在 2,227 名疑似遗传病 probands 中做 phenotype-guided diagnosis；在约 1.8 万名无近亲关系的华人 participants 中建立 dominant disease、recessive carrier 和 pharmacogenomic 频率参考。"
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
      <span>Nature Medicine · 2026</span>
    </div>
    <h1>HongKongGenomeProject</h1>
    <p>Population-scale genomic medicine with the Hong Kong Genome Project</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41591-026-04410-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for HongKongGenomeProject">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/hkgi-steam/hkgi_flagship_paper_2025" target="_blank" rel="noopener noreferrer" aria-label="Open code for HongKongGenomeProject">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 香港基因组计划（HKGP）：群体规模基因组医学方法解读

### 一句话理解

HKGP 把全基因组测序用于两个互补目标：在 2,227 名疑似遗传病 probands 中做 phenotype-guided diagnosis；在约 1.8 万名无近亲关系的华人 participants 中建立 dominant disease、recessive carrier 和 pharmacogenomic 频率参考。关键不是发明单一算法，而是用同一套经过人工临床解释的 WGS 数据，把诊断、筛查面板和用药指南从以欧洲人群为主的参考重新校准到华人人群。

### 为什么需要人群特异参考

变异是否罕见、carrier screening 应包含哪些 genes、药物代谢 allele 有多常见，都依赖参考人群。若华人样本在 gnomAD、ACMG carrier-screening tiers 或 CPIC allele references 中不足，常见华人 allele 可能被误判为罕见，真正重要的华人疾病 genes 可能不在筛查面板，PGx 检测也可能漏掉高频 star alleles。

HKGP 共招募 24,112 人。分析分为：

- **诊断 cohort**：2,227 probands，按 HPO phenotype、family structure 和 inheritance 做临床诊断；
- **HKGP Chinese cohort**：排除近亲并确认 ancestry 后，用约 17,949–18,257 人完成不同 population analyses（各分析因 QC/可用 genotype 略有不同）。

论文 Methods 位于 `paper.md:804-940`，主要结果位于第 33–145 行。

### 计算与临床流程

```text
PCR-free short-read WGS（GRCh38，约 30×）
  ├─ SNV/indel：GATK HaplotypeCaller
  ├─ SV：Manta + CNVKit
  ├─ STR：ExpansionHunter
  └─ 特殊区域：HBA1/2、SMN1/2、CYP2D6、HLA 等专用 caller
          ↓
统一 annotation + frequency/QC + ACMG/ClinGen interpretation
  ├─ 诊断：HPO-guided prioritization + family segregation + clinical review
  ├─ dominant：73 个 ACMG SF genes 的 GCF/cGCF
  ├─ recessive：carrier GCF、at-risk couple frequency、Chinese re-tiering
  └─ PGx：star allele → phenotype → actionable prescriptions
```

### 1. 诊断 cohort：从 phenotype 到可报告变异

诊断流程结合 HPO terms、PanelApp/Exomiser、家系模式和 ACMG/ClinGen classification；SNV/indel、CNV/SV 和 STR 均进入审阅。总体 553/2,227 probands 得到 positive diagnosis，yield 为 24.8%，不同疾病类别从 4.65% 到 56.8%（论文第 37–54 行；Fig. 1a）。

阳性诊断并不只等于“找到基因”：88.2% 有至少一种潜在 clinical-management change，包括 surveillance、medication guidance、procedure 和 lifestyle 等。Fig. 1b 的环形条图把这些类别和重叠直接显示出来。

这里的人工作用很关键。公开 repository 包含部分 variant processing，但 S-BCAW 半自动 curation 和最终 ACMG clinical judgment 不在仓库，不能从 scripts 自动重建 553 个诊断。

### 2. dominant disease burden：GCF 与 cGCF

对一个 dominant gene $g$，gene carrier frequency 可写为：

$$
\mathrm{GCF}_g=\frac{\#\text{携带该 gene P/LP variant 的个体}}{N}.
$$

某疾病组的 cumulative GCF（cGCF）汇总相关 genes 的携带负担，同时需避免同一人的重复计数。17,949 人中 3.73% 携带 73 个 dominant genes 中的 P/LP variants。华人 cohort 的 cardiovascular cGCF（2.48%）高于 cancer（1.23%），SCN5A、DSG2 等显示明显人群差异（论文第 55–124 行；Fig. 2）。

Fig. 2 不只是频率柱图：它把 variant type、gene-level GCF、疾病类 cGCF 和跨人群 comparison 连在一起，说明为何不能直接搬用欧洲频率阈值。

### 3. recessive carrier screening：从 individual carrier 到 couple risk

对 recessive gene，individual carrier frequency 不等于生育风险。随机配对下，同一 gene 的 at-risk couple frequency 近似与 carrier frequency 的平方相关；论文还用 2,864 对真实 couples 检查 random-mating estimate（Methods 第 888–915 行）。

ACMG pan-ethnic panel 在 HKGP 中的 carrier rate 为 48.1%，cACF 约 6.60%。以华人 GCF 和疾病严重度重新分 tier 后，panel 从 105 genes 调整到 61 genes，却把 carrier coverage 提高到 65.4%、cACF 提高到 15.4%；38 个在华人中重要的 genes 被加入，82 个低频 ACMG genes 被移出优先 tiers（Fig. 3）。这不是宣称原 ACMG genes“无效”，而是资源有限时的人群特异优先级。

特殊区域需要专门 caller。例如 SMN processing 既保留 `isCarrier=True`，也把 `SMN1_CN=2` 且 `g.27134T>G_CN=1` 的 silent carrier 纳入（`02.result_processing.py:9-19`）。HBA caller 只有 wrapper，核心 source 不公开，应保留 Inferred 边界。

### 4. PGx：从 allele frequency 到处方影响

PGx stream 用 Aldy、Cyrius、HLA-HD 和常规 VCF 派生不同 genes 的 diplotype/star allele，再按 CPIC phenotype 转换成 actionable recommendations。18,257 人中 99.98% 至少有一个 actionable phenotype，平均每人 5.20 个；VKORC1、CYP2C19、NUDT15、CYP2D6、ABCG2 等与其他参考人群差异明显（论文第 139–145、916–929 行；Fig. 4）。

处方影响估计把 phenotype frequency 与香港 Hospital Authority 的年度 prescription counts 结合，估计约 90 万张处方可能受 PGx guidance 影响。这是 population-level opportunity，不等于 90 万次已经证实的不良用药事件。

### 5. 结构变异代码实际做什么

公开 `sv.py` 读取 Manta 与 CNVKit VCF 并直接拼接（`sv.py:442-453`），再按 RefSeq transcript boundaries 标注受影响 genes/exons，包括 BND 两端（`sv.py:137-183`）。它还定义 paired-read/split-read 支持过滤（`sv.py:114-135`），但现有 code map 指出该 helper 未必在主路径调用。

因此 repo 能证明的是 downstream merge/annotation 逻辑，而不是 BWA、GATK、Manta、CNVKit 从 raw FASTQ 到 VCF 的完整运行。脚本中大量 institution paths 和 patient-level inputs 也限制独立 rerun。

### 如何读四张主图

- **Fig. 1**：17 类疾病的 diagnostic yield 与 positive findings 对 clinical management 的影响。
- **Fig. 2**：dominant genes 的 variant type、华人 GCF/cGCF 和跨人群差异。
- **Fig. 3**：recessive carrier burden、真实/模拟 couple risk 和 Chinese-specific re-tiering。
- **Fig. 4**：PGx altered-function allele、每人 actionable phenotype 数、检测 panel coverage 与 prescription impact。

这些图已从 `paper.pdf` 直接检查；`figure_analysis.md` 提供逐 panel 证据。

### 复现边界与正确用法

仓库的优势是 secondary analysis、SV annotation、specialized caller wrappers 和主图 notebooks 较完整，并提供容器化 figure build。限制是 patient-level WGS 受治理访问控制，S-BCAW/人工 curation、部分 caller source 和完整 primary pipeline 缺失。

因此 HKGP 最重要的可迁移方法不是某个公式，而是四层证据纪律：高质量 WGS → 人群适配频率 → 临床标准解释 → 用真实医疗场景校验。其频率与 re-tiering 结论适用于研究定义的香港华人 cohort；迁移到其他华人地区或 ancestry mixtures 时仍需重新验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## HKGP Flagship Paper — Summary

**Paper**: Population-scale genomic medicine with the Hong Kong Genome Project
**Journal**: Nature Medicine | **Year**: 2026 | **DOI**: 10.1038/s41591-026-04410-w
**Type**: atlas/population resource | **Analysis**: paper+code

---

### Motivation & Novelty

#### Biological Problem

Chinese and other East Asian populations are severely underrepresented in the genomic databases and guidelines that underpin precision medicine. gnomAD — the primary allele frequency reference — is predominantly European. The ACMG secondary findings (SF) gene list and carrier screening (CS) panel were calibrated using European allele frequencies. CPIC pharmacogenomic guidelines cite allele frequencies from European-dominant studies.

This Eurocentric foundation creates three clinical harms:
1. **Diagnostic inequity**: Pathogenic variants common in Chinese populations may be misclassified as VUSs; European-enriched variants trigger unnecessary testing.
2. **Screening inadequacy**: ACMG CS panels under-detect Chinese-prevalent conditions (e.g., CD36-associated bleeding disorders, SERPINB7-linked palmoplantar keratoderma) while wasting capacity on genes with negligible Chinese carrier rates.
3. **Pharmacogenomic miscalibration**: Chinese-specific alleles (VKORC1 rs9923231, CYP2C19\*37, CYP2D6\*10+\*36, ABCG2 rs2231142-T) are absent from or underweighted in AMP minimum allele sets, causing incorrect dose recommendations.

#### Limitations of Prior Approaches

| Method/Project | Journal | Year | Limitation |
|---|---|---|---|
| 100,000 Genomes Project (UK) | N. Engl. J. Med. | 2021 | European-focused; 25% diagnostic yield |
| All of Us (US) | Genome Med. | 2022 | Multi-ancestry but not Chinese-specific |
| Japan IRUD | J. Hum. Genet. | 2022 | Targeted sequencing, not WGS |
| Korea KGDP | Eur. J. Hum. Genet. | 2023 | Targeted panels; Korean ≠ Chinese |
| Taiwan PMI | J. Adv. Res. | 2024 | Exome only; limited rare disease focus |
| ACMG CS panel | Genet. Med. | 2021 | gnomAD 2.0 European calibration |
| Mackenzie's Mission | Eur. J. Hum. Genet. | 2021 | Australian population; European allele freq |
| gnomAD v4 | Genet. Med. | 2025 | Still predominantly European |

#### Novel Contributions

1. **First large-scale Chinese WGS rare disease resource**: 2,227 probands with comprehensive GS diagnostic pipeline achieving 24.8% yield — equivalent to UK's 100,000 Genomes Project but from an underrepresented population.
2. **Chinese-specific dominant disease landscape**: Identifies cardiovascular gene burden (cGCF 2.48%) exceeding cancer genes (1.23%), a reversal from European profiles; documents novel SCN5A and DSG2 enrichment.
3. **HKGP CS re-tiering**: Replaces European-calibrated ACMG CS tiers with Chinese-specific GCF thresholds, reducing panel from 105 to 61 genes while doubling at-risk couple coverage (6.60% → 15.4% cACF), identifying 38 clinically important genes missed by ACMG.
4. **Chinese PGx reference**: Documents that 99.98% of Chinese carry ≥1 actionable PGx phenotype; identifies 6 pharmacogenes with major alleles absent from AMP minimum allele sets; estimates 0.9M actionable annual prescriptions.
5. **Blueprint for precision medicine in underrepresented populations**: Establishes methodology for population-specific guideline recalibration applicable to other non-European populations.

---

### Method Overview

#### Cohort Design

Two complementary cohorts from 24,112 HKGP participants (July 2021–November 2024):
- **Diagnostic cohort** (n=2,227): Probands with suspected genetic disease; phenotype-guided diagnostic analysis including family structures (trios/duos).
- **HKGP Chinese cohort** (n=18,261): Unrelated Chinese participants filtered by kinship coefficient (>0.177 excluded) and genomic ancestry confirmation; used for population-level genotype-driven analyses.

#### Sequencing Platform

Short-read WGS on Illumina NovaSeq 6000/X Plus; ≥29.5× mean coverage; PCR-free library preparation; aligned to GRCh38 via BWA 0.7.17; variant calling via GATK HaplotypeCaller (SNVs/indels), Manta (SVs), CNVKit (CNVs), ExpansionHunter (STRs). Specialized callers for HBA1/HBA2 and SMN1/SMN2.

#### Four Analysis Streams

1. **Rare disease diagnosis**: HPO-guided variant prioritization (Exomiser + PanelApp) → ACMG/ClinGen curation → S-BCAW semi-automated cohort analysis.
2. **Dominant disorder screening**: 73 ACMG SF v3.2 genes → GCF/cGCF computation → cross-population comparison.
3. **Recessive carrier screening**: 1,459 consolidated genes → Chinese-specific re-tiering → GCF/ACF computation (random mating model validated against 2,864 actual couples).
4. **Pharmacogenomics**: Multi-tool genotyping (Cyrius, HLA-HD, Aldy, VCF-derived) → CPIC phenotype assignment → actionable prescription estimation from Hospital Authority data.

See `doc_method.md` for full pipeline documentation.

---

### Evaluation

#### Diagnostic Cohort Results

- **24.8% overall diagnostic yield** (553/2,227), consistent with 100,000 Genomes Project pilot (25%) and HKGP pilot (24%)
- **Category range**: 4.65% (gastrointestinal) to 56.8% (hearing disorder) (Figure 1a)
- **Family structures increase yield**: non-singleton 26.4% vs singleton 22.6% (p=0.041)
- **High HPO term count increases yield**: >8 HPO terms 27.1% vs ≤8 22.6% (p=0.014)
- **88.2% clinical utility**: 488/553 positive probands had ≥1 management change; 81.7% recommended enhanced surveillance (Figure 1b)
- **13-year diagnostic odyssey ended** on average; 31.1% of diagnostic SNVs/indels are novel

#### Dominant Disorder Results

- **3.73% carry P/LP in dominant genes** (670/17,949); 20 individuals carry ≥2
- **Novel finding — cardiovascular > cancer**: cGCF cardiovascular 2.48% vs cancer 1.23%; higher than Korean (2.17%), Icelandic (1.80%), African (0.66%) (Figure 2c)
- **Novel enrichment**: SCN5A (arrhythmia) and DSG2 (ARVC) are dramatically enriched in Chinese vs all other populations (Figure 2d); not previously reported
- **Lynch syndrome** (MLH1/MSH2/MSH6/PMS2) burden approaches half that of BRCA1/BRCA2, suggesting underdiagnosis
- **25.8% novel P/LP variants** among dominant gene findings; 20.8% ClinVar non-P/LP variants reclassified

#### Recessive Carrier Screening Results

- **48.1% carry P/LP in ACMG CS genes** (8,693/18,065); cACF 6.60% (virtual), 6.77% (actual couples, n=2,864)
- **HKGP re-tiering**: 105 → 61 genes; carriers 48.1% → 65.4%; cACF 6.60% → 15.4% (Figure 3e)
- **38 additional clinically important genes** not in ACMG CS: includes CD36, SERPINB7, SLC25A13, DUOX2, GALC, F7, C6, CAPN3, TH, DNAH11 (Figure 3d)
- **82 ACMG CS genes excluded** from HKGP tiers due to low Chinese carrier frequency (Figure 3f)
- HBA1/2 (thalassemia, tier 1) and GJB2 (hearing loss, tier 2) dominate Chinese carrier burden

#### Pharmacogenomics Results

- **99.98% of Chinese have ≥1 actionable PGx phenotype**; mean 5.20 per person (Figure 4c)
- **Key Chinese-specific PGx landscape** (Figure 4a): VKORC1 (3.4× higher than CPIC reference), ABCG2 rs2231142-T (31.8%), NUDT15 (~7% vs 0.2%), CYP2D6 (CYP2D6\*10+\*36 freq 0.36)
- **6 pharmacogenes with major alleles absent from AMP minimum set**: ABCG2, CYP2B6, UGT1A1, HLA-B, SLCO1B1, NAT2 (Figure 4d)
- **0.9 million annual prescriptions actionable** (30.8% of top-prescribed drug prescriptions); pantoprazole has the highest absolute actionable count (373K/year) due to CYP2C19 frequency (Figure 4e)
- **108 novel putative LoF PGx variants** in 340 individuals (1.86%); 81 unique to single individuals; requires WGS to detect

---

### Reproducibility: 3 / 5

**Justification**: The paper provides substantial reproducibility infrastructure: (1) analysis code for all secondary analyses and figure generation is publicly available on GitHub (hkgi-steam/hkgi_flagship_paper_2025); (2) figure generation notebooks run in a containerized Docker→Apptainer environment with pre-computed resource CSVs for external reproducibility; (3) all variant calls uploaded to ClinVar in batches. However, reproducibility is limited by: (a) primary patient-level WGS data is not publicly available — IRB approval and data access request required (available post-2030 for full main-phase data); (b) the S-BCAW semi-automated curation workflow is described in a separate paper (Ying et al. *Hum. Genet.* 2025) but not in the code repository; (c) R version discrepancy between code (R 4.4.1 in Dockerfile) and Reporting Summary (R 4.1.2); (d) specialized tools (Aldy 4.6, Cyrius 1.1.1, HLA-HD 1.7.0, SMNCopyNumberCaller) require separate installation; (e) HBA1/HBA2 in-house caller is not distributed.

**Practical notes**: The pre-computed resource CSVs in `figures/src/*/resources/` enable figure reproduction without patient data access. The Apptainer container (`r_hkgi_flagship_figures-v0.0.1.sif`) is the key reproducibility artifact. The analysis notebooks for variant filtering and GCF/ACF computation require institutional data access to generate outputs from scratch.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
