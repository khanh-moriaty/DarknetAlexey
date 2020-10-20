import os
import shutil
import xml.etree.ElementTree as ET
from random import randint
from time import time
from skimage import io
import numpy as np
from itertools import repeat
from multiprocessing import Pool

CLASSES = {
    'topleft': 0, 
    'topright': 1, 
    'botleft': 2, 
    'botright': 3,
}

def proc(fi, INP_DIR, IMG_DIR, OUT_DIR):
    # print(fi)
    if fi.split('.')[-2] in [str(x) for x in range(1,15)]: 
        # print(fi.split('.')[-3])
        # return None
        pass
    inp_path = os.path.join(INP_DIR, fi)
    fn, _ = os.path.splitext(fi)
    img_path = os.path.join(IMG_DIR, fn + '.jpg')
    out_path = os.path.join(OUT_DIR, fn + '.{}.txt'.format(int(time())))
    out_img_path = os.path.join(OUT_DIR, fn + '.{}.jpg'.format(int(time())))
    if not os.path.exists(img_path): return
    try:
        img = io.imread(img_path)
    except:
        print('IMAGE ERROR:', img_path)
        return None
    shutil.copyfile(img_path, out_img_path)
    tree = ET.parse(inp_path)
    root = tree.getroot()
    size = root.find('size')
    width, height = int(size.findtext('width')), int(size.findtext('height'))
    fo = open(out_path, 'w')
    check = {name: None for name in CLASSES}
    for obj in root.iter('object'):
        name = obj.findtext('name')
        if name not in CLASSES or name not in check:
            continue
        check.pop(name)
        bbox = obj.find('bndbox')
        xmin = int(bbox.findtext('xmin')) / width
        xmax = int(bbox.findtext('xmax')) / width
        ymin = int(bbox.findtext('ymin')) / height
        ymax = int(bbox.findtext('ymax')) / height
        x = np.clip((xmax+xmin)/2, 0.01, .99)
        y = np.clip((ymax+ymin)/2, 0.01, .99)
        # x = (xmax+xmin)/2
        # y = (ymax+ymin)/2
        if x <= 0 or x >= 1:
            print('x out of bound:', x, img_path)
        if y <= 0 or y >= 1:
            print('x out of bound:', y, img_path)
        w = np.clip(max(xmax-xmin, randint(50, 100)/width), .01, .99)
        h = np.clip(max(ymax-ymin, randint(50, 100)/height), .01, .99)
        # w = max(xmax-xmin, randint(50, 100)/width)
        # h = max(ymax-ymin, randint(50, 100)/height)
        if w <= 0 or w >= 1:
            print('w out of bound:', w, img_path)
        if h <= 0 or h >= 1:
            print('h out of bound:', h, img_path)
        if x-w/2 <= 0 or x+w/2 >= 1:
            print('xw out of bound:', x-w/2, x+w/2, img_path)
        if y-h/2 <= 0 or y+h/2 >= 1:
            print('yh out of bound:', y-h/2, y+h/2, img_path)
        content = [CLASSES[name], x, y, w, h]
        content = ' '.join([str(x) for x in content])
        fo.write(content + '\n')
        
    if 'topleft' in check:
        fo.write('0 0.05 0.05 0.1 0.1\n')
    if 'topright' in check:
        fo.write('1 0.95 0.05 0.1 0.1\n')
    if 'botleft' in check:
        fo.write('2 0.05 0.95 0.1 0.1\n')
    if 'botright' in check:
        fo.write('3 0.95 0.95 0.1 0.1\n')
        
    fo.close()
    return out_img_path

def proc_dir(INP_DIR, IMG_DIR, OUT_DIR):
    print(INP_DIR)
    dir = os.listdir(INP_DIR)
    with Pool(100) as pool:
        res = pool.starmap(proc, zip(dir, repeat(INP_DIR), repeat(IMG_DIR), repeat(OUT_DIR)))
    res = [x for x in res if x is not None]
    print('Write', len(res), 'files.')
    train_path = os.path.join(OUT_DIR, 'train.txt')
    train = open(train_path, 'a')
    train.write('\n'.join(res) + '\n')
    train.close()


INP_DIR_LIST = [
    # "/dataset/crawl/front_cmtnd_resized/label/",
    # "/dataset/crawl/back_cmtnd_resized/label/",
    "/dataset/crawl/front_cccd_resized/label/",
    "/dataset/crawl/back_cccd_resized/label/",
    # "/dataset/crawl/hc_resized/label/",
    
    # "/dataset/augmented/front_cmtnd_resized/label/",
    # "/dataset/augmented/back_cmtnd_resized/label/",
    "/dataset/augmented/front_cccd_resized/label/",
    "/dataset/augmented/back_cccd_resized/label/",
    # "/dataset/augmented/hc_resized/label/",
]
IMG_DIR_LIST = [
    # "/dataset/crawl/front_cmtnd_resized/image/",
    # "/dataset/crawl/back_cmtnd_resized/image/",
    "/dataset/crawl/front_cccd_resized/image/",
    "/dataset/crawl/back_cccd_resized/image/",
    # "/dataset/crawl/hc_resized/image/",
    
    # "/dataset/augmented/front_cmtnd_resized/image/",
    # "/dataset/augmented/back_cmtnd_resized/image/",
    "/dataset/augmented/front_cccd_resized/image/",
    "/dataset/augmented/back_cccd_resized/image/",
    # "/dataset/augmented/hc_resized/image/",
]

OUT_DIR_LIST = [
    # "/storage/data/ocr/front_cmtnd_resized/",
    # "/storage/data/ocr/back_cmtnd_resized/",
    "/storage/data/ocr/front_cccd_resized/",
    "/storage/data/ocr/back_cccd_resized/",
    # "/storage/data/ocr/hc_resized/",
    
    # "/storage/data/ocr/front_cmtnd_resized/",
    # "/storage/data/ocr/back_cmtnd_resized/",
    "/storage/data/ocr/front_cccd_resized/",
    "/storage/data/ocr/back_cccd_resized/",
    # "/storage/data/ocr/hc_resized/",
]

for INP_DIR, IMG_DIR, OUT_DIR in zip(INP_DIR_LIST, IMG_DIR_LIST, OUT_DIR_LIST):
    os.makedirs(OUT_DIR, exist_ok=True)
    # train_path = os.path.join(OUT_DIR, 'train.txt')
    # train = open(train_path, 'w')
    # train.close()
    proc_dir(INP_DIR, IMG_DIR, OUT_DIR)
    