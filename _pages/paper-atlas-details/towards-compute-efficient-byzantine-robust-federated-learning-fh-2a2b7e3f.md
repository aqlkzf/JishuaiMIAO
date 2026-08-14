---
layout: default
permalink: /paper-atlas/towards-compute-efficient-byzantine-robust-federated-learning-fh-2a2b7e3f/
title: "Towards_compute_efficient_Byzantine_robust_federated_learning_FHE"
nav: false
wide: true
description: "联邦学习中的恶意客户端可以投毒模型更新；同时，明文更新或中间模型可能泄露训练样本。Lancelot 将拜占庭鲁棒聚合与 CKKS 全同态加密结合，使服务器在密文上计算距离和聚合。 补充材料描述了九个通信步骤、加密距离列表和加密 mask 的通信成本。mask 大小主要由客户端数决定，而模型密文大小由模型参数量决定。 直接在 CKKS 密文上排序会产生很深的乘法电路。"
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
      <span>Computational Tools</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>Towards_compute_efficient_Byzantine_robust_federated_learning_FHE</h1>
    <p>Towards compute-efficient Byzantine-robust federated learning with fully homomorphic encryption</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01107-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Towards_compute_efficient_Byzantine_robust_federated_learning_FHE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/kimandrik/HEAAN" target="_blank" rel="noopener noreferrer" aria-label="Open code for Towards_compute_efficient_Byzantine_robust_federated_learning_FHE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Lancelot 方法说明

### 解决什么问题

联邦学习中的恶意客户端可以投毒模型更新；同时，明文更新或中间模型可能泄露训练样本。Lancelot 将拜占庭鲁棒聚合与 CKKS 全同态加密结合，使服务器在密文上计算距离和聚合（主文摘要，`paper source/nature_html/paper.md:9-12`）。

### 核心流程

```text
客户端本地训练
  -> 加密模型更新并发送到计算服务器
  -> 服务器计算密文距离
  -> KGC 接收密文距离列表并生成密文 mask
  -> 服务器用 mask 隐藏排序/筛选，执行 Krum、Multi-Krum 或 Median
  -> 密文聚合模型降模后交给 KGC 解密
  -> 客户端收到新的全局模型
```

补充材料描述了九个通信步骤、加密距离列表和加密 mask 的通信成本（`supplement/supplement.md:177-189,219-238`）。mask 大小主要由客户端数决定，而模型密文大小由模型参数量决定。

### 为什么更快

直接在 CKKS 密文上排序会产生很深的乘法电路。Lancelot 用 mask-based encrypted sorting 隐藏距离顺序，并结合三类优化：延迟重线性化（lazy relinearization）、动态 hoisting，以及 GPU 上的 RNS/double-CRT 和 Karatsuba 密文乘法。补充消融实验显示延迟重线性化在 Krum 和 Median 上约有 1.85x/1.98x 的收益，动态 hoisting 还会进一步降低运行时间（`supplement/supplement.md:617-630`）。

### 实验结论

在 12 个 MedMNIST 数据集上，Krum（10 客户端）、Multi-Krum（50）和 Median（100）场景的加速比为 15.75x-25.60x；ImageNet 和 MosMedData 的加速比分别为 19.03x 和 20.50x（`supplement/supplement.md:44-160`）。外部梯度反演/后门攻击在密文步骤不能恢复可用数据，且 Byzantine 比例 0.1 时密文训练曲线接近明文基线（`supplement/supplement.md:314-350,424-426`）。

### 复现边界

论文链接的 Lancelot GitHub/Zenodo 代码无法匿名下载。HEAAN 的 `Scheme::mult` 可以验证一般的密文乘法和重线性化（`code/HEAAN/HEAAN/src/Scheme.cpp:368-420`），但不能验证 Lancelot 的 mask 排序、FL 编排、GPU kernel 或论文基准。精确的 CKKS 参数、训练超参数和排序公式在可访问范围内 **Not found**。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Lancelot Summary

### Problem

Federated learning needs robust aggregation against Byzantine/poisoning clients, but transmitting or exposing model updates can leak training data. Existing Byzantine-robust FHE systems provide security at prohibitive cost, especially for encrypted distance sorting and ciphertext multiplication. The paper introduces **Lancelot**, a CKKS-based Byzantine-robust FL framework with mask-based encrypted sorting, lazy relinearization, dynamic hoisting and GPU acceleration (`paper source/nature_html/paper.md:9-12`).

### Method

Clients train locally and send encrypted updates to a computation server. The server computes encrypted distances; a key-generation center returns an encrypted mask used for hidden sorting/selection, after which Krum, Multi-Krum or Median aggregation is performed on ciphertexts. The aggregate is modulus-reduced, decrypted at the KGC and distributed as the next global model. The accessible supplement provides the nine-step communication flow and CKKS/GPU arithmetic details (`supplement/supplement.md:177-189,732-819`).

### Evidence and Results

Experiments cover MNIST, FMNIST, CIFAR-10, SVHN, 12 MedMNIST datasets, ImageNet and MosMedData. In Supplementary Table 1, Lancelot is 15.75x-25.60x faster than OpenFHE across Krum (10 clients), Multi-Krum (50) and Median (100), while retaining comparable accuracy (`supplement/supplement.md:44-118`). Real-world ImageNet/MosMedData speedups are 19.03x/20.50x, and the edge testbed reduces CIFAR-10 server computation from 10,322.21 s to 501.35 s (`supplement/supplement.md:88-160,207-245`). Attack studies report failed reconstruction in ciphertext settings and plaintext-like convergence under a 0.1 Byzantine ratio (`supplement/supplement.md:314-350`).

### Reproducibility

The primary Lancelot GitHub/Zenodo implementation was unavailable to anonymous cloning. The workspace therefore contains only supporting HEAAN and Fashion-MNIST snapshots. HEAAN verifies generic CKKS multiplication/relinearization (`code/HEAAN/HEAAN/src/Scheme.cpp:368-420`) but not Lancelot's encrypted sorting, masking, GPU kernels, FL orchestration or benchmarks. Exact cryptographic parameters, training configuration and sorting equations are **Not found** in the accessible paper/supplement scope. Reproducibility rating: **2/5**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
