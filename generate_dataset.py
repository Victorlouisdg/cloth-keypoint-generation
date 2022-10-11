import argparse
import sys
from typing import List
import time
import subprocess


def find_already_generated_seeds(output_directory) -> List[int]:
    return []


def generate_dataset(
    amount_to_generate: int,
    scene: str,
    output_directory,
    image_width: int,
    image_height: int,
):
    start_seed = 0  # TODO discover highest generated seed and continue from there
    generated_seeds = find_already_generated_seeds(output_directory)

    # TODO possible cleanup of unfinished samples
    seeds = [start_seed + i for i in range(amount_to_generate)]
    seeds = [s for s in seeds if s not in generated_seeds]

    for seed in seeds:
        start = time.time()
        command = (
            f"blender -b -P generate_sample.py -- {seed} {scene} {output_directory} {image_width} {image_height} "
        )
        subprocess.run([command], shell=True, stdout=subprocess.DEVNULL)
        end = time.time()
        print(f"Finished generating sample {seed} in {end - start:.1f} seconds.")

    # TODO automatically attempt merge?


if __name__ == "__main__":
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
        parser = argparse.ArgumentParser()

        # TODO COPY GENERATE SAMPLE ARGS AND ONLY HAVE AMOUNT TO GENERATE ARG HERE
        parser.add_argument("amount_to_generate", type=int)
        parser.add_argument("scene")
        parser.add_argument("output_directory")
        parser.add_argument("image_width", type=int)
        parser.add_argument("image_height", type=int)
        args = parser.parse_known_args(argv)[0]

        generate_dataset(
            args.amount_to_generate, args.scene, args.output_directory, args.image_width, args.image_height
        )
    else:
        print("See usage instructions in README.md")
