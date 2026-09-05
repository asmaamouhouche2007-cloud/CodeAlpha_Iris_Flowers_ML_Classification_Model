from src.data_loader import input_output
from src.preprocessing import creating_preprocessor
from src.model import pipline_creation,randomForestClassification_model_creation,cross_validation
import joblib
from src.data_loader import load_data

def train(df):
    '''
    This function splits the data , creates the pipline and fit it with training data
    args:
        df: the dataframe that will be splitted into training set and testing set
        model_creation: model creation function that creates a specific classification model
    output:
        pipline: trained model linked to the preprocessing logic using piplines
    '''
    # splitting the dataframe into X and y
    X,y=input_output(df)
    # creating preprocessor 
    preprocessor=creating_preprocessor(df,'Species')

    # model creation 
    model=randomForestClassification_model_creation()
    # pipline creation 
    pipline=pipline_creation(preprocessor,model)

    # fitting the model and the preprocessor 
    pipline.fit(X,y)

    # saving the model 
    def save_model(pipline):
        joblib.dump(pipline,'piplines/pipline.pkl')
        print('The pipline was saved successfully')

    save_model(pipline)

    # model validation
    val_score=cross_validation(pipline,X,y)
    print("The accuracy of the model is :",val_score)

    return pipline
if __name__=='__main__':
    train(load_data('dataset/Iris.csv'))   
