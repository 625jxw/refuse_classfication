import torchvision
from my_resnet50 import *
import ssl
from torch.utils.tensorboard import SummaryWriter
from data_operate import *
import time
import torch
from PIL import ImageFile
import random
import os
from sklearn.metrics import cohen_kappa_score, hamming_loss, jaccard_score
import numpy as np
from torch.nn import functional as F

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
ImageFile.LOAD_TRUNCATED_IMAGES = True
# 取消全局认证
ssl._create_default_https_context = ssl._create_unverified_context

# 可改变参数字典
parameter_50 = {
    'data_path': 'C:/Users/sunshenao/deeplearn/data/rubbish_catalog',  # 数据路径
    'tensorboard_save_path': '/tmp/pycharm_project_692/my_resnet50_train/logs_1/loss_function/CrossEntropy',    # tensorboard图保存路径
    'train_device': 'cuda',  # 选择使用什么设备训练网络，可选'cpu'和 'cuda'
    'epoch': 2,  # 训练的epoch轮数
    'loss_function': 'CrossEntropy',  # 损失函数选择，可以选择CrossEntropy,MSELoss,L1Loss
    'learn_rate': 0.0001,  # 学习率
    'CosineAnnealing': True,  # 是否对学习率使用余弦退火算法改动
    'lr_cos_period': 1,  # 前一个参数为True改变该参数才有用，学习率根据余弦退火公式变化，该参数为改变余弦退火算法的周期
    'optim': "RMSprop",  # 优化器的选择，可以选择Adam,Momentum,SGD,RMSprop,Adagrad
    'model_save_path': './model.pth',  # 模型参数文件保存路径
    'batch_size': 8,  # batch_size数量
    'num_worker': 0,  # num_worker数量
    'use_random_or_not': True
}

