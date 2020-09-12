import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import LeNet
import numpy as np
from torch.optim import lr_scheduler

def save_model(model,optimizer,epoch):
    
    path = '../models/'+'lenet_%d.pth'%(epoch)
    print('save net:',path)
    torch.save(model.state_dict(),path)


def load_model(path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net = LeNet.Net().to(device)
    net.load_state_dict(torch.load(path))
    return net
    


def data_and_lenet_define():
    #use gpu to load and train data
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    #define transform：
    #1:resize MNIST data to 32x32, so adapter to LeNet struct
    #2：transform PIL.Image to  torch.FloatTensor
    resize = 32
    transform = transforms.Compose([transforms.Resize(size=(resize, resize)),
                                    torchvision.transforms.ToTensor()
                                    ])
     
    train_data = torchvision.datasets.MNIST(root="../datas",    #data dir 
                                            train=True,               #it is train data
                                            transform=transform,      #use defined transform
                                            download=False)            #use local data
    test_data = torchvision.datasets.MNIST(root="../datas",
                                            train=False,
                                            transform=transform,
                                            download=False)

    #define DataLoder,and shuffle data
    train_loader = torch.utils.data.DataLoader(dataset = train_data,batch_size =320 ,shuffle = True)
    test_loader = torch.utils.data.DataLoader(dataset = test_data,batch_size = 10000,shuffle = False)


    #use already define Lenet
    net = LeNet.Net().to(device)
    
    loss_fuc = nn.CrossEntropyLoss() 
    optimizer = optim.Adam(net.parameters(),lr = 0.001,weight_decay = 0.005) 
    return device,train_loader,test_loader,net,loss_fuc,optimizer

def test_net(device,test_loader,net):
    correct = 0
    total = 0
    for data in test_loader:
        test_inputs, labels = data
        test_inputs, labels = test_inputs.to(device), labels.to(device)
        outputs_test = net(test_inputs)#输出的是10000张图片的10个分类值
        #print(outputs_test.shape)
        predict_value, predicted_label = torch.max(outputs_test.data, 1)  #输出每个数据得分最高的那个分类id
        total += labels.size(0) #统计50个batch 图片的总个数
        correct += (predicted_label == labels).sum()  #统计50个batch 正确分类的个数
        print('avg accuracy：%d%%' % ((100 * correct // total)))



def train_net(device,train_loader,test_loader,net,loss_fuc,optimizer):
    #Star train
    EPOCH = 3   #训练总轮数
    adjust_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)#定义学习率衰减函数
    print('start train with epoch:',EPOCH)
    iteration = 0
    for epoch in range(EPOCH):
        sum_loss = 0
        #数据读取
        for i,data in enumerate(train_loader):
            inputs,labels = data
            #有GPU则将数据置入GPU加速
            inputs, labels = inputs.to(device), labels.to(device)   
     
            # 梯度清零
            optimizer.zero_grad()
     
            # 传递损失 + 更新参数
            output = net(inputs)
            loss = loss_fuc(output,labels)
            loss.backward()
            optimizer.step()
            
            iteration = iteration+1
     
            # print loss every 100 iteration
            sum_loss += loss.item()
            if i % 100 == 99:
                lr = optimizer.param_groups[0]["lr"]#get current lr
                #print(lr)
                print('###iteration[:%d],[Epoch:%d],[Lr:%.08f] train loss: %.03f' % (iteration,epoch + 1, lr, sum_loss / 100))
                #用网络测试验证数据
                test_net(device,test_loader,net)
                #保存模型
                save_model(net,optimizer,epoch+1)
                sum_loss = 0.0
                adjust_lr_scheduler.step()#更新学习率




path = '../models/'+'lenet_2.pth'
def load_model_and_test(path):


    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #加载模型
    model = load_model(path)
    #加载数据
    resize = 32
    transform = transforms.Compose([transforms.Resize(size=(resize, resize)),
                                    torchvision.transforms.ToTensor()
                                    ])
    test_data = torchvision.datasets.MNIST(root="../datas",
                                            train=False,
                                            transform=transform,
                                            download=False)

    test_loader = torch.utils.data.DataLoader(dataset = test_data,batch_size = 10000,shuffle = False)
    #开始测试
    test_net(device,test_loader,model)
    #print(model)
    


load_model_and_test(path)


#device,train_loader,test_loader,net,loss_fuc,optimizer = data_and_lenet_define()
#train_net(device,train_loader,test_loader,net,loss_fuc,optimizer)
