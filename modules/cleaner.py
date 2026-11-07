from pathlib import Path
from datetime import datetime
import sys
import time
import shutil

# Принудительно добавляем корень проекта в sys.path, чтобы Python видел модуль database
sys.path.append(str(Path(__file__).resolve().parent.parent))
from database.models import SessionLocal, SortedFileLog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class AdvencedFileSorterHandler(FileSystemEventHandler):

  def __init__(self, source_dir):
    self.source_dir = Path(source_dir)

    # Папки для отсортированных файлов
    self.code_dir = self.source_dir / "Code"
    self.docs_dir = self.source_dir / "Documents"
    self.photo_dir = self.source_dir / "Photos"
    self.video_dir = self.source_dir / "Video"

    # Подпапки для документов по контексту
    self.presentations_dir = self.docs_dir / "Presentations"
    self.alevel_dir = self.docs_dir / "A-Level"
    self.lyceum_dir = self.docs_dir / "Lyceum"
    self.other_docs_dir = self.docs_dir / "Other"

    # Подпапки для кода по языкам
    self.python_code = self.code_dir / "Python"
    self.csharp_code = self.code_dir / "CSharp"
    self.web_code = self.code_dir / "Web"
    self.other_code = self.code_dir / "Other_Code"

    # Создание всех папок автоматически
    for folder in [
      self.code_dir,
      self.docs_dir,
      self.photo_dir,
      self.video_dir,
      self.presentations_dir,
      self.alevel_dir,
      self.lyceum_dir,
      self.other_docs_dir,
      self.python_code,
      self.csharp_code,
      self.web_code,
      self.other_code,
    ]:
      folder.mkdir(parents=True, exist_ok=True)

  def process_file(self, file_path: Path):
    # Игнорируем сами папки сортировки, чтобы избежать рекурсии
    if any(
        parent.resolve() == file_path.resolve().parent
        for parent in [
            self.code_dir,
            self.docs_dir,
            self.photo_dir,
            self.video_dir,
        ]
    ):
      # Проверяем глубже по иерархии
      pass

    if file_path.relosve().parent in [
      self.code_dir,
        self.docs_dir,
        self.photo_dir,
        self.video_dir,
        self.presentations_dir,
        self.alevel_dir,
        self.lyceum_dir,
        self.other_docs_dir,
        self.python_code,
        self.csharp_code,
        self.web_code,
        self.other_code,
    ]:
      return

    extension = file_path.suffixes.lower()
    filename_lower = file_path.name.lower()
    target_dir = None

    # 1. Логика сортировки КОДА по подпапкам
    if extension in [".py"]:
      target_dir = self.python_code
    elif extension in [".cs"]:
      target_dir = self.csharp_code
    elif extension in [".html", ".css", ".js"]:
      target_dir = self.web_code
    elif extension in [".cpp", ".cpp", ".h"]:
      target_dir = self.other_code

    # 2. Логика сортировки ДОКУМЕНТОВ по контексту (ключевым словам в названии)
    elif extension in [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".ppt"]:
      if "presentation" in filename_lower or extension in [".pptx", ".ppt"]:
        target_dir = self.presentations_dir
      elif "a-level" in filename_lower or "sat" in filename_lower or "math" in filename_lower:
        target_dir = self.alevel_dir
      elif "alwiut" in filename_lower or "lyceum" in filename_lower or "лицей" in filename_lower:
        target_dir = self.lyceum_dir
      else:
        target_dir = self.other_docs_dir

    # 3. Фото и видео
    elif extension in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".svg"]:
      target_dir = self.photo_dir
    elif extension in [".mp4", ".mkv", ".mov", ".avi", ".webm", ".wmv"]:
      target_dir = self.video_dir

    # Защита от дубликатов: добавляем таймстамп
    if target_dir:
      new_path = target_dir/file_path.name

      if new_path.exists():
        new_path = (
          target_dir / f"{file_path.stem}_{int(time.time())}{extension}"
        )

      try:
        shutil.move(str(file_path), str(new_path))
        print(f"[Успешно] '{file_path.name}' -> {target_dir.relative_to(self.source_dir)}")

        #Log в БД
        session = SessionLocal()
        db_log = SortedFileLog(
          file_name = file_path.name,
          original_path = str(file_path),
          new_path = str(new_path),
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
  event_handler = AdvencedFileSorterHandler(path_to_watch)
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