# 主函数
if __name__ == '__main__':
    # 图片存在路径
    # path = 'C:/Users/51730/Desktop/rubbish_catalog'
    path = parameter_50['data_path']
    # path = '/data/qiucx/rubbish_catalog'
    write = SummaryWriter(parameter_50['tensorboard_save_path'])
    # 如果选择使用cuda训练先测试能够使用gpu，能就使用，不能则返回错误并且改用cpu
    if parameter_50['train_device'] == 'cuda':
        if torch.cuda.is_available():
            device = torch.device('cuda')
        else:
            device = torch.device('cpu')
            print('无法使用gpu，改用cpu')
    elif parameter_50['train_device'] == 'cpu':
        print('使用cpu')
        device = torch.device('cpu')
    else:
        device = torch.device('cpu')
        print('你输入了违规的字符,我们自动给您设置为cpu')

    # 模型加载,断点续训
    if os.path.exists(parameter_50['model_save_path']):
        print('------------------------------------------加载模型参数--------------------------------------------')
        model = ResNet50_Improve()
        model.load_state_dict(torch.load(parameter_50['model_save_path']))
        print('------------------------------------------加载模型完毕--------------------------------------------')
    else:
        print('-------------------------------------------创建新模型---------------------------------------------')
        model = ResNet50_Improve()
        print('-----------------------------------------新模型创建完毕--------------------------------------------')
    # 将模型加载到gpu上运行
    mdoel = model.to(device)

    # 选择损失函数
    if parameter_50['loss_function'] == 'CrossEntropy':
        loss_fn = torch.nn.CrossEntropyLoss()
        print('loss选择CrossEntropy')
    elif parameter_50['loss_function'] == 'L1Loss':
        loss_fn = torch.nn.L1Loss()
        print('loss选择L1loss')
    elif parameter_50['loss_function'] == 'MSELoss':
        loss_fn = torch.nn.MSELoss()
        print('loss选择MSELoss')
    else:
        print('输入了违法字符，我们自动选择了CrossEntropyLoss')
        loss_fn = torch.nn.CrossEntropyLoss()
    loss_fn = loss_fn.to(device)

    # 设置学习率
    learn_rate = parameter_50['learn_rate']
    print("初始学习率为:", learn_rate)
    if parameter_50['optim'] == 'Momentum':
        print('选用的优化器为Momentum')
        # 优化器的选择,优化方式为mini-batch Momentum
        optim = torch.optim.SGD(model.parameters(), lr=learn_rate, momentum=0.8, nesterov=True)
    elif parameter_50['optim'] == 'Adam':
        print('选用的优化器为Adam')
        # 优化器的选择,优化方式为Adam
        optim = torch.optim.Adam(model.parameters(), lr=learn_rate, betas=(0.9, 0.999), weight_decay=5e-4)
    elif parameter_50['optim'] == 'SGD':
        print('选用的优化器为SGD')
        # 优化器的选择,优化方式为SGD
        optim = torch.optim.SGD(model.parameters(), lr=learn_rate)
    elif parameter_50['optim'] == 'RMSprop':
        print('选用的优化器为RMSprop')
        # 优化器的选择,优化方式为RMSprop
        optim = torch.optim.RMSprop(model.parameters(), lr=learn_rate, alpha=0.9)
    elif parameter_50['optim'] == 'Adagrad':
        print('选用的优化器为Adagrad')
        # 优化器的选择,优化方式为Adagrad，权重衰减
        optim = torch.optim.Adagrad(model.parameters(), lr=learn_rate, weight_decay=5e-4)
    else:
        print('你输入了违法字符,我们设置为Adam优化器')
        # 优化器的选择,优化方式为Adam
        optim = torch.optim.Adam(model.parameters(), lr=learn_rate, betas=(0.9, 0.999), weight_decay=5e-4)

    # 学习率采用退火余弦算法改变
    if parameter_50['CosineAnnealing']:
        print('余弦退火')
        torch.optim.lr_scheduler.CosineAnnealingLR(optim, parameter_50['lr_cos_period'], eta_min=0, last_epoch=-1)
    elif not parameter_50['CosineAnnealing']:
        print('lr静态')
        pass
    else:
        print('你输入了违法字符')

    # 迭代轮数
    epoch = parameter_50['epoch']

    # 记录目前最佳值以便与最新得准确率比较以获得最佳模型
    old_accuracy = 0
    for i in range(1, epoch + 1):
        random_num = random.randint(0, 10000)
        # random_num = 1
        # 训练集
        file_train, file_test = image_path_list(path, seed_num=random_num)
        target_train, target_test = image_to_target(path, seed_num=random_num)
        print(len(file_train), len(file_test), len(target_train), len(target_test))
        train_data = trainset(train_path=file_train, number_train=target_train)
        test_data = trainset(train_path=file_test, number_train=target_test,train = False)

        # 获取长度
        train_lenth = len(train_data)
        test_lenth = len(test_data)
        print(test_lenth)
        print(train_lenth)
        # 数据加载
        train_dataloader = DataLoader(train_data, batch_size=parameter_50['batch_size'],
                                      num_workers=parameter_50['num_worker'])
        test_dataloader = DataLoader(test_data, batch_size=parameter_50['batch_size'],
                                     num_workers=parameter_50['num_worker'])
        train_loss_all = 0
        batch_loss_all = 0
        star_time = time.time()
        print("--------------------------第{0}轮测试---------------------------------".format(i))
        # 模型训练
        total_train_step = 0
        model.train()
        for data in train_dataloader:
            imgs, targets = data
            imgs = imgs.to(device)
            targets = targets.to(device)
            output = model.forward(imgs)
            if parameter_50['loss_function'] == 'L1Loss' or parameter_50['loss_function'] == 'MSELoss':
                result_loss = loss_fn(output, F.one_hot(targets, num_classes=4).long())
            elif parameter_50['loss_function'] == 'CrossEntropy':
                result_loss = loss_fn(output, targets)
            else:
                print('loss损失函数的选择输入了违法字符')
            train_loss_all = train_loss_all + result_loss
            batch_loss_all = batch_loss_all + result_loss
            # 梯度归零
            optim.zero_grad()
            # 获取逆向传播的梯度以便后续更新参数
            result_loss.backward()
            # 更新参数
            optim.step()
            total_train_step += 1
            if total_train_step % 50 == 0:
                print("训练batch:{0},loss:{1}".format(total_train_step, batch_loss_all))
                batch_loss_all = 0
        end_time = time.time()
        print('一轮训练时间{0}'.format(end_time - star_time))
        print('训练集上平均loss{0}'.format(train_loss_all / train_lenth))
        write.add_scalar('train_loss', train_loss_all / train_lenth, i)
        # 加载到tensoboard里面画图

        # 模型测试
        model.eval()
        total_test_loss = 0
        total_accuracy = 0
        y_predict = torch.tensor([]).long().to(device)
        y_true = torch.tensor([]).long().to(device)
        with torch.no_grad():
            for data in test_dataloader:
                imgs, targets = data
                # print(targets)
                imgs = imgs.to(device)
                targets = targets.to(device)
                output = model.forward(imgs)
                # print('output',output.argmax(1))
                if parameter_50['loss_function'] == 'L1Loss' or parameter_50['loss_function'] == 'MSELoss':
                    result_loss = loss_fn(output, F.one_hot(targets, num_classes=4).float())
                elif parameter_50['loss_function'] == 'CrossEntropy':
                    result_loss = loss_fn(output, targets)
                else:
                    print('loss损失函数的选择输入了违法字符')
                total_test_loss += result_loss
                accuracy = (output.argmax(1) == targets).sum()
                total_accuracy += accuracy
                y_true = torch.cat([y_true, targets], dim=0)
                y_predict = torch.cat([y_predict, output.argmax(1)], dim=0)
        y_true.reshape(-1)
        y_predict.reshape(-1)
        y_true = y_true.cpu()
        y_predict = y_predict.cpu()
        print(y_true)
        print("测试集上的loss:{0}".format(total_test_loss))
        print(test_lenth, total_accuracy.item())
        print("整体测试集上的accuracy:{0}".format(total_accuracy.item() / test_lenth))
        kapa = cohen_kappa_score(y_true, y_predict)
        hamming = hamming_loss(y_true, y_predict)
        jaccard = jaccard_score(y_true, y_predict, average='macro')
        print('kapa:{0},hamming:{1},jaccard:{2}'.format(kapa, hamming, jaccard))
        write.add_scalar('test_loss', total_test_loss / test_lenth, i)
        write.add_scalar('test_accuracy', total_accuracy.item() / test_lenth, i)
        write.add_scalar('kappaa', kapa, i)
        write.add_scalar('hamming', hamming, i)
        write.add_scalar('jaccard', jaccard, i)
        if old_accuracy < total_accuracy.item():
            torch.save(model.state_dict(), './model.pth')
            print("模型已保存")
            old_accuracy = total_accuracy.item()
    write.close()
