import pandas as pd
import fuzzy_pandas as fpd

df1 = pd.DataFrame({
  'name': [
    'thi', 
    'that', 
    'Big',
    'fire'
    ], 
  'pop': [
    'Tart', 
    'corn', 
    'social',
    'clue'
    ], 
    'cow': [
      'Milk', 
      'cheese', 
      'cottage',
      'soda'
      ]
    })

df2 = pd.DataFrame({
  'name': [
    'this', 
    'that', 
    'Big',
    'fire'
    ], 
  'pop': [
    'Tart', 
    'corn', 
    'social',
    'Clue'
    ], 
    'cow': [
      'Milk', 
      'cheese', 
      'cottage',
      'da'
      ]
    })


# This is how we MATCH, and keep the matching indices! You must reset_index(), and set_index('index')
matches = fpd.fuzzy_merge(df2.reset_index(), df1,
                          on=df1.columns.to_list(),
                          ignore_case=True,
                          method='levenshtein',
                          threshold=1,
                          keep='all',
                          join='inner' # use full-outer to show failed matches
                          ).set_index('index')
idx = matches.index.to_list()
matches = df2.loc[idx]
print('Matched:\n', matches)

#########

# This is how we DIFFERENTIATE, and keep the Differing indices! You must reset_index(), and set_index('index')
matches = fpd.fuzzy_merge(df2, df1.reset_index(),
                          on=df1.columns.to_list(),
                          ignore_case=True,
                          method='levenshtein',
                          threshold=1,
                          keep='all',
                          join='right-outer' # use full-outer to show failed matches
                          )
matches.columns = ['_left_' + i if n < len(df1.columns) else i for n, i in enumerate(matches)]
col1 = matches.filter(regex='_left_').columns.to_list()
match_idx = matches.loc[:, col1]
idx = match_idx[match_idx.applymap(lambda x: len(x) == 0)].dropna().index.to_list()
non_match_idx = matches.iloc[idx].drop(col1, axis=1)['index'].to_list()
not_matched = df2.iloc[non_match_idx]
print('Non-Matched:\n', not_matched)