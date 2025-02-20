# Some functions for manipulating dataframes

import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.exceptions import NotFittedError
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import shapiro
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import string

def split_dataframe(df, columns_to_split):
    '''
    Splits a DataFrame into two parts:
    - One containing the specified columns
    - One containing the remaining columns

    Args:
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

    Parameters:
    - df: The dataframe to scale.
    - scaler_choice: The type of scaler to use. Choices are 'standard', 'minmax', or 'robust'. Default is 'standard'.
    - fitted_scaler: An optional pre-fitted scaler. If provided, it will scale using this scaler. Default is None.

    Returns:
    - Scaled dataframe.
    - Fitted scaler if it was fitted in the process.
    '''

    # Identify numerical columns
    numerical_cols = df.select_dtypes(include='number').columns

    # If no numerical columns exist, raise an error
    if len(numerical_cols) == 0:
        raise ValueError('No numerical columns found in the dataframe.')

    # Initialize the scaler based on user choice, unless a fitted_scaler is provided
    if fitted_scaler is not None:
        print("Using provided fitted scaler")
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

    Parameters:
    - df: The dataframe to split and scale.
    - test_size: The fraction of the dataset to be used for testing. Default is 0.2 (80% training, 20% test).
    - scaler_choice: The type of scaler to use. Choices are 'standard', 'minmax', or 'robust'. Default is 'standard'.
    - fitted_scaler: An optional pre-fitted scaler. If provided, it will be used to transform the data. Default is None.

    Returns:
    - scaled_train_df: Scaled training dataframe.
    - scaled_test_df: Scaled test dataframe.
    - fitted_scaler: The fitted scaler used to transform the data.
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
    # PCA for Dimensionality Reduction
    if fitted_pca is None:
        pca = PCA(n_components=n)  # Reduce to n components
        df_pca = pca.fit_transform(df)
    else:
        df_pca = pca.transform(df)
    return (df_pca, pca)


def outlier_detection_and_removal(df):
    # IQR Method
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    df_no_outliers = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
    return df_no_outliers


# Text Vectorization
