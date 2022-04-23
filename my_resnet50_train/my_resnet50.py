import torch.nn as nn
from torch.nn import functional as F


# 基本卷积层
class ResNet50BasicBlock(nn.Module):
    def __init__(self, in_channel, outs, kernel_size, stride, padding):
        super(ResNet50BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channel, outs[0], kernel_size=kernel_size[0], stride=stride[0], padding=padding[0])
        self.bn1 = nn.BatchNorm2d(outs[0])
        self.conv2 = nn.Conv2d(outs[0], outs[1], kernel_size=kernel_size[1], stride=stride[0], padding=padding[1])
        self.bn2 = nn.BatchNorm2d(outs[1])
        self.conv3 = nn.Conv2d(outs[1], outs[2], kernel_size=kernel_size[2], stride=stride[0], padding=padding[2])
        self.bn3 = nn.BatchNorm2d(outs[2])

    def forward(self, input_image):
        y = input_image
        out_image = self.conv1(input_image)
        out_image = F.relu(self.bn1(out_image))
        out_image = self.conv2(out_image)
        out_image = F.relu(self.bn2(out_image))
        out_image = self.conv3(out_image)
        out_image = self.bn3(out_image)
        out_image = F.relu(out_image + y)
        return out_image


# 经过下采样的卷积层
class ResNet50DownBlock(nn.Module):
    def __init__(self, in_channel, outs, kernel_size, stride, padding):
        super(ResNet50DownBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channel, outs[0], kernel_size=kernel_size[0], stride=stride[0], padding=padding[0])
        self.bn1 = nn.BatchNorm2d(outs[0])
        self.conv2 = nn.Conv2d(outs[0], outs[1], kernel_size=kernel_size[1], stride=stride[1], padding=padding[1])
        self.bn2 = nn.BatchNorm2d(outs[1])
        self.conv3 = nn.Conv2d(outs[1], outs[2], kernel_size=kernel_size[2], stride=stride[2], padding=padding[2])
        self.bn3 = nn.BatchNorm2d(outs[2])
        self.extra = nn.Sequential(
            nn.Conv2d(in_channel, outs[2], kernel_size=1, stride=stride[3], padding=0),
            nn.BatchNorm2d(outs[2])
        )

    def forward(self, input_image):
        x_shortcut = self.extra(input_image)
        y = self.conv1(input_image)
        y = self.bn1(y)
        y = F.relu(y)
        y = self.conv2(y)
        y = self.bn2(y)
        y = F.relu(y)
        y = self.conv3(y)
        y = self.bn3(y)
        y = F.relu(x_shortcut + y)
        return y


class ResNet50_Improve(nn.Module):
    def __init__(self):
        super(ResNet50_Improve, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = nn.Sequential(
            # 进行一次下采样卷积以及2次基本卷积层
            ResNet50DownBlock(64, outs=[64, 64, 256], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1], padding=[0, 1, 0]),
            ResNet50BasicBlock(256, outs=[64, 64, 256], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1], padding=[0, 1, 0]),
            ResNet50BasicBlock(256, outs=[64, 64, 256], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1], padding=[0, 1, 0]),
        )

        self.layer2 = nn.Sequential(
            # 进行一次下采样卷积以及3次基本卷积层
            ResNet50DownBlock(256, outs=[128, 128, 512], kernel_size=[1, 3, 1], stride=[1, 2, 1, 2], padding=[0, 1, 0]),
            ResNet50BasicBlock(512, outs=[128, 128, 512], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
            ResNet50BasicBlock(512, outs=[128, 128, 512], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
            ResNet50BasicBlock(512, outs=[128, 128, 512], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1], padding=[0, 1, 0])
        )

        self.layer3 = nn.Sequential(
            # 进行一次下采样卷积以及3次基本卷积层
            ResNet50DownBlock(512, outs=[256, 256, 1024], kernel_size=[1, 3, 1], stride=[1, 2, 1, 2],
                              padding=[0, 1, 0]),
            ResNet50BasicBlock(1024, outs=[256, 256, 1024], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
            ResNet50BasicBlock(1024, outs=[256, 256, 1024], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
            ResNet50BasicBlock(1024, outs=[256, 256, 1024], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
            # 再一次进行下采样卷积以及3次基本卷积层
            ResNet50DownBlock(1024, outs=[512, 512, 1024], kernel_size=[1, 3, 1], stride=[1, 2, 1, 2],
                              padding=[0, 1, 0]),
            ResNet50BasicBlock(1024, outs=[256, 256, 1024], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
            ResNet50BasicBlock(1024, outs=[256, 256, 1024], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
            ResNet50BasicBlock(1024, outs=[256, 256, 1024], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
        )

        self.layer4 = nn.Sequential(
            ResNet50DownBlock(1024, outs=[512, 512, 2048], kernel_size=[1, 3, 1], stride=[1, 2, 1, 2],
                              padding=[0, 1, 0]),
            ResNet50BasicBlock(2048, outs=[512, 512, 2048], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0]),
            ResNet50BasicBlock(2048, outs=[512, 512, 2048], kernel_size=[1, 3, 1], stride=[1, 1, 1, 1],
                               padding=[0, 1, 0])
        )
        self.avgpool = nn.AdaptiveAvgPool2d(output_size=(1, 1))
        # 线性层对于resnet50来说进行了改动，加深了线性层网络的结构
        self.fc0 = nn.Linear(2048, 512)
        self.drop1 = nn.Dropout(0.15)
        self.fc1 = nn.Linear(512, 16)
        self.drop2 = nn.Dropout(0.15)
        self.fc3 = nn.Linear(16, 4)

    def forward(self, x):
        out_image = self.conv1(x)
        out_image = self.maxpool(out_image)
        out_image = self.layer1(out_image)
        out_image = self.layer2(out_image)
        out_image = self.layer3(out_image)
        out_image = self.layer4(out_image)
        out_image = self.avgpool(out_image)
        out_image = out_image.reshape(x.shape[0], -1)
        out_image = self.fc0(out_image)
        out_image = self.drop1(out_image)
        out_image = self.fc1(out_image)
        out_image = self.drop2(out_image)
        out_image = self.fc3(out_image)
        return out_image
