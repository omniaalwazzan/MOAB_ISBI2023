import timm 
import torch
import torch.nn as nn
import math
from torchvision import models


class Linear_Layer(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.Linear_ = nn.Sequential(
            nn.Linear(in_channels,out_channels),
            nn.ReLU(inplace=True),
            nn.LayerNorm(out_channels)
            )

    def forward(self, x):
        return self.Linear_(x)
    
class MLP_Genes(nn.Module):
    def __init__(self, num_class=3):
        super(MLP_Genes, self).__init__()
        self.layer_1 = Linear_Layer(80, 80)
        self.layer_2 = Linear_Layer(80, 40)
        self.layer_3 = Linear_Layer(40, 32)
        self.dropout = nn.Dropout(p=0.1)
    def forward(self, x):
        x = self.layer_1(x)
        x = self.layer_2(x)
        x = self.dropout(x) 
        x = self.layer_3(x)
        x = self.dropout(x)
        return x




class convNext(nn.Module):
    def __init__(self, n_classes=32):
        super().__init__()
        convNext = models.convnext_base(pretrained=True)
        convNext.avgpool = nn.AdaptiveAvgPool2d((1))
        convNext.classifier = nn.Sequential(nn.Flatten(1, -1),
                                            nn.Dropout(p=0.2),
                                            nn.Linear(in_features=1024, out_features=n_classes)
                                            )
        self.base_model = convNext

        #self.sigm = nn.Sigmoid()

    def forward(self, x):
        #print(x.shape)

        x = self.base_model(x)
        #print(x.shape)
        return x





class stand_add_parm(nn.Module):
    def __init__(self, model_image,model_gens, nb_classes=3):
        super(stand_add_parm, self).__init__()
        self.model_image =  model_image
        self.model_gens = model_gens 

        self.fc = nn.Linear(32,85) # project this to match the same parameters as outer addition
        self.layer_out = nn.Linear(85, nb_classes) 

    
    def forward(self, x1,x3):
        x1 = self.model_image(x1)
        
        x3 = self.model_gens(x3)
        x3 = x3.view(x3.size(0), -1) 

        x = torch.add(x3,x1)
        x = self.fc(x)        
        x = self.layer_out(x)

        return x
    
    
from torchinfo import summary 
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
mlp = MLP_Genes()
img = convNext()
model = stand_add_parm(img,mlp)  
model.to(device=DEVICE,dtype=torch.float)
print(summary(model,[(8,3, 224, 224),(8,80)]))
