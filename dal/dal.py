from automapper import mapper
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, MetaData,
                        Numeric, String, Text, create_engine, func, text)
from sqlalchemy.orm import DeclarativeBase, Session

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

    def __str__(self) -> str:
        return f'id: {self.id},\n' \
            + f'platform: {self.platform},\n' \
            + f'name: {self.name},\n' \
            + f'rating: {self.rating},\n'


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    sentimental_score = Column(Numeric, default=0) # x2
    triggered_keywords = Column(Numeric, default=0) # x
    triggered_topics = Column(Numeric, default=0) # x7
    text_simplicity_deviation = Column(Numeric, default=0) # x5
    confidence_factor = Column(Numeric, default=100) # x6
    clickbait = Column(Numeric, default=0) # x10
    subjective = Column(Numeric, default=0) # x1
    call_to_action = Column(Numeric, default=0) # x8
    repeated_take = Column(Numeric, default=0) # x3
    repeated_note = Column(Numeric, default=0) # x4
    total_score = Column(Numeric, default=50)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __str__(self) -> str:
        return f'sentimental_score: {int(self.sentimental_score * 100)}%,\n' \
            + f'triggered_keywords: {self.triggered_keywords}%,\n' \
            + f'triggered_topics: {int(self.triggered_topics)}%,\n' \
            + f'text_simplicity_deviation: {int(self.text_simplicity_deviation)}%,\n' \
            + f'confidence_factor: {int(self.confidence_factor)}%,\n' \
            + f'clickbait: {int(self.clickbait)}%,\n' \
            + f'subjective: {int(self.subjective)}%,\n' \
            + f'call_to_action: {int(self.call_to_action)}%,\n' \
            + f'repeated_take: {int(self.repeated_take)}%,\n' \
            + f'repeated_note: {int(self.repeated_note)}%,\n' \
            + f'total_score: {int(self.total_score)}%,\n'

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

    def get_by_id(self, record_id):
        return super().get_by_id(Note, record_id)

    def get_by_source_id(self, source_id):
        return self.session.query(Note).filter_by(source_id=source_id).all()

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
                self.session.add_all(models_to_save)
            model_from_db = mapper.to(model_to_save.__class__).map(model_to_save)
        self.session.commit()
