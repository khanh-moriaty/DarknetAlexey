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
parser.add_argument('--thresh', type=float, 
                    default=0.1,
                    help="Maximum distance between predicted and gt. Value in range 0 to 1, scaled by cmtnd's size. (Default: 0.1)")

args = parser.parse_args()

PRED_DIR = args.pred
GT_DIR = args.gt
THRESHOLD = args.thresh

pred_dir = os.listdir(PRED_DIR)
gt_dir = os.listdir(GT_DIR)
gt_dir = [x for x in gt_dir if x.endswith('txt')]

TP = [0] * 5
FP = [0] * 5
TN = [0] * 5
FN = [0] * 5

for fi in gt_dir:
    # input()
    gt_path = os.path.join(GT_DIR, fi)
    pred_path = os.path.join(PRED_DIR, fi)
    if not os.path.isfile(pred_path): 
        print('No matching prediction file found: ', fi)
        continue
    
    found = [False] * 4
    positive = [False] * 4
    
    gt_pts = [(-1, -1)] * 4
    xmax = -1
    xmin = 10**9
    ymax = -1
    ymin = 10**9
    with open(gt_path, 'r') as f:
        lines = f.read().splitlines()
    for line in lines:
        content = line.split()
        name = int(content[0])
        if name not in range(4): continue
        found[name] = True
        positive[name] = True
        x, y, w, h = [float(x) for x in content[1:]]
        gt_pts[name] = (x, y)
        xmax = max(x, xmax)
        xmin = min(x, xmin)
        ymax = max(y, ymax)
        ymin = min(y, ymin)
        
    w = xmax - xmin if xmax != -1 and xmin != 10**9 else -1
    h = ymax - ymin if ymax != -1 and ymin != 10**9 else w
    w = w if w != -1 else h
    size = w ** 2 + h ** 2 if w != -1 else 2
    with open(pred_path, 'r') as f:
        lines = f.read().splitlines()
    for line in lines:
        content = line.split()
        name = int(content[0])
        assert name in range(4), pred_path + " ERROR: invalid class."
        x, y = gt_pts[name]
        if x == -1:
            FP[name] += 1
            continue
        
        found[name] = False
        dist = (x - float(content[1])) ** 2 + (y - float(content[2])) ** 2
        if dist <= size * THRESHOLD ** 2:
            positive[name] = False
            TP[name] += 1
        else:
            FP[name] += 1
        
    for i, x in enumerate(found):
        if x:
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