---
layout: default
permalink: /paper-atlas/janus-pro-cxr-0cef8f59/
title: "Janus-Pro-CXR"
nav: false
description: "Janus-Pro-CXR 的输入是一张胸部 X 光片（临床试验阶段还把关键病史写入提示词），输出是包含 FINDINGS 与 IMPRESSION 的放射学报告。它不是只判断“有无肺炎”的分类器，而要同时完成病灶描述、解剖定位、诊断归纳和专业文本组织。 论文的重点也不只是提出一个模型：它把模型开发、回顾性评价和前瞻性人机协作串成一条证据链。Figure 1 展示了三层问题：先在 MIMIC-CXR 与中国 27 家医院数据上微调；"
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
      <span>Representation Models</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>Janus-Pro-CXR</h1>
    <p>From Bench to Bedside: A DeepSeek-Powered AI System for Automated Chest Radiograph Interpretation in Clinical Practice</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-72680-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Janus-Pro-CXR 中文方法解读：从通用视觉语言模型到胸片报告协作系统

### 1. 这项工作真正解决什么问题

Janus-Pro-CXR 的输入是一张胸部 X 光片（临床试验阶段还把关键病史写入提示词），输出是包含 `FINDINGS` 与 `IMPRESSION` 的放射学报告。它不是只判断“有无肺炎”的分类器，而要同时完成病灶描述、解剖定位、诊断归纳和专业文本组织。

论文的重点也不只是提出一个模型：它把模型开发、回顾性评价和前瞻性人机协作串成一条证据链。Figure 1 展示了三层问题：先在 MIMIC-CXR 与中国 27 家医院数据上微调；再用自动指标和五名放射科专家评估生成报告；最后在三家医院让初级放射科医师分别采用标准流程或 AI 辅助流程，比较报告质量和用时。

### 2. 数据与两阶段领域适配

#### 2.1 第一阶段：学习通用胸片报告能力

基础模型是 1B 参数的 Janus-Pro。论文 Supplementary Appendix 1 写明，第一阶段在清洗后的 MIMIC-CXR 上用 166,025 张图像微调 35K steps，batch size 128，使用 4 张 RTX 3090（24GB），约 72 小时。目标是建立从胸片视觉特征到英文 `FINDINGS + IMPRESSION` 的基本映射。

#### 2.2 第二阶段：适配 CXR-27 域

随后在来自中国 27 家医院的 5,267 张图像上继续微调 0.4K steps，同样 batch size 128，约 1 小时。这个阶段不仅应对成像设备和疾病构成差异，也让输出接近目标医院的报告写作风格。

Figure 2 给出了数据流：MIMIC-CXR 清洗后 167,496 张，其中 166,025 张用于微调、1,471 张用于测试；回顾性队列筛选后 6,584 例，其中 5,267 例用于第二阶段、1,317 例测试；前瞻性计划 300 例，退出 3 例后分析 297 例。这里必须区分“训练样本”“回顾性测试”和“前瞻性人机协作”，不能把 27 家医院数据全部理解为独立外部验证集。

#### 2.3 LoRA 做了什么

论文说明两阶段都使用 rank 64 的 LoRA。对被冻结的权重矩阵 $W$，LoRA 学习低秩更新：

$$
W'=W+BA,
$$

其中秩 $r=64$。这样不必更新全部 1B 参数，降低领域适配成本。但公开仓库没有训练脚本、目标层列表、LoRA alpha、dropout、优化器和学习率配置。因此“rank 64、两阶段步数与硬件”是论文证据，不是本地代码可复跑的训练配方。

### 3. 推理主链：图像怎样变成报告

#### 3.1 图像预处理

论文补充材料描述：保持长宽比缩放长边，以灰色 `(127,127,127)` 填充短边，最终得到 $384\times384$ 图像。源码 `janus/models/image_processing_vlm.py:127-192` 实现了保持比例缩放、扩展为正方形、重缩放和归一化；但其填充色来自 `image_mean * 255`，实际数值由加载 checkpoint 的 processor 配置决定。源码默认均值是 CLIP 风格数值而不是精确的 `(0.5,0.5,0.5)`，因此论文填充值与运行时配置需要分开报告。

