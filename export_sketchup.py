"""Create SketchUp reference files from a floor-plan image."""
import argparse

from floorplan_ai.sketchup import export_sketchup_reference


parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("--output-dir", default="out")
parser.add_argument("--scale-mm-per-pixel", type=float, default=10.0)
parser.add_argument("--lang", default="kor+eng")
args = parser.parse_args()
for output in export_sketchup_reference(args.input, args.output_dir, args.scale_mm_per_pixel, args.lang):
    print(output)
