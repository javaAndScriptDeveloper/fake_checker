from automapper import mapper
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, MetaData,
                        Numeric, String, Text, create_engine, func, text, Boolean)
from sqlalchemy.orm import DeclarativeBase, Session

from enums import PLATFORM_TYPE

engine = create_engine('postgresql://postgres:password@localhost:5432/fake_checker')

session = Session(engine)


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    name = Column(String, nullable=False)
    rating = Column(Numeric, nullable=True)
    is_hidden = Column(Boolean, nullable=True)


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)

    sentimental_score_coeff = Column(Numeric, default=0)
    sentimental_score_raw = Column(Numeric, default=0)
    sentimental_score = Column(Numeric, default=0)  # x2

    triggered_keywords_coeff = Column(Numeric, default=0)
    triggered_keywords_raw = Column(Numeric, default=0)
    triggered_keywords = Column(Numeric, default=0)  # x

    triggered_topics_coeff = Column(Numeric, default=0)
    triggered_topics_raw = Column(Numeric, default=0)
    triggered_topics = Column(Numeric, default=0)  # x7

    text_simplicity_deviation_coeff = Column(Numeric, default=0)
    text_simplicity_deviation_raw = Column(Numeric, default=0)
    text_simplicity_deviation = Column(Numeric, default=0)  # x5

    confidence_factor_coeff = Column(Numeric, default=0)
    confidence_factor_raw = Column(Numeric, default=0)
    confidence_factor = Column(Numeric, default=100)  # x6

    clickbait_coeff = Column(Numeric, default=0)
    clickbait_raw = Column(Numeric, default=0)
    clickbait = Column(Numeric, default=0)  # x10

    subjective_coeff = Column(Numeric, default=0)
    subjective_raw = Column(Numeric, default=0)
    subjective = Column(Numeric, default=0)  # x1

    call_to_action_coeff = Column(Numeric, default=0)
    call_to_action_raw = Column(Numeric, default=0)
    call_to_action = Column(Numeric, default=0)  # x8

    repeated_take_coeff = Column(Numeric, default=0)
    repeated_take_raw = Column(Numeric, default=0)
    repeated_take = Column(Numeric, default=0)  # x3

    repeated_note_coeff = Column(Numeric, default=0)
    repeated_note_raw = Column(Numeric, default=0)
    repeated_note = Column(Numeric, default=0)  # x4

    messianism_coeff = Column(Numeric, default=0)
    messianism_raw = Column(Numeric, default=0)
    messianism = Column(Numeric, default=0)

    opposition_to_opponents_coeff = Column(Numeric, default=0)
    opposition_to_opponents_raw = Column(Numeric, default=0)
    opposition_to_opponents = Column(Numeric, default=0)

    generalization_of_opponents_coeff = Column(Numeric, default=0)
    generalization_of_opponents_raw = Column(Numeric, default=0)
    generalization_of_opponents = Column(Numeric, default=0)

    total_score_coeff = Column(Numeric, default=0)
    total_score_raw = Column(Numeric, default=0)
    total_score = Column(Numeric, default=50)

    cosine_similarity_coeff = Column(Numeric, default=0)
    cosine_similarity_raw = Column(Numeric, default=0)
    cosine_similarity = Column(Numeric, default=0)

    total_score_sum = Column(Numeric, default=0)
    cosine_similarity_sum = Column(Numeric, default=0)
    total_score_size = Column(Numeric, default=0)
    cosine_similarity_size = Column(Numeric, default=0)

    fehner_type = Column(String)
    is_propaganda = Column(Boolean)
    reason = Column(Text, nullable=True)
    amount_of_propaganda_scores = Column(Numeric, nullable=True)
    hash = Column(String)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    reposted_from_source_id = Column(Integer, ForeignKey('sources.id'), nullable=True)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    @classmethod
    def get_all_sentimental_scores(cls):
        return [row[0] for row in session.query(cls.sentimental_score).all()]

    @classmethod
    def get_all_triggered_keywords(cls):
        return [row[0] for row in session.query(cls.triggered_keywords).all()]

    @classmethod
    def get_all_triggered_topics(cls):
        return [row[0] for row in session.query(cls.triggered_topics).all()]

    @classmethod
    def get_all_text_simplicity_deviations(cls):
        return [row[0] for row in session.query(cls.text_simplicity_deviation).all()]

    @classmethod
    def get_all_confidence_factors(cls):
        return [row[0] for row in session.query(cls.confidence_factor).all()]

    @classmethod
    def get_all_clickbait_scores(cls):
        return [row[0] for row in session.query(cls.clickbait).all()]

    @classmethod
    def get_all_subjectivity_scores(cls):
        return [row[0] for row in session.query(cls.subjective).all()]

    @classmethod
    def get_all_call_to_action_scores(cls):
        return [row[0] for row in session.query(cls.call_to_action).all()]

    @classmethod
    def get_all_repeated_takes(cls):
        return [row[0] for row in session.query(cls.repeated_take).all()]

    @classmethod
    def get_all_repeated_notes(cls):
        return [row[0] for row in session.query(cls.repeated_note).all()]

    @classmethod
    def get_all_messianism(cls):
        return [row[0] for row in session.query(cls.messianism).all()]

    @classmethod
    def get_all_opposition_to_opponents(cls):
        return [row[0] for row in session.query(cls.opposition_to_opponents).all()]

    @classmethod
    def get_all_generalization_of_opponents(cls):
        return [row[0] for row in session.query(cls.generalization_of_opponents).all()]

    # Raw result methods for historical average calculation
    @classmethod
    def get_all_sentimental_scores_raw(cls):
        return [row[0] for row in session.query(cls.sentimental_score_raw).all()]

    @classmethod
    def get_all_triggered_keywords_raw(cls):
        return [row[0] for row in session.query(cls.triggered_keywords_raw).all()]

    @classmethod
    def get_all_triggered_topics_raw(cls):
        return [row[0] for row in session.query(cls.triggered_topics_raw).all()]

    @classmethod
    def get_all_text_simplicity_deviations_raw(cls):
        return [row[0] for row in session.query(cls.text_simplicity_deviation_raw).all()]

    @classmethod
    def get_all_confidence_factors_raw(cls):
        return [row[0] for row in session.query(cls.confidence_factor_raw).all()]

    @classmethod
    def get_all_clickbait_scores_raw(cls):
        return [row[0] for row in session.query(cls.clickbait_raw).all()]

    @classmethod
    def get_all_subjectivity_scores_raw(cls):
        return [row[0] for row in session.query(cls.subjective_raw).all()]

    @classmethod
    def get_all_call_to_action_scores_raw(cls):
        return [row[0] for row in session.query(cls.call_to_action_raw).all()]

    @classmethod
    def get_all_repeated_takes_raw(cls):
        return [row[0] for row in session.query(cls.repeated_take_raw).all()]

    @classmethod
    def get_all_repeated_notes_raw(cls):
        return [row[0] for row in session.query(cls.repeated_note_raw).all()]

    @classmethod
    def get_all_messianism_raw(cls):
        return [row[0] for row in session.query(cls.messianism_raw).all()]

    @classmethod
    def get_all_opposition_to_opponents_raw(cls):
        return [row[0] for row in session.query(cls.opposition_to_opponents_raw).all()]

    @classmethod
    def get_all_generalization_of_opponents_raw(cls):
        return [row[0] for row in session.query(cls.generalization_of_opponents_raw).all()]

