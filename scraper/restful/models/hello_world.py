from flask_restful import Resource


class HelloWorld(Resource):
    @staticmethod
    def get():
        return {'hello': 'world'}
