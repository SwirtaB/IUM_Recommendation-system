import json
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from preprocessors import preprocessors

"""
    Advanced recommender generates predictions based on similar user groups.
    
    Based on interaction-matrix we can conclude, which users are similar,
    or at least have similar interests.
    After generating the interaction_matrix, dimensionality reduction is 
    performed on it. 
    After that, k-means clustering takes place in order to sign users to groups.
    Finally, for each group, top n products from each category are taken depending 
    on their popularity in this user group (popularity === amount of interactions). 
"""

PRODUCTS_SPACE_DIMENSION = 10
SVD_ITER_AMOUNT = 10

K_MEANS_N_INIT = 50
K_MEANS_N_CLUSTERS = 8


class Recommender:

    def __init__(self, user_to_group: dict, group_recommendations: dict):
        """
        Constructs advanced recommender based on recommendation dictionaries.

        Dictionaries MUST contain all user_ids present in the system and
        all category paths specified for the products.

        :param user_to_group: dictionary containing mapping user_id -> group_id.
        :param group_recommendations:  dictionary containing mapping group_id -> category_path -> list of products.
        """
        self.user_to_group = user_to_group
        self.group_recommendations = group_recommendations

    def recommend(self, user_id: int, category: str) -> list:
        """
        Generates recommendation for the user.

        :param user_id: id of the user for which the recommendation will be generated.
        :param category: name of the currently browsing category.
        :return: list of products recommended to the user.
        """
        return self.group_recommendations[self.user_to_group[user_id]][category]

    def dump(self, user_to_group_fp: str, group_recommendations_fp: str):
        """
        Saves advanced model into two files for convenience with reading.

        In order to reduce it into single file, same clever function is needed
        to distinguish between 2 dictionaries.

        :param user_to_group_fp: file path to store user_to_group dictionary in.
        :param group_recommendations_fp: file path to store group_recommendations dictionary in.
        """
        with (open(user_to_group_fp, 'w')) as file:
            json.dump(self.user_to_group, file, sort_keys=True, indent=4)
        with open(group_recommendations_fp, 'w') as file:
            json.dump(self.group_recommendations, file, sort_keys=True, indent=4)


#####################################################################
# Code below is associated with building the advanced recommender.  #
#####################################################################


def _create_group_predictions(
        sessions_df: pd.DataFrame,
        full_interaction_matrix: pd.DataFrame,
        user_to_group: pd.DataFrame,
        products_df: pd.DataFrame
        ) -> dict:
    # Main dictionary mapping group_id into dictionary category_path -> top predictions.
    user_groups_predictions = {}
    # Include user group information in sessions_df.
    sessions_df = sessions_df.merge(user_to_group, on="user_id")
    # Obtain all possible groups for users to belong to.
    possible_user_groups = user_to_group["group_id"].unique()

    for user_group in possible_user_groups:
        # Obtain dataFrame containing information product_id : popularity within the user_group.
        product_activities_in_group = _product_activities_in_group(user_group, sessions_df, full_interaction_matrix)
        # Merge performed in order to add information on product category_path.
        product_activities_in_group = product_activities_in_group.merge(products_df, on="product_id")
        product_groups = product_activities_in_group.groupby("category_path")
        # Second dictionary, mapping category_path -> array of top products for user group currently looping over.
        category_predictions = {}

        for product_group in product_groups.groups.keys():
            top_products = _top_products_in_group(
                group=product_group,
                product_groups=product_groups,
                products_count=10
            )
            category_predictions[product_group] = top_products["product_id"].to_list()

        user_groups_predictions[int(user_group)] = category_predictions

    return user_groups_predictions


def _product_activities_in_group(
        group: int,
        sessions_df: pd.DataFrame,
        interaction_matrix: pd.DataFrame
        ) -> pd.DataFrame:
    users_in_group = sessions_df[sessions_df["group_id"] == group]["user_id"].unique()
    users_activities = interaction_matrix[interaction_matrix.index.isin(users_in_group)]
    return pd.DataFrame(data=users_activities.sum(axis=0), columns=["activities"])


def _top_products_in_group(
        group,
        product_groups,
        products_count: int = 10
        ) -> pd.DataFrame:
    return product_groups.get_group(group).sort_values(by="activities", ascending=False).head(n=products_count)