#### 3.2 视觉理解分支

Janus 的统一架构有视觉理解和视觉生成两套分支。胸片报告任务只需要理解分支：

$$
I\xrightarrow{\text{SigLIP ViT}}F
\xrightarrow{\text{MLP projector}}E_{img}.
$$

`janus/models/clip_encoder.py:30-121` 构建默认名为 `siglip_large_patch16_384` 的视觉塔；`janus/models/projector.py:27-86` 把视觉特征映射到语言模型嵌入维度。`janus/models/modeling_vlm.py:190-260` 同时实例化理解、生成与语言模块，但 `prepare_inputs_embeds()` 在胸片推理中走 `vision_model → aligner`，再把图像嵌入替换进文本序列中的图像占位位置。VQ 生成分支存在于模型定义中，却不参与这条报告生成路径。

#### 3.3 576 个视觉 token

`VLChatProcessor` 默认把每张图展开为 576 个图像 token（`processing_vlm.py:84-118`）。对于 $384/16=24$ 的 patch 网格，$24\times24=576$，与 SigLIP patch16 配置一致。处理器把 `<image_placeholder>` 扩展成相应 token 区间，模型再用投影后的视觉特征替换这些占位嵌入。

#### 3.4 对话模板和贪心解码

公开入口 `inference.py:30-92` 的默认提示词是：

> Give a radiology report based on the chest x-ray image, including FINDINGS and IMPRESSION.

脚本将图像占位符和提示词组织为 User/Assistant 对话，加载 processor 与 checkpoint，将模型转为 bfloat16、移到 CUDA，然后调用语言模型生成：`max_new_tokens=512`、`do_sample=False`。因此当前入口是确定性的贪心解码，而不是温度采样。README 还示范把外部诊断模型的发现写入提示词，但这只是可选 prompt 注入，不是仓库内置的专家模型融合模块。

### 4. 报告如何转成可评价的疾病标签

自由文本无法直接计算 14 类疾病的 F1/AUC。论文对 MIMIC-CXR 使用 CheXbert/CheXpert 类工具，对 CXR-27 使用基于 DeepSeek 的标签器。公开 `label_with_deepseek.py:11-61` 定义 14 个 finding，通过 `deepseek-chat` 请求返回 0/1 JSON，温度为 0.1；若解析失败则全部回退为 0。

这个脚本证明了单报告标签提取路径，但它不是论文所称的完整批处理评价系统：仓库版本没有 CSV batch、增量保存、ROC/AUC、BLEU、ROUGE、RadGraph、Kappa 或统计检验代码。它还依赖外部 API、模型版本和提示词，标签误差会直接传导到 F1/AUC。

### 5. 三层验证证据应该怎样读

#### 5.1 自动指标

论文在 MIMIC-CXR 测试集报告 Macro-F1-14 34.7、Macro-F1-5 50.1、RadGraph 26.4；在 CXR-27 测试集报告 ROUGE-L 60.5、BLEU-4 44、RadGraph 61.1、Micro-F1-14 56.2、Macro-F1-14 35.1。Figure 3 的雷达图和 ROC/Kappa 面板说明评价覆盖文本相似度、实体关系和疾病识别，而非单一 BLEU。

这些指标也有边界：不同测试集使用不同自动标签器，且词面指标高不等于临床事实完全正确。补充材料显示水肿阳性样本过少，无法形成有代表性的 ROC；骨折和其他胸膜异常的 AUC/F1 较低。

#### 5.2 盲法专家回顾性评价

