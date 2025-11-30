使用M&Ms数据集，包含Training、Validation、Testing，训练集中只用到了其中Labeled部分进行监督学习。  
链接https://mega.nz/folder/FxAmhbRJ#Dwugf8isRSR9CCZ6Qnza4w

/prepare/get_m&ms_dataset.py
    对Training、Validation、Testing数据集分别处理，把每个样本的图像及标注分开放到不同目录结构下
    1.Training里面的图像统一放在train_images目录下，里面的标注统一放在train_masks目录下(一一对应)
    2.Validation里面的图像统一放在validation_images目录下，里面的标注统一放在validation_masks目录下(一一对应)
    3.Testing里面的图像统一放在test_images目录下，里面的标注统一放在test_masks目录下(一一对应)