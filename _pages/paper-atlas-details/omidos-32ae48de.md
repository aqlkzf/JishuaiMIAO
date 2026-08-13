---
layout: default
permalink: /paper-atlas/omidos-32ae48de/
title: "OmiDos"
nav: false
wide: true
description: "单细胞 RNA 测序回答“哪些基因正在表达”，单细胞 ATAC 测序回答“哪些染色质区域处于开放状态”。二者有关联，却不会完全同步：染色质先开放、转录随后发生，转录因子活性又可能处在另一时间尺度；而单细胞实验只拍下一张瞬时快照。因此，同一个细胞状态中天然混合了两类信息： 私有信号（private）：只在 RNA 或 ATAC 中明显的模态特征； 共享信号（shared）：跨模态一致、反映共同调控程序的特征。"
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
      <span>PNAS · 2026</span>
    </div>
    <h1>OmiDos</h1>
    <p>Orthogonal disentanglement of single-cell multi-omics reveals private and shared drivers of tissue development and pathogenesis</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/fanyi21/OmiDos" target="_blank" rel="noopener noreferrer" aria-label="Open code for OmiDos">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## OmiDos 方法详解：把“模态特有信号”和“跨模态共享信号”分开学习

### 一、论文想解决什么问题？

单细胞 RNA 测序回答“哪些基因正在表达”，单细胞 ATAC 测序回答“哪些染色质区域处于开放状态”。二者有关联，却不会完全同步：染色质先开放、转录随后发生，转录因子活性又可能处在另一时间尺度；而单细胞实验只拍下一张瞬时快照。因此，同一个细胞状态中天然混合了两类信息：

- **私有信号（private）**：只在 RNA 或 ATAC 中明显的模态特征；
- **共享信号（shared）**：跨模态一致、反映共同调控程序的特征。

多数整合方法主要追求一个联合低维空间。论文认为，这样容易把真正有意义的模态差异当作噪声抹掉，也可能让私有变化污染共享表示（`paper source/pnas_2519870123/paper.md:21-29`）。OmiDos 的核心选择不是“把两个模态混得越像越好”，而是先把私有与共享成分显式拆开，再分别解释。

### 二、与已有方法相比，新意在哪里？

论文比较了 GLUE、DeepMAPS、LIGER、MultiVI、iNMF、Harmony、Scanpy 和 Seurat 等方法。它们分别采用图链接、深度生成模型、矩阵分解、批次校正或常规单细胞整合，但主输出通常仍是联合表示。OmiDos 的差异在于：

1. 为 RNA、ATAC 各建一个私有编码器，同时建一个共享编码器；
2. 用正交约束迫使私有空间和共享空间少重叠；
3. 同时输出 PREM（private representation）和 SHEM（shared representation），让研究者比较“模态特有驱动”和“共同驱动”；
4. 论文还提出面向非配对数据的 NCE + 对抗域适配，以及面向批次数据的 CVAE + 解码器层 MMD。

需要提前说明：本地代码能验证第 1–3 点的核心实现，但没有找到第 4 点中 NCE/对抗与 CVAE/MMD 的明确实现。

### 三、输入、输出与整体流程

**输入**是 scRNA 计数矩阵和 scATAC 峰矩阵，可以来自配对细胞，也可以来自同一群体但没有一一对应关系的细胞；论文还考虑多批次数据。代码中 RNA 会过滤细胞/基因、保留原始计数、按细胞归一化、计算 size factor 并做 `log1p`；ATAC 会二值化、过滤并选择高变特征（`OmiDos/OmiDos/dataset.py:100-127,283-314`）。

**输出**包括 RNA-PREM、ATAC-PREM、RNA-SHEM、ATAC-SHEM。代码提供四个独立提取接口（`OmiDos/OmiDos/Module_OmiDos.py:486-588`）。

```text
RNA ──预处理──┬── RNA 私有编码器 ── RNA-PREM ─┐
              └── RNA 前置层 ─┐               │
                              ├── 共享编码器 ──┼── SHEM
ATAC ─预处理──┬── ATAC 前置层 ┘               │
              └── ATAC 私有编码器 ─ ATAC-PREM ┘

训练约束：
  私有/共享重建 + 私有/共享正交 + 模态分类
  论文扩展：非配对 NCE/对抗；批次 CVAE/MMD
```

直观地说，PREM 像是每种组学自己的“方言”，SHEM 像是两种组学都能表达的“共同语义”。正交约束要求方言和共同语义尽量不要重复编码同一信息。

### 四、三个编码器如何工作？

论文把共享编码器写作 $E_S(x_{n,m};\omega_S)$，把 RNA 与 ATAC 私有编码器写作 $E_{rna}(x_{n,rna};\omega_{rna})$ 和 $E_{atac}(x_{n,atac};\omega_{atac})$（`paper.md:134-138`）。

