---
layout: default
permalink: /paper-atlas/miso-cryo-em-bd11e64f/
title: "MISO_cryo_EM"
nav: false
description: "MISO 通过“微型层析 + 在线荧光定位 + 毛细管直连网格 + 自动 blot/plunge”，把约 1 μl 的蛋白洗脱峰直接变成多张冷冻电镜网格，并在多个约 1–2 μg 输入的示例中得到 2.2–3.5 Å 结构；论文充分证明了平台的可行性，但完整复现仍依赖定制硬件和当前仓库中不可读或缺失的 LabVIEW 主控逻辑。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>MISO_cryo_EM</h1>
    <p>MISO: microfluidic protein isolation enables single-particle cryo-EM structure determination from a single cell colony</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/EfremovLab/MISO" target="_blank" rel="noopener noreferrer" aria-label="Open code for MISO_cryo_EM">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MISO 方法详解：把微量蛋白纯化直接接到冷冻电镜制样

### 1. 这篇论文要解决什么问题？

单颗粒冷冻电镜真正被成像的蛋白只有皮克级，但传统流程通常从毫克级蛋白、毫升到升级细胞培养开始。问题不只在显微镜，而在显微镜之前：亲和纯化、凝胶过滤、浓缩、转移和制备冷冻电镜网格都会损失样品。传统制样往网格上滴加数微升蛋白，再用滤纸吸走绝大部分液体，最终留在网格上的比例极低（`paper.md:21-30`）。

MISO（micro isolation）的核心目标是：把“蛋白纯化—检测—选择洗脱峰—上网格—吸 blot—液氮乙烷快速冷冻”缩小并连成一个连续过程，让约 1–2 μg 目标蛋白也能完成高分辨率结构测定。

### 2. 现有微量制样方案为什么还不够？

Spotiton（*Journal of Structural Biology*, 2012）、pin-printing/jet vitrification（*Nature Communications*, 2020）、VitroJet（*Acta Crystallographica D*, 2024）和 cryoWriter（*ACS Nano* / *Journal of Structural Biology*, 2016）都在减少网格沉积体积。2019 年 *PNAS* 的 cryoWriter 相关工作进一步用磁珠在毛细管内捕获蛋白。

但论文指出，这些方案通常有一个或多个限制：

- 重点是“少量上网格”，没有完整缩小多步蛋白纯化；
- 只完成一次简单亲和捕获，难以控制最终浓度或增加 SEC 缓冲液置换；
- 把亲和配体放在网格表面时，可能受到非特异吸附影响；
- 纯化和上网格仍然是分开的步骤，微升级洗脱峰在中间转移时容易扩散和损失（`paper.md:27`）。

MISO 的新意不是发明新的冷冻电镜重构算法，而是把常见的亲和层析、可选 SEC、在线荧光检测和网格冷冻工程化为一个不可拆分的微型系统。

### 3. 输入、输出和基本假设

**输入：**澄清后的细胞裂解液，其中含有带亲和标签的目标蛋白。目标可通过两种方式被检测：

1. 用 Chromeo P503 等染料标记表面伯胺，检测总蛋白；
2. 给目标蛋白融合 YFP/eGFP，只检测目标蛋白。

**输出：**从约 1 μl 洗脱峰不同位置制备的一组冷冻电镜网格；必要时还收集微量组分，用 SDS–PAGE 或负染电镜检查纯度与单分散性。

**基本假设：**目标蛋白有可用的亲和标签/树脂，能够耐受微柱流动和荧光标签；表面吸附、死体积和扩散损失没有超过样品总量；一根亲和柱或“亲和柱 + SEC”足以得到可用于冷冻电镜的样品。

### 4. 系统由哪些部分组成？

#### 4.1 显微镜和荧光检测模块

芯片安装在电动显微镜平台上。LED 激发检测区，光电二极管接收荧光，经放大器和 National Instruments DAQ 转成数字信号，再由 LabVIEW 形成“电压—泵送体积”色谱图（`paper.md:228-237`）。

PDMS 对 280 nm 紫外光吸收很强，因此不能像普通蛋白色谱那样直接看 A280。MISO 改用荧光，论文展示最低可稳定检测 0.001 mg ml⁻¹ GFP，即约 37 nM（`paper.md:53-59`）。

#### 4.2 微流控芯片和流路控制

芯片可以是一柱或两柱结构。两柱芯片通常包括：

