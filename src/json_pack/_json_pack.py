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
  with open(filename, 'r') as fr:
    data = json.load(fr)
  return TraverseUnpack(data)

def JSLoadStr(s):
  data = json.loads(s)
  return TraverseUnpack(data)

def JSSave(filename, data):
  with open(filename, 'w') as fw:
    json.dump(data, fw, indent=2, default=DataPack)

def JSSaveStr(data):
  return json.dumps(data, indent=2, default=DataPack)

