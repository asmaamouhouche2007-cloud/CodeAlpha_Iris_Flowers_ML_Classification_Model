from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler


def creating_preprocessor(df,target,scale=False):
    '''
    Create a preprocessing pipline in which the steps of preprocessing both categorical and numerical columns are available
        args:
            df: the dataframe we want to preprocess its data , inorder to extract numerical and categorical columns from it .
        output:
            preprocessor: pipline that contains steps of preprocessing both categorical and numerical columns are available in the input dataframe
    '''
    # dropping the target column since it is not meant to be preprocessed + the Id column since it 
    # do not help in the prediction 
    df=df.drop(columns=[target,'Id'])
    # first we must identify categorical columns from numerical columns :
    def split_categorical_from_numerical_cols(df):
        cols=df.columns
        num_cols=df.select_dtypes(exclude='str').columns
        cat_cols=[col for col in cols if col not in num_cols]
        return num_cols,cat_cols
        
    num_cols,cat_cols=split_categorical_from_numerical_cols(df)

    # identifying the preprocessing steps of numerical columns
    num_preprocessing=SimpleImputer(strategy='median')

    if scale:
        scaler=StandardScaler()
        num_preprocessing=Pipeline(steps=[
            ('imputing',SimpleImputer(strategy='median')),
            ('scaling features',scaler)
        ])
     
    #identifying preprocessing steps of categorical data
    cat_preprocessing=Pipeline(steps=[
        ('imputation',SimpleImputer(strategy='most_frequent')),
        ('encoding',OneHotEncoder(handle_unknown='ignore'))
    ])

    #combining numerical and categorical preprocessing in one pipline (preprocessor)
    preprocessor=ColumnTransformer(transformers=[
        ('num',num_preprocessing,num_cols),
        ('cat',cat_preprocessing,cat_cols)
    ])
    return preprocessor