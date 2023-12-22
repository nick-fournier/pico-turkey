# Simple linear regression
# df is a list of list of float values
# m is the slope of the line that best fits df, b is the y-intercept
def best_fit(x, y):
  
  ave_x = sum(x) / len(x)
  ave_y = sum(y) / len(y)
  
  m_numer = sum([x_i * (y_i - ave_y) for x_i, y_i in zip(x, y)])
  m_denom = sum([x_i * (x_i - ave_x) for x_i, y_i in zip(x, y)])
  
  m = m_numer / m_denom
  b = ave_y - m * ave_x

  return (b, m)
  
# Simplified fit assuming equal intervals
def calc_slope(y):
    ave_x = (len(y) - 1) / 2
    ave_y = sum(y) / len(y)
      
    m_numer = 0
    m_denom = 0
    
    for x_i, y_i in enumerate(y):
        m_numer += x_i * (y_i - ave_y)
        m_denom += x_i * (x_i - ave_x)
    
    return m_numer / m_denom  
    