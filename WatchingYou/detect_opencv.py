#source: https://www.learnopencv.com/deep-learning-based-object-detection-using-yolov3-with-opencv-python-c/

import cv2, os, argparse
import numpy as np
import datetime, time
from django.utils import timezone
import PIL.Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import NullLocator

def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]


def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    return indices, boxes, classIds, confidences

def draw_mat(path, indices, boxes, classIds, confidences):
    img = np.array(PIL.Image.open(path))
    plt.figure()
    fig, ax = plt.subplots(1)
    ax.imshow(img)
    cmap = plt.get_cmap('tab20b')
    colors = [cmap(i) for i in np.linspace(0, 1, 20)]
    for indice in indices:
        i = indice[0]
        box = boxes[i]
        x1 = box[0]
        y1 = box[1]
        print('\t+ Label: %s, Conf: %.5f' % (classes[classIds[i]], confidences[i]))
        box_h = box[3]
        box_w = box[2]
        color = colors[classIds[i]%20]
        # Create a Rectangle patch
        bbox = patches.Rectangle((x1, y1), box_w, box_h, linewidth=2,
                                 edgecolor=color,
                                 facecolor='none')
        # Add the bbox to the plot
        ax.add_patch(bbox)
        # Add label
        plt.text(x1, y1, s=classes[classIds[i]], color='white', verticalalignment='top',
                 bbox={'color': color, 'pad': 0})

    # Save generated image with detections
    plt.axis('off')
    plt.gca().xaxis.set_major_locator(NullLocator())
    plt.gca().yaxis.set_major_locator(NullLocator())
    timeStamp = datetime.datetime.now().strftime('%M%S%f')
    savepath = 'detectresult/' + timeStamp + '.png'
    plt.savefig('cctv/static/' + savepath, bbox_inches='tight', pad_inches=0.0)
    plt.close()
    return savepath


def drawPred(tmppath, indices, boxes, classIds, confidences):
    # Draw a bounding box
    img = cv2.imread(tmppath)
    for ind in indices:
        i = ind[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        cv2.rectangle(img, (left, top), (left+width, top+height), (0, 0, 255),thickness=2)

        label = '%.2f' % confidences[i]

        # Get the label for the class name and its confidence
        if classes:
            assert (classIds[i] < len(classes))
            label = '%s:%s' % (classes[classIds[i]], label)
        # Display the label at the top of the bounding box
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv2.putText(img, label, (left, top), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255),thickness=1)
    timeStamp = datetime.datetime.now().strftime('%M%S%f')
    savepath = 'detectresult/' + timeStamp + '.png'
    cv2.imwrite('cctv/static/' + savepath, img)
    return savepath


if __name__ == '__main__':

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WatchingYou.settings")
    import django

    django.setup()
    from cctv.models import Image, Camera

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--camera", required=True, help="id of the camera")
    opt = parser.parse_args()
    cameras = Camera.objects.filter(camera_id=opt.camera)
    camera = cameras[0]
    confThreshold = 0.4
    nmsThreshold = 0.4
    inpWidth = 416
    inpHeight = 416

    classesFile = "data/coco.names"
    classes = None
    with open(classesFile, 'rt') as f:
        classes = f.read().rstrip('\n').split('\n')

    modelConfiguration = "config/yolov3-tiny.cfg"
    modelWeights = "weights/yolov3-tiny.weights"

    net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    while True:
        prev_time = time.time()
        imgs = camera.image_set.filter(detection_type='None').order_by('-add_time')
        imgpath = "cctv/static/" + str(imgs[0].img)
        img = cv2.imread(imgpath)
        shape = img.shape
        img = cv2.resize(img, dsize=(int(480 * shape[1] / shape[0]), 480))
        tmppath = "cctv/static/detecttmp/temp.jpg"
        cv2.imwrite(tmppath, img)
        img = cv2.imread(tmppath)
        try:
            blob = cv2.dnn.blobFromImage(img, 1 / 255, (inpWidth, inpHeight), [0, 0, 0], 1, crop=False)
            net.setInput(blob)
            outs = net.forward(getOutputsNames(net))
            indices, boxes, classIds, confidences = postprocess(img, outs)
            savepath = drawPred(tmppath, indices, boxes, classIds, confidences)
            camera.image_set.create(img=savepath, detection_type='Easy')
            camera.image_set.filter(add_time__lte=timezone.now() - datetime.timedelta(seconds=2),
                                    detection_type='Easy').delete()
            current_time = time.time()
            inference_time = datetime.timedelta(seconds=current_time - prev_time)
            prev_time = current_time
            print('\t Inference Time: %s' % (inference_time))
        except:
            print('opencv detect failed')
            continue