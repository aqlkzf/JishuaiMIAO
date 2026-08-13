---
layout: default
permalink: /paper-atlas/ctpnet-8a756dd5/
title: "cTPnet"
nav: false
description: "很多单细胞研究只有 scRNA-seq，没有同一个细胞上的表面蛋白测量。但在免疫学、造血、肿瘤研究里，CD3、CD4、CD8、CD19、CD34、CD38 这类表面蛋白往往比对应 RNA 更直接地定义细胞类型、分化阶段和治疗靶点。论文提出的问题是：能否利用已有 CITE-seq/REAP-seq 这类“同一细胞同时测 RNA 和表面蛋白”的数据，训练一个模型，把新的 scRNA-seq-only 数据映射成表面蛋白丰度 。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Communications · 2020</span>
    </div>
    <h1>cTPnet</h1>
    <p>Surface protein imputation from single cell transcriptomes by deep neural networks</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/zhouzilu/cTPnet" target="_blank" rel="noopener noreferrer" aria-label="Open code for cTPnet">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## cTP-net 方法中文解释

### 这篇论文要解决什么问题

很多单细胞研究只有 scRNA-seq，没有同一个细胞上的表面蛋白测量。但在免疫学、造血、肿瘤研究里，CD3、CD4、CD8、CD19、CD34、CD38 这类表面蛋白往往比对应 RNA 更直接地定义细胞类型、分化阶段和治疗靶点。论文提出的问题是：能否利用已有 CITE-seq/REAP-seq 这类“同一细胞同时测 RNA 和表面蛋白”的数据，训练一个模型，把新的 scRNA-seq-only 数据映射成表面蛋白丰度 (`paper.md:12-21`)。

### 方法总览

cTP-net 的核心是两步：

```text
原始 UMI RNA count
  -> 过滤低质量基因/细胞
  -> SAVER-X 去噪，估计更接近真实表达的 RNA count
  -> Seurat LogNormalize，得到神经网络输入 X
  -> 多分支深度神经网络 F
  -> 每个细胞的多个表面蛋白相对丰度
```

第一步 SAVER-X 是为了减少 scRNA-seq 的 dropout 和测量噪声。第二步才是 cTP-net 本身：输入一个细胞的全转录组特征，输出多个表面蛋白的相对丰度 (`paper.md:27-41`)。论文强调，单纯看某个蛋白对应基因的 RNA 往往不够，因为 RNA 到表面蛋白之间还经过转录后调控、翻译、转运、蛋白修饰等过程，而且这些过程依赖细胞状态和其他基因活动 (`paper.md:30-41`)。

### 输入和输出如何定义

论文先对 denoised RNA count \(\Lambda\) 做归一化：

