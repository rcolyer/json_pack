# json_pack

This repository provides a solution to the common data science need for long term storage of structured data including dictionaries, lists, pandas tables, and numpy numerical data.  This format should remain robustly safe across environment version upgrades, and is trivial to write loaders for in other languages.

These properties make it suitable for both quick intermediate data storage during processing runs, and long term archival of results.  We can have high confidence in being able to access data in this format long into the future.  If you are new to data science, trust that this will be important to you sooner than you might realize.

# API

* `data = jp.JSLoad('filename.json')` -- Loads from a file.
* `data = jp.JSLoadStr(data_in_string_form)` -- Parses a string.
* `jp.JSSave('filename.json', data)` -- Saves to a file.
* `data_as_string = jp.JSSaveStr(data)` -- Converts data to a string.

# Format

The data should be any dictionary of results, and may contain pandas tables and numpy numerical data.  No attempt is made to support every possible data type that could go into pandas or numpy, but instead this focuses on the simple common data types.  Pandas data is embedded into the output json as a string containing the equivalent of a CSV file, and so it will save and restore data as reliably as if the pandas table had been converted to a CSV file and saved as a separate file.  Numpy array contents are embedded as a json string as base64 binary data, and consequently occupy about 33% more space than if they had been saved in a separate binary file.  But in exchange for that modest space overhead, a simple archival format is obtained which is easy to parse, and the collections of data are all kept associated with each other in a unified file, which can improve tracking of associated information in data science.

When the saved data is reloaded, the data saved as embedded pandas or numpy information is unpacked as in-place pandas or numpy objects again.  This is facilitated by the sentinel formats of the strings of `"@array;datatype;shape_tuple;base64data"` for numpy arrays, and `"@table;csv_data"` for pandas tables.

# Example

`In:`
```
import numpy as np
import pandas as pd
import json_pack as jp

df = pd.DataFrame({'subjects': ['R1234', 'R6784', 'R8543'], 'recall_rate':[43.
2, 65.1, 19.5], 'sessions':[4,5,2]})
print(df)
```
`Out:`
```
  subjects  recall_rate  sessions
0    R1234         43.2         4
1    R6784         65.1         5
2    R8543         19.5         2
```
`In:`
```
a = np.random.random((3,2))
print(a)
```
`Out:`
```
[[0.06129445 0.22756133]
 [0.06816441 0.95939617]
 [0.58314975 0.73769206]]
```
`In:`
```
data = {'subjects': ['R1234', 'R6784', 'R8543'], 'stats': df, 'results': a}
print('\n'.join(f'-- {k}: --\n{v}' for k,v in data.items()))
```
`Out:`
```
-- subjects: --
['R1234', 'R6784', 'R8543']
-- stats: --
  subjects  recall_rate  sessions
0    R1234         43.2         4
1    R6784         65.1         5
2    R8543         19.5         2
-- results: --
[[0.06129445 0.22756133]
 [0.06816441 0.95939617]
 [0.58314975 0.73769206]]
```
`In:`
```
jp.JSSave('results.json', data)
print(jp.JSSaveStr(data))

data2 = jp.JSLoad('results.json')
print('----------------------')
print('\n'.join(f'-- {k}: --\n{v}' for k,v in data2.items()))
```
`Out:`
```
{
  "subjects": [
    "R1234",
    "R6784",
    "R8543"
  ],
  "stats": "@table;subjects,recall_rate,sessions\nR1234,43.2,4\nR6784,65.1,5\nR8543,19.5,2\n",
  "results": "@array;<f8;3,2;wHVeTPxhrz9obf/QuiDNP+iTCwk5c7E/aHifl1+z7j/LsHypKaniP69pNmMsm+c/"
}
----------------------
-- subjects: --
['R1234', 'R6784', 'R8543']
-- stats: --
  subjects  recall_rate  sessions
0    R1234         43.2         4
1    R6784         65.1         5
2    R8543         19.5         2
-- results: --
[[0.06129445 0.22756133]
 [0.06816441 0.95939617]
 [0.58314975 0.73769206]]
```

# License

json_pack is licensed under the MIT license for permissive use.

