from PIL import Image, ImageFile
from tqdm import trange
import imagehash
import os
import sys

ImageFile.LOAD_TRUNCATED_IMAGES = True


def generate_hashes(
    files: list, hash_size: int
) -> tuple[list[imagehash.ImageHash], list[int]]:
    hashes = []
    non_img_indices = []
    for i in trange(len(files)):
        try:
            with Image.open(files[i]) as im:
                hashes.append(imagehash.phash(im, hash_size=hash_size))
        # ignore non-image files and save index for later
        except Image.UnidentifiedImageError:
            non_img_indices.append(i)
            continue
        except IsADirectoryError:
            continue
    return hashes, non_img_indices


def is_similar(
    hash_1: imagehash.ImageHash, hash_2: imagehash.ImageHash, cutoff: int = 0
) -> bool:
    """
    Uses hamming difference to see if the hashes (and therefore images in this
    case) are similar. The similarity is then determined on the given cutoff
    value.

    A lower cutoff value means that the hashes are more similar while a higher
    cutoff value will signify that the hashes are more different.
    Example: a hamming difference of 0 means that the hashes are identical.
    A hamming difference of 32 means the hashes are very different.
    """
    if abs(hash_1 - hash_2) <= cutoff:
        return True
    else:
        return False


def get_pixel_count(infile: str) -> int:
    with Image.open(infile) as im:
        width, height = im.size

    return width * height


def get_smallest_img(img_1, img_2):
    size_1 = get_pixel_count(img_1)
    size_2 = get_pixel_count(img_2)

    if size_1 >= size_2:
        return img_2
    else:
        return img_1


def main(
    search_folder: str,
    cutoff: int = 0,
    *,
    delete_files: bool = False,
    hash_size: int = 10,
) -> list[str] | None:
    results = []

    try:
        files = list(os.listdir(os.chdir(search_folder)))
    except FileNotFoundError:
        raise FileNotFoundError(f"The folder {search_folder} doesn't exist.")

    print("Step 1 of 2:")
    print("Generating hashes.")
    hashes, non_img_indices = generate_hashes(files, hash_size)

    print("\nStep 2 of 2:")
    # no images were found
    if len(hashes) == 0:
        print("No images were found in the given folder.")
        return None

    # remove non-image files from analysis
    for d in non_img_indices:
        files.pop(d)

    if delete_files:
        print("Analyzing hashes and DELETING similar images.")
    else:
        print("Analyzing hashes.")

    for i in trange(len(files)):  # use trange for loading bar
        for j in range(i + 1, len(files)):
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
    search_folder = None
    # a lower difference means images are more similar
    # 0 -> the images are identical
    DIFFERENCE = 0
    DELETE_FILES = False

    while search_folder is None:
        print("No folder to analyse was given.\n")
        print("Please input a folder to analyze or q to quit.")
        search_folder = input("Type . to analyze the current folder:\n> ")
        if search_folder == "q":
            print("Quitting")
            sys.exit()
    try:
        results = main(
            search_folder, DIFFERENCE, delete_files=DELETE_FILES, hash_size=16
        )
    except FileNotFoundError:
        print(f"{search_folder} does not exist")
        sys.exit(1)

    print("\n\nSimilar images:\n", results)
    sys.exit()
