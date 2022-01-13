from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime
from uuid import uuid4
from logger import Logger
from models.advanced import from_files as advanced_from_files
from models.basic import from_file as basic_from_file

basic_recommender_fp = "../models/basic/recommendations.json"

advanced_user_to_group_fp = "../models/advanced/user_to_group.json"
advanced_group_recommendations_fp = "../models/advanced/group_recommendations.json"

logs_fp = "logs/logs.txt"

############################################################################
# NOTE                                                                     #
# Models should be already created before running the service.             #
# Code will crash, if files specified in paths above (ending with _fp)     #
# do not exist or are corrupted!                                           #
############################################################################

advanced_model = advanced_from_files(
    user_to_group_fp=advanced_user_to_group_fp,
    group_recommendations_fp=advanced_group_recommendations_fp
)

basic_model = basic_from_file(
    recommendations_fp=basic_recommender_fp
)

logger = Logger(logging_fp=logs_fp)

# Setting up the flask application.
app = Flask(__name__)
api = Api(app)


class Recommender(Resource):
    @staticmethod
    def get():
        response = {
            "id": str(uuid4()),
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        try:
            query_param_dict = Recommender.__query_args()
        except RuntimeError as err:
            response["message"] = str(err)
            return Recommender.__send_response(response, 400)

        response["user_id"] = int(query_param_dict["user_id"])
        response["model"] = query_param_dict["model"]

        if query_param_dict["model"] == "advanced":
            recommendations = advanced_model.recommend(
                user_id=int(query_param_dict["user_id"]),
                category=str(query_param_dict["category_path"])
            )
        elif query_param_dict["model"] == "basic":
            recommendations = basic_model.recommend(
                user_id=int(query_param_dict["user_id"]),
                category=str(query_param_dict["category_path"])
            )
        else:
            response["message"] = "unknown model type!"
            return Recommender.__send_response(response, 400)

        response["recommendations"] = recommendations
        return Recommender.__send_response(response)

    @staticmethod
    def __query_args() -> dict:
        args = request.args
        needed_keys = ["user_id", "category_path", "model"]
        for key in needed_keys:
            if key not in args:
                raise RuntimeError("{} value is missing!".format(key))
        return args.to_dict()

    @staticmethod
    def __send_response(response, code: int = 200):
        logger.log(response)
        return response, code


api.add_resource(Recommender, '/')

if __name__ == '__main__':
    app.run()
