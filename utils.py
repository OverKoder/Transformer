# PyTorch utils
import torch
from torch import mean
import torchvision.transforms as transforms
from adabound import AdaBound

# For plotting
import seaborn as sn
from numpy import linspace as linspace
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Sklearn metrics
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from sklearn.metrics import  balanced_accuracy_score, roc_curve, auc

# Models
import torchvision.models as models
from models.LeNet5 import *
from models.AlexNet import *
from models.IDCNet import *
from vit_pytorch.distill import DistillableViT, DistillWrapper

# Utils
import numpy as np

# Others
import pickle
import sys
import time
import math
from typing import Union, Tuple

# For PCA projection
from cv2 import merge

TOTAL_BAR_LENGTH = 70
last_time = time.time()
begin_time = last_time

# Uncomment both lines if you want to see the output in the terminal
# _, term_width = os.popen('stty size', 'r').read().split()
# term_width = int(term_width)

# Comment this next line if you want to see the output in the terminal
term_width = 100

def progress_bar(current, total, msg=None):
    global last_time, begin_time
    if current == 0:
        begin_time = time.time()  # Reset for new bar.

    cur_len = int(TOTAL_BAR_LENGTH*current/total)
    rest_len = int(TOTAL_BAR_LENGTH - cur_len) - 1

    sys.stdout.write(' [')
    for i in range(cur_len):
        sys.stdout.write('=')
    sys.stdout.write('>')
    for i in range(rest_len):
        sys.stdout.write('.')
    sys.stdout.write(']')

    cur_time = time.time()
    step_time = cur_time - last_time
    last_time = cur_time
    tot_time = cur_time - begin_time

    L = []
    L.append('  Step: %s' % format_time(step_time))
    L.append(' | Tot: %s' % format_time(tot_time))
    if msg:
        L.append(' | ' + msg)

    msg = ''.join(L)
    sys.stdout.write(msg)
    for i in range(term_width-int(TOTAL_BAR_LENGTH)-len(msg)-3):
        sys.stdout.write(' ')

    # Go back to the center of the bar.
    for i in range(term_width-int(TOTAL_BAR_LENGTH/2)+2):
        sys.stdout.write('\b')
    sys.stdout.write(' %d/%d ' % (current+1, total))

    if current < total-1:
        sys.stdout.write('\r')
    else:
        sys.stdout.write('\n')
    sys.stdout.flush()


def format_time(seconds):

    # Just in case it takes a long time...
    days = seconds // (3600/24)
    seconds = seconds - days*3600*24

    hours = seconds // 3600
    seconds = seconds - hours*3600

    minutes = seconds // 60
    seconds = seconds - minutes*60

    real_seconds = int(seconds)
    seconds = seconds - real_seconds

    millis = int(seconds*1000)

    f = ''
    # Maximum units to show is 2
    max_units = 1
    if days > 0:
        f += str(days) + 'D'
        max_units += 1

    if hours > 0 and max_units <= 2:
        f += str(hours) + 'h'
        max_units += 1
    if minutes > 0 and max_units <= 2:
        f += str(minutes) + 'm'
        max_units += 1
    if real_seconds > 0 and max_units <= 2:
        f += str(real_seconds) + 's'
        max_units += 1
    if millis > 0 and max_units <= 2:
        f += str(millis) + 'ms'
        max_units += 1

    # If it took less than 1ms
    if f == '':
        f = '0ms'

    return f


