import argparse
import os
import sys
import shutil
import subprocess

if __name__ == "__main__":
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
        parser = argparse.ArgumentParser()
        parser.add_argument("output_directory")
        args = parser.parse_known_args(argv)[0]


        annotations_json = os.path.join(args.output_directory, "annotations.json")
        annotations_directory = os.path.join(args.output_directory, "annotations")
        annotations = [f for f in os.listdir(annotations_directory) if f.endswith(".json")]
        annotation_files = [os.path.join(annotations_directory, a) for a in annotations]

        shutil.copyfile(annotation_files[0], annotations_json)

        file_extend = annotations_json
        for file_add in annotation_files[1:]:
            command = (
                f"pyodi coco merge {file_extend} {file_add} {file_extend}"
            )
            subprocess.run([command], shell=True, stdout=subprocess.DEVNULL)
