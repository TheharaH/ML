# Import necessary libraries
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from PIL import Image

# Step 1: Load the CSV file
csv_file = "/path/to/your/dataset.csv"  # Replace with your file path
df = pd.read_csv(csv_file)

# Step 2: Split dataset into training and testing
train_df, test_df = train_test_split(df, test_size=0.3, random_state=42)


# Step 3: Define a custom dataset class
class BirdDataset(Dataset):
    def __init__(self, dataframe, transform=None):
        self.dataframe = dataframe
        self.transform = transform

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        img_path = self.dataframe.iloc[idx, 0]  # Assuming first column has file paths
        label = self.dataframe.iloc[idx, 1]  # Assuming second column has labels
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label


# Step 4: Define transforms for AlexNet (224x224 input size)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Step 5: Create DataLoader objects
train_dataset = BirdDataset(train_df, transform=transform)
test_dataset = BirdDataset(test_df, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Step 6: Load prebuilt AlexNet model and modify it
model = models.alexnet(pretrained=True)
model.classifier[6] = nn.Linear(4096, 1)  # Assuming binary classification
model = model.to("cuda" if torch.cuda.is_available() else "cpu")

# Step 7: Define loss and optimizer
criterion = nn.BCEWithLogitsLoss()  # Use BCE for binary classification
optimizer = optim.Adam(model.parameters(), lr=0.001)


# Step 8: Train the model
def train_model(model, train_loader, criterion, optimizer, epochs=10):
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for images, labels in train_loader:
            images = images.to("cuda" if torch.cuda.is_available() else "cpu")
            labels = labels.to("cuda" if torch.cuda.is_available() else "cpu").float()

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs.squeeze(), labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
        print(f"Epoch {epoch + 1}, Loss: {running_loss / len(train_loader)}")


train_model(model, train_loader, criterion, optimizer, epochs=10)


# Step 9: Evaluate the model
def evaluate_model(model, test_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to("cuda" if torch.cuda.is_available() else "cpu")
            labels = labels.to("cuda" if torch.cuda.is_available() else "cpu").float()
            outputs = model(images)
            predictions = torch.round(torch.sigmoid(outputs.squeeze()))
            correct += (predictions == labels).sum().item()
            total += labels.size(0)
    print(f"Accuracy: {correct / total * 100:.2f}%")


evaluate_model(model, test_loader)
