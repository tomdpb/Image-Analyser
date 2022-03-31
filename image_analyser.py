from PIL import Image, ImageFile
from scipy.spatial.distance import hamming
from tqdm import trange
import numpy as np
import imagehash
import os 
import sys


def generate_hashes(files, hash_size):
    hashes = np.array([])
    non_img_indices = np.array([], dtype=int)
    for i in trange(files.size):
        try:
            with Image.open(files[i]) as im:
                hashes = np.append(hashes,
                                   imagehash.phash(im, hash_size=hash_size))
        # ignore non-image files and save index for later
        except Image.UnidentifiedImageError:
            non_img_indices = np.append(non_img_indices, i)
            continue
        except IsADirectoryError:
            continue
    return hashes, non_img_indices


def is_similar(hash_1, hash_2, cutoff=0):
    """
    Uses hamming difference to see if the hashes (and therefore images in this
    case) are similar. The similarity is then determined on the given cutoff
    value.
    
    A lower cutoff value means that the hashes are more similar while a higher
    cutoff value will signify that the hashes are more different.
    Example: a hamming difference of 0 means that the hashes are identical.
    A hamming difference of 32 means the hashes are very different.
    """
    if hamming(hash_1, hash_2)*len(hash_1) <= cutoff:
        return True
    else:
        return False


def get_pixel_count(infile):
    with Image.open(infile) as im:
        width, height = im.size
    
    return width*height


def get_smallest_img(img_1, img_2):
    size_1 = get_pixel_count(img_1)
    size_2 = get_pixel_count(img_2)

    if size_1 >= size_2:
        return img_2
    else:
        return img_1


def main(search_folder, cutoff=0, *, delete_files=False, hash_size=10):
    try:
        files = np.array(os.listdir(os.chdir(search_folder)))
    except FileNotFoundError:
        print(f"The folder {search_folder} doesn't exist.")
        raise

    print("Step 1 of 2:")    
    print("Generating hashes.")
    hashes, non_img_indices = generate_hashes(files, hash_size)

    print("\nStep 2 of 2:")
    # no images were found
    if hashes.size == 0:
        print("No images were found in the given folder.")
        sys.exit()
    
    # remove non-image files from analysis
    files = np.delete(files, non_img_indices)

    if delete_files:
        print("Analyzing hashes and DELETING similar images.")
    else:
        print("Analyzing hashes.")

    results = []
    for i in trange(files.size):  # use trange for loading bar
        for j in range(i+1, files.size):
            try:
                if is_similar(hashes[i], hashes[j], cutoff):
                    results.append(f"{files[i]} and {files[j]}")

                    if delete_files:
                        os.remove(get_smallest_img(files[i], files[j]))
            # FileNotFoundError can happen if the file was already deleted
            except (FileNotFoundError, Image.UnidentifiedImageError):
                continue
    # list is empty
    if not results:
        results.append(f"No similar images in folder {search_folder}.")

    return results


if __name__ == "__main__":
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    search_folder = None
    # a lower difference means images are more similar
    # 0 -> the images are identical
    DIFFERENCE = 0 
    DELETE_FILES = False

    if search_folder is None:
        print("No folder to analyse was given.") 
        print("Please input a folder to analyse.")
        search_folder = input("Put a . to analyse the current folder:\n> ")

    results = main(search_folder, DIFFERENCE, delete_files=DELETE_FILES, hash_size=16)

    print("\n\nSimilar images:\n", results)
    sys.exit()
