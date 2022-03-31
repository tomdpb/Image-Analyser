# Image Analyser

## About

This python script analyses all images in a given folder and returns information of which images are similar, with an option to automatically delete the smaller ones. 
Checking for similarity is achieved by generating hashes for each image and using a hamming difference between the hashes. The size of the hash can also be changed to generate a more precise comparison with the tradeoff of losing some speed. The similarity of the images can also be changed if desired.

## Usage
1. Provide a folder by either changing the script itself or running it and providing the input.
2. Set how different the images should be. The default is 0, so it is only triggered if images are identical.
3. Set whether to delete the similar files or not. The default is to **not** delete.

## Requirements

- PIL: for image analysis
- scipy: for hamming difference
- [tqdm](https://github.com/tqdm/tqdm): for loading bars
- numpy: for storing and quickly processing arrays
- [imagehash](https://github.com/jgraving/imagehash): for generating the image hashes

### Note

The `tqdm` requirement can be skipped entirely by changing tqdm's `trange` to python's standard `range`. This results in no progress bar, however.