def build_model(model_name: str) -> nn.Module:
    """
    Function that builds the model to train based on the provided name.

    Args:
        model_name (str): The name of the model to build.

    Raises:
        TypeError: The given model_name is not a str
        ValueError: The given name of the model is not available.

    Returns:
        nn.Module: The model to train.
    """    

    # Available models
    net_models = ["alexnet", "convnext_tiny", "convnext_small", "convnext_base", "convnext_large", "deit" , "densenet121", "densenet161", "efficientnetb0", "efficientnetb1", "efficientnetb2",
    "efficientnetb3", "efficientnetb4", "efficientnetb5", "efficientnetb6", "efficientnetb7", "googlenet", "idcnet", "lenet5",
     "resnet50",  "resnet101",  "resnet152", "vit_b_16", "vit_b_32", "vit_l_16", "vit_l_32", "vgg11", "vgg13", "vgg16","vgg19" ]

    if not isinstance(model_name, str): raise TypeError('"model_name" must be a str')
    if model_name not in net_models: raise ValueError('"model_name" must be one of the available models: ' + ','.join(net_models))

    if model_name == "alexnet":
        return AlexNet()

    if model_name == "convnext_tiny":
        return models.convnext_tiny(pretrained = True)
    
    if model_name == "convnext_small":
        return models.convnext_small(pretrained = True)
    
    if model_name == "convnext_base":
        return models.convnext_base(pretrained = True)
    
    if model_name == "convnext_large":
        return models.convnext_large(pretrained = True)

    if model_name == "deit":

        v = DistillableViT(
            image_size = 50,
            patch_size = 10,
            num_classes = 2,
            dim = 1024,
            depth = 6,
            heads = 8,
            mlp_dim = 2048,
            dropout = 0.1,
            emb_dropout = 0.1)

        teacher = LeNet5()
        deit = DistillWrapper(
            student = v,
            teacher = teacher,
            temperature = 3,
            alpha = 0.5,
            hard = True
        )

        return deit


    if model_name == "densenet121":
        return models.densenet121(pretrained = True)

    if model_name == "densenet161":
        return models.densenet161(pretrained = True)

    if model_name == "efficientnetb0":
        return models.efficientnet_b0(pretrained = True)

    if model_name == "efficientnetb1":
        return models.efficientnet_b1(pretrained = True)

    if model_name == "efficientnetb2":
        return models.efficientnet_b2(pretrained = True)

    if model_name == "efficientnetb3":
        return models.efficientnet_b3(pretrained = True)

    if model_name == "efficientnetb4":
        return models.efficientnet_b4(pretrained = True)

    if model_name == "efficientnetb5":
        return models.efficientnet_b5(pretrained = True)

    if model_name == "efficientnetb6":
        return models.efficientnet_b6(pretrained = True)

    if model_name == "efficientnetb7":
        return models.efficientnet_b7(pretrained = True)
    
    # Note: Not pretrained googlenet outputs an error for training loop
    if model_name == "googlenet":
        return models.googlenet(pretrained = True)
    
    if model_name == "idcnet":
        return IDCNet()

    if model_name == "lenet5":
        return LeNet5()

    if model_name == "resnet50":
        return models.resnet50(pretrained = True)

    if model_name == "resnet101":
        return models.resnet101(pretrained = True)

    if model_name == "resnet152":
        return models.resnet152(pretrained = True)

    if model_name == "vit_b_16":
        return models.vit_b_16(pretrained = True)

    if model_name == "vit_b_32":
        return models.vit_b_32(pretrained = True)

    if model_name == "vit_l_16":
        return models.vit_l_16(pretrained = True)

    if model_name == "vit_l_32":
        return models.vit_l_32(pretrained = True)

    if model_name == "vgg11":
        return models.vgg11_bn(pretrained = True)

    if model_name == "vgg13":
        return models.vgg13_bn(pretrained = True)

    if model_name == "vgg16":
        return models.vgg16_bn(pretrained = True)

    if model_name == "vgg19":
        return models.vgg19_bn(pretrained = True)

def build_optimizer(model: torch.nn.Module, optimizer_name: str) -> torch.optim.Optimizer:

    """
    Function that builds the optimizer to train based on the provided name.

    Args:
        optimizer_name (str): The name of the optimizer to build.

    Raises:
        TypeError: The given model is not a torch.nn.Module
        TypeError: The given model name is not a string.
        ValueError: The given name of the optimizer is not available.

    Returns:
        torch.optim: The optimizer (without initializing the parameters).
    """    
    # Available optimizers
    optimizers = ['sgd','adam','adabound']

    if not isinstance(model, torch.nn.Module): raise TypeError('"model" must be a torch.nn.Module')
    if not isinstance(optimizer_name, str): raise TypeError('"optimizer_name" must be a str')
    if optimizer_name not in optimizers: raise ValueError('"optimizer_name" must be one of the available models: ' + ','.join(optimizers))

    if optimizer_name == "sgd":
        return torch.optim.SGD(model.parameters(), lr= 1e-3, momentum = 0.9)

    if optimizer_name == "adam":
        return torch.optim.Adam(model.parameters(), lr= 1e-3)

    if optimizer_name == "adabound":
        return AdaBound(model.parameters(), lr= 1e-3, final_lr = 0.1)