五名具有 8–15 年经验的放射科医师对 CXR-27 测试集随机抽取的 300 例进行盲法评价。Janus-Pro-CXR 的报告质量分为 $3.22\pm1.12$，高于 Janus-Pro 的 $1.59\pm0.62$ 和 ChatGPT 4o 的 $1.72\pm0.75$；报告一致性分为 $3.10\pm1.02$。Figure 4A 只评价风格/格式是否像真实报告，不考虑内容正确性，所以不能把“难以辨别来源”解读成诊断正确。

#### 5.3 前瞻性人机协作

297 名患者来自三家医院。六名初级放射科医师按 1:1 随机分到 AI 辅助组和标准临床流程（SCP）组；每位患者由两组不同医师独立出具报告，随后均由高级医师审阅。AI 辅助组可把模型报告作为参考并修改，而不是直接自动签发。

论文报告 AI 辅助组质量分 $4.37\pm0.50$，SCP 为 $4.11\pm0.81$；平均用时从 $146.6\pm49.8$ 秒降至 $119.4\pm45.3$ 秒，即减少 27.2 秒（18.5%）。Figure 4E–J 同时展示质量、一致性、偏好和用时。该结果支持“在这套三中心、有人复核的工作流中提供帮助”，不能外推为模型可以独立诊断或适用于所有医院。

### 6. 论文与公开代码的对应关系

| 论文要素 | 直接代码证据 | 状态 |
|---|---|---|
| 单张胸片到报告 | `inference.py:30-92` | Exact |
| 视觉塔、投影器、LLM 嵌入替换 | `modeling_vlm.py:190-260` | Exact |
| 576 图像 token | `processing_vlm.py:84-118` | Exact |
| 保比例缩放、方形填充和归一化 | `image_processing_vlm.py:127-192` | Partial；填充颜色由配置决定 |
| LoRA rank 64、两阶段训练 | 仓库无训练脚本 | Not found |
| BLEU/ROUGE/RadGraph/F1/AUC/Kappa | 仓库无完整评价脚本 | Not found |
| DeepSeek 14 类标签 | `label_with_deepseek.py:11-61` | Partial；单条 API 工具 |
| 临床交互界面和医院工作流 | 仓库无 UI/HIS 集成 | Not found |

公开仓库还包含较完整的上游 Janus 架构源码，但不能据此声称 Janus-Pro-CXR 的 LoRA 训练实现已经开放。README 提供两个 Hugging Face checkpoint 名称和推理命令；checkpoint 权重本身不在工作区内，因此本次没有实际执行 GPU 推理。

### 7. 临床使用边界

- 论文明确采用高级医师复核后才正式发布报告；模型输出不应绕过临床审核。
- 模型对细微或复杂征象、低频类别表现较弱，训练集疾病构成不均衡。
- 微调阶段没有纳入完整病史与既往影像；前瞻性阶段只是把关键病史写入 prompt。
- 前瞻性验证只有三家中国医院、297 名患者，跨国家、设备、人群和语言的泛化仍需验证。
- 自动标签器与外部 DeepSeek API 会引入版本、隐私和可复现性风险；临床报告不应在未完成合规评估时发送到外部服务。
- 公开代码没有训练、统计评价、批量推理、UI 或医院系统集成，因此“论文结果可理解”不等于“完整研究可一键复现”。

一句话概括：Janus-Pro-CXR 的价值来自低成本的两阶段领域适配以及把模型放进有人复核的临床协作试验；公开代码可靠覆盖的是视觉语言推理主链，而不是整套训练与临床验证工程。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Janus-Pro-CXR Summary

### Motivation & Novelty

#### Biological Problem

Radiologist shortages severely limit access to chest X-ray (CXR) interpretation globally — 1.9 per million in low-income countries vs. 97.9 in high-income countries. CXR is the most fundamental diagnostic imaging tool for detecting pneumonia, lung cancer, tuberculosis, and cardiac disease. Automated report generation could democratize radiology access and reduce radiologist workload.

#### Why Existing Methods Fall Short

