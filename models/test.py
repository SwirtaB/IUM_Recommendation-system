import random
import pandas as pd
from preprocessors import preprocessors
from basic import build as build_basic
from advanced import build as build_advanced

"""
    Code present in this file is responsible for models testing, both basic and advanced.
    
    Metric used for testing purposes is accuracy.
    
    Test and train set creation algorithm:
        - From all sessions pick those, which have some bigger events count (ex. 8).
        - From picked sessions choose BATCH_SIZE adjacent activities.
        - Add those 3 adjacent activities to test set.
        - Finally, form train set as the set difference of sessions set - test set.
        
    Model evaluation algorithm:
        - Sort test set by session_id column.
        - Iterate over test batch.
            - For each activity in batch, generate the model prediction.
            - Check, if prediction contains the next product which user had interaction with within the batch.
            - If yes, increment good predictions counter.
        - Calculate model accuracy. 
"""


# Batch is the adjacent activities count within the session.
BATCH_SIZE = 3


# Picks sessions having the size equal to or greater than n_min value.
def _sessions_with_min_size(sessions_df: pd.DataFrame, n_min: int = 8) -> pd.DataFrame:
    activity_count = sessions_df.groupby("session_id").size()
    big_sessions = activity_count[activity_count > n_min]
    return sessions_df[sessions_df["session_id"].isin(big_sessions.index)]


def _form_test_set(big_sessions_df: pd.DataFrame) -> pd.DataFrame:
    random.seed()
    events_grouped_by_session = big_sessions_df.groupby("session_id")
    test_set = pd.DataFrame(
        data=None,
        columns=big_sessions_df.columns
    )
    # Below loop picks BATCH_SIZE adjacent events from each big session,
    # and appends them to the test set.
    for session_key in events_grouped_by_session.groups.keys():
        single_session = events_grouped_by_session.get_group(session_key)
        picked_idx = random.randint(0, single_session.shape[0] - BATCH_SIZE)
        test_set = test_set.append(single_session.iloc[picked_idx: picked_idx+BATCH_SIZE])

    return test_set


def _form_train_set(sessions_df: pd.DataFrame, test_set: pd.DataFrame) -> pd.DataFrame:
    test_set_indices = [i for i in sessions_df.index.tolist() if i not in test_set.index.tolist()]
    return sessions_df[sessions_df.index.isin(test_set_indices)]


def _train_test_split_sessions_data(sessions_df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    #####################################################################
    # Group sessions by session_id                                      #
    # Select only sessions which has more than 8 activities in it.      #
    # From each selected pick at random BATCH_SIZE adjacent activities. #
    # Picked activities will form test set.                             #
    # From the rest of session data, erase picked activities.           #
    # Sessions with erased activities will form train set.              #
    #####################################################################

    # Big sessions stores sessions with size (aka. events_count) larger than 8.
    big_sessions = _sessions_with_min_size(sessions_df)
    print("Beginning to form test set...")
    test_set = _form_test_set(big_sessions)
    print("Finished creation of test set...")
    print("Beginning to form train set...")
    train_set = _form_train_set(sessions_df, test_set)
    print("Finished creation of train set...")
    return train_set, test_set


def _test_model(test_set: pd.DataFrame, model):
    ###################################################################
    # For each session activity without the last, perform prediction. #
    # Check, if next seen product is present in prediction obtained.  #
    # If it is, increment correct predictions.                        #
    # Metric used is Accuracy (good_predictions / all_predictions).   #
    ###################################################################
    test_set.sort_values(by="session_id", inplace=True)
    good_predictions, all_predictions = 0, (test_set.shape[0] / BATCH_SIZE) * (BATCH_SIZE - 1)
    for i in range(0, test_set.shape[0] - BATCH_SIZE, BATCH_SIZE):
        for j in range(0, BATCH_SIZE):
            current_session_action = test_set.iloc[i+j]
            predictions = model.recommend(
                user_id=current_session_action["user_id"],
                category=current_session_action["category_path"]
            )
            if test_set.iloc[i+j+1]["product_id"] in predictions:
                good_predictions += 1

    accuracy = (good_predictions / all_predictions) * 100
    print("{} recommender achieved {:.2f} accuracy.".format(model.name(), accuracy))


if __name__ == "__main__":
    sessions_df_fp = "../data/sessions.jsonl"
    products_df_fp = "../data/products.jsonl"

    sessionsDF = pd.read_json(sessions_df_fp, lines=True)
    productsDF = pd.read_json(products_df_fp, lines=True)

    train_df, test_df = _train_test_split_sessions_data(sessions_df=sessionsDF)
    # Adding category path column to the sessions in order to make predictions easier.
    # Now there is no need to pass products DataFrame to _test_model method.
    predictions_ready_test_set = preprocessors.preprocess_data_for_predictions(test_df, productsDF)
    print("Beginning to build models...")
    basic_train_set, basic_products_set = preprocessors.preprocess_data_for_basic_model(train_df, productsDF)
    basic_recommender = build_basic(basic_train_set, basic_products_set)
    print("Built basic recommender without errors...")
    adv_train_set, adv_products_set = preprocessors.preprocess_data_for_advanced_model(train_df, productsDF)
    advanced_recommender = build_advanced(adv_train_set, adv_products_set)
    print("Built advanced recommender without errors...")

    _test_model(predictions_ready_test_set, basic_recommender)
    _test_model(predictions_ready_test_set, advanced_recommender)
