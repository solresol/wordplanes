import numpy as np


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
    # This method calculates the orthogonal transformation matrix
    # The matrix is such that when you multiply it by point1, point2, or point3, the first two components will map to zero

    # Calculate the normal vector of the plane defined by point1, point2, and point3
    normal_vector = np.cross(point2 - point1, point3 - point1)

    # Normalize the normal vector
    normal_vector = normal_vector / np.linalg.norm(normal_vector)

    # Calculate the orthogonal transformation matrix
    M = np.eye(len(point1)) - 2 * np.outer(normal_vector, normal_vector)

    return M
