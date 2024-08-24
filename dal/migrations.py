from core.enums import PLATFORM_TYPE
from core.singletons import note_dao, source_dao
from dal.dal import Note, Source


def clean_tables():
    note_dao.session.query(Note).delete()
    source_dao.session.query(Source).delete()

def save_initial_sources():
    source_dao.save(
        Source(name='tmp12345678t', external_id = "2031253701", platform=PLATFORM_TYPE.TELEGRAM.name))
    source_dao.save(
        Source(name='pandoras_box_ua', external_id = "1360737249", platform=PLATFORM_TYPE.TELEGRAM.name))