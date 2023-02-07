import torch
from torch import nn

# Define the model architecture
class Pix2pixModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(Pix2pixModel, self).__init__()
        self.fc = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        
        
    def forward(self, x):
        x = x.view(-1, self.fc.in_features) # reshape the input tensor to have the correct shape
        x = torch.relu(self.fc(x))
        x = self.fc2(x)
        return x

# Initialize the model
model = Pix2pixModel(10, 100, 10)

x = torch.randn(100, 10)
y = model(x)
# Load the state dict
state_dict = torch.load("E:/Development/Qgis plugin/lcp/pretrained_model/latest_net_G.pth")

# Filter the state dict to only contain keys that match the model architecture
new_state_dict = {}
for key in model.state_dict().keys():
    if key in state_dict:
        new_state_dict[key] = state_dict[key]

# Load the filtered state dict into the model
model.load_state_dict(new_state_dict, strict=False)