def _construct_interaction_matrix(training_set: pd.DataFrame) -> pd.DataFrame:
    return pd.pivot_table(
        data=training_set,
        index="user_id",
        columns="product_id",
        aggfunc=len,
        fill_value=0
    )


def _reduce_dimensionality(interaction_matrix: pd.DataFrame) -> pd.DataFrame:
    svd = TruncatedSVD(
        n_components=PRODUCTS_SPACE_DIMENSION,
        n_iter=SVD_ITER_AMOUNT
    )
    return pd.DataFrame(
        data=svd.fit_transform(interaction_matrix),
        index=interaction_matrix.index
    )


def _perform_grouping(interaction_matrix: pd.DataFrame) -> pd.DataFrame:
    k_means = KMeans(
        n_clusters=K_MEANS_N_CLUSTERS,
        n_init=K_MEANS_N_INIT
    )
    return pd.DataFrame(
        data=k_means.fit_predict(interaction_matrix),
        index=interaction_matrix.index,
        columns=["group_id"]
    )


def build(
        sessions_df: pd.DataFrame,
        products_df: pd.DataFrame
        ) -> (dict, dict):
    """
        Function builds advanced model from sessions and products DataFrames.

        Sessions_df must contain columns named "user_id" and "product_id".
        Products_df must contain columns named "product_id" and "category_path".

        @:param sessions_df - pandas.DataFrame with session records.
        @:param products_df - pandas.DataFrame with products information.

        :returns Advanced model ready to perform predictions.
    """
    # In order to create correct interaction_matrix we need to have only those 2 columns
    # in the dataFrame.
    training_set = sessions_df[["user_id", "product_id"]]
    interaction_matrix = _construct_interaction_matrix(training_set)
    # Dimensionality reduction preformed in order to make grouping faster.
    reduced_interaction_matrix = _reduce_dimensionality(interaction_matrix)
    # Obtained information: dataFrame with user_id : group_id.
    user_to_group = _perform_grouping(reduced_interaction_matrix)
    # Those two lines below can be placed directly into return statement.
    # Decided to leave it for better visual context.
    user_to_group_dict = user_to_group["group_id"].to_dict()
    predictions_dict = _create_group_predictions(
        sessions_df=sessions_df,
        products_df=products_df,
        full_interaction_matrix=interaction_matrix,
        user_to_group=user_to_group,
    )

    return Recommender(
        user_to_group=user_to_group_dict,
        group_recommendations=predictions_dict
    )


def from_files(
        user_to_group_fp: str,
        group_recommendations_fp: str
        ) -> Recommender:
    """
    Function constructs advanced recommender from files provided.

    Files should contain dictionaries used during predictions (created with Recommender.dump()).

    :param user_to_group_fp: file path pointing to stored user_to_group dictionary data
    :param group_recommendations_fp: file path pointing to stored group_recommendations dictionary data.
    :return: Recommender constructed from files.
    """
    with (open(user_to_group_fp, 'r')) as file:
        user_to_group = json.load(file)
    with open(group_recommendations_fp, 'r') as file:
        group_recommendations = json.load(file)

    return Recommender(
        user_to_group={int(key): value for key, value in user_to_group.items()},
        group_recommendations={int(key): value for key, value in group_recommendations.items()}
    )


if __name__ == '__main__':
    sessionsDataPath = '../notebooks/data/v2/sessions.jsonl'
    productsDataPath = '../notebooks/data/v2/products.jsonl'

    productsDF = pd.read_json(productsDataPath, lines=True)
    sessionsDF = pd.read_json(sessionsDataPath, lines=True)

    sessionsDF, productsDF = preprocessors.preprocess_data_for_advanced_model(
        sessions_df=sessionsDF,
        products_df=productsDF
    )

    recommender = build(sessionsDF, productsDF)

    print("Recommender constructed without error is read to use...")
    print('Sample recommendation for user 102 browsing product with category path "Gry na konsole"...')
    print(recommender.recommend(102, "Gry na konsole"))
    recommender.dump(
        user_to_group_fp="advanced/user_to_group.json",
        group_recommendations_fp="advanced/group_recommendations.json"
    )
    restored_recommender = from_files(
        user_to_group_fp="advanced/user_to_group.json",
        group_recommendations_fp="advanced/group_recommendations.json"
    )
    print('\n')
    print("Recommender read from file is ready to use...")
    print('Sample recommendation for user 102 browsing product with category path "Gry na konsole"...')
    print(restored_recommender.recommend(102, "Gry na konsole"))
