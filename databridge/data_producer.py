import logging
import sys
from abc import ABC, abstractmethod
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import ChannelPrivateError

import mapper.mapper
from config import config
import asyncio

from core.enums import PLATFORM_TYPE
from exception.exceptions import NotSupportedPlatformTypeException
from model.model import DataMessage, ProduceDataMessagesCommand

class AbstractParser(ABC):

    @abstractmethod
    def fetch_messages(self, channel_names: [str], post_extract_message_func):
        pass

    @abstractmethod
    def listen_for_new_messages(self, channel_names: [str], post_extract_message_func):
        pass

    def log_data_message(self, data_message: DataMessage):
        TRUNCATED_TEXT_CONTENT_LOG_LENGTH = 50
        print(
            f"Received message with content {data_message.text_content[:TRUNCATED_TEXT_CONTENT_LOG_LENGTH]}")

class TelegramParser(AbstractParser):

    SESSION_NAME_FETCH_MESSAGES = 'session_fetch_messages'
    SESSION_NAME_LISTEN_FOR_NEW_MESSAGES = 'session_listen_for_new_messages'

    async def _async_fetch_messages(self, session_name, api_id, api_hash, channel_names, post_extract_message_func):
        async with TelegramClient(session_name, api_id, api_hash) as client:
            for channel_name in channel_names:
                try:
                    entity = await client.get_entity(channel_name)
                    async for message in client.iter_messages(entity):
                        data_message = mapper.mapper.ParserMapper.mapTelegramMessage(message)
                        self.log_data_message(data_message)
                        post_extract_message_func(data_message)

                except ChannelPrivateError:
                    print("The channel is private. Make sure to add the bot as an admin.")

    async def _async_listen_for_new_messages(self, session_name, api_id, api_hash, channel_names, post_extract_message_func):
        async with TelegramClient(session_name, api_id, api_hash) as client:
            for channel_name in channel_names:
                try:
                    entity = await client.get_entity(channel_name)
                    async for message in client.iter_messages(entity):
                        data_message = mapper.mapper.ParserMapper.mapTelegramMessage(message)
                        self.log_data_message(data_message)
                        post_extract_message_func(data_message)
                except ChannelPrivateError:
                    print("The channel is private. Make sure to add the bot as an admin.")

    async def async_fetch_messages(self, channel_names, post_extract_message_func):
        api_id = config.tg_api_id
        api_hash = config.tg_api_hash

        task_fetch_messages = asyncio.create_task(
            self._async_fetch_messages(self.SESSION_NAME_FETCH_MESSAGES, api_id, api_hash, channel_names, post_extract_message_func))
        await asyncio.gather(task_fetch_messages)

    async def async_listen_for_new_messages(self, channel_names, post_extract_message_func):
        api_id = config.tg_api_id
        api_hash = config.tg_api_hash

        listen_for_new_messages = asyncio.create_task(
            self._async_listen_for_new_messages(self.SESSION_NAME_FETCH_MESSAGES, api_id, api_hash, channel_names, post_extract_message_func))
        await asyncio.gather(listen_for_new_messages)

    def fetch_messages(self, channel_names, post_extract_message_func):
        asyncio.run(self.async_fetch_messages(channel_names, post_extract_message_func))

    def listen_for_new_messages(self, channel_names, post_extract_message_func):
        asyncio.run(self.async_listen_for_new_messages(channel_names, post_extract_message_func))

telegram_parser = TelegramParser()

class DataProducer:

    def produce(self, produce_data_messages_command: ProduceDataMessagesCommand):
        if (produce_data_messages_command.platform_type == PLATFORM_TYPE.TELEGRAM):
            if (len(produce_data_messages_command.sources_to_fetch)):
                telegram_parser.fetch_messages(produce_data_messages_command.sources_to_fetch, produce_data_messages_command.post_extract_func)

            if(len(produce_data_messages_command.sources_to_listen)):
                telegram_parser.listen_for_new_messages(produce_data_messages_command.sources_to_listen, produce_data_messages_command.post_extract_func)
            return

        raise NotSupportedPlatformTypeException(produce_data_messages_command.platform_type)

