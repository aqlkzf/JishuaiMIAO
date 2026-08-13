---
layout: default
permalink: /paper-atlas/wisdem-cc0b351d/
title: "WISDEM"
nav: false
description: "同时记录 EEG 与 fMRI 可以把毫秒级神经电活动和全脑血氧动力学联系起来，但传统方案需要把头部电极用电缆接到 MRI 外的 EEG 设备。电缆会拾取射频脉冲和梯度切换伪影，接触电阻变化还会造成基线漂移。已有无线方案减少了电缆，却通常仍需要电池、微控制器、射频发射器和梯度传感器，而且只能在梯度稳定的短窗口记录 EEG。"
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
    <h1>WISDEM</h1>
    <p>WISDEM: a hybrid wireless integrated sensing detector for simultaneous EEG and MRI</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02798-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for WISDEM">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## WISDEM 方法详解

### 它要解决什么问题？

同时记录 EEG 与 fMRI 可以把毫秒级神经电活动和全脑血氧动力学联系起来，但传统方案需要把头部电极用电缆接到 MRI 外的 EEG 设备。电缆会拾取射频脉冲和梯度切换伪影，接触电阻变化还会造成基线漂移。已有无线方案减少了电缆，却通常仍需要电池、微控制器、射频发射器和梯度传感器，而且只能在梯度稳定的短窗口记录 EEG。

WISDEM 的目标是：只用一个无线供能的植入式振荡器，让标准 MRI 接收线圈在整个 EPI 序列中同时收到电生理和 MR 信息。

### 核心创新

WISDEM 把两种带宽差异巨大的信号调制到同一个窄线宽载波的不同频率侧带：

- 电极上的 EEG/LFP 电压缓慢改变电压感知谐振器（VSR），进而移动载波频率；
- MR 信号与载波相互作用，形成约 81.5 kHz 偏移的高频调制；
- MRI 控制台记录复数载波后，对展开相位的时间导数做低通和高通，就能拆出两种模态。

装置由双模参量谐振器（PR）和“8”字形 VSR 构成。PR 有圆形模和蝴蝶模；外部泵浦频率满足

$$
\omega_{\mathrm{p}}=\omega_{\mathrm{b}}+\omega_{\mathrm{c}}.
$$

VSR 的空间对称布置使它主要耦合圆形模，却尽量不影响用于 MRI 接收的蝴蝶模。论文测得电压—频率转换率为 5.5 kHz mV$^{-1}$，载波线宽约 100 Hz，对应约 18 µV 的名义检测下限。

### 从原始载波到 EEG 和 MRI

```text
电极电压 ─┐
          ├─> 调制无线振荡载波 ─> MRI 复数接收信号
MR 信号 ──┘                              │
                                        v
                         φ(t)=unwrap(angle(signal))
                                        │
                                   dφ(t)/dt
                              ┌─────────┴─────────┐
                              v                   v
                         1 kHz 低通             高频残差
                              │                   │
                      除以 5.5 kHz/mV      exp(-jφ) 相位校正
                      梯度基线模板相减            │
                      中值滤波与插值        正/负读出梯度分离
                              │             2D FFT 后合并
                              v                   v
                           EEG/LFP              EPI 图像
```

#### 电生理支路

MRI 接收器采样率为 326,087 Hz。先用相邻采样点的相位差估计瞬时频移，再进行 1 kHz 以下低通，最后除以 FVR 得到电压。EPI 梯度会产生与每个切片重复的基线图样，其中 43 对正负峰对应 43 条 $k$ 空间线；算法对每个切片减去平均基线，并用中值滤波和线性插值处理切片间空白期造成的尖峰。

#### MRI 支路

论文把高通定义为

$$
\operatorname{HPF}(\dot\varphi_t)=\dot\varphi_t-\operatorname{smooth}(\dot\varphi_t,8),
$$

再构造复数 MR 样本

$$
s_t=\exp(-j\varphi_t)\operatorname{HPF}(\dot\varphi_t).
$$

正、负读出梯度的数据分别重建，再通过二维傅里叶变换合并为 EPI。为了避开镜像与混叠镜像，载波被放在扩展频率编码视野的四分之一位置；后续只使用中央裁剪区域。

### 实验结果如何支持方法？

