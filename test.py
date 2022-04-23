import torch
from my_resnet50_train.my_resnet50 import ResNet50_Improve
from PIL import Image
import torchvision
from data_operate import *
from my_resnet18_train.my_resnet18 import My_resnet_18
from my_resnet18_train.data_obtain import *
import time


# 参数选择
# 需要测试得图片路径

def pic_recognize():
    test_list = []
    list_y = []
    list_x = []
    list_z = []
    test_img_path = os.listdir(r'C:\Users\sunshenao\deeplearn\project\WebTest\refuse_classification\static\upload\icon')
    # test_img_path = r'D:\refuse_classification_extra\refuse_classification\static\upload\icon'
    for i in test_img_path:
        test_list.append(r'C:\Users\sunshenao\deeplearn\project\WebTest\refuse_classification\static\upload\icon' + '/' + i)
    print(test_list)
    # test_list.append()

    model50_path = r'./my_resnet50_train/model.pth'  # resnet50模型参数位置
    mdoel18_path = r'my_resnet18_train/model.pth'  # resnet18模型参数位置
    dict_path = r'./my_resnet18_train/dict1.txt'  # dict1.txt保存位置
    class_to_index = {'可回收垃圾': 0, '有害垃圾': 1, '厨余垃圾': 2, '其他垃圾': 3}
    print('------------------------------------加载模型----------------------------------------')
    # 开始加载数据
    file = open(dict_path, 'r', encoding='utf-8')
    list2 = file.readlines()
    out_num = int(list2[-1])
    dict1 = {}
    for fields in list2[:-1]:
        fields = fields.strip()
        fields = fields.strip("\n")
        fields = fields.split(":")
        dict1[fields[0]] = int(fields[1])
    file.close()
    # print(dict1, out_num)
    model50 = ResNet50_Improve()
    model50.load_state_dict(torch.load(model50_path, map_location='cpu'))
    model18 = My_resnet_18(out_num=out_num)
    model18.load_state_dict(
        torch.load(mdoel18_path, map_location='cpu'))
    print('------------------------------------加载模型----------------------------------------')
    # 循环遍历测试列表中的路径
    first = time.time()
    for i in range(len(test_list)):
        images_path = test_list[i]
        img = default_loader(images_path,train=False)
        img = torch.reshape(img, (1, 3, 224, 224))
        # print(img.shape)
        # print(class_to_index)
        model50.eval()
        with torch.no_grad():
            output = model50(img)
        output = int(output.argmax(1))
        # 四分类结果根据字典转化为汉字描述
        end50 = list(class_to_index.keys())[list(class_to_index.values()).index(output)]
        if end50 == '可回收垃圾':
            model18.eval()
            with torch.no_grad():
                output1 = model18(img)
                output1 = int(output1.argmax(1))
            # 细分类结果根据字典转化为汉字描述
            end18 = list(dict1.keys())[list(dict1.values()).index(output1)]
            # print(images_path)
            print('{0}中的{1}'.format(end50, end18) + images_path)
            lis_ = images_path.split('/')
            list_x.append('{0}中的{1}'.format(end50, end18))
            list_y.append(lis_[1])

        else:
            print('{0}'.format(end50))
            lis_ = images_path.split('/')
            list_x.append('{0}'.format(end50))
            list_y.append(lis_[1])
    end = time.time()
    print('时间为：', end - first)
    return list_x, list_y


