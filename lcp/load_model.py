import torch

def load_model(model_path):
    # Load the model weights
    model = torch.load(model_path)
    return model

# Call the load_model function and pass the path to the model weights file
model = load_model("E:/Development/Qgis plugin/lcp/pretrained_model/latest_net_G.pth")