- 亲和柱 AC；
- 第一检测区 DZ1；
- 废液出口和阀门；
- 下游 SEC 柱；
- 第二检测区 DZ2；
- 直接通往网格的熔融石英毛细管。

柱体是扁平的 PDMS 腔室，约 150 μm 高、2.5 mm 宽、最长约 20 mm；10 μm 高的微柱阵列用于挡住填料。论文使用过 0.5 μl Ni-NTA + 5 μl Superose 6、3 μl streptavidin 单柱、1 μl streptavidin + 10 μl Superose 6 Increase 等配置（`paper.md:53,264-291`）。

#### 4.3 冷冻电镜网格和快速冷冻模块

该模块包含步进电机驱动的镊子、释放网格的电磁铁、湿度腔、滤纸臂和控温乙烷杜瓦。网格先与出口毛细管精确对准，接收几十纳升洗脱液，然后 blot 并快速插入液态乙烷（`paper.md:246-255`）。

仓库中的 Arduino 源码直接验证了设备侧行为：步进电机脉冲、舵机 blot、串口命令、湿度/温度输出和加热 PWM（`Stepper_plunger_Temp_Controller_26.ino:77-395`）。但泵、阀门、色谱采集和位移台的主 LabVIEW 控制逻辑无法从可读文件中验证。

### 5. 从裂解液到网格：完整流程

```text
澄清裂解液
   │
   ├─ 总蛋白染料标记，或目标蛋白 YFP/eGFP 融合
   ▼
4 °C 条件下上样到微型亲和柱
   │
   ├─ DZ1 实时看荧光
   └─ 延长清洗直到基线稳定
   ▼
亲和洗脱，得到约微升级峰
   │
   ├─ 单柱路线：直接进入出口毛细管
   └─ 两柱路线：选择峰中一小段注入 SEC
                    │
                    └─ DZ2 再次检测
   ▼
把约 1 μl 洗脱峰分配到最多 8 张网格
   │
   ├─ 每张约 40–100 nl
   ├─ 无 blot：滴加 → 回吸 → 快速冷冻
   └─ 有 blot：滴加/铺展 → 0.5 s 滤纸吸液 → 快速冷冻
   ▼
筛选网格 → 采集电影 → CryoSPARC 重构和精修
   │
   └─ 未知蛋白时：ModelAngelo 无序列建模 → HMMER 搜索
```

#### 步骤 1：低温平衡

芯片、样品、缓冲液、泵注射器等与蛋白接触的部分都保持在 4 °C。虽然柱体只有亚微升到数微升，但连接管路和表面面积相对很大，因此实际平衡和清洗体积仍可能达到几十或上百微升（`paper.md:258-261,378-384`）。

#### 步骤 2：上样与在线清洗判断

样品进入亲和柱后，DZ1 连续记录荧光。清洗不是简单按固定时间结束，而是观察信号何时回到稳定基线。20 μg βG 实验中，仅为了稳定基线就需要约 60 μl 清洗液；作者认为这反映了死体积、扩散和表面吸附（`paper.md:77`）。

#### 步骤 3：亲和洗脱与可选 SEC

亲和峰到达 DZ1 时，系统可以把其中一小段切换到 SEC。βG 两柱流程中，0.5 μl 亲和洗脱液被送入下游 SEC；DZ2 再监测 SEC 峰，然后选择收集或直接上网格（`paper.md:378-384`）。

如果亲和纯化已经得到足够纯且单分散的样品，可以跳过 SEC。TMEM206、TMEM16F 和优化后的 TRPC6 都采用了亲和峰直接制网格的路线。这样避免常规离心浓缩器，也可能减少聚集和损失（`paper.md:134,149,186,201`）。

#### 步骤 4：校正“检测区到毛细管尖端”的延迟

荧光峰被检测到时，蛋白还没有到达网格。膜蛋白方案明确计算了检测区到毛细管尖端约 0.7 μl 的延迟体积（`paper.md:405-408`）。在只有约 1 μl 的峰里，这个校正非常关键；否则系统会在错误的峰位置制备网格。

#### 步骤 5：控制表面吸附

单菌落 βG 实验最初在 SEC 后看不到峰。加入 0.2% DDM 后，回收提高约 6 倍，两柱总回收率达到 65 ± 7%（`paper.md:97`）。这说明微量系统的主要敌人不是柱容量，而是芯片、管路和填料表面对蛋白的吸附。

#### 步骤 6：把一个峰分配给多张网格

