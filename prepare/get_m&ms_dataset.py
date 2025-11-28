import os
import shutil

########################################################################################################################
'''
预处理步骤 1
这个脚本的作用是把每一个样本的图像和标注分开放在不同目录下
'''
########################################################################################################################

# 定义数据集路径和保存路径
dataset_folders_folder = "D:\\PythonProject\\MMS\\Testing\\"  # 原始数据集根目录
dataset_folders = sorted(os.listdir(dataset_folders_folder))  # 获取所有样本文件夹并排序
image_save_folder = "D:\\PythonProject\\MMS\\test_images\\"  # 图像文件保存目录
mask_save_folder = "D:\\PythonProject\\MMS\\test_masks\\"  # 标注文件保存目录

# 遍历每个样本文件夹
for dataset_folder in dataset_folders:
    dataset_folder_all = dataset_folders_folder + dataset_folder + "\\"  # 构建完整样本路径
    dataset_file_names = sorted(os.listdir(dataset_folder_all))  # 获取样本内所有文件

    # 遍历样本内的每个文件
    for dataset_file_name in dataset_file_names:
        # 根据文件名判断是标注文件还是图像文件，并复制到相应目录
        if "_gt.nii.gz" in dataset_file_name:  # 标注文件（通常包含"_gt"标识）
            shutil.copy(dataset_folder_all + dataset_file_name, mask_save_folder + dataset_file_name)
        else:  # 图像文件
            shutil.copy(dataset_folder_all + dataset_file_name, image_save_folder + dataset_file_name)