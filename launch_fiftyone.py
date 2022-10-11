import fiftyone as fo
import fiftyone.zoo as foz

# First time running this script, uncomment the line below.
# dataset = foz.load_zoo_dataset("coco-2017", split="validation")

labels_file = r"/home/idlab185/fiftyone/coco-2017/raw/person_keypoints_val2017.json"
dataset_file = r"/home/idlab185/fiftyone/coco-2017/validation"

dataset = fo.Dataset.from_dir(
    dataset_type = fo.types.COCODetectionDataset,
    label_types = ["detections", "segmentations", "keypoints"],
    dataset_dir = dataset_file,
    labels_path = labels_file)

session = fo.launch_app(dataset)
session.wait()