from datetime import datetime
from sqlalchemy import Column, Date, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Актуальный импорт для SQLAlchemy 2.0
Base = declarative_base()


# 1. Таблица для базы знаний и сниппетов
class Snippet(Base):
  __tablename__ = "snippets"

  id = Column(Integer, primary_key=True, autoincrement=True)
  title = Column(String, nullable=False)
  content = Column(Text, nullable=False)
  language = Column(String, nullable=False)
  tags = Column(String, nullable=True)
  created_at = Column(DateTime, default=datetime.utcnow)


# 2. Таблица для трекера времени
class TimeLog(Base):
  __tablename__ = "time_logs"

  id = Column(Integer, primary_key=True, autoincrement=True)
  project_name = Column(String, nullable=False)
  duration_minutes = Column(Integer, nullable=False)
  category = Column(String, nullable=False)
  date = Column(Date, nullable=False)


# 3. Таблица для логов автоочистки файлов
class SortedFileLog(Base):
  __tablename__ = "sorted_files_log"

  id = Column(Integer, primary_key=True, autoincrement=True)
  file_name = Column(String, nullable=False)
  original_path = Column(String, nullable=False)
  new_path = Column(String, nullable=False)
  timestamp = Column(DateTime, default=datetime.utcnow)


# Подключение к SQLite
DATABASE_URL = "sqlite:///dev_study_hub.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
  Base.metadata.create_all(bind=engine)
  print("База данных и таблицы успешно созданы!")


if __name__ == "__main__":
  init_db()