代码中：

- `private_RNA_encoder` 和 `privat_enc_mu` 生成 RNA 私有潜变量；
- `private_ATAC_encoder` 和 `private_ATAC_sample` 生成 ATAC 私有高斯潜变量；
- RNA 与 ATAC 先分别经过 `layer_RNA`、`layer_ATAC`，再进入同一个 `shareEncoder`；
- `_enc_mu` 产生 RNA 共享潜变量，`sample` 产生 ATAC 共享潜变量；
- 两套解码器分别还原 RNA 与 ATAC（`Module_OmiDos.py:181-286`）。

这种结构并不意味着 RNA 与 ATAC 从输入开始共享全部参数。它先用模态前置层把维度对齐，再共享后续网络，因而允许输入统计分布不同。

### 五、重建损失：为什么 RNA 和 ATAC 不用同一种分布？

#### 5.1 RNA：零膨胀负二项分布

RNA 是稀疏计数数据。OmiDos 的 RNA 解码器预测均值 $\mu$、离散度 $\theta$ 和额外零概率 $\pi$，再用 ZINB 计算原始计数的负对数似然。代码中的 `ZINBLoss` 还把均值乘回细胞的 size factor（`Module_OmiDos.py:13-30`）。

#### 5.2 ATAC：VAE + 高斯混合

ATAC 峰矩阵在代码里按二值重建处理。编码器输出 $\mu$、$\log\sigma^2$，通过重参数化得到 $z$；GMM 潜变量 $c$ 则描述潜在簇。`elbo_ATAC` 同时计算二值重建项和关于 $p(z\mid c)$、$p(c)$、$q(z\mid x)$、$q(c\mid x)$ 的 KL 相关项（`Module_OmiDos.py:47-119`）。`get_gamma()` 计算每个样本属于各混合成分的后验责任度（`Module_OmiDos.py:672-691`）。

#### 5.3 一个重要的论文—代码差异

论文写道，重建“共同依赖共享和私有潜空间”（`paper.md:35`）。但当前代码的 `LossShare()` 实际执行 `z = z_s`；生成私有潜变量和 `z_p + z_s` 的 union 行被注释掉（`Module_OmiDos.py:403-445`）。所以应准确理解为：

- 私有分支有自己的重建损失；
- 共享分支当前从共享变量单独重建；
- 本地代码并没有在 `LossShare()` 中把二者相加后共同解码。

### 六、正交约束如何把两类信号拆开？

代码先逐个样本归一化私有潜变量 $Z_p$ 与共享潜变量 $Z_s$，再惩罚二者交叉相关矩阵的平方均值：

$$
\mathcal L_{orthogonality}
=\operatorname{mean}\left[\left(\widetilde Z_p^\top\widetilde Z_s\right)^2\right].
$$

若某个潜在方向同时大量出现在 PREM 和 SHEM 中，交叉相关会变大，损失也变大；优化因此推动两套表示学习不同方向。实现位于 `DiffLoss` 与 `LossDiff()`（`Module_OmiDos.py:160-179,447-465`）。

这里的“正交”是批次潜变量矩阵之间的软惩罚，不是严格把每个向量投影到数学上完全正交的子空间。

### 七、模态分类、非配对数据与批次校正

#### 7.1 模态分类 Eq. [1]

论文先定义普通交叉熵：

$$
\mathcal L_{modality}=-\sum_{i=1}^{N}\sum_{c=1}^{C}y_{i,c}\log\hat y_{i,c}.\tag{[1]}
$$

论文明确说 Eq. [1] 本身不是对抗损失，只是给共享空间较弱的模态约束（`paper.md:148-154`）。代码也确实是两层分类器加普通 `CrossEntropyLoss`，并正向加入总损失（`Module_OmiDos.py:277-283,467-484,630-645`）。

#### 7.2 非配对 NCE Eq. [2]

当 RNA 与 ATAC 没有细胞级配对时，论文在每个模态内部对同一样本做两次增强，把它们作为正样本对：

$$
\mathcal L_{NCE}=-\log\frac{\exp(\mathsf{sim}(z_i,z_j)/\tau)}{\sum_{k=1}^{2N}\exp(\mathsf{sim}(z_i,z_k)/\tau)}.\tag{[2]}
$$

同时，论文把对抗判别器 $G_{NCE}$ 接到共享编码器上（`paper.md:156-162`）。但在本地全部 Python 文件、`Analysis/run_palate.ipynb` 和仓库 Markdown 的关键词搜索中，没有找到 NCE 函数、正样本增强构造、梯度反转或交替判别器训练。状态：**Not found**。

