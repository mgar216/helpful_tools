import os, pandas as pd
from pathlib import Path
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWRITE, S_IWGRP, S_IWOTH
import fuzzy_pandas as fpd

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
      all_full_dirs.append('\\'.join([paths, k, v]).replace('\\\\', '\\'))
  return [all_files, all_full_dirs]


def fileToWriteMode(file_location: str):
  try:
    os.chmod(file_location, S_IWRITE|S_IWGRP|S_IWOTH)
    return 1
  except Exception as e:
    print(str(e))
    return 0


def fileToReadOnlyMode(file_location: str):
  try:
    os.chmod(file_location, S_IREAD|S_IRGRP|S_IROTH)
    return 1
  except Exception as e:
    print(str(e))
    return 0

  
def writeToReadOnlyXLSX(df: pd.DataFrame, file_location: str):
  fileToWriteMode(file_location)
  df.to_excel(file_location, index=False)
  fileToReadOnlyMode(file_location)
  return 1


def matchToDataFrame(
                        left_df: pd.DataFrame,
                        right_df: pd.DataFrame,
                        on: list,
                        match_to_left: bool=True,
                        ignore_case: bool=True,
                        method: str='levenshtein',
                        threshold: float=1.0,
                        ) -> pd.DataFrame:
  if not match_to_left:
    left_df, right_df = right_df, left_df
  matches = fpd.fuzzy_merge(right_df.reset_index(), left_df,
                          on=on,
                          ignore_case=ignore_case,
                          method=method,
                          threshold=threshold,
                          keep='all',
                          join='inner'
                          ).set_index('index')
  idx = matches.index.to_list()
  matched = right_df.loc[idx]
  return matched

def differingDataFrame(
                            left_df: pd.DataFrame,
                            right_df: pd.DataFrame,
                            on: list,
                            match_to_left: bool=True,
                            ignore_case: bool=True,
                            method: str='levenshtein',
                            threshold: float=1.0,
                            ) -> pd.DataFrame:
  if not match_to_left:
    left_df, right_df = right_df, left_df
  matches = fpd.fuzzy_merge(left_df, right_df.reset_index(),
                          on=on,
                          ignore_case=ignore_case,
                          method=method,
                          threshold=threshold,
                          keep='all',
                          join='right-outer'
                          )
  matches.columns = ['_left_' + i if n < len(left_df.columns) else i for n, i in enumerate(matches)]
  col1 = matches.filter(regex='_left_').columns.to_list()
  match_idx = matches.loc[:, col1]
  idx = match_idx[match_idx.applymap(lambda x: len(x) == 0)].dropna().index.to_list()
  non_match_idx = matches.iloc[idx].drop(col1, axis=1)['index'].to_list()
  non_matched = right_df.iloc[non_match_idx]
  return non_matched


def compareDataFrame(
                    left_df: pd.DataFrame,
                    right_df: pd.DataFrame,
                    on: list,
                    match_to_left: bool=True,
                    ignore_case: bool=True,
                    method: str='levenshtein',
                    threshold: float=1.0,
                    matching: bool=True
                    ) -> pd.DataFrame:
  if matching:
    return matchToDataFrame(left_df, right_df, on, match_to_left, ignore_case, method, threshold)
  else:
    return differingDataFrame(left_df, right_df, on, match_to_left, ignore_case, method, threshold)

