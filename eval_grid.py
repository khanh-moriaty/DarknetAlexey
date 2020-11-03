import os
import cv2
import argparse

parser = argparse.ArgumentParser(description="This script is used to evaluate the performance of Darknet's models.")
parser.add_argument('--pred', type=str, 
                    default="data/ocr/back_cmtnd_resized/",
                    help="Path to prediction directory, which should contain all .txt output files predicted by the model.")
parser.add_argument('--gt', type=str, 
                    default="data/ocr/test/",
                    help="Path to ground truth directory, which should contain all .txt label files.")
# parser.add_argument('--ratio', type=float, 
#                     default="data/test/",
#                     help="Ratio used f")

args = parser.parse_args()

PRED_DIR = args.pred
GT_DIR = args.gt

pred_dir = os.listdir(PRED_DIR)
gt_dir = os.listdir(GT_DIR)
gt_dir = [x for x in gt_dir if x.endswith('txt')]

TP = [0] * 5
FP = [0] * 5
TN = [0] * 5
FN = [0] * 5

for fi in gt_dir:
    # print(fi)
    gt_path = os.path.join(GT_DIR, fi)
    pred_path = os.path.join(PRED_DIR, fi)
    if not os.path.isfile(pred_path): 
        print('No matching prediction file found: ', fi)
        continue
    
    bbox = []
    check = [True] * 4
    with open(gt_path, 'r') as f:
        lines = f.read().splitlines()
    for line in lines:
        content = line.split()
        name = int(content[0])
        if name not in range(4): continue
        check[name] = False
        x, y, w, h = [float(x) for x in content[1:]]
        bbox += [
            [x-w/2, y-h/2],
            [x+w/2, y-h/2],
            [x+w/2, y+h/2],
            [x-w/2, y+h/2],
        ]
    xmin = min(bbox, key=lambda x: x[0], default=[0,0])[0]
    xmax = max(bbox, key=lambda x: x[0], default=[1,1])[0]
    ymin = min(bbox, key=lambda x: x[1], default=[0,0])[1]
    ymax = max(bbox, key=lambda x: x[1], default=[1,1])[1]
    
    def get_gt(x, y):
        if ymin <= y <= ymin + (ymax - ymin) / 3: 
            if xmin <= x <= xmin + (xmax - xmin) / 3: 
                return 0 # topleft
            if xmin + (xmax - xmin) / 3 <= x <= xmax: 
                return 1 # topright
        if ymax - (ymax - ymin) / 3 <= y <= ymax: 
            if xmin <= x <= xmin + (xmax - xmin) / 3: 
                return 2 # botleft
            if xmin + (xmax - xmin) / 3 <= x <= xmax: 
                return 3 # botright
        return -1 # not valid
    
    with open(pred_path, 'r') as f:
        lines = f.read().splitlines()
    for line in lines:
        content = line.split()
        name = int(content[0])
        assert name in range(4), pred_path + " ERROR: invalid class."
        check[name] = True
        x, y, w, h = [float(x) for x in content[1:]]
        gt = get_gt(x, y)
        if name == gt:
            TP[name] += 1
        else:
            FP[name] += 1
            FN[gt] += 1
    
    for i, x in enumerate(check):
        if not x:
            FN[i] += 1
        
precision = [tp/(tp+fp) if tp+fp > 0 else 0 for tp, fp in zip(TP, FP)]
recall = [tp/(tp+fn) if tp+fn > 0 else 0 for tp, fn in zip(TP, FN)]

avg_precision = sum(precision) / 4
avg_recall = sum(recall) / 4

print('--RESULT--')

# print(TP)
# print(FP)
# print(FN)

for i, (x, y) in enumerate(zip(precision[:-1], recall[:-1])):
    print("precision[{}] = {}".format(i, x))
    print("recall[{}] = {}".format(i, y))
    print()
print('===> avg_precision:', avg_precision)
print('===> avg_recall:', avg_recall)