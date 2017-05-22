import os
import cv2
import numpy as np
import random

path=os.getcwd()
labels_dir=os.path.join(path, '../data/labels.txt')
pos_dir=os.path.join(path, '../train/pos')
neg_dir=os.path.join(path, '../train/neg')
positiveSamples=4
negativeSamples=16
width=256
height=128

def createPositiveSamples(image, boxes):
    pBoxes=[]
    h=image.shape[0]; w=image.shape[1]
    shifts=[-3,-2,2,3]
    div=8;maxdiv=16
    for box in boxes:
        x=box[0]; y=box[1]; sw=box[2]; sh=box[3]
        deltax=sw//div; deltay=sh//div
        mindeltax=sw//maxdiv;mindeltay=sh//maxdiv;
        pBoxes.append(box)
        for i in range(positiveSamples):
            dx=0; dy=0
            if w<=div or h<=div:
                dx=shifts[random.randint(0,3)]
                dy=shifts[random.randint(0,3)]
            else:
                dx=random.randint(0, 2*deltax)-deltax
                dy=random.randint(0, 2*deltay)-deltay
            if dx>0 and dx<mindeltax:dx+=mindeltax
            elif dx<0 and dx>-mindeltax:dx-=mindeltax
            if dy>0 and dy<mindeltay:dy+=mindeltay
            elif dy<0 and dy>-mindeltay:dy-=mindeltay
            if x+dx<0:dx=0-x
            elif x+dx+sw>=w:dx=w-1-x-sw
            if y+dy<0:dy=0-y
            elif y+dy+sh>=h:dy=h-1-y-sh
            pBoxes.append([x+dx, y+dy, sw, sh])
    return pBoxes
        

