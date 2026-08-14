---
layout: default
permalink: /paper-atlas/the-sequence-read-archive-sra-9e662be5/
title: "The Sequence Read Archive (SRA)"
nav: false
wide: true
description: "Leinonen、Sugawara 和 Shumway 在 Nucleic Acids Research 2011 年数据库专刊中介绍 Sequence Read Archive（SRA）。测序成本下降、速度提高，使新一代测序数据快速增长；论文关注的是如何把一次测序实验的主要分析数据长期保存，跨机构交换，并让用户能够持续访问。SRA 是 INSDC 的公共归档资源，由 NCBI、EBI 和 DDBJ 共同运行。"
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
      <span>Nucleic Acids Research · 2011</span>
    </div>
    <h1>The Sequence Read Archive (SRA)</h1>
    <p>The Sequence Read Archive (SRA)</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/nar/gkq1019" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for The Sequence Read Archive (SRA)">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SRA 方法与资源设计说明

### 这篇论文要解决什么问题？

Leinonen、Sugawara 和 Shumway 在 *Nucleic Acids Research* 2011 年数据库专刊中介绍 Sequence Read Archive（SRA）。测序成本下降、速度提高，使新一代测序数据快速增长；论文关注的是如何把一次测序实验的主要分析数据长期保存，跨机构交换，并让用户能够持续访问。SRA 是 INSDC 的公共归档资源，由 NCBI、EBI 和 DDBJ 共同运行。具有伦理或授权限制的人类数据应提交到 dbGaP 或 EGA，而不是公共 SRA；SRA 可以提供这些数据的高层元数据（论文第 12、16 行；JATS 中 `THE SEQUENCE READ ARCHIVE` 小节）。

### 为什么仅保存最早的原始信号不现实？

论文把存储精度与成本放在一起考虑。图像和信号等早期原始数据理论上最精确，但存储成本很高。因此，所有提交都必须包含碱基调用（SOLiD 则为颜色调用）和质量值；Illumina GA 与 SOLiD 不再推荐提交信号数据，而 Roche/454 仍应保留信号信息（论文第 28 行）。这是 2011 年的归档策略描述，不是一个给出明确成本函数的算法。

### SRA 的核心设计

SRA 把序列载荷、描述实验的 XML 元数据、跨站点交换和格式转换连成一个归档流程：

```text
测序实验的主要分析数据
          |
          v
选择平台相关的保留层级
  必须：碱基/颜色调用 + 质量值
  454：保留信号；Illumina GA/SOLiD：不保留信号
          |
          v
选择提交格式：Illumina GA/SOLiD 用 SRF，454 用 SFF
          |
          +-----------------------------+
          |                             |
          v                             v
填写六类模式约束的 XML 元数据       受控人类数据转到 dbGaP/EGA
          |                             |
          v                             v
为对象分配永久 accession             在 SRA 中提供高层元数据
          |
          v
SRA Toolkit 校验并转换为内部格式
          |
          v
NCBI、EBI、DDBJ 每日交换公共数据
          |
          v
从任一合作站点检索，转换为 Fastq，或通过标准 API 使用
```

#### 六类元数据对象

论文称每个对象都受 XML Schema 约束，并有跨合作方通用的永久标识符（论文第 34 行）：

- `study`：项目概况、文献引用，可关联 INSDC 项目。
- `sample`：生物样本的详细信息。
- `experiment`：仪器与文库信息，直接关联序列数据。
- `run`：运行层面的仪器与文库信息，直接关联序列数据。
- `analysis`：参考序列比对、多重比对、组装等分析结果。
- `submission`：把其他对象组织成一次提交。

论文没有列出字段、基数约束或完整示例，所以这里不能据此推导具体 XML 文档结构。

#### 数据格式和交换

论文把 SRF 描述为 Illumina GA 与 SOLiD 的推荐格式，把 SFF 描述为 454 的推荐格式；两者已经高度压缩，不应再套用额外压缩（论文第 30 行）。文中还回顾了 Fastq、ZTR、SRF、SAM/BAM 的关系，并预计 BAM 可能成为优选归档格式，因为它同时支持比对和未比对 reads（论文第 40 行）。

