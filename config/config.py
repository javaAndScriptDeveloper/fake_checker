import os

import yaml

CONFIG_FILE_NAME = 'config/config.yaml'

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

class Config:

    def __init__(self):
        self.sentimental_score_coeff = 1
        self.triggered_keywords_coeff = 1
        self.triggered_topics_coeff = 1
        self.confidence_factor_coeff = 1
        self.clickbait_coeff = 1
        self.subjective_coeff = 1
        self.call_to_action_coeff = 1
        self.repeated_take_coeff = 1
        self.repeated_note_coeff = 1
        self.total_coeff = 1
        self.average_news_simplicity = 1
        self.text_simplicity = 1
        self.similarity_threshold = 1
        self.tg_api_id = 1
        self.tg_api_hash = 1

config = Config()
config_file = read_config(CONFIG_FILE_NAME)
config.average_news_simplicity = config_file['average_news_simplicity']
config.similarity_threshold = config_file['similarity_threshold']
