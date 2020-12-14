import sys
import os
from PIL import Image, ImageOps
from multiprocessing import Process, Queue, cpu_count
from datetime import datetime
from django.conf import settings

now = datetime.now()
date_time = now.strftime("%m_%d_%Y_%H_%M_%S")

TILE_MATCH_RES = 5  # tile matching resolution (higher values give better fit but require more processing)
SUB_IMAGE_SIZE = 30  # define the height and width of the sub images. Remain constant
ENLARGEMENT = 8  # 8 times bigger than the original one

TILE_BLOCK_SIZE = SUB_IMAGE_SIZE / max(min(TILE_MATCH_RES, SUB_IMAGE_SIZE), 1)

# My Computer is 4
WORKER_COUNT = max(cpu_count() - 1, 1)

out_file_name = 'mosaic_' + date_time + '.jpeg'
OUT_FILE = os.path.join(settings.RESULT_ROOT, out_file_name)
EOQ_VALUE = None


class ProcessSubImage:
    def __init__(self, tiles_directory):
        self.tiles_directory = tiles_directory

    def __process_tile(self, tile_path):
        try:

            # open file path
            img = Image.open(tile_path)

            # if an image has an EXIF Orientation tag, return a new image that is transposed accordingly.
            img = ImageOps.exif_transpose(img)

            # tiles must be square, so get the largest square that fits inside the image
            w = img.size[0]
            h = img.size[1]

            # get the min of (height, width) return the min values to crop following the min.
            min_dims = min(w, h)

            # ex: 400x600 image. min = 400. w_c = 0, h_c = 100. --> crop height.
            w_crop = (w - min_dims) / 2
            h_crop = (h - min_dims) / 2

            # ex: img.crop((0, 100, 400, 500)) ----> img.crop(left, upper, right, lower)
            img = img.crop((w_crop, h_crop, w - w_crop, h - h_crop))
            # After  crop, the images now is square and balance in with and height (w=h).

            # resize((width, height))
            large_tile_img = img.resize((SUB_IMAGE_SIZE, SUB_IMAGE_SIZE), Image.ANTIALIAS)
            small_tile_img = img.resize((int(SUB_IMAGE_SIZE / TILE_BLOCK_SIZE), int(SUB_IMAGE_SIZE / TILE_BLOCK_SIZE)),
                                        Image.ANTIALIAS)
            # We have Large title and small title on the same target.

            return large_tile_img.convert('RGB'), small_tile_img.convert('RGB')
        except:
            return None, None

    def get_tiles(self):
        large_tiles = []
        small_tiles = []

        print('Reading tiles from {}...'.format(self.tiles_directory))

        # search the tiles directory recursively
        for root, subFolders, files in os.walk(self.tiles_directory):
            for tile_name in files:
                print('Reading {:40.40}'.format(tile_name), flush=True, end='\r')
                tile_path = os.path.join(root, tile_name)
                large_tile, small_tile = self.__process_tile(tile_path)
                if large_tile:
                    large_tiles.append(large_tile)
                    small_tiles.append(small_tile)

        print('Processed {} tiles.'.format(len(large_tiles)))

        return large_tiles, small_tiles


class ProcessBigImage:
    def __init__(self, image_path):
        self.image_path = image_path

    def get_data(self):
        print('Processing main image...')
        img = Image.open(self.image_path)
        w = img.size[0] * ENLARGEMENT
        h = img.size[1] * ENLARGEMENT
        large_img = img.resize((w, h), Image.ANTIALIAS)
        w_diff = (w % SUB_IMAGE_SIZE) / 2
        h_diff = (h % SUB_IMAGE_SIZE) / 2

        # if necessary, crop the image slightly so we use a whole number of tiles horizontally and vertically
        if w_diff or h_diff:
            large_img = large_img.crop((w_diff, h_diff, w - w_diff, h - h_diff))

        small_img = large_img.resize((int(w / TILE_BLOCK_SIZE), int(h / TILE_BLOCK_SIZE)), Image.ANTIALIAS)

        image_data = (large_img.convert('RGB'), small_img.convert('RGB'))

        print('Main image processed.')

        return image_data


