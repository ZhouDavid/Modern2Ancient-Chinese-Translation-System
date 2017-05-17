import cntk as C
import numpy as np
import pandas as pd
x = C.input_variable(2)
y = C.input_variable(2)
x0 = np.asarray([[2., 1.]], dtype=np.float32)
y0 = np.asarray([[4., 6.]], dtype=np.float32)
res = C.squared_error(x, y).eval({x:x0, y:y0})
print type(res)