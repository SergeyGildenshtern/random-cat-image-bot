from sqlalchemy import Column, Integer

from models.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    phone = Column(Integer)
    chat_id = Column(Integer)

    def __repr__(self):
        return f'{self.id}, {self.phone}, {self.chat_id}'