$$X_{ij} = \log \left( {\frac&#123;&#123;{\mathrm{\Lambda }}_{ij} \ast 10,000}}&#123;&#123;m_j}}} \right)$$

其中 \(\Lambda_{ij}\) 是第 \(j\) 个细胞里第 \(i\) 个基因的 SAVER-X 去噪 count，\(m_j\) 是该细胞所有分子的总和。这个 \(X\) 是神经网络输入 (`paper.md:161-169`)。

蛋白端不用原始 ADT count 直接训练，而是把一个细胞的 ADT 向量 \(\mathbf{p}_c\) 转成相对丰度：

$$y_c = \left[ {\ln \left( {\frac&#123;&#123;p_{1c}}}&#123;&#123;g\left( &#123;&#123;\mathbf{p}}_c} \right)}}} \right),\ln \left( {\frac&#123;&#123;p_{2c}}}&#123;&#123;g\left( &#123;&#123;\mathbf{p}}_c} \right)}}} \right) \ldots {\mathrm{ln}}\left( {\frac&#123;&#123;p_{dc}}}&#123;&#123;g({\mathbf{p}}_c)}}} \right)} \right]$$

这里 \(g(\mathbf{p}_c)\) 是该细胞所有 ADT count 的几何平均。论文说，用这个相对丰度作为响应变量比直接用 protein barcode count 效果更好 (`paper.md:169-177`)。

### 网络结构

论文中的最终网络是一个 multiple-branch DNN：

```text
D 个基因输入
  -> 共享全连接/ReLU: 1000
  -> 共享瓶颈层/ReLU: 128
  -> 每个蛋白一条分支:
       全连接/ReLU: 64
       全连接/identity: 1
  -> d 个蛋白预测值
```

前两层共享，用来学习细胞类型、细胞状态、细胞周期等对多个蛋白都有用的特征；之后每个蛋白走自己的 64 节点分支，再输出该蛋白丰度 (`paper.md:180-191`)。Supplementary Figure 1 也画出了 128 节点共享瓶颈层再分支的结构，Supplementary Table 5 说明最终模型使用 128 bottleneck (`SUPP_MD:10-27`, `SUPP_MD:702-704`)。

训练目标是 L1 损失：

$$\mathop{\mathrm{argmin}}_{F} \left| {\mathbf{Y}} - F ( {\mathbf{X}} ) \right|_{1}$$

论文写明用 Adam 优化，学习率 `10e-5`，交叉验证得到 139 个 epoch (`paper.md:186-191`)。

### 怎么评估

论文不是只做普通随机验证，而是设置了几个更接近真实迁移场景的测试：

| 场景 | 含义 | 证据 |
|---|---|---|
| random holdout | 90% 细胞训练，10% 细胞测试；每个细胞类型在训练和测试里都有 | `paper.md:47-47`, `paper.md:194-197` |
| out-of-cell-type | 每次拿掉一个细胞类型，用其他细胞类型训练，再预测被拿掉的类型 | `paper.md:53-56`, `paper.md:200-200` |
| cross-tissue | PBMC 训练预测 CBMC，或反过来 | `paper.md:67-70` |
| cross-technology | CITE-seq 和 REAP-seq 之间迁移 | `paper.md:73-73` |
| Seurat v3 对比 | 与 Seurat v3 anchor transfer 比较 | `paper.md:76-84`, `paper.md:230-233` |

跨数据集预测时，不同实验的基因集合不完全一致。论文做法是：训练数据里有而测试数据里没有的基因填 0，预测后只比较两个数据集共有的蛋白 (`paper.md:203-203`)。这个逻辑在 R 包的 preprocessing 代码中也能看到：加载 shared-gene 列表，按 shared genes 取子集，缺失值填 0 (`cTPnet_repo/R/cTPnet_preprocess.R:1-44`)。

### 模型解释

为了理解网络学到了什么，论文设计了 permutation-based interpolation。基本思想是：先计算原始输入 \(X\) 下的误差，再随机打乱一批基因在细胞之间的表达，得到 \(X^{perm}\)，看误差变化：

$$\Delta_{gs}=|\epsilon^{orig}-\epsilon^{perm}|$$

如果打乱某批基因后误差明显变化，说明这批基因对某个蛋白预测有影响。论文设置 gene batch size 为 100，500 个 epoch，并且可以在所有细胞上做，也可以只在某个细胞类型里做，从而区分“细胞类型标记基因”和“细胞类型内部影响蛋白状态的基因” (`paper.md:206-227`)。

### 应用结果

在人类细胞图谱 HCA 的 CBMC/BMMC 数据中，论文用联合训练的模型预测 24 个表面蛋白。图 3 显示，imputed protein 比 cognate RNA 更容易解释 T 细胞、B 细胞、NK 细胞、单核细胞和 precursor 状态；例如 CD4/CD8 区分 T 细胞，CD45RA/CD45RO 区分 naive/memory T 细胞，CD56/CD16 在 NK 细胞中呈相反梯度 (`paper.md:94-114`; 本地 `figure_03.png` 已检查)。

在 AML 数据中，论文把正常骨髓细胞和 AML malignant cells 放到 imputed protein 空间中，看到了从 CD34+ progenitor 到 CD38/CD123 transition，再到 CD11c/CD14 mature monocyte-like 的髓系分化结构。不同 AML 样本的 malignant cells 落在不同区域，因此可以按分化阶段解释肿瘤异质性 (`paper.md:117-137`; 本地 `figure_04.png` 已检查)。

### 代码能复现到什么程度

本 workspace 中的代码是 `zhouzilu/cTPnet` R 包快照，commit 为 `6bd1565db65b321e8f972f9b23b01c05d0e87781`。它主要提供推理入口：

- `cTPnet()` 根据输入类型做 preprocessing，然后通过 `reticulate` 调用外部 Python `ctpnet` predictor (`cTPnet_repo/R/cTPnet.R:12-37`)。
- preprocessing 会按 12 或 24 个蛋白模型加载 shared genes，并把缺失基因填 0 (`cTPnet_repo/R/cTPnet_preprocess.R:1-44`)。
- postprocessing 会把每个蛋白预测值减去该蛋白的最小值，再写回 Seurat assay 或 matrix (`cTPnet_repo/R/cTPnet_postprocess.R:1-18`)。

但是，这个 R repo 快照不是完整论文复现包。SAVER-X、Python predictor 和模型权重需要外部安装或下载 (`cTPnet_repo/README.md:13-35`, `cTPnet_repo/vignette/cTPnet_vignette_v3.Rmd:42-63`)。仓库中有一个 released training script，但它和论文最终设置不完全一致：代码里第二个共享层是 256，不是论文的 128；用 `MSELoss`，不是 L1；Adam 学习率是 `0.001` 且带 `amsgrad=True` 和 `weight_decay=0.001`；最大 200 epoch 并带 early stopping，而论文写的是 Adam `10e-5`、139 epochs (`paper.md:180-191`; `cTPnet_repo/extdata/training_05152020.py:124-155`, `cTPnet_repo/extdata/training_05152020.py:160-239`)。

另外，本快照没有找到 Seurat v3 benchmark 脚本、interpolation 分析代码、HCA 下游分析脚本和 AML 下游分析脚本。因此这些结果在本文档中按“论文证据”解释，不升级为“代码已验证可复现”。

### 适用范围和限制

论文明确说，cTP-net 目前只在 UMI-based count 输入上测试，没有测试 TPM/RPKM 表达输入；模型训练在免疫/造血相关细胞上，尚未验证对完全无关细胞类型的泛化能力 (`paper.md:149-149`)。因此，cTP-net 更适合作为“利用已有多组学免疫数据给相关 scRNA-seq 数据补充表面蛋白特征”的方法，而不是任意组织、任意蛋白面板上的通用蛋白预测器。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## cTP-net Summary

### What Problem It Solves

Single-cell RNA-seq is widely available, but matched surface-protein measurements are often missing even when surface markers are the most interpretable features for immune cell state, cell type, and therapeutic targeting (`paper.md:18-21`). cTP-net asks whether existing paired CITE-seq/REAP-seq resources can teach a model to impute surface-protein abundance from scRNA-seq-only cells (`paper.md:12-12`, `paper.md:21-21`).

### Main Idea

cTP-net is a transfer-learning pipeline with two steps: denoise raw scRNA-seq counts with SAVER-X, then feed the denoised expression profile into a multiple-branch deep neural network that predicts a vector of relative surface-protein abundances (`paper.md:27-41`). The network has shared layers that encode transcriptome-wide cell-state information, then protein-specific branches that emit one abundance per marker (`paper.md:180-191`). The paper specifies normalized denoised RNA input \(X\), relative ADT response \(y_c\), a `D -> 1000 -> 128 -> 64 -> 1` branch architecture, and an L1 objective optimized with Adam (`paper.md:164-191`; `SUPP_MD:10-27`, `SUPP_MD:702-704`).

### Evaluation

The paper evaluates cTP-net on paired immune-cell datasets under random holdout, out-of-cell-type, cross-tissue, and cross-technology settings (`paper.md:47-73`, `paper.md:194-203`). Against raw RNA and denoised RNA proxies, cTP-net gives higher correlation with measured protein levels for many proteins, and it remains informative when the predicted cell type is excluded from training (`paper.md:47-56`). Compared with Seurat v3 anchor transfer, cTP-net is reported as comparable in ordinary validation but stronger in the out-of-cell-type setting, where nearest-neighbor anchoring struggles if the training data lack close cell-type counterparts (`paper.md:76-84`, `paper.md:230-233`).

The paper also introduces a permutation-based interpolation analysis to identify genes that influence each protein prediction and a bottleneck-layer analysis showing cell-type and protein-gradient structure (`paper.md:85-91`, `paper.md:206-227`; `SUPP_MD:544-548`, `SUPP_MD:694-700`).

### Applications

For Human Cell Atlas CBMC and BMMC scRNA-seq-only data, the paper uses a jointly trained model to impute 24 protein markers. The imputed markers provide interpretable T-cell, B-cell, NK-cell, monocyte, and precursor-state patterns that are clearer than cognate RNA expression for several markers (`paper.md:94-114`, `paper.md:236-242`; local `figure_03.png` inspected).

For AML, the paper applies imputed surface proteins to place malignant cells along a myeloid differentiation trajectory. The imputed markers distinguish progenitor-like, transition, and monocyte-like regions and separate patient samples by apparent differentiation stage (`paper.md:117-137`; local `figure_04.png` inspected).

### Reproducibility From This Workspace

The acquired code is the public R package snapshot `zhouzilu/cTPnet` at commit `6bd1565db65b321e8f972f9b23b01c05d0e87781`. It implements an inference wrapper that preprocesses Seurat/matrix/dataframe input, calls an external Python `ctpnet` predictor through `reticulate`, and postprocesses predictions into Seurat or matrix output (`cTPnet_repo/R/cTPnet.R:12-37`). The preprocessing code aligns inputs to stored shared-gene lists and zero-fills missing genes, matching the paper's cross-dataset feature-space handling (`paper.md:203-203`; `cTPnet_repo/R/cTPnet_preprocess.R:1-44`).

The repo does **not** fully reproduce the paper workflow by itself. SAVER-X and the Python predictor/weights are external to this acquired snapshot (`cTPnet_repo/README.md:13-35`; `cTPnet_repo/vignette/cTPnet_vignette_v3.Rmd:42-63`). The released training script is partial and diverges from Methods: it uses a 256-node second shared layer, `MSELoss`, Adam at `0.001` with weight decay/AMSGrad, up to 200 epochs, and early stopping, whereas the paper reports a 128-node bottleneck, L1 loss, Adam `10e-5`, and 139 epochs (`paper.md:180-191`; `cTPnet_repo/extdata/training_05152020.py:124-155`, `cTPnet_repo/extdata/training_05152020.py:160-239`). Seurat v3 benchmark scripts, interpolation code, and HCA/AML downstream workflows were not found in the checked repo files.

### Limitations

The paper states that cTP-net was tested on UMI-based count input, not TPM/RPKM expression, and that generalization to unrelated, non-hematopoietic cell types was not evaluated (`paper.md:149-149`). The public R repo is useful for applying a pretrained cTP-net model if external Python package/weights and denoising are available, but it should not be treated as a complete training/benchmark/application reproduction package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