class TileFitter:
    def __init__(self, tiles_data):
        # pass in small tiles
        self.tiles_data = tiles_data

    def __get_tile_diff(self, t1, t2, bail_out_value):
        diff = 0
        for i in range(len(t1)):
            '''
            t1[i]: Specific pixel of the image in list. Ex: (12,24,225)
            limit the computational python can cary
            t1[i][0]: red color.
            t1[i][1]: green color.
            t1[i][2]: blue color.
            '''
            diff += ((t1[i][0] - t2[i][0]) ** 2 + (t1[i][1] - t2[i][1]) ** 2 + (t1[i][2] - t2[i][2]) ** 2)
            if diff > bail_out_value:
                return diff
        return diff

    def get_best_fit_tile(self, img_data):
        best_fit_tile_index = None
        # Mine sys is 9223372036854775807 (limits the size of Python's data structures such as strings and lists.)
        # 64-bit: the value will be 2^63 – 1
        min_diff = sys.maxsize
        tile_index = 00

        # go through each tile in turn looking for the best match for the part of the image represented by 'img_data'
        for tile_data in self.tiles_data:
            diff = self.__get_tile_diff(img_data, tile_data, min_diff)
            if diff < min_diff:
                min_diff = diff
                best_fit_tile_index = tile_index
            tile_index += 1

        return best_fit_tile_index


def fit_tiles(work_queue, result_queue, tiles_data):
    """
    This method is try to take out the image data of work_queue which is
    contain the original_image_small data and coordinate of the box will
    be place by best fit image.

    By calling the class TileFilter parse in the title_data (all data of small titles)
    and calling the function get_best_fit_tile() from TitleFilter parse in the main
    image. So the function will find the best fit. and tile_index will store the index
    of the best fit image in the queue. Finally put() the coordinate and
    the index in the result_queue to continue the process 1)
    """
    # small tile
    tile_fitter = TileFitter(tiles_data)

    while True:
        try:
            # this is data of block images and coordinate of it
            img_data, img_coords = work_queue.get(True)
            if img_data == EOQ_VALUE:
                break

            tile_index = tile_fitter.get_best_fit_tile(img_data)
            result_queue.put((img_coords, tile_index))
        except KeyboardInterrupt:
            pass

    # let the result handler know that this worker has finished everything
    result_queue.put((EOQ_VALUE, EOQ_VALUE))


class ProgressCounter:
    def __init__(self, total):
        self.total = total
        self.counter = 0

    def update(self):
        self.counter += 1
        print("Progress: {:04.1f}%".format(100 * self.counter / self.total), flush=True, end='\r')


class MosaicImage:
    def __init__(self, original_img):
        self.image = Image.new(original_img.mode, original_img.size)

        # number of small image fit in the width of main image
        self.x_tile_count = int(original_img.size[0] / SUB_IMAGE_SIZE)

        # number of small image fit in the height of the main image
        self.y_tile_count = int(original_img.size[1] / SUB_IMAGE_SIZE)

        # this is the number of images fit in the main image
        self.total_tiles = self.x_tile_count * self.y_tile_count

    def add_tile(self, tile_data, coords):
        # Create a new image with h and w as defined
        img = Image.new('RGB', (SUB_IMAGE_SIZE, SUB_IMAGE_SIZE))
        '''
        putdata() Copies pixel data(tile_data) to this(img) image
        '''
        img.putdata(tile_data)

        # Paste the image(img :params) to self.main image(New Original) in specific coordinator.
        self.image.paste(img, coords)

    def save(self, path):
        self.image.save(path)


def build_mosaic(result_queue, all_tile_data_large, original_img_large):
    # Queue.
    mosaic = MosaicImage(original_img_large)

    active_workers = WORKER_COUNT
    while True:
        try:
            # Remove and return an item from the queue
            '''
            The queue is already contain the image and Coordinate 
            '''
            img_coords, best_fit_tile_index = result_queue.get()

            if img_coords == EOQ_VALUE:
                active_workers -= 1
                if not active_workers:
                    break
            else:
                # assign best fit title image from all titles (all_tile_data_large [list]).
                tile_data = all_tile_data_large[best_fit_tile_index]

                # paste the best title to main self.image's MosaicImage class.
                mosaic.add_tile(tile_data, img_coords)

        except KeyboardInterrupt:
            pass

    mosaic.save(OUT_FILE)
    print('\nFinished, output is in', OUT_FILE)


