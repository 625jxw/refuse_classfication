import torch
import os
from my_resnet50 import ResNet50_Improve
from data_operate import default_loader
from my_resnet18 import My_resnet_18
from easydict import EasyDict


def get_dict(path):
    dict_temp = {}
    with open(path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            name, num = line.split(':')
            dict_temp.update({int(num): name})
    return dict_temp


def image_to_target_test(path):
    target_list = []
    classificasion_list = os.listdir(path)
    for i in classificasion_list:
        target_list.append(path + '/' + i)
    return target_list


def predict(parameter):
    parameter = EasyDict(parameter)
    if parameter.is_GPU:  # 是否使用GPU
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    if parameter.is_china:  # 得到字典
        classficition = get_dict(parameter.classficition_path)

    # 创建模型
    model50 = ResNet50_Improve()
    # 导入模型参数文件
    model50.load_state_dict(torch.load(parameter.model50_path))
    model50 = model50.to(device)
    model50.eval()

    if parameter.is_classficition:  # 是否进行小分类
        model18 = My_resnet_18(29)
        model18.load_state_dict(torch.load(parameter.model18_path))
        model18 = model18.to(device)
        model18.eval()

    # 下面开始对图片数据进行预测
    y_predict = []
    img_path = image_to_target_test(parameter.data_path)
    with torch.no_grad():
        for i in img_path:
            im = default_loader(i, train=False)
            im = im.unsqueeze(0).to(device)  # 要和模型的相同
            output50 = model50.forward(im)
            res = output50.argmax(1).cpu().detach().numpy()[0]
            if parameter.is_classficition and not res:
                output18 = model18.forward(im)
                res = 100 + output18.argmax(1).cpu().detach().numpy()[0]
            if parameter.is_china:
                if res < 5:
                    y_predict.append(classficition.get(res))
                else:
                    y_predict.append('可回收垃圾中的' + classficition.get(res))
            else:
                y_predict.append(res)
    return y_predict


if __name__ == "__main__":
    # 此程序为测试接口
    # 将图片放入test_image文件夹下，程序可自动识别文件夹下的图片，并将结果返回
    # 同时可以调节下面的参数对模型的预测方式进行修改
    # 注意test_image文件夹下，必须且只有图片

    # 可回收垃圾: 0
    # 有害垃圾:  1
    # 厨余垃圾:  2
    # 其他垃圾:  3
    # 对可回收垃圾进行分类时，返回的数字均为大于等于100的数值，具体类别请参照文件classficition.txt

    parameter = {
        'data_path': './test_image',  # 测试图片存放的路径
        'model50_path': './my_resnet50_train/model.pth',  # 模型ResNet50的参数
        'model18_path': './my_resnet18_train/model.pth',  # 模型ResNet18的参数
        'classficition_path': './classficition.txt',  # 汉字对应的字典
        'is_classficition': True,  # 是否在对可回收垃圾进行细分类
        'is_GPU': False,  # 是否使用GPU
        'is_china': True,  # 是否将结果变为汉字
    }

    print(predict(parameter))
