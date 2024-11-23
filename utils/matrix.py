# Module contains matrix operations

def multiply(A, B):
    """
    Multiply two matrices A and B
    """

    # Convert to 2D array for handling single values
    A = [x if isinstance(x, list) else [x] for x in A]
    B = [x if isinstance(x, list) else [x] for x in B]
    
    if len(A[0]) != len(B):
        raise ValueError("Matrix dimensions do not match")

    result = [[0 for i in range(len(B[0]))] for j in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                result[i][j] += A[i][k] * B[k][j]

    # If any sublist is of length 1, convert back to flat list
    result = [x[0] if len(x) == 1 else x for x in result]

    return result

def transpose(A):
    """
    Transpose a 2D array.
    """
    rows = len(A)
    cols = len(A[0])
    
    return [[A[i][j] for i in range(rows)] for j in range(cols)]


def add(A, B):
    """
    Add two matrices A and B
    """
    
    # Convert to 2D array for handling single values
    A = [x if isinstance(x, list) else [x] for x in A]
    B = [x if isinstance(x, list) else [x] for x in B]
    
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Matrix dimensions do not match")
    result = [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
    
    # If any sublist is of length 1, convert back to flat list
    result = [x[0] if len(x) == 1 else x for x in result]
    
    return result

def subtract(A, B):
    """
    Subtract matrix B from matrix A
    """
    
    # Convert to 2D array for handling single values
    A = [x if isinstance(x, list) else [x] for x in A]
    B = [x if isinstance(x, list) else [x] for x in B]    
    
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Matrix dimensions do not match")
    result = [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
    
    # If any sublist is of length 1, convert back to flat list
    result = [x[0] if len(x) == 1 else x for x in result]
    
    return result

def scalar_multiply(A, c):
    """
    Multiply a matrix by a scalar
    """
    return [[A[i][j] * c for j in range(len(A[0]))] for i in range(len(A))]


def invert(matrix):
    """
    Inverts a 3x3 matrix using the determinant and cofactor method.
    """

    def determinant(matrix):
        """
        Calculates the determinant of a 3x3 matrix.
        """
        a, b, c = matrix[0]
        d, e, f = matrix[1]
        g, h, i = matrix[2]
        return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)

    def cofactor(matrix, row, col):
        """
        Calculates the cofactor of a 3x3 matrix for a given element.
        """
        minor = [row[:col] + row[col + 1:] for row in (matrix[:row] + matrix[row + 1:])]
        return (-1) ** (row + col) * determinant(minor)

    def adjoint(matrix):
        """
        Calculates the adjoint of a 3x3 matrix.
        """
        return [[cofactor(matrix, i, j) for j in range(3)] for i in range(3)]

    det = determinant(matrix)
    if det == 0:
        return None  # Matrix is not invertible

    adj = adjoint(matrix)
    return [[adj[i][j] / det for j in range(3)] for i in range(3)]
    