def build_transforms(model_name:str, pca:bool) -> list:

    """
    Function that builds the transforms to apply to the data based on the provided name.

    Args:
        model_name (str): The name of the model to build.
        pca (bool): Whether to apply PCA.

    Raises:
        ValueError: The given name of the model is not available.
        TypeError: The given boolean is not a boolean. (True or False)

    Returns:
        list: The transforms to apply to the training data.
        list: The transforms to apply to the test data.
    """    

    # Available models
    net_models = ["alexnet", "convnext_tiny", "convnext_small", "convnext_base", "convnext_large", "deit" , "densenet121", "densenet161", "efficientnetb0", "efficientnetb1", "efficientnetb2",
    "efficientnetb3", "efficientnetb4", "efficientnetb5", "efficientnetb6", "efficientnetb7", "googlenet", "idcnet", "lenet5",
     "resnet50",  "resnet101",  "resnet152", "vit_b_16", "vit_b_32", "vit_l_16", "vit_l_32", "vgg11", "vgg13", "vgg16","vgg19" ]

    if not isinstance(model_name, str): raise TypeError('"model_name" must be a str')
    if model_name not in net_models: raise ValueError('"model_name" must be one of the available models: ' + ','.join(net_models))
    if not type(pca) == bool: raise TypeError('"pca" must be a boolean (True or False)')

    if model_name == 'vit_b_16' or model_name == 'vit_l_16':
        
        if pca:

            train_transform = transforms.Compose([

                # Convert to tensor
                transforms.ToTensor(),
            
                # Allow random horizontal flips (data augmentation)
                transforms.RandomHorizontalFlip(p = 0.25),

                # Allow random vertical flips (data augmentation)
                transforms.RandomVerticalFlip(p = 0.05),
                
                # This resize is required to provide a correct input 
                # to a pretrained ViT
                transforms.Resize((224,224)),

                # Normalize train dataset with its mean and standard deviation
                transforms.Normalize((0.7595, 0.5646, 0.6882), (0.1496, 0.1970, 0.1428))
            ])

            test_transform = transforms.Compose([

                # Convert to tensor
                transforms.ToTensor(),

                # This resize is required to provide a correct input 
                # to a pretrained ViT
                transforms.Resize((224,224)),

                # Normalize test dataset with its mean and standard deviation
                transforms.Normalize((0.7594, 0.5650, 0.6884), (0.1504, 0.1976, 0.1431))
            ])
        
        else:

            train_transform = transforms.Compose([

                # Convert to tensor
                transforms.ToTensor(),
        
                # Allow random horizontal flips (data augmentation)
                transforms.RandomHorizontalFlip(p = 0.25),

                # Allow random vertical flips (data augmentation)
                transforms.RandomVerticalFlip(p = 0.05),

                # This resize is required to provide a correct input 
                # to a pretrained ViT
                transforms.Resize((224,224)),
            
                # Normalize train dataset with its mean and standard deviation
                transforms.Normalize((0.7595, 0.5646, 0.6882), (0.1496, 0.1970, 0.1428))
            ])

            test_transform = transforms.Compose([

                # Convert to tensor
                transforms.ToTensor(),
                
                # This resize is required to provide a correct input 
                # to a pretrained ViT
                transforms.Resize((224,224)),

                # Normalize test dataset with its mean and standard deviation
                transforms.Normalize((0.7594, 0.5650, 0.6884), (0.1504, 0.1976, 0.1431))
            ])

    # Not a ViT model
    else:
        
        if pca:

            train_transform = transforms.Compose([

                # Convert to tensor
                transforms.ToTensor(),
            
                # Allow random horizontal flips (data augmentation)
                transforms.RandomHorizontalFlip(p = 0.25),

                # Allow random vertical flips (data augmentation)
                transforms.RandomVerticalFlip(p = 0.05),

                # Normalize train dataset with its mean and standard deviation
                transforms.Normalize((0.7595, 0.5646, 0.6882), (0.1496, 0.1970, 0.1428))
            ])


        
        else:

            train_transform = transforms.Compose([

                # Convert to tensor
                transforms.ToTensor(),
        
                # Allow random horizontal flips (data augmentation)
                transforms.RandomHorizontalFlip(p = 0.25),

                # Allow random vertical flips (data augmentation)
                transforms.RandomVerticalFlip(p = 0.05),

                # Normalize train dataset with its mean and standard deviation
                transforms.Normalize((0.7595, 0.5646, 0.6882), (0.1496, 0.1970, 0.1428))
            ])

            test_transform = transforms.Compose([
                
                # Convert to tensor
                transforms.ToTensor(),
                
                # Normalize test dataset with its mean and standard deviation
                transforms.Normalize((0.7594, 0.5650, 0.6884), (0.1504, 0.1976, 0.1431))
            ])


    return train_transform, test_transform


