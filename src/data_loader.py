import pandas as pd
from sklearn.model_selection import train_test_split

def load_data(filepath):
    '''loading the data from the csv file into a pandas dataframe
            args:
                filepath : the relative path to the datasecsv file
            output:
                df : the dataframe that contain the data
    '''
    df=pd.read_csv(filepath)
    return df


def input_output(df):
    '''
    splitting the dataframe into input data and target 
    
    args:
        df: The dataframe 
    output:
        X: input data
        y: target data
    '''
    features=['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm']
    X=df[features]
    y=df['Species']
    return X,y


def spliting_data(X,y):
    '''
    Spliting Data in the dataset into : training set and testing set
    
    args:
         X: input data
         y: target 
    output:
        train_X,test_X,train_y,test_y : training set with train_X,train_y and validation set with test_X,test_y
    '''
    train_X,test_X,train_y,test_y=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
    return train_X,test_X,train_y,test_y