- 台架正弦电压实验中，重建波形与输入波形基本重合，幅度关系接近 1:1。
- 琼脂模体中，WISDEM 峰值 SNR 为 135，同尺寸有线线圈为 222，说明无线双模检测保留约 60% 灵敏度，但存在明确代价。
- 5 只大鼠的电刺激实验在 S1FP 区得到刺激同步的 BOLD 激活，变化最高约 1.5%。
- 4 只 ChR2 大鼠中，光刺激诱发的 LFP 随功率增大而增强、延迟缩短；0.97 mW 条件下 S1FP BOLD 平均约增加 3%。无 ChR2 对照鼠没有相同 LFP 峰。
- 同时 EPI 采集时，LFP 峰仍与无梯度/RF 时相近；较强 LFP 大体对应较强 BOLD，支持神经血管耦联的概念验证。

### 应如何理解局限？

这不是一个已经完成临床验证的通用 EEG–fMRI 系统，而是小样本大鼠原型。非正交编码使图像 SNR 明显低于有线线圈，并限制可用视野。原型只有一根 80-µm 电极，约 10-mm 探测深度；多电极复用、阵列、长期植入、人体安全性和体内单神经元记录都仍是未来工作。

论文给出了方程、器件尺寸、MRI 参数和重建流程，但精确的中值滤波参数、插值实现与图像合并细节未在正文中找到。作者声明 MATLAB 2023a 代码位于 Code Ocean（`10.24433/CO.6663434.v1`），本次获取返回 HTTP 403，因此无法做代码级核验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## WISDEM summary

WISDEM is a wirelessly powered, two-in-one detector for continuous electrophysiology and MRI acquisition through a standard MRI console. It addresses the cable motion, baseline drift, RF/gradient interference, shielding, and synchronization burden of conventional simultaneous EEG–fMRI. Earlier wireless electrophysiology systems could avoid cables but used batteries, RF transmitters, microcontrollers, and gradient sensors, and recorded only during stable-gradient windows.

The device couples a voltage-sensing resonator to a dual-mode parametric resonator. Electrode voltage shifts the circular-mode resonance, which shifts a narrow butterfly-mode oscillation carrier detectable by the MRI coil. Simultaneous MR interaction creates a much higher-offset modulation sideband. From the complex recorded carrier, WISDEM differentiates unwrapped phase: a <1-kHz low-pass branch, divided by the measured 5.5 kHz mV$^{-1}$ frequency-to-voltage ratio and baseline-corrected, yields EEG/LFP; a high-pass branch multiplied by $\exp(-j\varphi_t)$ and reconstructed with 2D FFT yields EPI images.

Bench voltage tests showed near 1:1 agreement between applied and reconstructed amplitudes. Phantom imaging reached peak SNR 135 versus 222 for a dimension-matched wired coil, retaining about 60% sensitivity. In five rats, electrical forepaw stimulation produced localized S1FP activation with up to about 1.5% BOLD modulation. In four ChR2-transfected rats, optogenetic stimulation produced power-dependent LFP responses and stimulus-locked BOLD changes; at 0.97 mW, the reported S1FP increase was about 3%. LFP amplitudes remained comparable with and without RF/gradient activity, a non-transfected control lacked evoked LFP peaks, and larger LFP responses approximately tracked larger BOLD responses.

The main advance is continuous frequency-multiplexed acquisition without a separate EEG receiver, internal battery, ADC, microprocessor, or gradient-synchronization hardware. The main trade-off is MRI sensitivity: non-quadrature reconstruction adds noise and restricts useful reconstruction to the center portion of an extended field of view. The prototype is also a small-cohort rodent demonstration with one 80-µm electrode, about 10-mm detection depth, and no demonstrated multiplexed array, chronic implant, human use, or in vivo single-unit recording.

Reproducibility is moderate (3/5). The full paper, 14 local figures, Figshare data DOI `10.6084/m9.figshare.26082115`, fabrication dimensions, scanner parameters, equations, and reconstruction outline are available. MATLAB 2023a code is cited at Code Ocean DOI `10.24433/CO.6663434.v1`, but the capsule returned HTTP 403 during this run, so median-filter settings, interpolation details, image-combination behavior, and exact executable workflows could not be verified. The physical WISDEM device is available only through a material transfer agreement.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
