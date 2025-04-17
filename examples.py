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
    print(manager.process(title, content, source_id))

process_file("data/examples/putin_speech.json")
process_file("data/examples/sockets.json")
process_file("data/examples/tucker_carlson.json")
process_file("data/examples/trump_on_economics.json")
process_file("data/examples/magic_of_math.json")
process_file("data/examples/space_x.json")
process_file("data/examples/nets_shorthanded_again.json")
process_file("data/examples/trump_liz_truss_moment.json")
process_file("data/examples/the_pitt_tv_show_at_the_moment.json")