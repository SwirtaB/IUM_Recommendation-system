import json
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

sessionsDataPath = '../notebooks/data/v2/sessions.jsonl'
productsDataPath = '../notebooks/data/v2/products.jsonl'
usersDataPath = '../notebooks/data/v2/users.jsonl'

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


def build_user_dict() -> dict:
    usersDF = pd.read_json(usersDataPath, lines=True)
    return pd.Series(usersDF["user_id"].values, index=usersDF.index).to_dict()


def preprocess_session_data() -> pd.DataFrame:
    sessionsDF = pd.read_json(sessionsDataPath, lines=True)

    df = sessionsDF.drop(
        columns=["timestamp", "event_type", "offered_discount", "purchase_id"])
    df["count"] = 1

    return df


def build_interaction_matrix(dataSet: pd.DataFrame) -> pd.DataFrame:
    interactionMatrixDF = pd.pivot_table(dataSet,
                                         index="user_id",
                                         columns="product_id",
                                         values="count",
                                         aggfunc=np.sum,
                                         fill_value=0)
    interactionMatrixDF = pd.DataFrame(
        preprocessing.MinMaxScaler().fit_transform(interactionMatrixDF))

    return interactionMatrixDF


def build_model(interactionMatrix: pd.DataFrame,
                epsilon: int = 1e-9,
                latentFactors: int = 10,
                clusters: int = 8,
                iterations: int = 1000) -> pd.DataFrame:

    #generate user latent features
    userSVD = TruncatedSVD(n_components=latentFactors)
    userFeatures = userSVD.fit_transform(interactionMatrix) + epsilon
    pd.DataFrame(userFeatures)

    kmeans = KMeans(n_clusters=clusters, n_init=iterations)

    model = kmeans.fit_predict(userFeatures)
    return pd.DataFrame(model).rename(columns={0: 'group'},
                                      index=build_user_dict())


def build_user_profile(userID: int, merged: pd.DataFrame) -> dict:
    profile = {}
    userActDF = merged.loc[merged['user_id'] == userID].drop(
        columns=['user_id'])

    for group in newGroups:
        g = userActDF.loc[userActDF['category_path'] == group].drop(
            columns=['category_path']).value_counts().to_frame().rename(
                columns={
                    0: 'count'
                }).reset_index()
        g = g[g['count'] >= g['count'].quantile(0.9)]
        profile[group] = g.set_index('product_id').to_dict()
    return profile


def build_profiles() -> dict:
    sessionsDF = pd.read_json(sessionsDataPath, lines=True)
    productsDF = pd.read_json(productsDataPath, lines=True)
    usersDF = pd.read_json(usersDataPath, lines=True)

    merged = pd.merge(sessionsDF, productsDF, how='inner', on='product_id')
    merged.drop(columns=[
        'session_id', "timestamp", "event_type", "offered_discount",
        "purchase_id", 'product_name', 'price', 'user_rating'
    ],
                inplace=True)
    merged['category_path'] = merged['category_path'].apply(castCategoryPath)

    usersID = usersDF['user_id'].unique()
    profileDict = {}

    for userID in usersID:
        profileDict[userID] = build_user_profile(userID, merged)

    #konieczne jest przepakowanie dict'a, gdyż konwersja z int64 na int ma w numpy'u buga, który dokonuje konwersji int64 na int32. Problem otwarty na Github'ie, tylko Windows.
    return {int(key): value for key, value in profileDict.items()}


def build_groups_top(clusters: int, model: pd.DataFrame) -> dict:
    profileDict = build_profiles()
    groupsTop = {}

    for label in range(0, clusters):
        group = model.loc[model['group'] == label].index
        categoryDict = {}
        for category in newGroups:
            dfListPre = []
            for user in group:
                dfListPre.append(pd.DataFrame(profileDict[user][category]))

            dfList = [
                df.reset_index().rename(columns={'index': 'product_id'})
                for df in dfListPre
            ]

            df = pd.concat(dfList).groupby([
                'product_id'
            ]).sum().reset_index().sort_values(by=['count'], ascending=False)

            df.reset_index(drop=True, inplace=True)
            df.drop(columns=['count'], inplace=True)
            categoryDict[category] = df['product_id'].to_list()

        groupsTop[label] = categoryDict

    #konieczne jest przepakowanie dict'a, gdyż konwersja z int64 na int ma w numpy'u buga, który dokonuje konwersji int64 na int32. Problem otwarty na Github'ie, tylko Windows.
    return {int(key): value for key, value in groupsTop.items()}


def save_model(model: pd.DataFrame, groupsTop: dict):
    model.to_json('../models/similar_users.json')
    with open('../models/groups_profiles.json', 'w') as file:
        json.dump(groupsTop, file, sort_keys=True, indent=4)