#### 7.3 批次 CVAE + MMD Eqs. [3]–[4]

论文先把批次标签 $b$ 条件化到 VAE：

$$
\mathcal L_{CVAE}(x,b)=-\mathbb E_{q(z\mid x,b)}[\log p(x\mid z,b)]
+\mathsf{KL}(q(z\mid x,b)\parallel p(z\mid b)),\tag{[3]}
$$

然后在解码器第一层加入 MMD：

$$
\mathcal L_{batch}=\mathcal L_{CVAE}+\beta\mathcal L_{MMD}.\tag{[4]}
$$

论文给出跨 $10^{-6}$ 到 $10^6$ 的多尺度 RBF 带宽（`paper.md:164-182`）。但本地代码中没有找到条件批次输入、MMD 估计器、核带宽列表或解码器层 MMD。状态同样是 **Not found**。

### 八、代码实际训练了什么？

`fit()` 用 Adam/AMSGrad 训练，并把梯度范数裁剪到 10（`Module_OmiDos.py:592-670`）。它实际组合的是：

- `LossDomainLabel`：普通模态分类；
- `LossDiff`：私有—共享正交；
- `LossShare`：共享分支重建；
- `LossscRNA` / `LossscATAC`：私有分支重建。

权重参数名是 `alfa`、`beda`、`delta`、`epsi`、`sita`。论文则列出七类损失并报告遗传算法搜索权重（`paper.md:176-182`）。因此，本地 `fit()` 只能复现较窄的核心配对模型，不能直接对应论文的全部扩展目标。

还有一个运行边界：多模态 `forward()` 计算了 `z_p` 和 `z_s`，随后却用该分支中未定义的 `z_x`、`z_y` 解码（`Module_OmiDos.py:298-373`）。训练之所以可能正常，是因为 `fit()` 不调用这个多模态 `forward()`，而是直接调用上面的损失函数。提取结果也应使用四个专门的 embedding API。

### 九、如何读主要结果？

#### 9.1 细胞类型分辨率

论文在主要 21 个数据集上用 NMI、ARI、运行时间和内存比较八种方法。Fig. 2 中 OmiDos 的 NMI 分布处于较高位置；BMMC 的 PREM 与 SHEM 大体形状相似，但子群划分不同，说明“私有/共享”比较可能揭示仅靠一个联合空间看不到的差异。

#### 9.2 Muc4 远端调控区域

Fig. 3 的关键不是普通 UMAP，而是 Muc4 附近的峰—基因连线：SHEM 比 PREM 多显示一个远端关联，并与 DNase 信号和 Rarb motif 背景相呼应。它是有多层证据支持的候选增强子，但主图没有提供扰动实验，因此不宜写成已证实的因果增强子。

#### 9.3 批次与非配对整合

Fig. 4 中 OmiDos 的 RNA/ATAC 颜色混合更充分，同时仍保持细胞类型岛，并进一步得到 BCL11B/CLOCK 关联。Fig. 5 中 OmiDos 保留了连贯的谱系、伪时间以及 Trps1/Sox5 的阶段模式。图像支持结果层面的比较，但不能证明这些结果来自本地可执行的 MMD 或 NCE 模块，因为相应实现未找到。

#### 9.4 髓母细胞瘤

Fig. 6 将 GNP、PNC、肿瘤状态、差异可及峰、bHLH/Neurod1 motif、Hi-C 和 Neurod1 区域轨迹串在一起，支持一个动态增强子网络假说。论文进一步提出 Stat2 缺失可能关联 Neurod1 远端调控区关闭；这是机制假说，不是主图已经确证的因果链。

### 十、复现性与使用建议

- 已验证：私有/共享编码器、RNA ZINB、ATAC VAE-GMM、正交损失、普通模态分类、PREM/SHEM 输出；
- **Not found**：显式 NCE/对抗非配对训练、CVAE/MMD 批次校正、完整 25 数据集基准流程；
- **MISSING**：SI Appendix，因自动下载失败，所有仅在补充材料中的细节和图不能验证；
- 已知代码问题：多模态 `forward()` 的 `z_x`/`z_y` 未定义；
- 数据边界：论文在 Figshare 提供处理后数据（`paper.md:222`），本地仓库未打包全部输入。

最稳妥的研究使用方式是：把当前仓库视为“配对数据私有/共享分解核心”的参考实现；若要复现论文中的非配对或批次扩展，应先向作者确认对应代码版本、训练脚本和 SI 参数，而不是假设 README 中提到的模块已经包含在本地包内。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## OmiDos Summary

### Problem

