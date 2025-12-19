import torch
import torch.nn as nn
from torchinfo import summary


class Conv3D_Block(nn.Module):
    def __init__(self, in_feat, out_feat, kernel=3, stride=1, padding=1, residual=True):
        """3D卷积块，包含两个卷积层，可选择是否使用残差连接"""
        super(Conv3D_Block, self).__init__()
        self.conv = nn.Sequential(
            # 第一个卷积层 + BN + ReLU激活
            nn.Conv3d(in_feat, out_feat, kernel_size=kernel, stride=stride, padding=padding, bias=True),
            nn.BatchNorm3d(out_feat),
            nn.ReLU(inplace=True),
            # 第二个卷积层 + BN + ReLU激活
            nn.Conv3d(out_feat, out_feat, kernel_size=kernel, stride=stride, padding=padding, bias=True),
            nn.BatchNorm3d(out_feat),
            nn.ReLU(inplace=True)
        )
        self.residual = residual  # 是否使用残差连接
        if self.residual:
            # 1x1x1卷积用于调整残差连接的通道数，确保与主路径维度匹配
            self.residual_conv = nn.Conv3d(in_feat, out_feat, kernel_size=1, stride=1, padding=0, bias=False)

    def forward(self, x):
        res = x  # 保存输入作为残差
        if self.residual:
            return self.conv(x) + self.residual_conv(res)  # 主路径输出 + 残差连接
        else:
            return self.conv(x)  # 仅返回主路径输出


class Up_Block(nn.Module):
    def __init__(self, init_feat, scale_factor=(2, 2, 2)):
        """上采样块，使用三线性插值和3D卷积减少通道数"""
        super(Up_Block, self).__init__()
        self.up = nn.Upsample(scale_factor=scale_factor, mode="trilinear", align_corners=True)
        # 3x3卷积将通道数减半
        self.conv = nn.Conv3d(init_feat, int(init_feat / 2), kernel_size=3, stride=1, padding=1, bias=True)

    def forward(self, x):
        """前向传播：先上采样，再通过卷积减少通道数"""
        out = self.up(x)
        out = self.conv(out)
        return out


class UNet3DMMS(nn.Module):
    def __init__(self, input_ch=1, output_ch=4, init_feats=16):
        """3D UNet模型，专为心脏MRI分割设计，采用多尺度下采样策略"""
        super(UNet3DMMS, self).__init__()

        # 编码器部分：使用不同kernel的MaxPool3d实现多尺度下采样
        self.pool1 = nn.MaxPool3d(kernel_size=(1, 2, 2), stride=(1, 2, 2))  # 仅在H/W维度下采样
        self.pool2 = nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))  # 在D/H/W维度下采样
        self.pool3 = nn.MaxPool3d(kernel_size=(1, 2, 2), stride=(1, 2, 2))
        self.pool4 = nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))
        self.pool5 = nn.MaxPool3d(kernel_size=(1, 2, 2), stride=(1, 2, 2))

        # 解码器部分：使用Up_Block逐步恢复空间分辨率
        self.up7 = Up_Block(init_feat=init_feats * 32, scale_factor=(1, 2, 2))
        self.up8 = Up_Block(init_feat=init_feats * 16, scale_factor=(2, 2, 2))
        self.up9 = Up_Block(init_feat=init_feats * 8, scale_factor=(1, 2, 2))
        self.up10 = Up_Block(init_feat=init_feats * 4, scale_factor=(2, 2, 2))
        self.up11 = Up_Block(init_feat=init_feats * 2, scale_factor=(1, 2, 2))

        # 卷积块：使用带残差连接的3D卷积块增强特征提取能力
        self.conv1 = Conv3D_Block(in_feat=input_ch, out_feat=init_feats)
        self.conv2 = Conv3D_Block(in_feat=init_feats, out_feat=init_feats * 2)
        self.conv3 = Conv3D_Block(in_feat=init_feats * 2, out_feat=init_feats * 4)
        self.conv4 = Conv3D_Block(in_feat=init_feats * 4, out_feat=init_feats * 8)
        self.conv5 = Conv3D_Block(in_feat=init_feats * 8, out_feat=init_feats * 16)
        self.conv6 = Conv3D_Block(in_feat=init_feats * 16, out_feat=init_feats * 32)  # 瓶颈层

        # 解码器卷积块
        self.conv7 = Conv3D_Block(in_feat=init_feats * 32, out_feat=init_feats * 16)
        self.conv8 = Conv3D_Block(in_feat=init_feats * 16, out_feat=init_feats * 8)
        self.conv9 = Conv3D_Block(in_feat=init_feats * 8, out_feat=init_feats * 4)
        self.conv10 = Conv3D_Block(in_feat=init_feats * 4, out_feat=init_feats * 2)
        self.conv11 = Conv3D_Block(in_feat=init_feats * 2, out_feat=init_feats)

        # 最终1x1x1卷积层：将特征图转换为类别预测
        self.conv12 = nn.Conv3d(init_feats, output_ch, kernel_size=1, stride=1, padding=0)

    def forward(self, x):
        """前向传播：编码器-解码器结构，带跳跃连接"""
        # 编码器路径：特征提取与下采样
        conv1 = self.conv1(x)  # 第一层卷积，保留原始分辨率特征
        pool1 = self.pool1(conv1)

        conv2 = self.conv2(pool1)
        pool2 = self.pool2(conv2)

        conv3 = self.conv3(pool2)
        pool3 = self.pool3(conv3)

        conv4 = self.conv4(pool3)
        pool4 = self.pool4(conv4)

        conv5 = self.conv5(pool4)
        pool5 = self.pool5(conv5)

        conv6 = self.conv6(pool5)  # 瓶颈层，捕获高级抽象特征

        # 解码器路径：上采样与特征融合（跳跃连接）
        up7 = self.up7(conv6)
        conv7 = self.conv7(torch.cat([conv5, up7], dim=1))  # 融合编码器和解码器特征

        up8 = self.up8(conv7)
        conv8 = self.conv8(torch.cat([conv4, up8], dim=1))

        up9 = self.up9(conv8)
        conv9 = self.conv9(torch.cat([conv3, up9], dim=1))

        up10 = self.up10(conv9)
        conv10 = self.conv10(torch.cat([conv2, up10], dim=1))

        up11 = self.up11(conv10)
        conv11 = self.conv11(torch.cat([conv1, up11], dim=1))

        # 最终分类层：将特征图转换为类别预测
        conv12 = self.conv12(conv11)

        return conv12


if __name__ == '__main__':
    # 测试模型结构
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = UNet3DMMS(1, 4).to(device)
    summary(model, (1, 1, 16, 128, 128))  # 打印模型概要信息