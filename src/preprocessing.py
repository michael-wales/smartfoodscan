# Some functions for manipulating dataframes

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gc # Garbage collection

import scipy.stats as stats
from scipy.stats import shapiro

from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from transformers import BertTokenizer, BertModel

import torch # Efficiency # Not necessary in production


def split_dataframe(df, columns_to_split):
    '''
    Splits a DataFrame into two parts:
    - One containing the specified columns
    - One containing the remaining columns

    Params:
        df (pd.DataFrame): The original DataFrame.
        columns_to_split (str or list): The column(s) to separate from the original DataFrame.

    Returns:
        tuple: (DataFrame with selected columns, DataFrame with remaining columns)
    '''
    if isinstance(columns_to_split, str):  # Ensure it's a list if a single column is passed
        columns_to_split = [columns_to_split]

    present_columns = [col for col in columns_to_split if col in df.columns]

    if not present_columns:
        raise ValueError('None of the specified columns exist in the DataFrame.')

    df_selected = df[present_columns].copy()
    df_remaining = df.drop(columns=present_columns).copy()

    return df_selected, df_remaining


def scale_dataframe(df, scaler_choice='standard', fitted_scaler=None):
    '''
    Scales a dataframe using a specified scaler. If the scaler is already fitted, it will use that.
    If the scaler is not fitted, it will fit and return the fitted scaler.

    Params:
        df: The dataframe to scale.
        scaler_choice: The type of scaler to use. Choices are 'standard', 'minmax', or 'robust'. Default is 'standard'.
        fitted_scaler: An optional pre-fitted scaler. If provided, it will scale using this scaler. Default is None.

    Returns:
        tuple: (Scaled DataFrame, fitted scaler)
    '''

    # Identify numerical columns
    numerical_cols = df.select_dtypes(include='number').columns

    # If no numerical columns exist, raise an error
    if len(numerical_cols) == 0:
        raise ValueError('No numerical columns found in the dataframe.')

    # Initialize the scaler based on user choice, unless a fitted_scaler is provided
    if fitted_scaler is not None:
        print('Fitting using fitted scaler.')
        scaler = fitted_scaler
    else:
        # If no fitted_scaler, initialize based on user choice
        if scaler_choice == 'standard':
            scaler = StandardScaler()
        elif scaler_choice == 'minmax':
            scaler = MinMaxScaler()
        elif scaler_choice == 'robust':
            scaler = RobustScaler()
        else:
            raise ValueError(f'Invalid scaler choice: "{scaler_choice}". Choose from "standard", "minmax", or "robust".')

    # Scale only the numerical columns
    if fitted_scaler is None:
        try:
            # Apply scaler only to the numerical columns
            scaled_numerical = scaler.fit_transform(df[numerical_cols])
            scaled_df = df.copy()
            scaled_df[numerical_cols] = scaled_numerical
            return scaled_df, scaler  # Return both scaled dataframe and fitted scaler
        except Exception as e:
            raise ValueError(f'An error occurred while fitting the scaler: {e}')
    else:
        try:
            # Apply existing fitted scaler to numerical columns only
            scaled_numerical = scaler.transform(df[numerical_cols])
            scaled_df = df.copy()
            scaled_df[numerical_cols] = scaled_numerical
            return scaled_df, scaler  # Use existing fitted scaler
        except NotFittedError:
            raise ValueError('The provided scaler is not fitted yet.')
        except Exception as e:
            raise ValueError(f'An error occurred while using the fitted scaler: {e}')

# Of course, you should just use a column transformer. It's a lot quicker.


def visualize_columns(df):
    '''
    Visualizes normality

    Params:
        df: The dataframe to check.

    Returns:
        None
    '''

    # Histograms
    df.hist(bins=30, figsize=(10, 8))
    plt.tight_layout()
    plt.show()

    numerical_cols = df.select_dtypes(include='number').columns

    for col in numerical_cols:

        # Q-Q Plot
        plt.figure(figsize=(6, 4))
        stats.probplot(df[col], dist='norm', plot=plt)
        plt.title(f'Q-Q Plot for {col}')
        plt.show()

        # Normality
        stat, p_value = shapiro(df[col])
        print(f'{col}: Shapiro-Wilk Test Statistic={round(stat, 3)}, p-value={round(p_value, 3)}')
        if p_value > 0.05:
            print(f'{col} appears to be normally distributed.\n')
        else:
            print(f'{col} does not appear to be normally distributed.\n')

        # Kurtosis
        skewness = df[col].skew()
        kurtosis = df[col].kurt()
        print(f'{col}: Skewness={skewness:.3f}, Kurtosis={kurtosis:.3f}')
        if abs(skewness) < 0.5 and abs(kurtosis - 3) < 1:
            print(f'{col} is likely to be normally distributed based on skewness and kurtosis.\n')
        else:
            print(f'{col} may not be normally distributed based on skewness and kurtosis.\n')


def scale_train_test_data(df, test_size=0.2, scaler_choice='standard', fitted_scaler=None):
    '''
    Scales the training and test datasets separately using a specified scaler.
    The scaler is fit to the training data and then used to transform both training and test datasets.

    Params:
        df (pd.Dataframe): The dataframe to split and scale.
        test_size (float): The fraction of the dataset to be used for testing. Default is 0.2 (80% training, 20% test).
        scaler_choice (str): The type of scaler to use. Choices are 'standard', 'minmax', or 'robust'. Default is 'standard'.
        fitted_scaler: An optional pre-fitted scaler. If provided, it will be used to transform the data. Default is None.

    Returns:
        pd.DataFrame: Scaled training dataframe.
        pd.DataFrame: Scaled test dataframe.
        scaler object: The fitted scaler used to transform the data.
    '''

    # Split the dataframe into train and test sets
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)

    # Scale the training data
    scaled_train_df, fitted_scaler = scale_dataframe(train_df, scaler_choice, fitted_scaler)

    # Transform the test data using the fitted scaler
    scaled_test_df, _ = scale_dataframe(test_df, scaler_choice, fitted_scaler)

    return scaled_train_df, scaled_test_df, fitted_scaler

