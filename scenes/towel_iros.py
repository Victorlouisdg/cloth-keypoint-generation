import airo_blender_toolkit as abt
import numpy as np
import sys
import argparse
from mathutils import Vector
from functools import partial


def randomize_waviness(wavy_cloth_group):
    corner_roundness = np.random.uniform(0.0, 1.0)
    noise_strength_max = np.random.uniform(0.0, 0.8)
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
    ground_material = ground.add_random_material(disallowed_tags=["fabric"])

    ground_nodes = ground_material.node_tree.nodes
    if "Displacement" in ground_nodes:
        ground_nodes["Displacement"].inputs["Scale"].default_value = 0.0

    towel_length = np.random.uniform(0.3, 1.0)
    towel_width = np.random.uniform(towel_length / 2, towel_length)
    towel = abt.Towel(towel_length, towel_width)
    towel.location = *np.random.uniform(-0.2, 0.2, size=2), 0.002
    towel.rotation_euler = [0, 0, np.random.uniform(0.0, 2 * np.pi)]
    towel.triangulate(minimum_triangle_density=200)
    towel.apply_transforms()
    towel.unwrap()

    # Randomizing the UV to get more varied texturing of the towel.
    # E.g. without this, the stripes are always horizontal
    towel.rotate_uvs(np.random.choice([0, 90, 180, 270]))
    towel.translate_uvs(np.random.uniform(0.0, 1.0, size=2))
    towel.scale_uvs(np.random.uniform(0.5, 1.5))

    towel.add_random_material(required_tags=["fabric"])

    wavy_cloth_group = towel.add_geometry_node_group(name="Wavy Cloth")
    randomize_waviness(wavy_cloth_group)

    abt.World()

    def gso_filter_no_towels(asset: abt.Asset) -> bool:
        return not any([t in asset.name.lower() for t in ["towel", "washcloth"]])

    n_distractors = 5
    for _ in range(n_distractors):
        random_object = abt.BlenderObject.random(
            required_tags=["Google Scanned Objects"], custom_filter=gso_filter_no_towels
        )
        random_object.location = (*np.random.uniform(-1.5, 1.5, size=2), 0.0)
        random_object.rotation_euler.z = np.random.uniform(2 * np.pi)

    camera = abt.Camera(focal_length=24)
    point = abt.sample_point(partial(abt.point_on_sphere, radius=1.0), lambda point: point.z > 0.8)
    camera.location = point
    noise_around_center = Vector([*(0.2 * np.random.randn(2)), 0])
    camera.look_at(noise_around_center)

    extra_data = {"keypointed_objects": [towel]}

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
    towel = extra_data["keypointed_objects"][0]
    towel.visualize_keypoints()
