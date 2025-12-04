# M&Ms 数据集准备说明

## 数据集概述

M&Ms数据集包含三个部分：
- **Training** - 训练集（仅使用Labeled部分进行监督学习）
- **Validation** - 验证集
- **Testing** - 测试集

## 数据下载

数据集链接：https://mega.nz/folder/FxAmhbRJ#Dwugf8isRSR9CCZ6Qnza4w

## 目录结构处理

运行 `prepare/get_m&ms_dataset.py` 脚本后，将生成以下目录结构：

```
data/
├── train_images/           # 训练集图像
├── train_masks/            # 训练集标注（与图像一一对应）
├── validation_images/      # 验证集图像
├── validation_masks/       # 验证集标注（与图像一一对应）
├── test_images/            # 测试集图像
└── test_masks/             # 测试集标注（与图像一一对应）
```

## 处理流程

### 1. Training 数据集处理
- 从原始Training数据集中提取Labeled部分
- 图像文件统一放置在 `train_images` 目录下
- 标注文件统一放置在 `train_masks` 目录下
- 确保图像和标注文件一一对应

### 2. Validation 数据集处理
- 图像文件统一放置在 `validation_images` 目录下
- 标注文件统一放置在 `validation_masks` 目录下
- 确保图像和标注文件一一对应

### 3. Testing 数据集处理
- 图像文件统一放置在 `test_images` 目录下
- 标注文件统一放置在 `test_masks` 目录下
- 确保图像和标注文件一一对应

## 使用说明

1. 首先下载M&Ms数据集
2. 运行准备脚本：
   ```bash
   python prepare/get_m&ms_dataset.py
   ```
3. 脚本将自动完成数据集的重新组织和目录结构创建

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

#### 处理流程：
1. **Training 数据集处理**
   - 从原始Training数据集中提取Labeled部分
   - 图像文件统一放置在 `train_images` 目录下
   - 标注文件统一放置在 `train_masks` 目录下
   - 确保图像和标注文件一一对应

2. **Validation 数据集处理**
   - 图像文件统一放置在 `validation_images` 目录下
   - 标注文件统一放置在 `validation_masks` 目录下
   - 确保图像和标注文件一一对应

3. **Testing 数据集处理**
   - 图像文件统一放置在 `test_images` 目录下
   - 标注文件统一放置在 `test_masks` 目录下
   - 确保图像和标注文件一一对应

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

## 使用说明

### 完整处理流程：
```bash

python prepare/get_m&ms_dataset.py

```

### 参数配置：
在运行序列数据处理脚本前，需要修改以下路径变量：
- `image_folder`: 原始图像文件夹路径
- `mask_folder`: 原始标注文件夹路径
- `image_save_folder`: 处理后图像保存路径
- `mask_save_folder`: 处理后标注保存路径

