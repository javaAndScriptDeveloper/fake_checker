import os

import yaml

CONFIG_FILE_NAME = 'config/config.yaml'

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
        self.call_to_action_coeff = None
        self.repeated_take_coeff = None
        self.repeated_note_coeff = None
        self.total_coeff = None
        self.average_news_simplicity = None
        self.text_simplicity = None
        self.similarity_threshold = None
        self.tg_api_id = None
        self.tg_api_hash = None
        self.tg_channel_names = []

config = Config()
config_file = read_config(CONFIG_FILE_NAME)
config.sentimental_score_coeff = config_file['coefficient']['sentimental_score']
config.triggered_keywords_coeff = config_file['coefficient']['triggered_keywords']
config.triggered_topics_coeff = config_file['coefficient']['triggered_topics']
config.confidence_factor_coeff = config_file['coefficient']['confidence_factor']
config.clickbait_coeff = config_file['coefficient']['clickbait']
config.subjective_coeff = config_file['coefficient']['subjective']
config.call_to_action_coeff = config_file['coefficient']['call_to_action']
config.repeated_take_coeff = config_file['coefficient']['repeated_take']
config.repeated_note_coeff = config_file['coefficient']['repeated_note']
config.total_coeff = (config.sentimental_score_coeff \
                     + config.triggered_keywords_coeff \
                     + config.triggered_topics_coeff \
                     + config.confidence_factor_coeff \
                     + config.clickbait_coeff \
                     + config.subjective_coeff \
                     + config.call_to_action_coeff \
                     + config.repeated_take_coeff \
                     + config.repeated_note_coeff)
config.text_simplicity_deviation = config_file['coefficient']['text_simplicity_deviation']
config.average_news_simplicity = config_file['average_news_simplicity']
config.similarity_threshold = config_file['similarity_threshold']
