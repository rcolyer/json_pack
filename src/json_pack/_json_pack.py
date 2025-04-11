import base64 as base64
import io as io
import numpy as np
import pandas as pd
import json as json


def DataPack(x):
  try:
    if isinstance(x, np.ndarray):
      if x.dtype == 'O':
        raise TypeError('Unsupported')
      '''Converts a numpy array to a serializable string.'''
      b64 = base64.encodebytes(x.tobytes()).strip().decode()
      shape_str = ','.join(str(s) for s in x.shape)
      return f'@array;{x.dtype.str};{shape_str};{b64}'
    elif isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
      '''Converts a pandas DataFrame or Series to a serializable string.'''
      s = x.to_csv(index=None)
      return f'@table;{s}'
  except Exception:
    pass
  raise TypeError('Unsupported')

def DataUnpack(s):
  try:
    if isinstance(s, str):
      parts = s.split(';')
      if len(parts) == 4 and parts[0] == '@array':
        '''Unpacks a numpy array from a serializable string.'''
        dtype, shape_str, b64 = parts[1:]
        buf = base64.decodebytes(b64.encode())
        shape = [int(e) for e in shape_str.split(',') if e]
        return np.frombuffer(buf, dtype=dtype).reshape(shape)
      elif len(parts) >= 2 and parts[0] == '@table':
        '''Unpacks a pandas DataFrame or Series from a serializable string.'''
        s = ';'.join(parts[1:])
        df = pd.read_csv(io.StringIO(s))
        if len(df.columns) == 1:
          # Convert to series
          df = df[df.columns[0]]
        return df
  except Exception:
    pass
  return s

def TraverseUnpack(d):
  if isinstance(d, dict):
    return {k:TraverseUnpack(v) for k,v in d.items()}
  elif isinstance(d, list):
    return [TraverseUnpack(e) for e in d]
  elif isinstance(d, str):
    return DataUnpack(d)
  else:
    return d

def JSLoad(filename):
  '''Load a json file with potentially string-packed numpy or pandas
  elements.'''
  with open(filename, 'r') as fr:
    data = json.load(fr)
  return TraverseUnpack(data)

def JSLoadStr(s):
  '''Parse a json string with potentially string-packed numpy or pandas
  elements.'''
  data = json.loads(s)
  return TraverseUnpack(data)

def JSSave(filename, data):
  '''Save a json file, packing any numpy or pandas elements as @array or
  @table strings.'''
  with open(filename, 'w') as fw:
    json.dump(data, fw, indent=2, default=DataPack)

def JSSaveStr(data):
  '''Create a json string, packing any numpy or pandas elements as @array or
  @table strings.'''
  return json.dumps(data, indent=2, default=DataPack)

def _JSLinesParse(i, L):
  try:
    return TraverseUnpack(json.loads(L))
  except Exception as e:
    raise ValueError(f'Error parsing JSON-lines data line {i+1}:\n{L}') from e

def JSLinesLoadStr(s):
  '''Parse a json-lines string with potentially string-packed numpy or pandas
  elements.'''
  lines = [L for L in s.split('\n') if L]
  return [_JSLinesParse(i, L) for i,L in enumerate(lines)]

def JSLinesLoad(filename):
  '''Load a json-lines file with potentially string-packed numpy or pandas
  elements.'''
  with open(filename, 'r') as fr:
    lines = fr.readlines()
  return [_JSLinesParse(i, L) for i,L in enumerate(lines)]

def JSLinesSaveStr(list_data):
  '''Create a json-lines string, packing any numpy or pandas elements as
  @array or @table strings.'''
  if not isinstance(list_data, list):
    raise ValueError(
        f'JSLinesSaveStr expects a list, but received {type(list_data)}')
  return ''.join([f'{json.dumps(e, separators=(",", ":"), default=DataPack)}\n'
      for e in list_data])

def JSLinesSave(filename, list_data):
  '''Save a json-lines file, packing any numpy or pandas elements as @array or
  @table strings.'''
  with open(filename, 'w') as fw:
    fw.write(JSLinesSaveStr(list_data))