# Again, use column transformers.


def use_pca(df, n=5, fitted_pca=None):
    '''
    Reduce dimensionality

    Args:
        df (pd.DataFrame)
        n (int): n_components
        fitted_pca (PCA object): optional PCA for fitting

    Returns:
        pd.DataFrame: Fitted and transformed DataFrame
        Fitted PCA object
    '''

    # PCA for Dimensionality Reduction
    if fitted_pca is None:
        pca = PCA(n_components=n)  # Reduce to n components
        df_pca = pca.fit_transform(df)
    else:
        df_pca = pca.transform(df)
    return (df_pca, pca)


def outlier_detection_and_removal(df):
    '''
    Removes outliers

    Args:
        df (pd.DataFrame)

    Returns:
        pd.DataFrame: Q1 - 1.5IQR <= df <= Q3 + 1.5IQR
    '''

    # IQR Method
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    df_no_outliers = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
    return df_no_outliers


# Text vectorization
def clean_text_vectorized(df, column_name):
    '''
    Cleans annoying text

    Args:
        df (pd.DataFrame): The DataFrame to clean.
        column_name (str): The column to clean.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    '''
    # Avoid pointer errors
    df = df.copy()

    df[column_name] = df[column_name].str.replace(r'\([^)]+\)|\[[^]]+\]|\{[^}]+\}', '', regex=True)
    df[column_name] = df[column_name].str.strip()
    df[column_name] = df[column_name].str.replace(', and', ', ', regex=False).str.replace('.', ',', regex=False)
    df[column_name] = df[column_name].str.replace(r'([^,]+)\s(E\d+)', r'\1, \2', regex=True)
    df[column_name] = df[column_name].str.lower()

    return df

# Helper function to process data in chunks # In the end, it's not necessary
def process_in_chunks(df, column_name, chunk_size=10_000, method='bow', max_features=5_000, use_bert=False):
    '''
    Processes a large DataFrame in chunks to avoid memory overload.

    Args:
        df (pd.DataFrame): Input DataFrame containing the text column.
        column_name (str): Column name to be used for text data.
        chunk_size (int): Number of rows per chunk for processing.
        method (str): Vectorization method: 'bow', 'tfidf', 'bert'.
        max_features (int): Maximum number of features for BoW and TF-IDF (default: 5_000).
        use_bert (bool): If True, uses BERT embeddings for vectorization (default: False).

    Returns:
        pd.DataFrame: DataFrame with the transformed text data (in chunks).
    '''
    df = df.copy()

    all_vectors = []

    # Process data in chunks
    for start_idx in range(0, len(df), chunk_size):
        end_idx = min(start_idx + chunk_size, len(df))
        chunk = df.iloc[start_idx:end_idx]
        chunk_vectors = vectorize_text(chunk, column_name, method, max_features, use_bert)
        all_vectors.append(chunk_vectors)

        # Clean up memory
        del chunk, chunk_vectors
        gc.collect()

    # Concatenate all chunks into a single DataFrame
    return pd.concat(all_vectors, axis=0)

def vectorize_text(df, column_name='text', method='bow', max_features=5_000):
    '''
    Vectorizes text data using various methods.

    Args:
        df (pd.DataFrame): Input DataFrame containing the text column.
        column_name (str): Column name to be used for text data (default: 'text').
        method (str): Vectorization method: 'bow', 'tfidf', or 'bert'.
        max_features (int): Maximum number of features for BoW and TF-IDF (default: 5_000).

    Returns:
        pd.DataFrame: DataFrame with the transformed text data.
        vectorizer if method != 'bert'
    '''

    df = df.copy()

    # Select the text column
    text_data = df[column_name].fillna('')

    # Bag of Words (BoW)
    if method == 'bow':
        vectorizer = CountVectorizer(max_features=max_features)
        vectors = vectorizer.fit_transform(text_data)
        vectorized_df = pd.DataFrame.sparse.from_spmatrix(vectors, columns=vectorizer.get_feature_names_out())

    # TF-IDF
    elif method == 'tfidf':
        vectorizer = TfidfVectorizer(max_features=max_features)
        vectors = vectorizer.fit_transform(text_data)
        vectorized_df = pd.DataFrame.sparse.from_spmatrix(vectors, columns=vectorizer.get_feature_names_out())

    # BERT
    elif method == 'bert':
        bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased') # For English
        bert_model = BertModel.from_pretrained('bert-base-uncased')

        # Extract BERT embeddings for each document
        embeddings = []
        for text in text_data:
            inputs = bert_tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = bert_model(**inputs)
                # Use the embeddings from the [CLS] token
                cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()
                embeddings.append(cls_embedding.flatten())
        vectorized_df = pd.DataFrame(np.array(embeddings))

    else:
        raise ValueError('Invalid method. Choose from "bow", "tfidf", or "bert".')

    return vectorized_df if method == 'bert' else (vectorized_df, vectorizer)
