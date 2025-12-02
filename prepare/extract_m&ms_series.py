import os
import numpy as np
import SimpleITK as sitk

########################################################################################################################
'''
预处理步骤 2
由于MMS数据集是序列数据（四维数据），本步骤根据第四维度（时间维度）来判断每个时间点的3D切片标注是否包含四个不同的类别
（左心室、右心室、心肌、背景），并提取符合条件的切片
'''
########################################################################################################################

# 定义数据路径
image_folder = "D:\\PythonProject\\MMS\\test_images\\"  # 原始图像文件夹路径
mask_folder = "D:\\PythonProject\\MMS\\test_masks\\"  # 原始标注文件夹路径
image_save_folder = "D:\\PythonProject\\MMS\\test_images_series\\"  # 处理后图像保存路径
mask_save_folder = "D:\\PythonProject\\MMS\\test_masks_series\\"  # 处理后标注保存路径

# 获取文件夹中所有文件并排序
image_names = sorted(os.listdir(image_folder))  # 图像文件名列表（按文件名排序）
mask_names = sorted(os.listdir(mask_folder))  # 标注文件名列表（按文件名排序）

# 遍历所有图像-标注文件对
for idx in range(len(image_names)):
    print("*******************************************************")
    print("正在处理: ", image_names[idx])
    image_path = image_folder + image_names[idx]

    # 尝试读取图像，如果读取失败则跳过当前文件
    try:
        image_sitk = sitk.ReadImage(image_path)  # 读取医学图像文件
    except RuntimeError:
        continue

    image_array = sitk.GetArrayFromImage(image_sitk)  # 将SimpleITK图像转换为NumPy数组

    # 读取对应的标注文件
    mask_path = mask_folder + mask_names[idx]
    mask_sitk = sitk.ReadImage(mask_path)
    mask_array = sitk.GetArrayFromImage(mask_sitk)

    ####################################################################################################################
    # 处理序列中的每个切片
    for series_idx in range(image_array.shape[0]):
        mask_series_idx = mask_array[series_idx]  # 获取当前切片的标注数据

        # 检查标注是否包含4个不同的标签值（0背景 + 3个器官类别），如果不满足则跳过
        if len(np.unique(mask_series_idx)) != 4:
            continue

        image_series_idx = image_array[series_idx]  # 获取当前切片的图像数据

        ################################################################################################################
        # 将NumPy数组转换回SimpleITK图像格式
        image_series_sitk = sitk.GetImageFromArray(image_series_idx)
        mask_series_sitk = sitk.GetImageFromArray(mask_series_idx)

        # 设置图像的空间间距信息（继承原始图像的间距）
        image_series_sitk.SetSpacing(image_sitk.GetSpacing()[:3])
        mask_series_sitk.SetSpacing(image_sitk.GetSpacing()[:3])

        # 保存处理后的图像和标注
        image_save_path = image_save_folder + image_names[idx][:-7] + "_" + str(series_idx) + ".nii.gz"
        mask_save_path = mask_save_folder + mask_names[idx][:-7] + "_" + str(series_idx) + ".nii.gz"
        sitk.WriteImage(image_series_sitk, image_save_path)
        sitk.WriteImage(mask_series_sitk, mask_save_path)