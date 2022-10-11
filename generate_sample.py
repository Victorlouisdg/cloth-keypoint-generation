import argparse
import json
import os
import sys
import bpy
import importlib
from airo_blender_toolkit.coco_parser import CocoKeypointAnnotation, CocoImage, CocoKeypoints
import numpy as np

def configure_render_settings(image_width, image_height):
    scene = bpy.context.scene
    scene.render.resolution_x = image_width
    scene.render.resolution_y = image_height
    scene.render.image_settings.color_mode = "RGB"
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.adaptive_threshold = 0.1


def generate_sample(seed, generate_scene, output_directory, image_width, image_height):
    output_directory = os.path.abspath(output_directory)
    images_directory = os.path.join(output_directory, "images")
    annotations_directory = os.path.join(output_directory, "annotations")
    annotation_json = os.path.join(annotations_directory, f"person_keypoints_{seed}.json")
    os.makedirs(images_directory, exist_ok=True)
    os.makedirs(annotations_directory, exist_ok=True)

    configure_render_settings(image_width, image_height)

    images = []
    categories = []
    annotations = []

    extra_data = generate_scene(seed)
    image_name = f"{seed}.png"
    image_id = seed
    image_path = os.path.join(images_directory, image_name)
    image_path_relative = os.path.relpath(image_path, output_directory)
    bpy.context.scene.render.filepath = image_path
    bpy.ops.render.render(write_still=True)

    image = CocoImage(file_name=image_path_relative, height=image_height, width=image_width, id=image_id)
    images.append(image)

    np.random.seed(seed)
    # Then we extract all the annotations
    for keypointed_object in extra_data["keypointed_objects"]:
        keypointed_object.visualize_keypoints()
        category = keypointed_object.category
        if category not in categories:
            categories.append(category)

        keypoints = keypointed_object.coco_keypoints

        annotation = CocoKeypointAnnotation(
            category_id=category.id,
            id=np.random.randint(np.iinfo(np.int32).max),
            image_id=image_id,
            keypoints=keypoints,
            segmentation=[],
            area=0.0,
            bbox=(0,0,0,0),
            iscrowd=0,
        )
        annotations.append(annotation)

    labels = CocoKeypoints(images=images, categories=categories, annotations=annotations)
    with open(annotation_json, "w") as file:
        json.dump(labels.dict(exclude_none=True), file)


if __name__ == "__main__":
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
        parser = argparse.ArgumentParser()
        parser.add_argument("seed", type=int)
        parser.add_argument("scene")
        parser.add_argument("output_directory")
        parser.add_argument("image_width", type=int)
        parser.add_argument("image_height", type=int)
        args = parser.parse_known_args(argv)[0]
        print(args.scene)

        file_path = args.scene
        module_name = args.scene.split("/")[-1].split(".")[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        generate_sample(args.seed, module.generate_scene, args.output_directory, args.image_width, args.image_height)
    else:
        print("See usage instructions in README.md")