def load_pca_matrix(n_components: int) -> dict:

    """
    Loads the PCA matrix.

    Args:
        n_components (int): The number of components to keep.

    Raises:
        ValueError: The given number of components is not available.

    Returns:
        dict: Dictionary with the PCA matrix for each of the 3 channels
    """    

    # Available components
    comp = [1, 2, 5, 10, 25, 50, 100, 250, 500, 1000, 1250, 1500, 2000, 2500]

    if n_components not in comp: raise ValueError('"n_components" must be one of the available components: ' + ','.join(comp))

    pca = {'red': None,
           'green': None,
           'blue': None}

    # Load pca matrix
    pca['red'] = pickle.load(open('data_projection/pca_red_' + str(n_components) + '.p','rb'))
    pca['green'] = pickle.load(open('data_projection/pca_green_' + str(n_components) + '.p','rb'))
    pca['blue'] = pickle.load(open('data_projection/pca_blue_' + str(n_components) + '.p','rb'))

    return pca

def apply_pca(red: np.ndarray, green: np.ndarray, blue: np.ndarray, pca:dict) -> np.ndarray:

    """
    Applies the PCA matrix to the given data.

    Args:
        red (np.ndarray): The red channel.
        green (np.ndarray): The green channel.
        blue (np.ndarray): The blue channel.
        pca (dict): The PCA matrix.

    Raises:
        TypeError: The given data is not a numpy array.

    Returns:
        np.ndarray: The projected data.
    """    

    if not isinstance(red, np.ndarray): raise TypeError('"red" must be a numpy ndarray')
    if not isinstance(green, np.ndarray): raise TypeError('"green" must be a numpy ndarray')
    if not isinstance(blue, np.ndarray): raise TypeError('"blue" must be a numpy ndarray')
    
    # Project data to lower dimensions
    new_red = pca['red'].transform([ red.flatten() ])
    new_green = pca['green'].transform([ green.flatten() ])
    new_blue = pca['blue'].transform([ blue.flatten() ])

    # Reconstruct data
    new_red = pca['red'].inverse_transform(new_red)
    new_green = pca['green'].inverse_transform(new_green)
    new_blue = pca['blue'].inverse_transform(new_blue)

    # Reshape into an image
    new_red = new_red.reshape(50,50)
    new_green = new_green.reshape(50,50)
    new_blue = new_blue.reshape(50,50)

    # Merge channels
    img = (merge((new_blue, new_green, new_red)))


    return img

def interval95(acc:float, n_data:int) -> float:

    """
    Calculates the confidence interval 95% on a given number of samples.

    Args:
        acc (float): The accuracy.
        n_data (int): The number of samples.

    Returns:
        float: The confidence interval.
    """    
    
    bound = 1.96 * math.sqrt((acc*(1-acc)) / n_data)

    return bound


def plot(x_axis, y_axis, x_label,y_label, name = "Plot"):
    """
    Creates plot using pyplot
    Args:
        x_axis = List with values for the x axis
        y_axis = List with values for the y axis (must contain tuples like: ([values], label))
        x_label = Label for the x axis
        y_label = Label for the y axis
        name: Name of the file where the plot will be saved

    """
    new_x_axis = linspace(min(x_axis), max(x_axis), 200)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    for y in y_axis:
        
        # There must be at least 4 values in x_axis and in y[0] for this to work
        spl = make_interp_spline(x_axis, y[0], k=3)
        
        y_smooth = spl(new_x_axis)

        plt.plot(new_x_axis, y_smooth, label= y[1])

    plt.legend()
    plt.savefig(name)
    plt.clf()

    # If saved correctly, return True
    return True