def compose(original_img, tiles):
    print('Building mosaic, press Ctrl-C to abort...')
    # This is a single main image assign for 2 params bellow
    original_img_large, original_img_small = original_img

    # 2 params bellow is list of tiles contain small and large images.
    tiles_large, tiles_small = tiles

    # get the info of Main image(enlarge image). Not does anything fancy here.
    mosaic = MosaicImage(original_img_large)

    # Function: getdata()
    # Returns the contents of this image as a sequence object containing pixel values. Flattened.
    # so that values for line one follow directly after the values of line zero, and so on. Credit: geeksforgeeks
    all_tile_data_large = [list(tile.getdata()) for tile in tiles_large]
    all_tile_data_small = [list(tile.getdata()) for tile in tiles_small]

    '''
    Using QUEUE is the best way for sharing data between processes. FIFO
    Queue passed parameters to process's target function. Let the process consume the data.
    By using put() function we are able to put the data into queue. 
    By using get() function we can get data out of queue and delete em from the queue.
    '''
    # WORKER_COUNT is limit on the number of items that can be placed in the queue
    work_queue = Queue(WORKER_COUNT)
    # infinite items
    result_queue = Queue()

    try:
        '''
        communication channel between processes
        start(): process will run and return its result.
        We don't really want the process to work permanently so we don't have to call join().
        If we don't terminate the process. It may scarcity your resource. You may need to kill the 
        process or wait until the work is finished
        '''
        # start the worker processes that will build the mosaic image
        Process(target=build_mosaic, args=(result_queue, all_tile_data_large, original_img_large)).start()

        # start the worker processes that will perform the tile fitting
        for n in range(WORKER_COUNT):
            # multiprocess program. Target = some_function. Args = some arguments.
            Process(target=fit_tiles, args=(work_queue, result_queue, all_tile_data_small)).start()

        progress = ProgressCounter(mosaic.x_tile_count * mosaic.y_tile_count)
        for x in range(mosaic.x_tile_count):
            for y in range(mosaic.y_tile_count):
                large_box = (x * SUB_IMAGE_SIZE,
                             y * SUB_IMAGE_SIZE,
                             (x + 1) * SUB_IMAGE_SIZE,
                             (y + 1) * SUB_IMAGE_SIZE)

                small_box = (x * SUB_IMAGE_SIZE / TILE_BLOCK_SIZE,
                             y * SUB_IMAGE_SIZE / TILE_BLOCK_SIZE,
                             (x + 1) * SUB_IMAGE_SIZE / TILE_BLOCK_SIZE,
                             (y + 1) * SUB_IMAGE_SIZE / TILE_BLOCK_SIZE)

                '''
                This work bellow will put into the queue a tuple(list,tuple) 
                list present for data of the image.
                tuple(large_box) is the coordinate of the image. (left, upper, right, and lower pixel coordinate)
                '''
                # getdata() return the color pixel of the block images with coordinate. RGB
                work_queue.put((list(original_img_small.crop(small_box).getdata()), large_box))
                progress.update()

    except KeyboardInterrupt:
        print('\nHalting, saving partial image please wait...')

    finally:
        # put these special values onto the queue to let the workers know they can terminate
        for n in range(WORKER_COUNT):
            work_queue.put((EOQ_VALUE, EOQ_VALUE))


def mosaic(img_path, tiles_path):
    # image_data is tuple(Large, Small) of Main target image.
    image_data = ProcessBigImage(img_path).get_data()

    # title_data is contain tuple(title_large, title_small)
    tiles_data = ProcessSubImage(tiles_path).get_tiles()

    # parse 2 tuple to compose() f.
    compose(image_data, tiles_data)

    return 'work is complete'
