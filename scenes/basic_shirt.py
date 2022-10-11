import airo_blender_toolkit as abt
import numpy as np
import sys
import argparse
from mathutils import Vector
from functools import partial


def randomize_waviness(wavy_cloth_group):
    corner_roundness = np.random.uniform(0.0, 1.0)
    noise_strength_max = np.random.uniform(0.0, 0.4)
    noise_frequency = np.random.uniform(0.0, 10.0)
    strength_reduction = 1.0 / (1.0 + noise_frequency)
    noise_strength = noise_strength_max * strength_reduction
    wavy_cloth_group.inputs["Corner Roundness"].default_value = corner_roundness
    wavy_cloth_group.inputs["Noise Strength"].default_value = noise_strength
    wavy_cloth_group.inputs["Noise Frequency"].default_value = noise_frequency


def generate_scene(seed):
    np.random.seed(seed)
    abt.clear_scene()

    ground = abt.Plane()
    ground.scale = (*np.random.uniform(0.75, 1.0, size=2), 1.0)
    ground.apply_transforms()
    ground_material = ground.add_random_material()  # required_tags=["wood"])

    ground_nodes = ground_material.node_tree.nodes
    if "Displacement" in ground_nodes:
        ground_nodes["Displacement"].inputs["Scale"].default_value = 0.0

    shirt = abt.PolygonalShirt()
    # a little height is needed to prevent (too much) occlusion from the ground material displacement
    shirt.location = (0, 0, 0.005)
    shirt.rotation_euler = [0, 0, np.random.uniform(0.0, 2 * np.pi)]
    shirt.triangulate(minimum_triangle_density=200)
    shirt.apply_transforms()
    shirt.unwrap()

    # Randomizing the UV to get more varied texturing of the shirt.
    # E.g. without this, the stripes are always horizontal
    shirt.rotate_uvs(np.random.choice([0, 90, 180, 270]))
    shirt.translate_uvs(np.random.uniform(0.0, 1.0, size=2))
    shirt.scale_uvs(np.random.uniform(0.5, 1.5))

    shirt.add_random_material(required_tags=["fabric"])

    wavy_cloth_group = shirt.add_geometry_node_group(name="Wavy Cloth")
    randomize_waviness(wavy_cloth_group)

    abt.World()

    camera = abt.Camera(focal_length=24)
    point = abt.sample_point(partial(abt.point_on_sphere, radius=1.2), lambda point: point.z > 0.9)
    camera.location = point
    noise_around_center = Vector([*(0.2 * np.random.randn(2)), 0])
    camera.look_at(noise_around_center)

    extra_data = {"keypointed_objects": [shirt]}

    return extra_data


if __name__ == "__main__":
    seed = 0
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
        parser = argparse.ArgumentParser()
        parser.add_argument("seed", type=int)
        args = parser.parse_known_args(argv)[0]
        seed = args.seed
    extra_data = generate_scene(seed)
    shirt = extra_data["keypointed_objects"][0]
    shirt.visualize_keypoints()
