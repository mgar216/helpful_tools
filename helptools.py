import os, pandas as pd
from pathlib import Path

def getAgedDirectoryFiles(base_directory: str, age: int=0):
  # Defaults to most recent last modified, while age=1 is the one last modified prior to that.
  all_files = {}
  paths = str(sorted(Path(base_directory).iterdir(), key=os.path.getmtime)[::-1][age])
  all_paths = [str(i.name) for i in os.scandir(paths) if i.is_dir()]
  if all_paths:
    for i in all_paths:
      all_files[i] = []
      for f in os.scandir(paths + '\\' + i):
        if not f.is_dir():
          all_files[i].append(f.name)
  else:
    all_files[paths.split('\\')[-1]] = []
    for f in os.listdir(str(paths)):
      all_files[paths.split('\\')[-1]].append(f)
  all_full_dirs = []
  for k in all_files.keys():
    for v in all_files[k]:
      all_full_dirs.append('\\'.join([base_directory, k, v]).replace('\\\\', '\\'))
  return [all_files, all_full_dirs]
