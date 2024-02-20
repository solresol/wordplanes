import numpy as np
from numpy.linalg import qr


class Plane:
    def __init__(self, point1, point2, point3):
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        # Calculate the orthogonal transformation matrix, self.M
        # This matrix is such that when you multiply self.M by point1, point2, or point3, the first two components will map to zero
        self.M = self.calculate_orthogonal_transformation_matrix(point1, point2, point3)

    def distance_to_plane(self, point):
        distance = np.abs(np.dot(self.normal_vector, point - self.point1)) / np.linalg.norm(self.normal_vector)
        closest_point = point - distance * self.normal_vector / np.linalg.norm(self.normal_vector)
        return distance, closest_point
        distance = np.linalg.norm(transformed_point)
        
        # The closest point on the plane to the input point is the original point minus the distance times the transformed point
        closest_point = point - distance * transformed_point
        return distance, closest_point
def calculate_orthogonal_transformation_matrix(self, point1, point2, point3):
    # This method calculates the orthogonal transformation matrix using QR decomposition
    # The matrix is such that when you multiply it by point1, point2, or point3, the first two components will map to zero

    # Stack point1, point2, and point3 as columns in a matrix A
    A = np.column_stack((point1, point2, point3))

    # Perform QR decomposition on matrix A to obtain matrices Q and R
    Q, R = qr(A)

    # Take the first two columns of Q and use them as the basis vectors for the plane
    basis_vectors = Q[:, :2]

    # Construct the projection matrix M onto the plane using these two basis vectors
    M = basis_vectors @ basis_vectors.T

    return M