def get_mean_and_std(dataloader: torch.utils.data.DataLoader) -> Tuple[float, float]:

    """
    Computes the mean and standard deviation of the dataset.

    Args:  
        dataloader (torch.utils.data.DataLoader): The dataloader.

    Raises:
        TypeError: The given data is not a torch.utils.data.DataLoader.


    Returns:
        tuple: The mean of the dataset.
        tuple: The standard deviation of the dataset.
    """    
    if not isinstance(dataloader, torch.utils.data.DataLoader): raise TypeError('"dataloader" must be a torch.utils.data.DataLoader')

    channels_sum, channels_squared_sum, num_batches = 0, 0, 0

    for data, _ in dataloader:
        # Computes mean over batch, height and width, not over the channels
        channels_sum += mean(data, dim=[0,2,3])
        channels_squared_sum += mean(data**2, dim=[0,2,3])
        num_batches += 1
    
    data_mean = channels_sum / num_batches

    # Var[X] = E[X**2] - E[X] ** 2
    # Standard deviation
    std = (channels_squared_sum / num_batches  - data_mean**2) ** 0.5

    return data_mean, std
    
def count_parameters(model: nn.Module) -> int:
    """
    Counts the number of trainable parameters in a model.

    Args:
        model (nn.Module): The model.

    Raises:
        TypeError: The given data is not a nn.Module.

    Returns:
        int: The number of trainable parameters.
    """ 


    if not isinstance(model, nn.Module): raise TypeError('"model" must be a nn.Module')

    return sum(param.numel() for param in model.parameters() if param.requires_grad)

    
def plot_confusion_matrix(true_labels: Union[list, np.ndarray], predicted_labels: Union[list, np.ndarray], file_name: str) -> float:

    """
    Plots the confusion matrix given true and predicted labels.

    Args:
        true_labels (list): The true labels.
        predicted_labels (list): The predicted labels.
        file_name (str): The name of the file where the plot will be saved.

    Raises:
        TypeError: The given data is not a list.
        TypeError: The given data is not a str.

    Returns:
        float: The specificity of the model.
    """    

    if not (isinstance(true_labels, list) or isinstance(true_labels, np.ndarray)): raise TypeError('"true_labels" must be a list or numpy ndarray')
    if not (isinstance(predicted_labels, list) or  isinstance(predicted_labels, np.ndarray)): raise TypeError('"predicted_labels" must be a list or a numpy ndarray')
    if not isinstance(file_name, str): raise TypeError('"file_name" must be a str')

    # Build confusion matrix
    cf_matrix = confusion_matrix(true_labels, predicted_labels)

    # Calculate specifity
    specificity = cf_matrix[0,0] / (cf_matrix[0,0] + cf_matrix[0,1])

    # Information that will appear in each cell
    group_names = ['True Neg','False Pos','False Neg','True Pos']
    group_counts = ["{0:0.0f}".format(value) for value in cf_matrix.flatten()]
    group_percentages = ["{0:.2%}".format(value) for value in cf_matrix.flatten()/np.sum(cf_matrix)]

    
    labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in zip(group_names,group_counts,group_percentages)]
    labels = labels[2:] + labels[:2]

    labels = np.asarray(labels).reshape(2,2)

    ax = sn.heatmap(cf_matrix, annot=labels, fmt='', cmap='Blues_r',cbar = False)
    ax.set_title(file_name+ " Confusion Matrix")
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label ')

    # Axis labels
    ax.xaxis.set_ticklabels(['Benign','Malignant'])
    ax.yaxis.set_ticklabels(['Malignant','Benign'])
    ax.set_ylim([0,2])

    fig = ax.get_figure()
    fig.savefig('Confussion_Matrix_' + file_name + '.png',dpi=400)
    fig.clf()
    
    return specificity

def plot_roc_auc(fpr: np.ndarray, tpr: np.ndarray, auc_value: float, file_name: str) -> None:
    """
    Plots the ROC curve.

    Args:
        fpr (np.ndarray): The false positive rate.
        tpr (np.ndarray): The true positive rate.
        auc_value (float): The area under the curve.
        file_name (str): The name of the file where the plot will be saved.

    Raises:
        TypeError: The given false positive rate is not a np.ndarray.
        TypeError: The given true positive rate is not a np.ndarray.
        TypeError: The given area under the curve is not a float.
        TypeError: The given file name is not a str.

    Returns:
        None: The plot is saved.
    """    

    if not isinstance(fpr, np.ndarray): raise TypeError('"fpr" must be a list or numpy ndarray')
    if not isinstance(tpr, np.ndarray): raise TypeError('"tpr" must be a list or a numpy ndarray')
    if not isinstance(auc_value, float): raise TypeError('"auc_value" must be a float')
    if not isinstance(file_name, str): raise TypeError('"file_name" must be a string')

    # Title of the plot
    plt.title('Receiver Operating Characteristic')

    # Plot ROC-AUC
    plt.plot(fpr,tpr,label = 'AUC = %0.3f' % auc_value, ls = "--")

    # Legend
    plt.legend(loc = 'lower right')

    # Limits of the X and Y axis
    plt.plot([0, 1], [0, 1])
    plt.xlim([0, 1])
    plt.ylim([0, 1])

    # X and Y axis labels
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')

    # Save plot and return
    plt.savefig('ROC-AUC_' + file_name + '.png')
    plt.clf()
    return 


