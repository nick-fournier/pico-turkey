# Caclulate the standard deviation of a column of data
# x is a list of floats
def stdev(x):
  ave = sum(x) / len(x)  
  stdev = (sum([(i - ave) ** 2 for i in x]) / len(x)) ** 0.5  

  return stdev


# Compute the average of a column of data
# df is a list of lists of floats, i is the index of the data within
# df to average.
def stats(df, i):
  ave = sum([l[i] for l in df]) / len(df)

  return ave

# df is a list of list of float values
# m is the slope of the line that best fits df, b is the y-intercept
def best_fit(x, y):
    
    ave_x = sum(x) / len(x)
    ave_y = sum(y) / len(y)
    
    m_numer = sum([l[0] * (l[1] - ave_y) for l in zip(x, y)])
    m_denom = sum([l[0] * (l[0] - ave_x) for l in zip(x, y)])
    
    m = m_numer / m_denom
    b = ave_y - m * ave_x

    return (b, m)