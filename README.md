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

## 文件命名规范

所有文件将按照统一的命名规范进行组织，确保：
- 图像文件和对应的标注文件具有相同的文件名
- 文件扩展名根据实际格式保留（如 .nii.gz, .png 等）

## 使用说明

1. 首先下载M&Ms数据集
2. 运行准备脚本：
   ```bash
   python prepare/get_m&ms_dataset.py
   ```
3. 脚本将自动完成数据集的重新组织和目录结构创建

