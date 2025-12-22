import random
import torch
import numpy as np
from torch.utils.data import Dataset


class Image_Label_train(Dataset):
    """训练数据集加载器，支持多种数据增强操作"""

    def __init__(self, image_label_pairs):
        """
        初始化训练数据集加载器

        参数:
            image_label_pairs: 包含图像和标签路径的元组列表，
                               格式为 [(图像路径1, 标签路径1), (图像路径2, 标签路径2), ...]
        """
        self.image_label_pairs = image_label_pairs

    def __getitem__(self, index):
        """获取单个数据样本并应用随机数据增强"""

        # 加载图像和标签数据
        image_path = self.image_label_pairs[index][0]  # 获取图像文件路径
        label_path = self.image_label_pairs[index][1]  # 获取标签文件路径
        image_array = np.float32(np.load(image_path))  # 加载图像数据并转换为float32格式
        label_array = np.float32(np.load(label_path))  # 加载标签数据并转换为float32格式

        # 30%的概率跳过数据增强（直接返回原始数据）
        if np.random.random_sample() > 0.7:
            # 不进行增强，直接添加通道维度并转换为PyTorch张量
            image_data = np.expand_dims(image_array, axis=0)  # 添加通道维度 (C=1, D, H, W)
            label_data = np.expand_dims(label_array, axis=0)  # 添加通道维度
            return torch.from_numpy(image_data), torch.from_numpy(label_data)
        else:
            # 70%的概率应用多种数据增强操作

            # 随机水平翻转（20%概率） - 沿深度维度翻转
            if np.random.random_sample() > 0.8:
                image_array = np.flip(image_array, axis=0).copy()  # 沿深度维度翻转图像
                label_array = np.flip(label_array, axis=0).copy()  # 同步翻转标签以保持一致性

            # 随机垂直翻转（20%概率） - 沿高度维度翻转
            if np.random.random_sample() > 0.8:
                image_array = np.flip(image_array, axis=1).copy()  # 沿高度维度翻转图像
                label_array = np.flip(label_array, axis=1).copy()  # 同步翻转标签

            # 随机前后翻转（20%概率） - 沿宽度维度翻转
            if np.random.random_sample() > 0.8:
                image_array = np.flip(image_array, axis=2).copy()  # 沿宽度维度翻转图像
                label_array = np.flip(label_array, axis=2).copy()  # 同步翻转标签

            # 随机90度倍数旋转（50%概率） - 在H-W平面旋转
            if np.random.random_sample() > 0.5:
                k = np.random.randint(-3, 4)  # 随机选择旋转次数（-3到3，对应-270到270度）
                image_array = np.rot90(image_array, k, axes=(1, 2)).copy()  # 在高度-宽度平面旋转图像
                label_array = np.rot90(label_array, k, axes=(1, 2)).copy()  # 同步旋转标签

            # 随机亮度缩放（10%概率） - 调整图像整体亮度
            if np.random.random_sample() > 0.9:
                scale = np.float32(np.random.uniform(low=0.9, high=1.1, size=1))  # 随机亮度缩放因子（0.9-1.1）
                image_array = image_array * scale  # 应用亮度调整

            # 随机添加高斯噪声（10%概率） - 模拟传感器噪声或环境干扰
            if np.random.random_sample() > 0.9:
                variance = random.uniform(0, 0.1)  # 随机噪声标准差（0-0.1）
                image_array = image_array + np.random.normal(0.0, variance, image_array.shape).astype(
                    'float32')  # 添加高斯噪声

            # 添加通道维度并转换为PyTorch张量
            image_data = np.expand_dims(image_array, axis=0)
            label_data = np.expand_dims(label_array, axis=0)
            return torch.from_numpy(image_data), torch.from_numpy(label_data)

    def __len__(self):
        """返回数据集大小"""
        return len(self.image_label_pairs)


class Image_Label_valid(Dataset):
    """验证数据集加载器，不进行数据增强"""

    def __init__(self, image_label_pairs):
        """
        初始化验证数据集加载器

        参数:
            image_label_pairs: 包含图像和标签路径的元组列表
        """
        self.image_label_pairs = image_label_pairs

    def __getitem__(self, index):
        """获取单个验证数据样本，不进行数据增强"""

        # 加载图像和标签数据（与训练集相同，但无增强）
        image_path = self.image_label_pairs[index][0]
        label_path = self.image_label_pairs[index][1]
        image_array = np.float32(np.load(image_path))
        label_array = np.float32(np.load(label_path))

        # 添加通道维度并转换为PyTorch张量
        image_data = np.expand_dims(image_array, axis=0)
        label_data = np.expand_dims(label_array, axis=0)
        return torch.from_numpy(image_data), torch.from_numpy(label_data)

    def __len__(self):
        """返回数据集大小"""
        return len(self.image_label_pairs)