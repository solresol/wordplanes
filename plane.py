#!/usr/bin/env python3

import numpy as np

class Plane:
    def __init__(self, point1, point2, point3):
        """
        Initialize a plane in high-dimensional space using three points.
        
        Args:
            point1 (np.ndarray): First point on the plane
            point2 (np.ndarray): Second point on the plane
            point3 (np.ndarray): Third point on the plane
        """
        self.origin = point1
        
        # Compute direction vectors from the points
        direction1 = point2 - point1
        direction2 = point3 - point1
        
        # Normalize and orthogonalize the direction vectors using Gram-Schmidt
        self.direction1 = direction1 / np.linalg.norm(direction1)
        
        # Make direction2 orthogonal to direction1
        proj = np.dot(direction2, self.direction1) * self.direction1
        orthogonal_dir2 = direction2 - proj
        
        # Check if points are collinear
        if np.linalg.norm(orthogonal_dir2) < 1e-10:
            raise ValueError("The three points appear to be collinear. They must span a 2D plane.")
            
        self.direction2 = orthogonal_dir2 / np.linalg.norm(orthogonal_dir2)
        
        # Calculate the normal space basis
        self.normal_basis = self._calculate_normal_basis()
        
    def _calculate_normal_basis(self):
        """
        Calculate an orthonormal basis for the normal space of the plane.
        """
        dim = len(self.origin)
        
        # Create matrix for null space calculation
        plane_vectors = np.vstack([self.direction1, self.direction2])
        
from typing import List, Tuple
        # Get the null space (normal space) using SVD
        _, _, Vh = np.linalg.svd(plane_vectors, full_matrices=True)
        normal_basis = Vh[2:]  # All vectors except the first two form the normal space basis
        
        return normal_basis
        
    def distance_to_plane(self, point):
        """
        Calculate the distance from a point to the plane and its projection onto the plane.
        
        Args:
            point (np.ndarray): The point to calculate distance from
        
        Returns:
            tuple: (distance, projected_point)
        """
        # Vector from origin to point
        vector = point - self.origin
        
        # Project the vector onto the normal space
        #normal_projection = np.sum(np.dot(vector, self.normal_basis.T) * self.normal_basis, axis=0)
        
        # Project the vector onto each normal vector and sum the components
        normal_projection = np.zeros_like(vector)
        for normal_vec in self.normal_basis:
            proj = np.dot(vector, normal_vec) * normal_vec
            normal_projection += proj
        
        # Distance is the magnitude of the normal projection
        distance = np.linalg.norm(normal_projection)
        
        # Projected point is the original point minus the normal projection
        projected_point = point - normal_projection
        
        return distance, projected_point

    def project_point(self, point):
        """
        Project a point onto the plane and return its coordinates in the plane's basis.
        
        Args:
            point (np.ndarray): The point to project
            
        Returns:
            tuple: (plane_coordinates, projected_point)
        """
        # Get the projected point
        _, projected_point = self.distance_to_plane(point)
        
        # Calculate coordinates in the plane's basis
        vector = projected_point - self.origin
        coord1 = np.dot(vector, self.direction1)
        coord2 = np.dot(vector, self.direction2)
        
        return np.array([coord1, coord2]), projected_point

def parse_point(point_str: str) -> np.ndarray:
    """
    Parse a comma-separated string of numbers into a numpy array.
    
    Args:
        point_str (str): Comma-separated string of numbers
        
    Returns:
        np.ndarray: Array of parsed numbers
    """
    try:
        return np.array([float(x) for x in point_str.split(',')])
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid point format: {point_str}. Must be comma-separated numbers.") from e


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Calculate distance from a point to a plane in high-dimensional space.')
    parser.add_argument('--point1', type=parse_point, required=True,
                      help='First point on plane (comma-separated floats)')
    parser.add_argument('--point2', type=parse_point, required=True,
                      help='Second point on plane (comma-separated floats)')
    parser.add_argument('--point3', type=parse_point, required=True,
                      help='Third point on plane (comma-separated floats)')
    parser.add_argument('--point', type=parse_point, required=True,
                      help='Point to calculate distance from (comma-separated floats)')
    
    args = parser.parse_args()
    
    # Verify all points have the same dimension
    dim = len(args.point1)
    if not all(len(p) == dim for p in [args.point2, args.point3, args.point]):
        parser.error("All points must have the same dimension")
    
    plane = Plane(args.point1, args.point2, args.point3)
    distance, _ = plane.distance_to_plane(args.point)
    print(f"{distance}")


if __name__ == '__main__':
    main()
