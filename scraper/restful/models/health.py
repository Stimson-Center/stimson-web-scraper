import psutil
from flask_restful import Resource


class Health(Resource):
    @staticmethod
    def get():
        return {
            'cpu_in_use': psutil.cpu_percent(),
            'memory_in_use': psutil.virtual_memory().percent
        }