| Method | Limitation |
|---|---|
| **Scratch-built CXR models** (Chen et al. 2020 *EMNLP*; Miura et al. 2020 *arXiv*; Endo et al. 2021 *PMLR*) | Low data efficiency, modal fragmentation, poor transfer to new populations |
| **General VLMs (ChatGPT 4o, GPT-4V)** | Not CXR-specialized; English-only; proprietary; low RadGraph/F1 scores even with 200B parameters |
| **Medical VLMs (LLaVA-Med 2023 *arXiv*, HealthGPT 2025 *arXiv*, FlamingoCXR 2025 *Nat Med*)** | Larger models (3-12B); lower CXR-specific metrics; no prospective clinical validation |
| **Existing CXR AI systems** | Evaluated only on retrospective data with automated metrics; no prospective randomized clinical trial |

#### Unique Contributions

1. **Lightweight CXR specialist**: 1B parameter model achieves SOTA on both MIMIC-CXR and CXR-27 test sets, outperforming models with 3–200B parameters. Runs in 1-2 seconds on a laptop GPU.

2. **Two-stage domain adaptation**: Stage 1 on MIMIC-CXR for general CXR diagnostics; Stage 2 on 5,267 images from 27 Chinese hospitals for style/terminology adaptation. Only ~6,000 images needed for full domain adaptation.

3. **Prospective clinical validation**: First prospective randomized trial (NCT06874647) of an AI report generation system. 297 patients across 3 hospitals.

4. **Practical results**: AI assistance improves junior radiologist report quality (4.37 vs 4.11, P<0.001), reduces reading time 18.5%, and AI-assisted reports are preferred by senior experts in 52.7% of cases.

---

### Method Overview