MISO 通常把约 1 μl 洗脱峰分成最多 8 个网格位置，相当于沿峰采样不同蛋白浓度。这样不需要先知道最佳浓度，也不需要单独浓缩。论文使用约 40–100 nl/网格（`paper.md:65,91,134,186,294-303`）。

无 blot 路线通过滴加后回吸形成薄液膜，能制得可用网格，但可采集区域有限且重复性较差。最终最可靠的路线仍是高湿度下用 Whatman 4 滤纸 blot 0.5 s（`paper.md:65,91,300-303`）。

### 6. 定量表征

#### 6.1 SEC 理论塔板数

$$
N=5.54\left(\frac{V_{\mathrm{p}}}{W_{0.5}}\right)^2
$$

其中 $V_{\mathrm{p}}$ 是峰洗脱体积，$W_{0.5}$ 是半峰宽。柱效为 $N/L$。论文测得塔板数 $210\pm40$，约 10,000 plates m⁻¹，低于分析型 HPLC；作者认为它足以完成缓冲液置换和“大分子与小分子”的粗分离，而不是高分辨率 SEC（`paper.md:62,312-324`）。

#### 6.2 Taylor 扩散

$$
I_{\mathrm f}=A\exp\left[-\frac{(x-x_0)^2}{2\sigma^2}\right],
\qquad W_{0.5}\approx2.35\sigma
$$

荧光示踪峰用高斯函数拟合。亲和柱和 SEC 测得约 2 μl FWHM，说明 Taylor 扩散是限制微柱分辨率的重要因素（`paper.md:62,327-336`）。

#### 6.3 βG 定量

$$
N=\frac{A_{420}V}{\varepsilon l},
\qquad
a=\frac{N}{t\,m_{\mathrm{tot}}}
$$

论文用 ONPG 水解吸光度估算 βG 活性和裂解液中 βG 浓度，最终得到约 1.40 μg μl⁻¹（`paper.md:423-447`）。

### 7. 论文做出了哪些验证？

| 样品 | 起始量 | 芯片配置 | 结果 |
|---|---:|---|---|
| βG 方法验证 | 粗裂解液中约 20 μg | 0.5 μl Ni-NTA + 5 μl SEC | 2.3 Å 结构 |
| 单菌落 βG | 约 1 μg | 同上，加入 0.2% DDM | 2.16/2.2 Å 结构 |
| btTMEM206–YFP | 半个 10-cm 培养皿，约 2 μg | 3 μl streptavidin 单柱 | 3.0 Å；传统法为 2.9 Å |
| mTMEM16F–YFP | 一个 10-cm 培养皿，约 1–2 μg | 3 μl streptavidin 单柱 | 3.5 Å |
| TRPC6 | 约 2.5 μg 目标蛋白 | 3 μl 单柱直接制样；另做两柱表征 | 3.4/3.5 Å，并从密度图识别蛋白 |

TMEM206 是最直接的传统法对照：传统方案使用 150 个培养皿，MISO 使用半个培养皿，结构 RMSD 为 0.75 Å/763 个 Cα，论文概括为约 300 倍起始细胞量缩减（`paper.md:117-140`）。

TRPC6 实验还展示了一个下游用途：先用 ModelAngelo 在不知道序列的情况下从密度图建立 151 个多肽片段，再把片段 HMM profile 交给 HMMER 搜索，TRPC6 成为最高匹配。由于不同物种 TRPC6 序列相似，具体物种仍不确定（`paper.md:169-192`）。

### 8. 代码到底验证了什么？

#### 可直接验证

Arduino 文件 `Stepper_plunger_Temp_Controller_26.ino` 中可以直接看到：

- 初始化舵机、步进电机、磁铁、按键、温度/湿度输入和加热输出（`:77-113`）；
- 解析串口命令，设置网格移动、blot、舵机角度和延迟（`:159-213`）；
- 执行手动/自动移动、blot 和 plunge 序列（`:216-340`）；
- 输出“湿度,温度”，并用有界 PI 风格控制计算加热 PWM（`:343-395`）。

源码中，按钮触发和 LabVIEW 触发的自动 plunge 使用不同固定步数（`:294-313`）。论文最优 blot 条件是 8°、0.5 s，但 Arduino 默认值是 5°、1000 ms；这些参数可以通过串口修改，因此这是“默认配置差异”，不能据此断言论文实验使用了源码默认值。

#### 只能部分验证或 Not found

