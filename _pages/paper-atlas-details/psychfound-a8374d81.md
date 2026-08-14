---
layout: default
permalink: /paper-atlas/psychfound-a8374d81/
title: "PsychFound"
nav: false
wide: true
description: "论文针对精神科临床中的医生短缺、诊断和用药依赖经验，以及现有面向患者的心理健康大模型不能贴合医生工作流的问题，提出 PsychFound。它面向中文临床场景，覆盖诊断、治疗计划和长期管理。当前工作区只有 Nature HTML 预览，正文 Methods/Results 和补充 PDF 未能取得，因此对数据构建和实验数值只保留论文摘要、图注明确给出的内容。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>PsychFound</h1>
    <p>A domain-adapted large language model to support clinicians in psychiatric clinical practice</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01224-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for PsychFound">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/wrx33/PsychFound" target="_blank" rel="noopener noreferrer" aria-label="Open code for PsychFound">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PsychFound 方法中文解读

### 要解决什么问题

论文针对精神科临床中的医生短缺、诊断和用药依赖经验，以及现有面向患者的心理健康大模型不能贴合医生工作流的问题，提出 PsychFound。它面向中文临床场景，覆盖诊断、治疗计划和长期管理。

### 方法与创新

论文摘要称模型使用专家整理的精神科语料和 64,588 条脱敏中文真实 EHR，通过三阶段框架注入专业知识、增强临床推理并适配多种临床任务，最终得到 7B 参数模型。公开代码展示了与该叙述相匹配的工程骨架：ShareGPT 格式病例、Qwen ChatML 监督微调、诊断/用药任务的强化学习提示、GRPO 训练和 LoRA 合并；但私有 EHR、模型权重和临床应用服务没有公开在仓库中。

### 计算流程

```text
病例 JSONL (patient_info, target)
        |
        +--> SFT: ChatML + prompt 标签屏蔽 + LoRA
        |
        +--> RL 数据: 诊断/用药 × 类别/亚型，固定随机种子抽样
                    |
                    v
          <think>推理</think><answer>结论</answer>
                    |
             GRPO + 临床奖励
                    |
          合并 LoRA，导出模型
```

`data/io.py:27-41` 检查每行 JSON 并抽取首个非空 human/gpt 对；`training/sft.py:31-55` 对 prompt 和答案分别编码，prompt 标签设为 `-100`；`prompts.py:16-51` 规定 ICD-10 诊断和通用名用药的输出格式；`rewards.py:38-60` 对 XML 风格输出计算格式、推理关键词和答案正确性，`Reward.total` 使用 `format + reasoning + 2 * accuracy`；`training/grpo.py:37-53` 还检查 WORLD_SIZE 和全局 prompt batch 语义。

### 评估与边界

摘要报告三项专业知识测试、五项 PsychBench 临床任务、22 个 LLM 对比、双臂前瞻性研究及 60 名精神科医生阅读者研究。论文声称 PsychFound 总体领先，辅助住院医师提高咨询质量、诊断准确性和用药适当性并缩短记录时间（均 *P* < 0.01），推理表现达到 attending 医师水平。图 3-6 和扩展图 1-4 提供可视化支持；扩展图 4 的病例扰动显示移除关键信息时 ICD-10 输出随之改变。

可复现边界：代码、公开 PsychCorpus/PsychBench 接口和训练逻辑可检查；因此 PsychFound 是有公开训练骨架的研究原型，不能仅凭此仓库直接重现实验或替代临床判断。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PsychFound Summary

### Problem and Motivation

Psychiatric care is constrained by workforce shortages and experience-dependent decisions. The paper argues that patient-facing mental-health LLMs do not align with clinician workflows spanning diagnosis, treatment planning and longitudinal management. The local Nature HTML conversion contains the abstract and figure captions, but the subscription-only Methods/Results text is unavailable; numerical details below are therefore limited to claims explicitly present in the abstract/captions.

### Proposed Technology

PsychFound is a clinician-oriented, domain-adapted language model built around psychiatric professional knowledge, clinical reasoning and task adaptation in Chinese clinical settings. The abstract reports expert-curated psychiatric corpora plus 64,588 Chinese real-world EHRs, a 7B model, three development phases, and support for diagnosis, treatment planning and longitudinal management. The linked repository exposes a practical SFT plus GRPO training pipeline: clinical records are read as ShareGPT pairs, prompts are task-specific, reasoning is elicited in `<think>` and `<answer>` tags, and rewards combine format, reasoning and answer accuracy.

### Evaluation

The abstract reports three professional-knowledge assessments, five PsychBench clinical-task benchmarks, comparisons against 22 LLMs, a two-arm prospective study, and a reader study of 60 psychiatrists (20 residents, 20 attendings and 20 seniors). It states that PsychFound led overall benchmark performance; residents assisted by PsychFound had higher consultation quality and diagnostic accuracy, more appropriate medication selection, and lower documentation time (all *P* < 0.01); and reader-study reasoning matched attending psychiatrists. Local figures provide visual support for benchmark, ablation, prospective and reader-study comparisons. Public PsychBench data and the PsychFound repository are available; PsychClinical EHRs and prospective data are controlled-access.

### Reproducibility

Reproducibility is **3/5 (medium)**. The code snapshot is linked by the paper and contains testable data validation, prompt construction, SFT/GRPO training, reward calculation and adapter merging. Exact data curation, full three-phase schedule, 7B checkpoint, clinical integration service, prospective cohort analysis and private EHRs are not present in the inspected workspace. Claims about those components are explicitly marked Partial or Not found in `doc_code.md` and `doc_method.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
