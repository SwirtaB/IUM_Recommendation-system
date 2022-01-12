from flask import Flask, request
from flask_restful import Resource, Api
from models.advanced import from_files as advanced_from_files
from models.basic import from_file as basic_from_file

basic_recommender_fp = "../models/basic/recommendations.json"

advanced_user_to_group_fp = "../models/advanced/user_to_group.json"
advanced_group_recommendations_fp = "../models/advanced/group_recommendations.json"

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

# Setting up the flask application.
app = Flask(__name__)
api = Api(app)


class Recommender(Resource):
    @staticmethod
    def get():
        try:
            query_param_dict = Recommender.__query_args()
        except RuntimeError as err:
            return {
                "message": str(err)
            }, 400

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
            return {
                "message": "unknown model type!"
            }, 400

        return {
            "recommendations": recommendations
        }

    @staticmethod
    def __query_args() -> dict:
        args = request.args
        needed_keys = ["user_id", "category_path", "model"]
        for key in needed_keys:
            if key not in args:
                raise RuntimeError("{} value is missing!".format(key))
        return args.to_dict()


api.add_resource(Recommender, '/')

if __name__ == '__main__':
    app.run()