- LabVIEW 与 Arduino 通信：只能看到 Arduino 接收端，主机端协议不可读，属于 **Partial**。
- AMF、Fluigent、Thorlabs 依赖：README 和 `.lvproj` 能证明项目声明了这些依赖，但不能恢复执行顺序，属于 **Partial**。
- 泵/阀门自动流程、DAQ 色谱采集与保存、位移台控制、论文各样品的自动化 protocol：在所有可读文件中 **Not found**。
- README 提到的两个顶层 LabVIEW 应用文件在该快照中只有空白文本行；其他 `.vi` 是二进制 LabVIEW 文件，未推断其 block diagram。

因此，仓库对 Arduino 硬件控制层的匹配度较好，但不足以端到端复现 MISO 纯化和制网格流程。

### 9. 怎样理解这项工作的真正贡献？

MISO 的关键不是“柱子更小”这一件事，而是保持微升级峰从出现到冷冻都不失联：

1. **荧光检测**告诉系统蛋白在哪里；
2. **微阀和小死体积流路**让系统能在峰到达时切换路线；
3. **出口毛细管直连网格**减少中间转移；
4. **一个峰制多张网格**把未知最佳浓度转化为可筛选的浓度梯度；
5. **快速完成纯化和冷冻**避免常规浓缩与长时间操作带来的损失或聚集。

换句话说，它把过去靠人手分开的多个步骤变成了一个以荧光峰为中心的闭环实验过程。

### 10. 局限与尚未证明的部分

- 微柱 SEC 分辨率明显低于分析型 HPLC，Taylor 扩散仍是瓶颈。
- 管路和 PDMS 表面吸附在微量条件下非常严重，长时间清洗抵消了部分“小柱体积”的优势。
- 染料标记改变了 βG 局部 loop，说明总蛋白化学标记可能影响结构。
- 脆弱复合物可能不适合层析流动，温和批量纯化或梯度方法仍有优势。
- 无 blot 制网格重复性不足，成功的高分辨率实验主要仍依赖滤纸 blot。
- 所有演示样品都是高表达、带标签的目标。内源低丰度复合物、原代组织、类器官和活检样品只是未来设想，并未在本文验证。
- 完整 LabVIEW 控制逻辑、可运行示例、自动化测试和硬件仿真模式缺失，限制了软件层面的可复现性。

### 11. 一句话总结

MISO 通过“微型层析 + 在线荧光定位 + 毛细管直连网格 + 自动 blot/plunge”，把约 1 μl 的蛋白洗脱峰直接变成多张冷冻电镜网格，并在多个约 1–2 μg 输入的示例中得到 2.2–3.5 Å 结构；论文充分证明了平台的可行性，但完整复现仍依赖定制硬件和当前仓库中不可读或缺失的 LabVIEW 主控逻辑。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MISO: Microfluidic Protein Isolation for Cryo-EM

### Overview

MISO is an integrated experimental platform that connects microfluidic protein purification, fluorescence-guided fraction selection, nanoliter deposition on cryo-EM grids, blotting, and plunge freezing. The goal is to close a major efficiency gap in single-particle cryo-EM: only picograms of protein are imaged, yet conventional purification and grid preparation often require milligrams of protein and large cultures. The Nature Methods paper reports structures from approximately 1–2 μg of target protein, including β-galactosidase expressed from a single *E. coli* colony and mammalian membrane proteins from one or half of one 10-cm dish (`paper.md:12,21-30,94-166`).

### Why existing approaches are insufficient

Conventional grid preparation deposits microliter volumes and discards most of the sample during blotting. Miniaturized grid technologies reduce deposition loss: Spotiton (*Journal of Structural Biology*, 2012) jets droplets; pin-printing/jet vitrification was demonstrated in *Nature Communications* (2020); VitroJet was described in *Acta Crystallographica D* (2024); and cryoWriter conditioning/deposition appeared in *ACS Nano* and *Journal of Structural Biology* (2016). A later cryoWriter-based microfluidic isolation workflow (*PNAS*, 2019) combined magnetic-bead capture with grid preparation. According to the MISO paper, these approaches either focus on grid preparation, use a single simple purification step, provide limited concentration control, or risk nonspecific adsorption on affinity grids. They do not provide a general miniature analogue of multistep affinity-plus-SEC purification directly connected to grid preparation (`paper.md:27`).

### Method

The MISO instrument has three coupled modules:

- a microscope/photodetector that reads fluorescence at on-chip detection zones;
- syringe-pump and pressure control for samples, buffers, pneumatic valves, affinity columns, and optional SEC;
- a cryo-plunger with motorized tweezers, humidity chamber, blotting arm, and temperature-controlled ethane dewar.

