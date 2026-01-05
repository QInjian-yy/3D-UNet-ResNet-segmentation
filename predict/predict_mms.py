import os
import torch
import numpy as np
import SimpleITK as sitk
from scipy.ndimage import zoom
from model.UNet3DMMS import UNet3DMMS

# 原始医学图像路径（NIfTI格式）
data_folder = "D:\\PythonProject\\MMS\\test_images_series\\"
# 预测结果保存路径
pred_folder = "D:\\PythonProject\\MMS\\testing_images_pred_new\\"
# 目标体素尺寸（X, Y, Z方向）
new_voxel = [1.3056, 1.3056, 9.5422]
# 处理块大小（block size）
b_nx, b_ny, b_nz = 128, 128, 16
# 滑动步长（stride）
st_nx, st_ny, st_nz = 64, 64, 8
# 填充尺寸（padding）
pad_nx, pad_ny, pad_nz = 32, 32, 4
# 设备选择（GPU优先）
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# 加载预训练模型
model = UNet3DMMS(input_ch=1, output_ch=4).to(device)
model.load_state_dict(
    torch.load("..\\modelsave\\UNet\\MMS\\ResUNet_000241.pth",
               map_location="cuda:0"))
model.eval()  # 设置为评估模式

# 读取原始图像
data_names = sorted(os.listdir(data_folder))
for data_name in data_names:
    print(f"正在处理: {data_name}")
    data_path = os.path.join(data_folder, data_name)
    # 使用SimpleITK读取图像
    image_sitk = sitk.ReadImage(data_path)
    # 转换为numpy数组（维度顺序：Z,Y,X）
    image_array = sitk.GetArrayFromImage(image_sitk)
    # 获取原始体素尺寸（X,Y,Z方向）
    old_voxel = image_sitk.GetSpacing()

    # 将图像重采样到目标体素尺寸
    image_resized = zoom(
        input=image_array,
        zoom=[old_voxel[2] / new_voxel[2], old_voxel[1] / new_voxel[1], old_voxel[0] / new_voxel[0]],
        order=3  # 三次样条插值
    )

    # 去除噪声或异常亮/暗区域，保留主要信息
    q5 = np.quantile(image_resized, 0.05)  # 计算第5百分位像素值
    q95 = np.quantile(image_resized, 0.95)  # 计算第95百分位像素值
    image_resized[image_resized < q5] = q5  # 将所有小于q5的像素设置为q5
    image_resized[image_resized > q95] = q95  # 将所有大于q95的像素设置为q95

    # 图像归一化
    image_normalized = (image_resized - np.mean(image_resized)) / np.std(image_resized)
    # 转换为32位浮点数（PyTorch深度学习模型常用格式）
    image_normalized = np.float32(image_normalized)

    # 对图像进行填充以处理边界条件
    image_padded = np.pad(
        image_normalized,
        ((pad_nz, pad_nz), (pad_ny, pad_ny), (pad_nx, pad_nx)),
        mode="constant",
        constant_values=0
    )

    # 获取填充后图像的尺寸
    v_nx = image_padded.shape[2]  # X维度（列数）
    v_ny = image_padded.shape[1]  # Y维度（行数）
    v_nz = image_padded.shape[0]  # Z维度（切片数）

    # 计算每个维度上的块数量
    blks_nx = np.int32(np.floor((v_nx - b_nx) / st_nx) + 1)
    blks_ny = np.int32(np.floor((v_ny - b_ny) / st_ny) + 1)
    blks_nz = np.int32(np.floor((v_nz - b_nz) / st_nz) + 1)

    # 初始化预测数组（4个类别 × Z × Y × X）
    label_pred = np.zeros(shape=(4, image_normalized.shape[0], image_normalized.shape[1], image_normalized.shape[2]))

    # 遍历3D空间中所有可能的块位置
    for z_idx in np.arange(0, blks_nz):
        # 计算Z维度起始位置，防止越界
        z_start = np.min((z_idx * st_nz, v_nz - b_nz))
        z_start_pred = np.min((z_idx * b_nz / 2, label_pred.shape[1] - b_nz / 2))
        z_start_pred = int(z_start_pred)

        for y_idx in np.arange(0, blks_ny):
            # 计算Y维度起始位置，防止越界
            y_start = np.min((y_idx * st_ny, v_ny - b_ny))
            y_start_pred = np.min((y_idx * b_ny / 2, label_pred.shape[2] - b_ny / 2))
            y_start_pred = int(y_start_pred)

            for x_idx in np.arange(0, blks_nx):
                # 计算X维度起始位置，防止越界
                x_start = np.min((x_idx * st_nx, v_nx - b_nx))
                x_start_pred = np.min((x_idx * b_nx / 2, label_pred.shape[3] - b_nx / 2))
                x_start_pred = int(x_start_pred)

                # 从填充图像中提取块
                image_patch = image_padded[z_start: z_start + b_nz, y_start: y_start + b_ny, x_start: x_start + b_nx]
                # 重塑为模型输入格式：批次×通道×深度×高度×宽度
                image_patch = np.reshape(image_patch, [1, 1, b_nz, b_ny, b_nx])
                image_patch = torch.from_numpy(image_patch)
                image_patch = image_patch.to(device)

                # 获取模型预测结果
                pred_patch = model(image_patch)

                # 更新预测数组（仅更新块的中心区域，避免边缘效应）
                label_pred[:, z_start_pred: z_start_pred + int(b_nz / 2),
                          y_start_pred: y_start_pred + int(b_ny / 2),
                          x_start_pred: x_start_pred + int(b_nx / 2)] = pred_patch[0][:, 4:12, 32:96, 32:96].cpu().detach().numpy()

    # --------------------------- 后处理及保存结果 ---------------------------
    # 沿类别维度取argmax，获取每个体素的预测类别（形状：Z×Y×X）
    label_pred = np.argmax(label_pred, axis=0)

    # 将预测结果重采样回原始体素尺寸（使用最近邻插值以保留离散类别标签）
    label_resized = zoom(
        input=label_pred,
        zoom=[new_voxel[2] / old_voxel[2], new_voxel[1] / old_voxel[1], new_voxel[0] / old_voxel[0]],
        order=0  # 最近邻插值（适用于离散标签）
    )

    # 转换为uint8类型（适用于医学图像标签存储）
    label_resized = np.uint8(label_resized)

    # 将预测结果转换为SimpleITK图像并设置元数据
    label_resized_sitk = sitk.GetImageFromArray(label_resized)  # 数组转图像（维度顺序Z,Y,X）
    label_resized_sitk.SetOrigin(image_sitk.GetOrigin())  # 设置原点坐标
    label_resized_sitk.SetSpacing(image_sitk.GetSpacing())  # 设置体素尺寸（恢复原始尺寸）
    label_resized_sitk.SetDirection(image_sitk.GetDirection())  # 设置方向矩阵

    # 保存预测结果为NIfTI文件
    sitk.WriteImage(label_resized_sitk, os.path.join(pred_folder, data_name))