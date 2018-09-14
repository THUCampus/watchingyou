import cv2
import os
import time
import datetime
from django.utils import timezone
import argparse
import torch
import numpy as np
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable
import PIL.Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import NullLocator
from models import *
from utils.utils import *
from utils.datasets import *


def detectionInit():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--camera", required=True, help="id of the camera")
    parser.add_argument('--image_folder', type=str, default='cctv/static/detecttmp', help='path to dataset')
    parser.add_argument('--config_path', type=str, default='config/yolov3.cfg', help='path to model config file')
    parser.add_argument('--weights_path', type=str, default='weights/yolov3.weights', help='path to weights file')
    parser.add_argument('--class_path', type=str, default='data/coco.names', help='path to class label file')
    parser.add_argument('--conf_thres', type=float, default=0.8, help='object confidence threshold')
    parser.add_argument('--nms_thres', type=float, default=0.4, help='iou thresshold for non-maximum suppression')
    parser.add_argument('--batch_size', type=int, default=1, help='size of the batches')
    parser.add_argument('--n_cpu', type=int, default=0, help='number of cpu threads to use during batch generation')
    parser.add_argument('--img_size', type=int, default=416, help='size of each image dimension')
    parser.add_argument('--use_cuda', type=bool, default=False, help='whether to use cuda if available')
    opt = parser.parse_args()

    cuda = torch.cuda.is_available() and opt.use_cuda

    os.makedirs('output', exist_ok=True)

    # Set up model
    model = Darknet(opt.config_path, img_size=opt.img_size)
    model.load_weights(opt.weights_path)

    model.eval() # Set in evaluation mode

    classes = load_classes(opt.class_path)
    dataloader = DataLoader(ImageFolder(opt.image_folder, img_size=opt.img_size),
                            batch_size=opt.batch_size, shuffle=False, num_workers=opt.n_cpu)
    return dataloader, model, opt, classes


def detect(dataloader, model, opt, classes):
    imgs = []           # Stores image paths
    img_detections = [] # Stores detections for each image index
    print ('\nPerforming object detection:')
    prev_time = time.time()
    trans = transforms.Compose([transforms.ToTensor()])
    for batch_i, (img_paths, input_imgs) in enumerate(dataloader):

        # Get detections
        with torch.no_grad():
            detections = model(input_imgs)
            detections = non_max_suppression(detections, 80, opt.conf_thres, opt.nms_thres)


        # Log progress
        current_time = time.time()
        inference_time = datetime.timedelta(seconds=current_time - prev_time)
        prev_time = current_time
        print ('\t+ Batch %d, Inference Time: %s' % (batch_i, inference_time))

        # Save image and detections
        imgs.extend(img_paths)
        img_detections.extend(detections)

    # Bounding-box colors
    cmap = plt.get_cmap('tab20b')
    colors = [cmap(i) for i in np.linspace(0, 1, 20)]

    print ('\nSaving images:')
    # Iterate through images and save plot of detections
    for img_i, (path, detections) in enumerate(zip(imgs, img_detections)):

        print ("(%d) Image: '%s'" % (img_i, path))

        # Create plot
        img = np.array(PIL.Image.open(path))
        plt.figure()
        fig, ax = plt.subplots(1)
        ax.imshow(img)

        # The amount of padding that was added
        pad_x = max(img.shape[0] - img.shape[1], 0) * (opt.img_size / max(img.shape))
        pad_y = max(img.shape[1] - img.shape[0], 0) * (opt.img_size / max(img.shape))
        # Image height and width after padding is removed
        unpad_h = opt.img_size - pad_y
        unpad_w = opt.img_size - pad_x

        # Draw bounding boxes and labels of detections
        if detections is not None:
            unique_labels = detections[:, -1].cpu().unique()
            n_cls_preds = len(unique_labels)
            bbox_colors = random.sample(colors, n_cls_preds)
            for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:

                print ('\t+ Label: %s, Conf: %.5f' % (classes[int(cls_pred)], cls_conf.item()))

                # Rescale coordinates to original dimensions
                box_h = ((y2 - y1) / unpad_h) * img.shape[0]
                box_w = ((x2 - x1) / unpad_w) * img.shape[1]
                y1 = ((y1 - pad_y // 2) / unpad_h) * img.shape[0]
                x1 = ((x1 - pad_x // 2) / unpad_w) * img.shape[1]

                color = bbox_colors[int(np.where(unique_labels == int(cls_pred))[0])]
                # Create a Rectangle patch
                bbox = patches.Rectangle((x1, y1), box_w, box_h, linewidth=2,
                                        edgecolor=color,
                                        facecolor='none')
                # Add the bbox to the plot
                ax.add_patch(bbox)
                # Add label
                plt.text(x1, y1, s=classes[int(cls_pred)], color='white', verticalalignment='top',
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


if __name__ == '__main__':

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WatchingYou.settings")
    import django

    django.setup()
    from cctv.models import Image, Camera

    dataloader, model, opt, classes = detectionInit()

    cameras = Camera.objects.filter(camera_id=opt.camera)
    camera = cameras[0]

    while True:
        imgs = camera.image_set.all().filter(detection_type='None').order_by('-add_time')
        imgpath = "cctv/static/" + str(imgs[0].img)
        img = cv2.imread(imgpath)
        try:
            shape = img.shape
            img = cv2.resize(img, dsize=(int(416 * shape[1] / shape[0]), 416))
            timeStamp = datetime.datetime.now().strftime('%M%S%f')
            cv2.imwrite("cctv/static/detecttmp/temp.jpg", img)
            resultpath = detect(dataloader, model, opt, classes)
            camera.image_set.create(img="tmp/" + timeStamp + ".jpg", detection_type='Easy')
            camera.image_set.filter(add_time__lte=timezone.now() - datetime.timedelta(seconds=2),
                                    detection_type='Easy').delete()
        except:
            print('detect failed')
            continue