NCBI SRA Toolkit 被描述为所有新一代序列数据在 SRA 内部存储和交换的基础。合作方会用它校验、转换提交，使用其内部格式交换数据，再转换成 Fastq 或通过标准 API 提供给其他程序；论文举例说明 BLAST 可使用 Toolkit 生成的文件（论文第 42 行）。

### 论文报告的规模与评估

这不是算法基准测试，而是数据库资源说明。论文在 2010 年 9 月中旬的快照中报告超过 5000 亿条 reads、60 万亿个碱基；Illumina GA、SOLiD 和 454 分别约占 80%、15% 和 5% 的提交碱基。1000 Genomes 项目产生了接近总量一半的数据，*Homo sapiens* 与 *Mus musculus* 分别占 65% 和 4%（论文第 20 行）。论文没有给出可复现的吞吐量、延迟、压缩率、数据完整性或跨站点一致性基准，也没有图像文件可供视觉复核。

### 可复现性与已知缺口

**Not found / 未找到：** 本次结构化来源、可用性扫描和全文 GitHub URL 扫描均没有发现与论文绑定的代码仓库；工作区没有 `code source`。因此不能把文中描述的 Toolkit 行为标成代码验证结果。论文和 JATS 也没有提供可执行提交命令、Toolkit 版本及参数、XML Schema 字段清单、错误处理、完整交换协议或参考实现。图像目录为空，JATS 没有 figure/table 元素，因此不存在可做图像分析的直接证据。

本文档的确定性来源是 `paper source/PMC3013647/paper.md` 与同目录的 `article.source.xml`；`scratch/evidence_index.json` 只用作导航。所有关于数据规模的数字都限定为论文的 2010 年历史快照，不应外推为当前 SRA 状态。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## The Sequence Read Archive (SRA)

### Problem

The paper addresses the archival problem created by rapidly increasing next-generation sequencing output: preserve primary sequence data as part of the scientific record, exchange it between international repositories, and provide durable public access despite storage and format pressures. It distinguishes public SRA records from controlled-access human submissions routed to dbGaP or EGA.

### Resource introduced

SRA is presented as an INSDC resource operated by NCBI, EBI, and DDBJ. The design combines platform-aware submission policies, six schema-constrained metadata XML objects (`study`, `sample`, `experiment`, `run`, `analysis`, and `submission`), permanent accessions, daily partner exchange, and the NCBI SRA Toolkit as the internal storage/conversion/API layer.

### High-level workflow

Submissions retain base or SOLiD color calls and qualities. The 2011 recommendations use SRF for Illumina Genome Analyzer and SOLiD, SFF for Roche/454, and retain 454 signal information while dropping Illumina/SOLiD signal data because of its reported storage cost. Partners validate and convert submissions into toolkit format, exchange public records daily, and expose retrieval, Fastq conversion, and API access. BAM is discussed as a future archival direction because it supports aligned and unaligned reads.

### Historical evaluation and scale

This database-issue article is a resource description, not a controlled benchmark. Its historical content snapshot (mid-September 2010) reports more than 500 billion reads and 60 trillion base pairs; approximately 80% of bases came from Illumina GA, 15% from SOLiD, and 5% from Roche/454. The 1000 Genomes project contributed nearly half of submitted data, and *Homo sapiens* represented 65% of bases versus 4% for *Mus musculus* (paper line 20). No independent accuracy, throughput, latency, or compression benchmark is reported.

### Reproducibility

The paper gives a useful architecture and policy description, but not a runnable implementation. No paper-linked GitHub repository or local code snapshot was found after structured-source, availability, and full-paper discovery; code-paper matching is therefore **Not found**. The workspace also has no local article figures, supplementary Markdown, executable submission examples, schema field listings, toolkit version/parameters, validation/error semantics, or reproducible benchmark data. Claims above are grounded in `paper source/PMC3013647/paper.md` and its bundled JATS XML, with historical values kept separate from current-state assumptions.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
