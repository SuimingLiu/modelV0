# Geophysical Simulation Models / 地球物理仿真模型库

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

### Introduction
This repository contains a collection of **COMSOL Multiphysics** simulation models exported as **MATLAB (.m)** code. These models focus on geophysical exploration methods, designed for parametric studies and dataset generation.

### Contents

The models are categorized into three main geophysical methods:

*   **Seismic (`/Seismic`)**:
    *   Simulations of seismic wave propagation.
    *   Includes scenarios with varying target depths, sizes, and hazard types.
    *   Useful for forward modeling of seismic reflection/refraction.

*   **Ground Penetrating Radar (GPR) (`/GPR`)**:
    *   High-frequency electromagnetic wave simulations (e.g., 100 MHz).
    *   Scenarios include leakage detection, hazard type classification, and varying water levels.
    *   Models account for dielectric properties of subsurface materials.

*   **High-Density Resistivity (`/HighDensity`)**:
    *   Electrical resistivity tomography (ERT) models.
    *   Features complex geological structures and infinite element domains for boundary handling.
    *   Simulates potential field distributions for different electrode arrays.

### Usage
To use these models, you need **COMSOL Multiphysics** (tested with v6.x) and the **LiveLink™ for MATLAB**.

1.  Ensure the COMSOL LiveLink for MATLAB is running.
2.  Run the `.m` script in MATLAB.
3.  The script will rebuild the COMSOL `model` object from scratch.
4.  You can then visualize results (`mphplot`) or save the model as a binary file:
    ```matlab
    mphsave(model, 'reconstructed_model.mph');
    ```

**Note**: To reduce repository size, the binary `.mph` files (containing mesh and solution data) are **not included**. Please execute the scripts to regenerate the models locally.

---

<a name="chinese"></a>
## 中文说明

### 项目简介
本项目包含一系列由 **COMSOL Multiphysics** 导出的 **MATLAB (.m)** 仿真模型代码。这些模型主要用于地球物理勘探领域的正演模拟，支持参数化扫描和数据集生成。

### 目录结构

模型根据地球物理探测方法分为三类：

*   **地震勘探 (`/Seismic`)**:
    *   模拟地震波在不同地质结构中的传播。
    *   包含不同埋深 (`Var_Depth`)、不同尺寸 (`Var_Size`) 和不同隐患类型 (`Var_HazardType`) 的仿真场景。

*   **探地雷达 (`/GPR`)**:
    *   高频电磁波仿真（如 100 MHz 中心频率）。
    *   场景涵盖渗漏检测 (`_Leakage`)、隐患分类以及地下水位变化 (`Var_WaterLevel`) 对雷达图谱的影响。

*   **高密度电法 (`/HighDensity`)**:
    *   直流电阻率法/高密度电法仿真模型。
    *   包含复杂地质模型 (`_Complex`) 及使用无限元域 (`_InfiniteElem`) 处理边界的案例。

### 使用方法
使用这些代码需要安装 **COMSOL Multiphysics** (建议 v6.x 版本) 以及 **LiveLink™ for MATLAB**。

1.  启动 COMSOL with MATLAB。
2.  在 MATLAB 中运行对应的 `.m` 脚本。
3.  脚本将自动重建 COMSOL `model` 对象。
4.  重建完成后，您可以使用 `mphsave` 命令保存为可视化的二进制文件：
    ```matlab
    % 示例
    model = Range_0_to_0_Var_Depth(); % 运行函数重建模型
    mphsave(model, 'reconstructed_model.mph'); % 保存为 MPH 文件
    ```

**注意**：为了减小仓库体积，**不包含** 带有解和网格数据的二进制 `.mph` 文件。请运行代码在本地重新生成这些模型。
