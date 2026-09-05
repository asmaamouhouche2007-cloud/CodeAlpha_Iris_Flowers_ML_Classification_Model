from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline

def randomForestClassification_model_creation():
    ''' 
    Creates a classification model
        output:
            model: classification model
    '''
    model=RandomForestClassifier(random_state=42)
    return model


# evaluating the model using cross validation since the iris dataset is too small
def cross_validation(model,X,y):
    '''
    cross validation of the machine learning model 
        args:
            model: ml model 
        output:
            cross validation scores's mean  
    '''
    scores=cross_val_score(model,X,y,cv=5,scoring='f1_macro')
    return scores.mean()

def pipline_creation(preprocessor,model):
    '''
    Creates a pipline that links the preprocessing logic with the model
        args:
            model : the machine learning model
            preprocessor : the preprocsessor that is a pipline that link the preprocessing steps 
        output:
            a pipline in which both the ml model and the preprocessor are combined
    '''
    pipline=Pipeline(steps=[
        ('Preprocessing',preprocessor),
        ('model',model)
    ])
    return pipline

