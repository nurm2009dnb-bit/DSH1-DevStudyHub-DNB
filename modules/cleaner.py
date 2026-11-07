from pathlib import Path
import sys

# Принудительно добавляем корень проекта в sys.path, чтобы Python видел модуль database
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import shutil
import time
from database.models import SessionLocal, SortedFileLog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class FileSorterHandler(FileSystemEventHandler):

  def __init__(self, source_dir):
    self.source_dir = Path(source_dir)

    # Папки для отсортированных файлов
    self.code_dir = self.source_dir / "Code"
    self.docs_dir = self.source_dir / "Documents"
    self.photo_dir = self.source_dir / "Photos"
    self.video_dir = self.source_dir / "Video"

    self.code_dir.mkdir(exist_ok=True)
    self.docs_dir.mkdir(exist_ok=True)
    self.photo_dir.mkdir(exist_ok=True)
    self.video_dir.mkdir(exist_ok=True)

  def process_file(self, file_path: Path):
    if file_path.resolve() in [
      self.code_dir.resolve(),
      self.docs_dir.resolve(),
      self.photo_dir.resolve(),
      self.video_dir.resolve(),
    ]:
      return

    extension = file_path.suffix.lower()
    target_dir = None
    
    # Правила сортировки
    if extension in [".py", ".cs", ".js", ".cpp", ".html", ".css"]:
      target_dir = self.code_dir
    elif extension in [".pdf", ".docx", ".txt", ".xlsx"]:
      target_dir = self.docs_dir
    elif extension in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".svg"]:
      target_dir = self.photo_dir
    elif extension in [".mp4", ".mkv", ".mov", ".avi", ".webm", ".wmv"]:
          target_dir = self.video_dir

    if target_dir:
      new_path = target_dir / file_path.name

      # Если файл с таким именем уже существует, добавляем метку времени
      if new_path.exists():
        new_path = (
            target_dir / f"{file_path.stem}_{int(time.time())}{extension}"
        )

      try:
        shutil.move(str(file_path), str(new_path))
        print(
            f"[Успешно] Файл '{file_path.name}' перемещен в {target_dir.name}"
        )

        # Запись лога в базу данных SQLite
        session = SessionLocal()
        db_log = SortedFileLog(
            file_name=file_path.name,
            original_path=str(file_path),
            new_path=str(new_path),
        )
        session.add(db_log)
        session.commit()
        session.close()

      except Exception as e:
        print(f"[Ошибка] Не удалось переместить файл: {e}")
    
  def sort_existing_files(self):
    print("Сканирование папки на наличие уже существующих файлов...")
    for item in self.source_dir.iterdir():
      if item.is_file():
        self.process_file(item) 

  def on_created(self, event):
    if event.is_directory:
      return

    file_path = Path(event.src_path)

    # Небольшая пауза, чтобы файл успел полностью сохраниться/скачаться
    time.sleep(1)

    if not file_path.exists():
      return

    self.process_file(file_path)


def start_cleaner(path_to_watch):
  # Используем наш класс FileSorterHandler
  event_handler = FileSorterHandler(path_to_watch)
  event_handler.sort_existing_files() 
  observer = Observer()
  observer.schedule(event_handler, path=path_to_watch, recursive=False)

  observer.start()
  print(f"Запущен мониторинг папки: {path_to_watch}")
  print("Нажми Ctrl+C для остановки.")

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()


if __name__ == "__main__":
  test_folder = Path("./TestDownloads")
  test_folder.mkdir(exist_ok=True)
  start_cleaner(str(test_folder.absolute()))