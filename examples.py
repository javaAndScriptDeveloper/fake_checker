import json
import random

from dal.dal import Source
from enums import PLATFORM_TYPE
from singletons import manager, source_dao


def create_new_source():
    id = random.randint(10000, 99999)
    source = Source(id=id, name=str(id), external_id=str(id), platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=False)
    source_dao.save(source)
    return id


def read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def process_file(path):
    source_id = create_new_source()
    file = read_file(path)
    title = file.get("title", "")
    content = file.get("content", "")
    print(manager.process(title, content, source_id, "english"))

process_file("data/examples/putin_address_to_general_assambly.json")
process_file("data/examples/macron_vision.json")
process_file("data/examples/trump_tulsa.json")
process_file("data/examples/trump_we_will_never_give_up.json")
process_file("data/examples/hitler_proclamation_to_german_nation.json")
process_file("data/examples/hitler_sportpalats_speech.json")
process_file("data/examples/linear_geometry.json")
process_file("data/examples/magic_of_math.json")
process_file("data/examples/ocean_investigations.json")
process_file("data/examples/farming_apples.json")
