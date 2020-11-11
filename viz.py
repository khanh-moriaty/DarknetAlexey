import cv2
import os
import numpy as np

CLASSES = [
    'topleft',
    'topright',
    'botleft',
    'botright',
]

INP_DIR = '/dataset/thuann_resized/'
OUT_DIR = '/dataset/viz/'
os.makedirs(OUT_DIR, exist_ok=True)

dir = os.listdir(INP_DIR)
dir = [fi for fi in dir if os.path.splitext(fi)[1] in ['.jpg', '.jpeg', '.png']]
dir.sort()

for fi in dir:
    print(fi)
    fn, _ = os.path.splitext(fi)
    img_path = os.path.join(INP_DIR, fi)
    img = cv2.imread(img_path)
    height, width = img.shape[:2]
    label_path = os.path.join(INP_DIR, fn + '.txt')
    bbox = []
    label = []
    with open(label_path, 'r') as content:
        lines = content.read().splitlines()
        for line in lines:
            line = line.split()
            label.append(CLASSES[int(line[0])])
            x, y, w, h = [float(x) for x in line[1:]]
            xmin = (x - w/2) * width
            xmax = (x + w/2) * width
            ymin = (y - h/2) * height
            ymax = (y + h/2) * height
            bbox.append([
                [[xmin, ymin]],
                [[xmax, ymin]],
                [[xmax, ymax]],
                [[xmin, ymax]],
            ])
    bbox = np.array(bbox).astype(np.int32)
    img = cv2.polylines(img, bbox, isClosed=True, color=(0,0,224), thickness=2)
    for lb, bb in zip(label, bbox):
        x = bb[0][0][0]
        y = bb[0][0][1] if bb[0][0][1] > 100 else bb[2][0][1] + 40
        cv2.putText(img, lb, (x,y), cv2.FONT_HERSHEY_COMPLEX, 0.6, color=(32,32,32), thickness=2)
        pass
    
    out_path = os.path.join(OUT_DIR, fi)
    cv2.imwrite(out_path, img)
