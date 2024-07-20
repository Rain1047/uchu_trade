from datetime import datetime, timedelta
import os
import json


class DateUtils:
    @staticmethod
    def current_time2string():
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    @staticmethod
    def past_time2string(days):
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def get_config():
        script_dir = os.path.dirname(os.path.realpath(__file__))
        config_file_path = os.path.join(script_dir, '../config.json')
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        return config


class CheckUtils:
    @staticmethod
    def is_empty(value):
        if value is None:
            return True
        if isinstance(value, (str, list, tuple, dict, set)):
            return len(value) == 0
        return False

    @staticmethod
    def is_not_empty(value):
        return not CheckUtils.is_empty(value)


# 示例用法
if __name__ == "__main__":
    print(DateUtils.current_time2string())

    print(DateUtils.past_time2string(20))