def createNegativeSamples(image, boxes):
    if len(boxes)==0:
        return None
    nBoxes=[]
    h=image.shape[0]; w=image.shape[1]
    movx=w//16; movy=h//16
    prod=10
    #corners=[[0,0,w//3-1,h//3-1],[2*w//3,0,w//3-1,h//3-1],[0,2*h//3,w//3-1,h//3-1],[2*w//3,2*h//3,w//3-1,h//3-1]]
    corners=[[0,0,w//2-1,h//2-1],[w//2,0,w//2-1,h//2-1],[0,h//2,w//2-1,h//2-1],[w//2,h//2,w//2-1,h//2-1]]
    coeff=[[1,1],[-1,1],[1,-1],[-1,-1]]
    scale=[0.01* i for i in range(50,100,5)];scale.append(1.0)
    for i in range(negativeSamples):
        posIndex=random.randint(0, len(boxes)-1)
        sw=boxes[posIndex][2]; sh=boxes[posIndex][3]
        if sw>int(0.667*w) or sh>int(0.667*h):
            _scale=scale[random.randint(0,len(scale)-1)]
            index=random.randint(0,3)
            dx=(random.randint(0, movx))*coeff[index][0]
            dy=(random.randint(0, movy))*coeff[index][1]
            cx=corners[index][0]; cy=corners[index][1]
            nsw=int(corners[index][2]*_scale)
            nsh=int(corners[index][3]*_scale)
            if cx+dx<0:dx=0-cx
            elif cx+dx+nsw>=w:dx=w-1-cx-nsw
            if cy+dy<0:dy=0-cy
            elif cy+dy+nsh>=h:dy=h-1-cy-nsh
            nBoxes.append([cx+dx,cy+dy,nsw,nsh])
        else:
            _scale=scale[random.randint(0,len(scale)-1)]
            nsw=int(sw*_scale)
            nsh=int(sh*_scale)
            deltax=sw*prod; deltay=sh*prod
            innerx=int(0.9*sw);innery=int(0.9*sh)
            x=boxes[posIndex][0]; y=boxes[posIndex][1]
            dx=random.randint(0,2*deltax)-deltax
            dy=random.randint(0,2*deltay)-deltay
            if dx>0 and dx<innerx:dx=innerx
            elif dx<0 and dx>-innerx:dx=-innerx
            if dy>0 and dy<innery:dy=innery
            elif dy<0 and dy>-innery:dy=-innery
            if x+dx<0:dx=0-x
            elif x+dx+nsw>=w:dx=w-1-x-nsw
            if y+dy<0:dy=0-y
            elif y+dy+nsh>=h:dy=h-1-y-nsh
            nBoxes.append([x+dx,y+dy,nsw,nsh])
    return nBoxes
    

def loadSamples():
    if not os.path.exists(labels_dir):
        print('could not find label file')
        return None
    print('labels: '+labels_dir)
    sampleFiles=[]
    bounding_boxes=[]
    with open(labels_dir) as labels:
        lines=labels.readlines()
        i=0;is_box=0;
        fileIndexes=[]
        while i<len(lines):
            line=lines[i]
            if line[0]!='{'  and not is_box:
                sampleFiles.append(line.rstrip())
                fileIndexes.append(i)
            elif line[0]=='{':
                is_box=1;i+=1
                box_line=lines[i]
                box=[]
                #print(line)
                while box_line[0]!='}':
                    i+=1
                    #print(box_line)
                    rect=box_line.rstrip().split(' ')
                    box.append([int(i) for i in rect])
                    box_line=lines[i]
                is_box=0
                #print(box_line)
                bounding_boxes.append(box)
            i+=1
        if len(sampleFiles)!=len(bounding_boxes):
            print('error occured')
            for i in range(len(sampleFiles)):
                fileName=lines[fileIndexes[i]]
                if sampleFiles[i]!=fileName:
                    print('file name %s not exist'%fileName)
    labels.close()
    return sampleFiles, bounding_boxes

def saveSampleImages(sampleFiles, bounding_boxes):
    pcnt=0;ncnt=0
    for i in range(len(sampleFiles)):
        print(sampleFiles[i])
        image=cv2.imread(sampleFiles[i],0)
        boxes=bounding_boxes[i]
        pBoxes=createPositiveSamples(image, boxes)
        nBoxes=createNegativeSamples(image, boxes)
        for box in boxes:
            roi=image[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
            flipx=cv2.flip(roi,0)
            flipy=cv2.flip(roi,1)
            equalized=cv2.equalizeHist(roi)
            roi=cv2.resize(roi, (width, height), interpolation=cv2.INTER_CUBIC)
            flipx=cv2.resize(flipx, (width, height), interpolation=cv2.INTER_CUBIC)
            flipy=cv2.resize(flipy, (width, height), interpolation=cv2.INTER_CUBIC)
            equalized=cv2.resize(equalized, (width, height), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(os.path.join(pos_dir, '%d.jpg'%pcnt), roi)
            pcnt+=1
            cv2.imwrite(os.path.join(pos_dir, '%d.jpg'%pcnt), flipx)
            pcnt+=1
            cv2.imwrite(os.path.join(pos_dir, '%d.jpg'%pcnt), flipy)
            pcnt+=1
            cv2.imwrite(os.path.join(pos_dir, '%d.jpg'%pcnt), equalized)
            pcnt+=1
        for box in pBoxes:
            roi=image[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
            roi=cv2.resize(roi, (width, height), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(os.path.join(pos_dir, '%d.jpg'%pcnt), roi)
            pcnt+=1
        for box in nBoxes:
            roi=image[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
            roi=cv2.resize(roi, (width, height), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(os.path.join(neg_dir, '%d.jpg'%ncnt), roi)
            ncnt+=1

if __name__=='__main__':
    sampleFiles, bounding_boxes=loadSamples()
    print('sampleFile len: %d, boxes len: %d'%(len(sampleFiles), len(bounding_boxes)))
    if len(sampleFiles)!=len(bounding_boxes):
        print('label file error!')
    else:
        saveSampleImages(sampleFiles, bounding_boxes)
        

        
            
            
        




