import random
import pandas as pd


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
    # Below loop picks 3 adjacent events from each big session,
    # and appends them to the test set.
    # Printing is used for verbose communication with the user.
    for session_key in events_grouped_by_session.groups.keys():
        single_session = events_grouped_by_session.get_group(session_key)
        picked_idx = random.randint(0, single_session.shape[0] - 3)
        test_set = test_set.append(single_session.iloc[picked_idx: picked_idx+3])

    return test_set


def _form_train_set(sessions_df: pd.DataFrame, test_set: pd.DataFrame) -> pd.DataFrame:
    test_set_indices = [i for i in sessions_df.index.tolist() if i not in test_set.index.tolist()]
    return sessions_df[sessions_df.index.isin(test_set_indices)]


def _train_test_split_sessions_data(sessions_df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    ################################################################
    # Group sessions by session_id                                 #
    # Select only sessions which has more than 8 activities in it. #
    # From each selected pick at random 3 adjacent activities.     #
    # Picked activities will form test set.                        #
    # From the rest of session data, erase picked activities.      #
    # Sessions with erased activities will form train set.         #
    ################################################################

    # Big sessions stores sessions with size (aka. events_count) larger than 8.
    big_sessions = _sessions_with_min_size(sessions_df)
    print("Beginning to form test set...")
    test_set = _form_test_set(big_sessions)
    print("Finished creation of test set...")
    print("Beginning to form train set...")
    train_set = _form_train_set(sessions_df, test_set)
    print("Finished creation of train set...")
    return train_set, test_set


if __name__ == "__main__":
    sessions_df_fp = "../data/sessions.jsonl"
    products_df_fp = "../data/products.jsonl"

    sessionsDF = pd.read_json(sessions_df_fp, lines=True)
    productsDF = pd.read_json(products_df_fp, lines=True)

    train_df, test_df = _train_test_split_sessions_data(sessions_df=sessionsDF)
    print(train_df.shape[0])
    print(test_df.shape[0])
