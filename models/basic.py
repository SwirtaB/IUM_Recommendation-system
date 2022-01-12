import json
import pandas as pd
import numpy as np
from preprocessors import preprocessors

"""
    Basic model creates predictions based on score assigned to each product.
    
    Predictions are constant in time (they are the same list containing the 
    best products in the store for each user). 
    
    Score metric is based on the IMDB metric.   
"""


class Recommender:

    def __init__(self, recommendations: list):
        """
        Constructs basic Recommender based on recommendation list.

        Recommendations list should contain BEST products from the whole store.
        The way it is calculated is left to the provider.

        :param recommendations: list containing the best products.
        """
        self.recommendations = recommendations

    def recommend(self, unused_user_id: int, unused_category: str) -> list:
        """
        Generates recommendation for the user.

        :param unused_user_id: this parameter is not used.
        :param unused_category: this parameter is not used.
        :return: list of products recommended to the user.
        """
        return self.recommendations

    def dump(self, recommendations_fp: str):
        """
        Saves basic model into file.

        :param recommendations_fp: file path to store recommendations list in.
        """
        with (open(recommendations_fp, 'w')) as file:
            json.dump(self.recommendations, file)


################################################################
#  Code below is associated with building basic Recommender.   #
################################################################


def _calculate_score(rating, popularity, min_popularity, avg_rating) -> pd.Series:
    return ((popularity / (popularity + min_popularity)) * rating) + (
            (min_popularity / (popularity + min_popularity)) * avg_rating)


def _products_with_score(products_df: pd.DataFrame) -> pd.DataFrame:
    avg_rating = products_df['user_rating'].mean()
    min_popularity = np.percentile(products_df['popularity'], 80)
    # Deep copy because products df is modified and returned as the result.
    products = products_df[products_df['popularity'] >= min_popularity].copy(deep=True)
    user_ratings = products['user_rating']
    popularity = products['popularity']
    products['score'] = _calculate_score(
        user_ratings,
        popularity,
        min_popularity,
        avg_rating
    )

    return products


def _assign_popularity_to_products(
        sessions_df: pd.DataFrame,
        products_df: pd.DataFrame
        ) -> pd.DataFrame:
    popularity = sessions_df['product_id'].value_counts().rename_axis('product_id').reset_index(name='popularity')
    return pd.merge(products_df, popularity, how='inner', on='product_id')


def _best_list_products(scored_products: pd.DataFrame, n: int = 10) -> list:
    return scored_products.sort_values('score', ascending=False).head(n=n)["product_id"].to_list()


def build(sessions_df: pd.DataFrame, products_df: pd.DataFrame) -> Recommender:
    """
    Builds basic model based on provides sessions and products DataFrames.

    Sessions_df must contain columns named "product_id".
    Products_df must contain columns named "user_rating" and "product_id".

    :param products_df: pd.DataFrame containing products information.
    :param sessions_df: pd.DataFrame containing sessions information.
    :return: basic Recommender.
    """
    products_with_popularity = _assign_popularity_to_products(sessions_df, products_df)
    products_with_scores = _products_with_score(products_with_popularity)
    recommendations = _best_list_products(products_with_scores)
    return Recommender(
        recommendations=recommendations
    )


def from_file(recommendations_fp: str) -> Recommender:
    """
    Function restores basic Recommender from file.

    :param recommendations_fp: file containing recommendations for basic Recommender (created with Recommender.dump())
    :return: basic Recommender constructed from data in file.
    """
    with open(recommendations_fp, 'r') as file:
        recommendations = json.load(file)
    return Recommender(
        recommendations=recommendations
    )


if __name__ == "__main__":
    productsDataPath = '../notebooks/data/v2/products.jsonl'
    sessionsDataPath = '../notebooks/data/v2/sessions.jsonl'

    sessionsDF = pd.read_json(sessionsDataPath, lines=True)
    productsDF = pd.read_json(productsDataPath, lines=True)

    sessionsDF, productsDF = preprocessors.preprocess_data_for_basic_model(
        sessions_df=sessionsDF,
        products_df=productsDF
    )

    recommender = build(sessionsDF, productsDF)

    print("Recommender constructed without error is read to use...")
    print('Sample recommendation for user 102 browsing product with category path "Gry na konsole"...')
    print(recommender.recommend(102, "Gry na konsole"))
    recommender.dump(
        recommendations_fp="basic/recommendations.json"
    )
    restored_recommender = from_file(
        recommendations_fp="basic/recommendations.json"
    )
    print('\n')
    print("Recommender read from file is ready to use...")
    print('Sample recommendation for user 102 browsing product with category path "Gry na konsole"...')
    print(restored_recommender.recommend(102, "Gry na konsole"))
