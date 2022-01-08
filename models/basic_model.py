import pandas as pd
import numpy as np

separator = ';'
newGroups = [
    'Gry komputerowe', 'Gry na konsole', 'Sprzęt RTV', 'Komputery',
    'Telefony i akcesoria'
]


def castCategoryPath(categoryPath):
    categories = categoryPath.split(separator)
    foundGroups = [group for group in newGroups if group in categories]
    if len(foundGroups) != 1:
        raise RuntimeError('wrong group cast: {}'.format(foundGroups))
    return foundGroups[0]


def calculate_raiting(raiting, popularity, minPopularity,
                      avgRaiting) -> pd.Series:
    return ((popularity / (popularity + minPopularity)) * raiting) + (
        (minPopularity / (popularity + minPopularity)) * avgRaiting)


def assigne_raiting(productsDF: pd.DataFrame) -> pd.Series:
    avgRaiting = productsDF['user_rating'].mean()
    minPopularity = np.percentile(productsDF['count'], 80)
    #deep copy because it is modified and returned as result
    products = productsDF[productsDF['count'] >= minPopularity].copy(deep=True)
    userRaitings = products['user_rating']
    popularity = products['count']

    products['score'] = calculate_raiting(userRaitings, popularity,
                                          minPopularity, avgRaiting)
    return products


def preprocess_data(productsDF: pd.DataFrame,
                    sessionsDF: pd.DataFrame) -> pd.DataFrame:
    popularity = sessionsDF['product_id'].value_counts().rename_axis(
        'product_id').reset_index(name='count')
    products = productsDF.drop(columns=['product_name', 'price'])
    products['category_path'] = products['category_path'].apply(
        castCategoryPath)

    return pd.merge(products, popularity, how='inner', on='product_id')


def build_profile(ratingsDF: pd.DataFrame):
    #Nwm czy o to chodziło, na końcu notatnika 'basic_model.ipynb' zaimplementowałem stosowny kod.
    pass


def build(productsDF: pd.DataFrame, sessionsDF: pd.DataFrame) -> pd.DataFrame:
    raitings = assigne_raiting(preprocess_data(productsDF, sessionsDF))
    raitings.drop(columns=['user_rating', 'count'])
    raitings.sort_values('score', ascending=False)

    return raitings