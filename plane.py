import numpy as np


class Plane:
    def __init__(self, point1, point2, point3):
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        try:
            self.normal_vector = np.cross(point2 - point1, point3 - point1)
        except Exception as e:
            self.normal_vector = None
            print(f'Error calculating normal vector: {e}')
        if self.normal_vector is not None:
            try:
                self.distance_to_origin = np.abs(np.dot(self.normal_vector, point1)) / np.linalg.norm(self.normal_vector)
            except Exception as e:
                self.distance_to_origin = None
                print(f'Error calculating distance to origin: {e}')

    def distance_to_plane(self, point):
        distance = np.abs(np.dot(self.normal_vector, point - self.point1)) / np.linalg.norm(self.normal_vector)
        closest_point = point - distance * self.normal_vector / np.linalg.norm(self.normal_vector)
        return distance, closest_point