Janus-Pro-CXR is Janus-Pro-1B (DeepSeek's unified multimodal LLM) fine-tuned for CXR report generation using Low-Rank Adaptation (LoRA, rank=64).

**Input**: CXR image + optional clinical history text
**Output**: Structured radiology report (FINDINGS + IMPRESSION sections)
**Architecture**: SigLIP ViT (understanding encoder) → MLP projector → LLaMA-based LLM
**Training**: Two-stage LoRA fine-tuning — Stage 1 (35K steps on MIMIC-CXR 166K images), Stage 2 (400 steps on CXR-27 5,267 images)
**Inference**: Greedy decoding, max 512 tokens, ~1-2s on RTX 4060 8GB

The key algorithmic insight is that **domain-specific fine-tuning with domain-appropriate evaluation** matters more than model scale. Chinese hospital CXR reports have different style, terminology, and disease prevalence than US MIMIC-CXR data. The authors also built a custom DeepSeek-based labeling tool (vs. CheXpert) to accurately evaluate Chinese-language reports — achieving F1 > 0.95 across 13/14 conditions vs. CheXpert's F1 often < 0.2 on the same data.

See `doc_method.md` for full algorithm walkthrough and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Role | Size | Source |
|---|---|---|---|
| MIMIC-CXR | Stage 1 training | 166,025 images | US ICU, English reports |
| MIMIC-CXR test | Evaluation | 1,471 images | US ICU, English |
| CXR-27 training | Stage 2 fine-tuning | 5,267 images | 27 Chinese hospitals |
| CXR-27 test | Retrospective evaluation | 1,317 images | 27 Chinese hospitals |
| Prospective trial | Primary clinical outcomes | 297 patients | 3 Chinese hospitals |

#### Automated Metrics (Retrospective)

**MIMIC-CXR test set** (vs. best prior open-source, CheXbert labeling):
- Macro-avg F1-14: **34.7** (best) vs CvT-21DistillGPT2 28.2
- Macro-avg F1-5: **50.1** (best) vs RGRG 42.7
- RadGraph F1: **26.4** (best open-source) vs Med-PaLM M (12B) 25.2
- GPT-4V comparison: RadGraph only 13.2 vs our 26.4

**CXR-27 test set** (DeepSeek labeling):
- ROUGE-L: **60.5** (best) vs HealthGPT 19.2
- BLEU-4: **44** (best) vs HealthGPT 5.1
- RadGraph F1: **61.1** (best) vs HealthGPT 21.1
- Macro-avg F1-14: **35.1** (best) vs HealthGPT 13.6

**Stage 2 impact**: Zero-shot vs. fine-tuned on CXR-27: RadGraph 16.1 → 61.1 (+280%), ROUGE-L 22.0 → 60.5 (+175%).

#### Diagnostic Performance (AUC)

8 conditions achieved AUC > 0.8 on CXR-27:
- Support Devices: 0.967 (F1: 0.736)
- Pleural Effusion: 0.927 (F1: 0.652)
- Pneumothorax: 0.916 (F1: 0.268)
- Atelectasis: 0.872, Consolidation: 0.846, Cardiomegaly: 0.811, Lung Opacity: 0.803

Limitations: Fracture (AUC 0.653), Pleural Other (0.687), and Edema (excluded — only 1 positive case) remain challenging.

#### Clinical Evaluation (Retrospective, N=300 from CXR-27 test)

Expert evaluation by 5 radiologists (8-15 years experience), blinded to report source:
- Report quality (5-point Likert): 3.22 ± 1.12 vs Janus-Pro 1.59 vs ChatGPT 4o 1.72
- RADPEER agreement: 3.10 ± 1.02 vs Janus-Pro 1.67 vs ChatGPT 4o 1.75
- Pairwise preference: 15.1% (≥3/5 experts prefer AI over published) vs Janus-Pro 2.7%

Figure 4B-D show violin/bar plots confirming these significant differences.

#### Prospective Clinical Trial (NCT06874647, N=297 patients)

**Primary outcomes** (junior radiologist with AI assistance vs. standard clinical practice):
- Report quality: **4.37 ± 0.50 vs 4.11 ± 0.81** (Δ=0.24, P<0.001, 95% CI: 0.160–0.328)
- Agreement (RADPEER): 4.27 ± 0.60 vs 4.09 ± 0.86 (P<0.001)
- Pairwise preference: **52.7% of AI-assisted reports preferred** by ≥3/5 experts

**Secondary outcomes**:
- Reading time: 119.4 ± 45.3 vs 146.6 ± 49.8 seconds (**18.5% reduction**, P<0.001)
- Complex cases (≥3 findings): 21.5% reduction (P<0.001)
- Pneumonia detection: AI-assisted group diagnosed 55.2% vs 36.4% (P<0.001) — AI improves diagnostic confidence for uncertain cases

---

### Reproducibility Rating: 2/5

**Justification**: The published code includes only inference functionality. Key components are absent:
- ❌ Training/fine-tuning scripts (Stage 1 and Stage 2)
- ❌ LoRA configuration details (which layers, dropout, alpha)
- ❌ Evaluation scripts (RadGraph, CheXbert F1, BLEU, ROUGE)
- ❌ The prospective clinical trial software interface (Gradio UI in Supp Fig 3)
- ✓ Inference code is functional and well-documented
- ✓ Model checkpoints available on HuggingFace (`ZrH42/Janus-Pro-CXR-Zero`, `ZrH42/Janus-Pro-CXR-Final`)
- ✓ MIMIC-CXR test set is publicly available (requires PhysioNet credentials)
- ✓ Detailed training description in Supplementary Appendix 1
- ⚠ CXR-27 data (27 Chinese hospitals) is not publicly available; available "upon reasonable request" only

**Practical notes**:
- Install: Python 3.10 + PyTorch 2.2.1 + CUDA 11.8 + `pip install -r requirements.txt`
- Inference requires ~4-6GB VRAM (RTX 4060 or better)
- `transformers` version pinning is strict: 4.41.2–4.49.0, excluding 4.46/4.47/4.48
- DeepSeek labeler requires a valid DeepSeek API key (placeholder `sk-***` in repo)
- To reproduce training results, one would need to: obtain MIMIC-CXR (public), configure LoRA training with `peft`, follow Supp App 1 description with likely trial-and-error on hyperparameters not fully specified

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
