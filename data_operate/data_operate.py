import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import random


# 传入路径返回一个存储着所有图片路径的训练列表与测试列表
def image_path_list(path1, seed_num=0):
    path_list = []
    classificasion_list = os.listdir(path1)
    print(classificasion_list)
    # 遍历三次得到该路径下的所有图片路径
    for i in classificasion_list[:4]:
        classificasion_name_list = os.listdir(path1 + '/' + i)
        classificasion_name_path = path1 + '/' + i
        for j in classificasion_name_list:
            image_list = os.listdir(classificasion_name_path + '/' + j)
            image_path = classificasion_name_path + '/' + j
            for k in image_list:
                path_list.append(image_path + '/' + k)
    # 利用随机产生的随机数种子保持打乱后的数据以及标签能够对应上
    random.seed(seed_num)
    random.shuffle(path_list)
    lenth = len(path_list)
    # 以3：7的比例切割成测试集，训练集，测试集为3，训练集为7
    train_path_list = path_list[:int(lenth * 0.7)]
    test_path_list = path_list[int(lenth * 0.7):]
    # 返回测试集，训练集的图片路径
    return train_path_list, test_path_list


# 传入路径返回一个存储着所有图片标签的训练列表，测试列表
def image_to_target(target_num_path, seed_num=0):
    target_list = []
    target_dic = {'kehuishoulaji': 0, 'youhailaji': 1, 'chuyulaji': 2, 'qitalaji': 3}
    classificasion_list = os.listdir(target_num_path)
    # 遍历三次得到该路径下的所有图片路径并且根据文件夹的不同对不同的图片打上对应的标签
    for i in classificasion_list[:4]:  # ubantu
        target = target_dic[i]
        classificasion_name_list = os.listdir(target_num_path + '/' + i)
        classificasion_name_path = target_num_path + '/' + i
        for j in classificasion_name_list:
            image_list = os.listdir(classificasion_name_path + '/' + j)
            for k in image_list:
                target_list.append(target)
    # 利用随机产生的随机数种子保持打乱后的数据以及标签能够对应上
    random.seed(seed_num)
    random.shuffle(target_list)
    lenth = len(target_list)
    # 以3：7的比例切割成测试集，训练集，测试集为3，训练集为7
    train_target_list = target_list[:int(lenth * 0.7)]
    test_target_list = target_list[int(lenth * 0.7):]
    # 返回对应的测试集，训练集标签列表
    return train_target_list, test_target_list


# 对图片三通道数据进行归一化处理的方差与均值，该组数据能够使得数据处于[-1,1]区间，使得网络能够更快趋向于最好的结果
normalize = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)
# 进行数据类型转化和数据归一化
preprocess = {
    'train':transforms.Compose([
                transforms.ToTensor(),
                # transforms.Resize([224, 224]),
                normalize,
                # 对图片进行0.5概率水平翻转
                transforms.RandomHorizontalFlip(0.5),
                # 对图像进行随机垂直翻转
                transforms.RandomVerticalFlip(0.5),
                # 随机旋转图片
                transforms.RandomRotation((-45, 45)),
                # 调整亮度，对比度，饱和度,色相
                transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
            ]),
    'test':transforms.Compose([
        transforms.ToTensor(),
        # transforms.Resize([224, 224]),
        normalize,
    ])
}


# img_pil = np.asanyarray(img_pil)
# img_pil = cv2.GaussianBlur(img_pil, (3, 3), 0)
# img_pil = cv2.Canny(img_pil, 50, 150)
# img_pil = cv2.cvtColor(img_pil, cv2.COLOR_GRAY2RGB)


# 打开图片得到对应的像素数据矩阵，对其进行大小的剪裁使其输入网络的大小能够保持一致
def default_loader(path2, target=None,train = True):
    # 打开图片
    img_pil = Image.open(path2).convert('RGB')
    # 改变图片大小
    img_pil = img_pil.resize((224, 224), Image.ANTIALIAS)
    # 对像素矩阵进行数据类型转化和数据归一化
    # print(path2)
    if train:
        img_tensor = preprocess['train'](img_pil)
    else:
        img_tensor = preprocess['test'](img_pil)

    return img_tensor


# 对上述的图片路径列表和标签列表进行遍历并且对其进行default_loader函数的处理之后返回一个包含了所有的数据tensor，其中每个单元由[data,target]组成
class trainset(Dataset):
    def __init__(self, train_path, number_train, loader=default_loader, seed_num=0,train=True):
        self.images = train_path
        self.target = number_train
        self.loader = loader
        self.seed = seed_num
        self.train = train

    def __getitem__(self, index):
        fn = self.images[index]
        target = self.target[index]
        img = self.loader(fn, target,self.train)
        return [img, target]

    def __len__(self):
        return len(self.images)

# if __name__ == '__main__':
#     file_train, file_test = image_path_list(path)
#     target_train, target_test = image_to_target(path)
#     print(len(file_train), len(file_test), len(target_train), len(target_test))
#     train_data = trainset(train_path=file_train, number_train=target_train)
#     trainloader = DataLoader(train_data, batch_size=4, shuffle=True)
#     for data in trainloader:
#         imgs, targets = data
#         print(imgs, targets)
