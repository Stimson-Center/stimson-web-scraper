import psutil
import shutil
from flask_restful import Resource

class Health(Resource):
    @staticmethod
    def get():
        total, used, free = shutil.disk_usage("/")
        return {
            'cpu_in_use': psutil.cpu_percent(),
            'memory_in_use': psutil.virtual_memory().percent,
            'diskspace_in_use': round(used / total * 100, 1)
        }
