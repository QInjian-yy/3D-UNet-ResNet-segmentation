# M&Ms 数据集准备说明

## 数据集概述

M&Ms数据集包含三个部分：
- **Training** - 训练集（仅使用Labeled部分进行监督学习）
- **Validation** - 验证集
- **Testing** - 测试集

## 数据下载

数据集链接：https://mega.nz/folder/FxAmhbRJ#Dwugf8isRSR9CCZ6Qnza4w

## 完整数据处理流程

### 步骤1：基础数据准备 (`prepare/get_m&ms_dataset.py`)
运行此脚本将原始数据集重新组织为以下目录结构：

```
data/
├── train_images/           # 训练集图像
├── train_masks/            # 训练集标注（与图像一一对应）
├── validation_images/      # 验证集图像
├── validation_masks/       # 验证集标注（与图像一一对应）
├── test_images/            # 测试集图像
└── test_masks/             # 测试集标注（与图像一一对应）
```



### 步骤2：序列数据处理 (`prepare/extract_m&ms_series.py`)
**此脚本用于处理4D序列数据，提取符合条件的3D切片**

#### 处理目标：
由于M&Ms数据集是序列数据（四维数据），本步骤根据第四维度（时间维度）来判断每个时间点的3D切片标注是否包含四个不同的类别（左心室、右心室、心肌、背景），并提取符合条件的切片。

#### 生成的目录结构：
```
data/
├── train_images_series/    # 处理后的训练集图像切片
├── train_masks_series/     # 处理后的训练集标注切片
├── validation_images_series/  # 处理后的验证集图像切片
├── validation_masks_series/   # 处理后的验证集标注切片
├── test_images_series/     # 处理后的测试集图像切片
└── test_masks_series/      # 处理后的测试集标注切片
```

# 数据集信息统计工具

## 文件位置
`tools/read_data_information.py`

## 功能概述
此脚本用于批量读取医学图像数据集中的 NIfTI 格式文件，提取关键元数据信息（如体素尺寸、图像维度、空间范围等），并将这些信息整理保存到 Excel 表格中，方便后续数据分析和处理。

## 主要功能

### 1. 数据提取
- 提取每个 NIfTI 文件的完整路径
- 获取体素尺寸（X, Y, Z 方向的体素大小，单位：mm）
- 获取图像维度（宽度、高度、深度，单位：体素数量）
- 计算空间范围（X, Y, Z 方向的总空间大小，单位：mm）

### 2. 信息整理
- 将提取的信息结构化存储到 Excel 表格
- 支持批量处理指定文件夹中的所有 NIfTI 文件

## 依赖库

```bash
conda install nibabel openpyxl
```

- **nibabel**: 用于读取 NIfTI 格式医学图像
- **openpyxl**: 用于创建和写入 Excel 文件



