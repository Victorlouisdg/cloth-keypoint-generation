from typing import List
import airo_blender_toolkit as abt
import numpy as np
from mathutils import Vector

abt.clear_scene()

robots_x = 0.39
abt.Cube(size=0.14, location=(robots_x, 0, 0), scale=(1, 1, 0.1))
abt.Cube(size=0.14, location=(-robots_x, 0, 0), scale=(1, 1, 0.1))


# Set up example towel
towel_length = 0.7
towel_width = 0.5
towel = abt.Towel(towel_length, towel_width)
towel.blender_object.data.vertices[0].co += Vector([0.05, 0.1, 0])
towel.location = 0.02, 0.05, 0.0
towel.rotation_euler = 0, 0, np.pi / 16

# Random towel
# np.random.seed(2)
# towel_length = np.random.uniform(0.3, 1.0)
# towel_width = np.random.uniform(towel_length / 2, towel_length)
# towel = abt.Towel(towel_length, towel_width)
# towel.location = *np.random.uniform(-0.1, 0.1, size=2), 0.0
# towel.rotation_euler = [0, 0, np.random.uniform(0.0, 2 * np.pi)]
# for i in range(4):
#     towel.blender_object.data.vertices[0].co += Vector([np.random.uniform(0.0, 0.05), np.random.uniform(0.0, 0.05), 0])


towel.apply_transforms()

# Anonymize keypoint as detector can't differentiate between them.
keypoints = {"corner": list(towel.keypoints_3D.values())}


def vector_cosine(v0, v1):
    return np.dot(v0, v1) / np.linalg.norm(v0) / np.linalg.norm(v1)


def angle_2D(v0, v1):
    x1, y1, *_ = v0
    x2, y2, *_ = v1
    dot = x1 * x2 + y1 * y2  # dot product between [x1, y1] and [x2, y2]
    det = x1 * y2 - y1 * x2  # determinant
    angle = np.arctan2(det, dot)  # atan2(y, x) or atan2(sin, cos)
    return angle


def get_ordered_keypoints(keypoints):
    keypoints = np.array(keypoints)
    keypoint0 = keypoints[0]
    keypoints_remaining = keypoints[1:]

    angles = [angle_2D(keypoint0, keypoint) for keypoint in keypoints_remaining]
    angles = [angle % (2 * np.pi) for angle in angles]  # make angles positive from 0 to 2*pi
    keypoints_remaining_sorted = keypoints_remaining[np.argsort(angles)]
    keypoints_sorted = np.row_stack([keypoint0[np.newaxis, :], keypoints_remaining_sorted])
    return list(keypoints_sorted)


def closest_point(point, candidates):
    distances = [np.linalg.norm(point - candidate) for candidate in candidates]
    return candidates[np.argmin(distances)]


def select_towel_pull(corners: List[np.ndarray], margin=0.05):
    corners = np.array(corners)
    towel_center = np.mean(corners, axis=0)

    corners = get_ordered_keypoints(corners)
    edges = [(i, (i + 1) % 4) for i in range(4)]

    edge_lengths = [np.linalg.norm(corners[id0] - corners[id1]) for (id0, id1) in edges]

    edge_pairs = [(0, 2), (1, 3)]
    edge_pairs_mean_length = []
    for eid0, eid1 in edge_pairs:
        edge_length_mean = np.mean([edge_lengths[eid0], edge_lengths[eid1]])
        edge_pairs_mean_length.append(edge_length_mean)

    short_edge_pair = edge_pairs[np.argmin(edge_pairs_mean_length)]
    short_edges = [edges[eid] for eid in short_edge_pair]

    # By convention widht is smaller than length
    towel_width = min(edge_pairs_mean_length)
    towel_length = max(edge_pairs_mean_length)

    # We want the short edges parallel to the x-axis
    tx = towel_width / 2
    ty = towel_length / 2
    desired_corners = [
        np.array([tx, ty, 0]),
        np.array([-tx, ty, 0]),
        np.array([-tx, -ty, 0]),
        np.array([tx, -ty, 0]),
    ]

    corner_destination_pairs = []
    for edge in short_edges:
        id0, id1 = edge
        corner0 = corners[id0]
        corner0_options = [desired_corners[0], desired_corners[2]]
        destination0 = closest_point(corner0, corner0_options)

        corner1 = corners[id1]
        corner1_options = [desired_corners[1], desired_corners[3]]
        destination1 = closest_point(corner1, corner1_options)

        corner_destination_pairs.append((corner0, destination0))
        corner_destination_pairs.append((corner1, destination1))

    cosines = []
    for corner, destination in corner_destination_pairs:
        center_to_corner = corner - towel_center
        corner_to_destination = destination - corner
        cosine = vector_cosine(center_to_corner, corner_to_destination)
        cosines.append(cosine)

    best_pair = corner_destination_pairs[np.argmax(cosines)]
    corner, destination = best_pair

    corner_to_center = towel_center - corner
    corner_to_center_unit = corner_to_center / np.linalg.norm(corner_to_center)
    margin_vector = corner_to_center_unit * margin

    start = corner + margin_vector
    end = destination + margin_vector
    return start, end


corners = keypoints["corner"]
start, end = select_towel_pull(corners)

gripper_Z = np.array([0, 0, -1])
gripper_Y = np.array([0, 1, 0])
gripper_X = np.cross(gripper_Y, gripper_Z)
gripper_start_pose = abt.Frame.from_vectors(gripper_X, gripper_Y, gripper_Z, start)

path = abt.LinearPath(start, end, gripper_start_pose.orientation)

for i in np.linspace(0, 1, 4):
    pose = path.pose(i)
    abt.visualize_transform(pose)


# abt.visualize_path(path)
