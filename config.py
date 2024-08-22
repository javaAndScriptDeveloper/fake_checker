import os

import yaml

CONFIG_FILE_NAME = 'config.yaml'

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

class Config:

    def __init__(self):
        self.sentimental_score_coeff = None
        self.triggered_keywords_coeff = None
        self.triggered_topics_coeff = None
        self.confidence_factor_coeff = None
        self.clickbait_coeff = None
        self.subjective_coeff = None
        self.average_news_simplicity = None
        self.text_simplicity = None
        self.tg_api_id = None
        self.tg_api_hash = None
        self.tg_channel_names = []

config = Config()
config_file = read_config(CONFIG_FILE_NAME)
config.sentimental_score_coeff = config_file['coefficient']['sentimental_score']
config.triggered_keywords_coeff = config_file['coefficient']['triggered_keywords']
config.triggered_topics_coeff = config_file['coefficient']['triggered_topics']
config.confidence_factor_coeff = config_file['coefficient']['confidence_factor']
config.text_simplicity_deviation = config_file['coefficient']['text_simplicity_deviation']
config.clickbait_coeff = config_file['coefficient']['clickbait']
config.subjective_coeff = config_file['coefficient']['subjective']
config.average_news_simplicity = config_file['average_news_simplicity']
config.tg_channel_names = config_file['tg']['channel_names']
config.tg_api_id = os.environ['TG_API_ID']
config.tg_api_hash = os.environ['TG_API_HASH']