Single-cell RNA and chromatin-accessibility measurements contain both coordinated regulation and modality-specific variation. Because regulation is asynchronous and assays capture one snapshot, forcing both modalities into one latent space can erase RNA- or ATAC-specific information and confound biological variation with modality or batch effects (`paper source/pnas_2519870123/paper.md:21-29`). OmiDos asks whether explicitly separating private and shared latent components yields more interpretable multi-omics integration.

### What OmiDos Introduces

OmiDos—Omics Separation Modeling using Domain Adaptation—is an annotation-free deep generative framework with RNA-private, ATAC-private, and shared encoders. An orthogonality loss separates private representations (PREM) from shared representations (SHEM); RNA is reconstructed with a zero-inflated negative-binomial model and ATAC with a VAE/GMM objective. The paper adds within-modality NCE plus adversarial domain adaptation for unpaired data and a batch-conditioned CVAE with decoder-layer multikernel MMD for batch correction (`paper.md:33-42,134-182`).

The conceptual output is not merely one integrated embedding. Researchers can compare PREM and SHEM to ask whether a cell state or regulatory link is modality-specific or cross-modal, then use the learned representations for clustering, biomarkers, trajectories, peak-to-gene links, and enhancer hypotheses.

### Evidence and Main Results

The paper reports 25 datasets spanning 19 human and 6 mouse samples (`paper.md:29`). In the main 21-dataset integration comparison, OmiDos is evaluated against GLUE, DeepMAPS, LIGER, MultiVI, iNMF, Harmony, Scanpy, and Seurat using NMI, ARI, runtime, and memory (`paper.md:39-44`). The main figures show:

- OmiDos near the top of the NMI comparison and resolving different BMMC substructure in SHEM versus PREM (Fig. 2).
- A SHEM-specific additional Muc4 distal peak-to-gene link in embryonic palate epithelium, supported by accessibility and Rarb motif context (Fig. 3). This is a computational enhancer hypothesis, not perturbational proof.
- Stronger modality/batch mixing while retaining immune cell structure, followed by a BCL11B/CLOCK regulatory association (Fig. 4).
- Coherent unpaired RNA/ATAC lineage structure, Slingshot pseudotime, and stage-specific Trps1/Sox5 patterns (Fig. 5).
- Medulloblastoma state separation, bHLH/Neurod1 motif enrichment, and Neurod1-region chromatin dynamics across GNP-to-PNC-to-tumor progression (Fig. 6). The Stat2-linked mechanism remains a hypothesis.

The paper evaluates clustering with NMI/ARI; batch correction with batch ASW and kBET; and manifold preservation with graph connectivity (`paper.md:184`). Main-image inspection supports the comparative geometry and locus-level narratives, but exact supplementary analyses could not be checked because the SI Appendix is **MISSING**.

### Code-Paper Match

Overall fidelity is **medium-low**. The GitHub snapshot at commit `5a58fd1f8963b3465cf060046604ab8a9e3af877` directly implements the private/shared encoders, ZINB RNA reconstruction, ATAC VAE/GMM ELBO, orthogonality/DiffLoss, an ordinary modality classifier, and PREM/SHEM extraction (`OmiDos/OmiDos/Module_OmiDos.py`). RNA/ATAC preprocessing is present in `dataset.py`, and one palate analysis notebook is included.

Important limitations are source-verified:

- Explicit NCE/adversarial unpaired training and CVAE/MMD batch correction are **Not found** after searching all package Python files, the palate notebook, and repository Markdown for the corresponding terms.
- The paper says reconstruction jointly uses shared and private latents, but `LossShare()` operates on `z_s` alone; private extraction and `z_p + z_s` union are commented (`Module_OmiDos.py:403-445`).
- The multimodal `forward()` branch decodes undefined `z_x`/`z_y` (`Module_OmiDos.py:298-373`). `fit()` bypasses it through dedicated loss methods (`Module_OmiDos.py:592-670`).
- Full 25-dataset benchmark orchestration and bundled inputs are **Not found** in the repository snapshot.

### Reproducibility

**Rating: 2/5.** The core paired architecture is inspectable and the repository gives installation instructions and a palate notebook. The paper also links processed data on Figshare (`paper.md:222`). However, central paper extensions are absent from the searched code snapshot, the multimodal forward path is incomplete, full benchmark scripts are missing, and the SI Appendix could not be acquired. Reproducing the published full method and all claims therefore requires material beyond this workspace.

### Bottom Line

OmiDos offers a useful scientific framing: treat modality-private state as signal to model, not nuisance to erase, and compare it directly with cross-modal shared state. The paper presents broad benchmark and biological evidence for that framing. The released local code substantiates the paired private/shared core, but not the advertised unpaired NCE/adversarial or batch CVAE/MMD extensions; those claims should be read as paper-described, not package-verified.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