def compute_stats(true_labels: Union[list, np.ndarray], predicted_labels: Union[list, np.ndarray], probabilities: Union[list, np.ndarray]) -> Tuple[float, float, float, float, np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Computes the accuracy, precision, recall, specificity, f1-score and ROC-AUC of the model.

    Args:
        true_labels (list): The true labels.
        predicted_labels (list): The predicted labels.
        file_name (str): The name of the model used.

    Raises:
        TypeError: The given true labels is not a list or a np.ndarray.
        TypeError: The given predicted labels is not a list or a np.ndarray.
        TypeError: The given probabilities is not a list or a np.ndarray.

    Returns:
        float: The precision of the model.
        float: The recall of the model.
        float: The f_score of the model.
        float: The balanced accuracy of the model.
        np.ndarray: The false positive rate.
        np.ndarray: The true positive rate.
        np.ndarray: The threshold of the ROC-AUC curve.
        float: The AUC value of the model
    """    
    if not (isinstance(true_labels, list) or isinstance(true_labels, np.ndarray)): raise TypeError('"true_labels" must be a list or numpy ndarray')
    if not (isinstance(predicted_labels, list) or  isinstance(predicted_labels, np.ndarray)): raise TypeError('"predicted_labels" must be a list or a numpy ndarray')
    if not (isinstance(probabilities, list) or isinstance(probabilities, np.ndarray)): raise TypeError('"probabilities" must be a list or numpy ndarray')

    # Precision
    precision = precision_score(y_true = true_labels, y_pred = predicted_labels)

    # Recall
    recall = recall_score(y_true = true_labels, y_pred = predicted_labels)

    # F1 - Score
    f_score = f1_score(y_true = true_labels, y_pred = predicted_labels)

    # Balanced accuracy (BAC)
    bac = balanced_accuracy_score(y_true = true_labels, y_pred = predicted_labels)
    
    # Receiver operating characteristic (ROC)
    fpr, tpr, _ = roc_curve(true_labels, probabilities)

    # Area Under the Curve (AUC)
    auc_value =  auc(fpr, tpr)

    return precision, recall, f_score, bac, fpr, tpr, auc_value

def compute_and_plot_stats(true_labels: Union[list, np.ndarray], predicted_labels: Union[list, np.ndarray], probabilities: Union[list, np.ndarray], file_name: str) -> Tuple[float, float, float, float, float]:

    """
    Computes and plots the accuracy, precision, recall, specificity, f1-score and ROC-AUC of the model.

    Args:
        true_labels (list): The true labels.
        predicted_labels (list): The predicted labels.
        file_name (str): The name of the model used.

    Raises:
        TypeError: The given true labels is not a list or a np.ndarray.
        TypeError: The given predicted labels is not a list or a np.ndarray.
        TypeError: The given probabilities is not a list or a np.ndarray.
        TypeError: The given name is not a str.

    Returns:
        float: The precision of the model.
        float: The recall of the model.
        float: The specificity of the model.
        float: The f_score of the model.
        float: The balanced accuracy of the model.
    """    
    if not (isinstance(true_labels, list) or isinstance(true_labels, np.ndarray)): raise TypeError('"true_labels" must be a list or numpy ndarray')
    if not (isinstance(predicted_labels, list) or  isinstance(predicted_labels, np.ndarray)): raise TypeError('"predicted_labels" must be a list or a numpy ndarray')
    if not (isinstance(probabilities, list) or isinstance(probabilities, np.ndarray)): raise TypeError('"probabilities" must be a list or numpy ndarray')
    if not isinstance(file_name, str): raise TypeError('"file_name" must be a str')

    precision, recall, f_score , bac, fpr, tpr, auc_value = compute_stats(true_labels, predicted_labels, probabilities)

    # Plot ROC-AUC curve
    plot_roc_auc(fpr, tpr, auc_value, file_name)

    # Plot confussion matrix
    specificity = plot_confusion_matrix(true_labels, predicted_labels, file_name)

    return precision, recall, specificity, f_score, bac