Base.metadata.create_all(engine)


class BaseDao:

    def __init__(self):
        self.session = session

    def create(self, *model):
        self.session.add_all(model)
        self.session.commit()

    def get_by_id(self, model_class, record_id):
        return self.session.query(model_class).get(record_id)


class NoteDao(BaseDao):

    def get_notes(self):
        return self.session.query(Note).all()

    def get_by_id(self, record_id):
        return super().get_by_id(Note, record_id)

    def get_by_hash(self, hash):
        return self.session.query(Note).filter_by(hash=hash).first()

    def get_by_source_id(self, source_id):
        return self.session.query(Note).filter_by(source_id=source_id).all()

    def get_upper_third_rating(self):
        notes = self.session.query(Note).all()
        if not notes:
            return 100

        total_scores = sorted([note.total_score for note in notes], reverse=True)
        upper_third_index = max(1, len(total_scores) // 3)  # At least one value in the upper third
        upper_third_scores = total_scores[upper_third_index:]

        return sum(upper_third_scores) / len(upper_third_scores)

    def update(self, model_to_update):
        model_from_db = self.get_by_id(model_to_update.__class__, model_to_update.id)
        model_from_db.name = model_to_update.name
        self.session.commit()

    def save(self, *models_to_save):
        for model_to_save in models_to_save:
            model_from_db = self.get_by_id(model_to_save.id)
            if (model_from_db == None):
                self.session.add_all(models_to_save)
            model_from_db = mapper.to(model_to_save.__class__).map(model_to_save)
        self.session.commit()

    def get_last_note(self):
        return (
            self.session.query(Note)
            .order_by(Note.created_at.desc())
            .first()
        )


class SourceDao(BaseDao):

    def get_all(self):
        return self.session.query(Source).all()

    def get_by_id(self, record_id) -> Source:
        return super().get_by_id(Source, record_id)

    def get_by_external_id(self, external_id) -> Source:
        sources = self.session.query(Source).filter_by(external_id=str(external_id)).all()
        if (len(sources) == 0):
            return None
        return sources[0]

    def update_rating(self, id, new_rating):
        initial_model = self.get_by_id(id)
        initial_model.rating = new_rating
        self.session.commit()

    def calculate_rating(self, source_id):
        notes = self.session.query(Note).filter_by(source_id=source_id).all()
        if notes:
            total_scores = [note.total_score for note in notes]
            return sum(total_scores) / len(total_scores)
        else:
            return None

    def save(self, *models_to_save):
        for model_to_save in models_to_save:
            model_from_db = self.get_by_id(model_to_save.id)
            if (model_from_db == None):
                self.session.add(model_to_save)
            model_from_db = mapper.to(model_to_save.__class__).map(model_to_save)
        self.session.commit()

class Migration:

    def __init__(self, note_dao: NoteDao, source_dao: SourceDao):
        self.note_dao = note_dao
        self.source_dao = source_dao

    def save_initial_sources(self, source_dao: SourceDao):
        initial_sources = [
            Source(id=1, name='1', external_id="1", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=2, name='2', external_id="2", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=3, name='3', external_id="3", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=4, name='4', external_id="4", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=5, name='5', external_id="5", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=6, name='6', external_id="6", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=7, name='7', external_id="7", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=8, name='8', external_id="8", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=9, name='9', external_id="9", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=10, name='10', external_id="10", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=11, name='11', external_id="11", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=12, name='12', external_id="12", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=13, name='13', external_id="13", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=14, name='14', external_id="14", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=15, name='15', external_id="15", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=16, name='16', external_id="16", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=17, name='17', external_id="17", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=18, name='18', external_id="18", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=19, name='19', external_id="19", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=20, name='20', external_id="20", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=21, name='21', external_id="21", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=22, name='22', external_id="22", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=23, name='23', external_id="23", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=24, name='24', external_id="24", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=25, name='25', external_id="25", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=26, name='26', external_id="26", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=27, name='27', external_id="27", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=28, name='28', external_id="28", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=29, name='29', external_id="29", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=30, name='30', external_id="30", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=31, name='31', external_id="31", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=32, name='32', external_id="32", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=33, name='33', external_id="33", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=34, name='34', external_id="34", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=35, name='35', external_id="35", platform=PLATFORM_TYPE.TELEGRAM.name, is_hidden=True),
            Source(id=36, name='CNN NEWS', external_id="36", platform=PLATFORM_TYPE.TWITCH.name, is_hidden=False),
            Source(id=37, name='FOX NEWS', external_id="37", platform=PLATFORM_TYPE.TWITCH.name, is_hidden=False),
            Source(id=38, name='NY NEWS', external_id="38", platform=PLATFORM_TYPE.TWITCH.name, is_hidden=False),
            Source(id=39, name='THE GUARDIAN NEWS', external_id="39", platform=PLATFORM_TYPE.TWITCH.name, is_hidden=False),
            Source(id=40, name='SUN NEWS', external_id="40", platform=PLATFORM_TYPE.TWITCH.name, is_hidden=False),
        ]
        source_dao.save(*initial_sources)

    def execute(self):
        self.save_initial_sources(self.source_dao)
