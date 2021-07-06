import torch 
import torch.nn as nn 

from py_trans import * 
from modules.my_resnet import resnet50 , resnet34 
import torch.nn.functional as F 

class Identity(nn.Module):
    
    def __init__(self):
        super(Identity,self).__init__()
    
    def forward(self,x):
        return x 


class BertAttnModel(nn.Module):

    def __init__(self, input_h=32, input_w=256, num_class=4001, n_token=64, c_feature=128, is_pretrain=False):
        
        super(BertAttnModel, self).__init__()
        
        d_midle_resnet = 64 
        d_second_resnet = 512

        self.featureExraction = resnet34(h_stride=2, w_stride=1)
        # self.featureExraction = resnet34(h_stride=1 , w_stride=1)
        if c_feature != 2048 :
            self.reduction = nn.Sequential(
                    nn.Conv2d(d_midle_resnet, c_feature,kernel_size=1, stride=1, bias=False),
                    nn.BatchNorm2d(c_feature),
                )
            self.elevation = nn.Sequential(
                    nn.Conv2d(c_feature, d_midle_resnet,kernel_size=1, stride=1, bias=False),
                    nn.BatchNorm2d(d_midle_resnet),
            )
        else :
            self.reduction = Identity()
            self.elevation = Identity()

        # TODO: modify the config 
        bert_cfg = BertConfig(
            hidden_size=c_feature,
            num_hidden_layers=2,
            num_attention_heads=4,
            intermediate_size=512,
            hidden_act="gelu",
            hidden_dropout_prob=0.1,
            attention_probs_dropout_prob=0.1,
            max_position_embeddings=1024        
        )


        self.globAttenBert = BertModel(bert_cfg)

        self.trans_matrix_1 = nn.Parameter(torch.Tensor(c_feature, c_feature))
        self.trans_matrix_2 = nn.Parameter(torch.Tensor(c_feature, c_feature))


        bert_cfg = BertConfig(
            hidden_size=d_second_resnet,
            num_hidden_layers=2,
            num_attention_heads=4,
            intermediate_size=512,
            hidden_act="gelu",
            hidden_dropout_prob=0.1,
            attention_probs_dropout_prob=0.1,
            max_position_embeddings=1024        
        )

        self.sequenAttnBert = BertModel(bert_cfg)

        self.prediction = nn.Linear(c_feature, num_class)
        # self.prediction_ex = nn.Linear(c_feature, num_class)

        if is_pretrain:
            self.loadPretrain()
            print('load pretrain model success !')

    def forward(self,x ):

        visual_feature = self.featureExraction(x, is_midle=True)
        visual_feature = self.reduction(visual_feature)
        
        b,c,*_ = visual_feature.shape

        # b,c,h,w -> b,w,h,c
        visual_feature = visual_feature.permute(0,3,2,1)
        # b,w,h,c -> b,k,c 
        visual_feature = visual_feature.contiguous().view(b,-1,c)
    
        # b,k,c  
        globel_feature= self.globAttenBert(visual_feature)[0]

        # b,k,c -> b,k,c 
        attn_m1 = F.linear(globel_feature, self.trans_matrix_1)
        attn_m1 = torch.tanh(attn_m1)

        # b,k,c -> b,n,k
        attn_m2 = F.linear(attn_m1, self.trans_matrix_2).permute(0,2,1)
        attn_m2 = F.softmax(attn_m2,-1)


        # b,n,k * b,k,c -> b,n,c
        attn_feature = torch.bmm(attn_m2,visual_feature)

        sequen_attn_feature = self.sequenAttnBert(attn_feature)[0]
        
        predict = self.prediction(sequen_attn_feature)

        if self.training : 
            predict_ex = self.prediction_ex(attn_feature)

            for i in range(predict.shape[0]):
                for j in range(predict.shape[1]):
                    _, idx = predict[i,j,:].max(-1)
                    if idx == 1 :
                        predict[i,j,idx+1:] = 0 
                        break
            
            for i in range(predict_ex.shape[0]):
                for j in range(predict_ex.shape[1]):
                    _, idx = predict_ex[i,j,:].max(-1)
                    if idx == 1 :
                        predict_ex[i,j,idx+1:] = 0 
                        break

            return (predict, predict_ex)
        else :
            # predict_ex = self.prediction_ex(attn_feature)
            # return predict_ex

            return predict 

    def loadPretrain(self):
        self.featureExraction.load_state_dict(torch.load('pretrain/my_resnet50.pth'))
        
        nn.init.uniform_(self.trans_matrix_1,0.0,0.02)
        nn.init.uniform_(self.trans_matrix_2,0.0,0.02)
        #  self.trans_matrix_1.uniform_(0.0, 0.02)
        #  self.trans_matrix_2.uniform_(0.0, 0.02)
        #  self.globAttenBert.load_state_dict(torch.load('pretrain/bert-base-chinese-pytorch_model.bin'))



if __name__ == '__main__':
    model = BertAttnModel(is_pretrain=True).cuda()

    images = torch.Tensor(1,3,32,512).cuda()

    import time 
    start = time.time()
    model.eval()
    for _ in range(100):
        print(_, end='\r')
        result = model(images)
    
    print(result[0].shape)
    print('time avg {}'.format((time.time()-start)/100))