One- and two-column PDMS chips use shallow, resin-packed compartments and downstream detection zones. A fused-silica outlet capillary minimizes the transfer between the final detection point and the grid. Fluorescence indicates when washing is complete, when an affinity fraction should enter SEC, and which part of an approximately microliter-scale elution peak should be sent to grids (`paper.md:36-65,228-303`).

The peak is divided across as many as eight grids, typically depositing 40–100 nl per grid. Blotless dispense-and-suck-back worked but produced limited usable areas; 0.5-s paper blotting at near-100% humidity was more reproducible. At microgram input, adsorption is critical: adding 0.2% DDM improved recovery in the single-colony βG workflow, and the paper reports two-column recovery of 65 ± 7% (`paper.md:65,91,97,294-303`).

### Evidence and results

- **β-galactosidase, 20 μg input:** a 0.5-μl Ni-NTA plus 5-μl SEC chip produced a 2.3-Å map. The fluorescent label perturbed two exposed loop regions, illustrating a labeling risk (`paper.md:77-91`).
- **β-galactosidase, single-colony scale:** approximately 1 μg βG yielded a 2.16/2.2-Å reconstruction from one selected grid; the refined structure matched the 20-μg result (`paper.md:94-114,507-510`).
- **TMEM206:** conventional preparation used material from 150 dishes, whereas MISO used half of one dish (~2 μg target) and produced a 3.0-Å map, compared with 2.9 Å conventionally. The structures differed by only 0.75 Å RMSD over 763 Cα atoms (`paper.md:117-140`).
- **TMEM16F:** one dish and two MISO experimental rounds produced a 3.5-Å map with interpretable Ca²⁺-binding and membrane-protein density (`paper.md:143-166`).
- **TRPC6:** a target with withheld identity was purified, vitrified, reconstructed at 3.4–3.5 Å, and identified by sequence-free ModelAngelo fragment building followed by HMMER profile search (`paper.md:169-192`).

The main figures visibly connect chromatograms, selected fractions, gels or negative stain, cryo-EM particles, and final density maps. They demonstrate feasibility across soluble and membrane proteins, but not a standardized head-to-head benchmark: tags, detergents, chip layouts, grids, microscopes, particle counts, and processing strategies vary among targets.

### Limitations

MISO still uses more protein than the theoretical particle-count limit. Surface adsorption and tubing dead volume become dominant at small scale, causing long washes and sample loss. The micro-SEC columns have lower resolution than analytical HPLC because of geometry and Taylor dispersion. Chromatographic flow may be unsuitable for fragile complexes. Fluorescent primary-amine labeling can alter local structure, while genetically encoded tags require construct engineering. Blotless grids were less reproducible, so the most successful demonstrations still relied on paper blotting (`paper.md:62,91,195-219`).

The demonstrations use abundant, overexpressed, tagged proteins. Endogenous low-copy complexes, primary tissue, organoids, biopsy material, and further 10–100-fold downscaling are proposed applications, not validated outcomes.

### Reproducibility and code-paper match

**Reproducibility rating: 3/5.** The paper provides detailed chip fabrication, buffers, flow rates, column sizes, grid conditions, image-processing procedures, deposited structures/maps/raw data, and a public device-software repository (`paper.md:228-567`). Source data and CAD files are linked by the article, but no supplementary Markdown was acquired in this workspace.

The repository snapshot is from `https://github.com/EfremovLab/MISO`, commit `cb743048fddb0d22a74c21c9fb0496156b8bd435`. Its README cites the preprint DOI `10.1101/2025.01.10.632437`, distinct from the final article DOI `10.1038/s41592-025-02894-x`.

Code fidelity is **medium for the supplied device-control snapshot but low for end-to-end execution**. The readable Arduino sketch directly implements stepper-driven grid movement, servo blotting, serial commands, humidity/temperature reporting, and heater PWM. However, the central LabVIEW pump/valve automation, DAQ-to-chromatogram logic, stage positioning, and paper-specific purification programs are unavailable in readable form. The two advertised top-level LabVIEW application files are blank placeholders in this snapshot; most remaining VIs are binary and were not interpreted. No automated tests, runnable example protocol, or simulated hardware mode is supplied.

MISO is therefore well documented as an experimental concept and protocol, and its Arduino hardware layer is inspectable, but reproducing the complete platform still requires custom fabrication, commercial/proprietary hardware and software, and LabVIEW logic not recoverable from the readable repository files.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
