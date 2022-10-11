# cloth-keypoint-generation

Blender python scripts to generate clothes with annotated keypoints.

## Installation

Install the [airo_blender_toolkit](https://github.com/airo-ugent/airo-blender-toolkit) package and clone this repo.
Install the [Poly Haven](https://github.com/Poly-Haven/polyhavenassets) addon and download its assets.

Optinionally generate fabric material with the airo-blender-toolkit fabric_generator addon.

## Usage
```bash
blender -b -P generate_dataset.py -- 100 scenes/towel_iros.py datasets/test2 256 256
blender -b -P merge_annotations.py -- datasets/test2
```
When running the second command, make sure the `pyodi` command is available.
