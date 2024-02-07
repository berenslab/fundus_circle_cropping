[![DOI](https://zenodo.org/badge/717013278.svg)](https://zenodo.org/doi/10.5281/zenodo.10137934)

# Overview
Fundus images are processed by (1) finding a circular mask with least-squares expectation-maximization fitting of a circle to the image edges, and (2) cropping the image tightly around the found circle.

With this preprocessing method, all images are equally centered, some background pixels are removed, and a boolean mask of the extracted circle is stored.


|   original   |   cropped  | mask |
|------------|------------|------------|
|<img src="./example_images/images/01_h.jpg" height="150">|<img src="./example_images/images_cropped/01_h.png" width="150">|<img src="./example_images/masks/01_h.png" width="150">|
|<img src="./example_images/images/02_h.jpg" height="150">|<img src="./example_images/images_cropped/02_h.png" width="150">|<img src="./example_images/masks/02_h.png" width="150">|
|<img src="./example_images/images/03_h.jpg" height="150">|<img src="./example_images/images_cropped/03_h.png" width="150">|<img src="./example_images/masks/03_h.png" width="150">|
|<img src="./example_images/images/04_h.jpg" height="150">|<img src="./example_images/images_cropped/04_h.png" width="150">|<img src="./example_images/masks/04_h.png" width="150">|


# Installation
Setup a python environment with a python version between `>=3.6` and `<3.12`.
Then, install all the other dependencies directly from source
```python
git clone https://github.com/berenslab/fundus_circle_cropping
cd fundus_circle_cropping
pip install -e .
```

# Basic example
Download some example data of healthy fundus images from https://www5.cs.fau.de/research/data/fundus-images/ with a bash script
```bash
bash download_data/download.sh
```
This will create a `data/images` folder to store the images and an image identity file `data/ids.lst` with a list of filenames.

To crop the downloaded fundus images, run the sample script [crop.py](crop.py), which expects a configuration [basic_example.yaml](configs/basic_example.yaml) and runs over the downloaded data.
```python
python crop.py -c ./configs/basic_example.yaml
```

The preprocessed images are stored in `data/images_cropped` and the corresponding circular masks in `data/masks`.

# Parallel processing with ray
Since the image preprocessing of images can be run independently, we also support code parallel processing with [ray](https://docs.ray.io/en/latest/ray-overview/installation.html). We have one example configuration file [ray_eyample.yaml](configs/ray_example.yaml) on how to run that.
```python
python crop.py -c ./configs/ray_example.yaml
```

# Note
If you run the code on other retinal fundus datasets, adjust the `root_folder` in the [config file](configs/basic_example.yaml) and provide a text file with image names. The `preprocessing parameters` were optimized with the [kaggle-dr-dataset](https://www.kaggle.com/c/diabetic-retinopathy-detection/data) and may need to be adjusted for other datasets.

# Cite 
If you use this software, please cite it as below.
```
@software{mueller_fundus_circle_cropping_2023,
  author = {M\"uller, Sarah and Heidrich, Holger and Koch, Lisa M. and Berens, Philipp},
  doi = {10.5281/zenodo.10137935},
  title = {fundus circle cropping},
  url = {https://github.com/berenslab/fundus_circle_cropping},
  version = {0.2.0},
  year = {2023}
}
```
