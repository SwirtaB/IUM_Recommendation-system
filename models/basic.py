import json

import pandas as pd
import numpy as np

"""
    Basic model creates predictions based on currently visited category.
    
    It picks the best scored products and recommends them to the user.
     
    It will store its predictions in basic/recommendations.json file.   
"""

# Constants associated with data pre-processing.
NEW_GROUPS = [
    'Gry komputerowe',
    'Gry na konsole',
    'Sprzęt RTV',
    'Komputery',
    'Telefony i akcesoria'
]
PATH_SEPARATOR = ';'

# Constants associated with model saving.
REC_FILE = 'basic/recommendations.json'
REC_THRESHOLD = 10


def _cast_category_path(category_path):
    categories = category_path.split(PATH_SEPARATOR)
    found_groups = [group for group in NEW_GROUPS if group in categories]
    if len(found_groups) != 1:
        raise RuntimeError('wrong group cast: {}'.format(found_groups))
    return found_groups[0]


def _calculate_score(rating, popularity, min_popularity, avg_rating) -> pd.Series:
    return ((popularity / (popularity + min_popularity)) * rating) + (
            (min_popularity / (popularity + min_popularity)) * avg_rating)


def _with_score(products_df: pd.DataFrame) -> pd.DataFrame:
    avg_rating = products_df['user_rating'].mean()
    min_popularity = np.percentile(products_df['count'], 80)
    # Deep copy because products df is modified and returned as the result.
    products = products_df[products_df['count'] >= min_popularity].copy(deep=True)
    user_ratings = products['user_rating']
    popularity = products['count']
    products['score'] = _calculate_score(user_ratings, popularity,
                                         min_popularity, avg_rating)
    return products


def _preprocess_data(products_df: pd.DataFrame, sessions_df: pd.DataFrame) -> pd.DataFrame:
    popularity = sessions_df['product_id'].value_counts().rename_axis('product_id').reset_index(name='count')
    products = products_df.drop(columns=['product_name', 'price'])
    products['category_path'] = products['category_path'].apply(_cast_category_path)
    return pd.merge(products, popularity, how='inner', on='product_id')


def _save(scored_products: pd.DataFrame):
    print(scored_products.sort_values('score', ascending=False).head(n=20))
    best_products = scored_products.sort_values('score', ascending=False).head(n=REC_THRESHOLD)["product_id"]
    with open(REC_FILE, 'w') as f:
        json.dump(best_products.to_json(orient='records'), f)


def build(products_df: pd.DataFrame, sessions_df: pd.DataFrame):
    preprocessed = _preprocess_data(products_df, sessions_df)
    scores = _with_score(preprocessed)
    _save(scores)


if __name__ == "__main__":
    productsDataPath = '../notebooks/data/v2/products.jsonl'
    sessionsDataPath = '../notebooks/data/v2/sessions.jsonl'
    sessionsDF = pd.read_json(sessionsDataPath, lines=True)
    productsDF = pd.read_json(productsDataPath, lines=True)
    build(productsDF, sessionsDF)
