import timm
import wandb
import torch
import torch.nn as nn
import torch.optim as optim
import click
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

wandb.init(entity="mlopsproject",project="TheMLOpsProject")

NUM_FINETUNE_CLASSES = 2

@click.group()
def cli():
    pass

@click.command()
@click.option("--learning_rate", default=1e-3, help = 'Learning rate to use for training')
@click.option("--batch_size", default = 64, help = "Batch size for the training and testing dataset")
@click.option("--epochs", default = 5, help = "Set the number of epochs")
@click.option("--model_arch", default = 'resnet18', help = "Model architecture available form TIMM")
@click.option("--optimizer_select", default = 'Adam', help = "Optimizer available from torch.optim")
def train(learning_rate, batch_size, epochs, model_arch, optimizer_select):

    config = wandb.config          # Initialize config
    config.batch_size = batch_size
    config.lr = learning_rate
    config.epochs = epochs   
    config.model_arch = model_arch
    config.optimizer_select = optimizer_select

    print("Training day and night")

    # Load model
    model = timm.create_model(model_arch, pretrained=True,num_classes=NUM_FINETUNE_CLASSES)

    # Set optimizer
    if optimizer_select == 'Adam':
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    elif optimizer_select == 'SGD':
        optimizer = optim.SGD(model.parameters(), lr=learning_rate)


    # Set loss function
    criterion = nn.CrossEntropyLoss()

    # Use DataLoader to load dataset
    train_data = torch.load("data/processed/processed_train_tensor.pt")
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True)

    training_loss = []
    for e in range(epochs):
        running_loss = 0
        for images, labels in train_loader:
            optimizer.zero_grad()
            output = model(images.float())
            loss = criterion(output, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        else:
            print(f"Training loss: {running_loss/len(train_loader)}")
            wandb.log({"Training loss": (running_loss/len(train_loader)),"Train Epoch Count": (e+1)})
            training_loss.append(running_loss/len(train_loader))
    
    # Save model

    timeStamp = str(datetime.now()).replace(" ","_")
    timeStamp = timeStamp.replace(".","_")

    wandb.log({"CheckpointID": (timeStamp + '_checkpoint.pth')})

    print("saving file to: " + "models/" + timeStamp + '_checkpoint.pth')
    torch.save(model.state_dict(),"models/" + timeStamp + '_checkpoint.pth')

    # Save figure
    plt.plot(training_loss)
    plt.xlabel("Epochs")
    plt.ylabel("Traning loss")
    plt.title("Training loss")
    plt.savefig('reports/figures/' + timeStamp +'_training_loss.png')


cli.add_command(train)
if __name__ == "__main__":
    cli()
