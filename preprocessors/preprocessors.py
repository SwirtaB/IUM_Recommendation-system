import typing
import pandas as pd

NEW_GROUPS = [
    'Gry komputerowe',
    'Gry na konsole',
    'Sprzęt RTV',
    'Komputery',
    'Telefony i akcesoria'
]

SEPARATOR = ';'


def _cast_category_path(category_path):
    categories = category_path.split(SEPARATOR)
    found_groups = [group for group in NEW_GROUPS if group in categories]
    if len(found_groups) != 1:
        raise RuntimeError('wrong group cast: {}'.format(found_groups))
    return found_groups[0]


def _preprocess_products_for_advanced_model(products_df: pd.DataFrame) -> pd.DataFrame:
    product_drop_columns = [
        "price",
        "product_name",
        "user_rating"
    ]
    new_products_df = products_df.drop(columns=product_drop_columns)
    new_products_df["category_path"] = new_products_df["category_path"].apply(_cast_category_path)
    return new_products_df


def _preprocess_sessions_for_advanced_model(sessions_df: pd.DataFrame) -> pd.DataFrame:
    session_drop_columns = [
        "timestamp",
        "event_type",
        "offered_discount",
        "purchase_id",
        "session_id"
    ]
    return sessions_df.drop(columns=session_drop_columns)


def preprocess_data_for_advanced_model(
        sessions_df: pd.DataFrame,
        products_df: pd.DataFrame
        ) -> typing.Tuple[pd.DataFrame, pd.DataFrame]:
    return (
        _preprocess_sessions_for_advanced_model(sessions_df=sessions_df),
        _preprocess_products_for_advanced_model(products_df=products_df)
    )


def preprocess_data_for_basic_model(
        sessions_df: pd.DataFrame,
        products_df: pd.DataFrame
        ) -> typing.Tuple[pd.DataFrame, pd.DataFrame]:
    product_drop_columns = [
        "product_name",
        "category_path",
        "price"
    ]
    session_drop_columns = [
        "timestamp",
        "event_type",
        "offered_discount",
        "purchase_id",
        "session_id",
        "user_id"
    ]
    new_sessions = sessions_df.drop(columns=session_drop_columns)
    new_products = products_df.drop(columns=product_drop_columns)
    return (
        new_sessions,
        new_products
    )


def preprocess_data_for_predictions(
        sessions_df: pd.DataFrame,
        products_df: pd.DataFrame) -> pd.DataFrame:
    result = sessions_df.merge(products_df, on="product_id")
    result["category_path"] = result["category_path"].apply(_cast_category_path)
    return result
