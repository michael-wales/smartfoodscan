import numpy as np
import pandas as pd
from pathlib import Path

def map_nutriscore_to_numeric(nutriscore_grade):
    # Mapping of nutriscore grades to numeric values
    grade_mapping = {
        'a': 1/5,
        'b': 2/5,
        'c': 3/5,
        'd': 4/5,
        'e': 5/5
    }

    # Return the mapped numeric value
    return grade_mapping.get(nutriscore_grade, None)

def map_nova_group_to_numeric(nova_group):
    # Mapping of nova groups to numeric values
    nova_mapping = {
        1: 1/4,
        2: 2/4,
        3: 3/4,
        4: 4/4
    }

    # Return the mapped numeric value
    return nova_mapping.get(nova_group, None)


def categorize_nutrition(df):
    """
    This function takes a DataFrame and creates a new feature 'nutrition_category'.
    It uses the 'nutriscore_grade' and 'nova_group' columns to calculate 'y',
    then categorizes 'y' as 'Excellent', 'Good', 'Poor', or 'Bad'.

    Args:
    - df: DataFrame of Openfoodfacts containing the columns 'nutriscore_grade' and 'nova_group'.

    Returns:
    - DataFrame with the new feature 'nutrition_category' added.
    """

    def create_target_variable(nutriscore_grade, nova_group):
        # Map the nutriscore and nova_group to their numeric values
        nutriscore_value = map_nutriscore_to_numeric(nutriscore_grade)
        nova_group_value = map_nova_group_to_numeric(nova_group)

        # Check if both mappings are valid
        if nutriscore_value is not None and nova_group_value is not None:
            # Calculate the average
            y = (nutriscore_value + nova_group_value) / 2
            return y
        else:
            return None  # Return None if invalid input

    def categorize_y(y):
        # Categorize 'y' according to the conditions defined
        # 'Excellent' means Highly nutritional and unprocessed foods.
        # 'Good' means Good nutritional with processed ingredients.
        # 'Poor' means Good/Poor nutritional value and processed/unprocessed ingredients.
        # 'Bad' means Highly processed and unhealthy foods.

        if y is None:
            return None

        if 0 <= y < 0.25:
            return 'Excellent'
        elif 0.25 <= y < 0.5:
            return 'Good'
        elif 0.5 <= y < 0.75:
            return 'Poor'
        elif 0.75 <= y <= 1:
            return 'Bad'
        else:
            return None  # In case y falls outside the expected range

    # Apply the target variable function to create 'y' for each row
    df['y'] = df.apply(lambda row: create_target_variable(row['nutriscore_grade'], row['nova_group']), axis=1)

    # Create the 'nutrition_category' column based on the 'y' value
    df['nutrition_category'] = df['y'].apply(categorize_y)

    return df
