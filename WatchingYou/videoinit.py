import cv2
import os
import datetime
from django.utils import timezone
import argparse


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--camera", required=True, help="id of the camera")
    args = vars(ap.parse_args())

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WatchingYou.settings")
    import django

    django.setup()
    from cctv.models import Image, Camera
    cameras = Camera.objects.filter(camera_id=args['camera'])
    source = 0
    if cameras and cameras[0].camera_id != 'local':
        source = cameras[0].camera_info
    #source = "rtsp://admin:admin@59.66.68.38:554/cam/realmonitor?channel=1&subtype=0"
    camLocal = cv2.VideoCapture(source)
    camera = cameras[0]

    while True:
        rtn, frame = camLocal.read()
        timeStamp = datetime.datetime.now().strftime('%M%S%f')
        cv2.imwrite("cctv/static/tmp/" + timeStamp + ".jpg", frame)
        camera.image_set.create(img="tmp/" + timeStamp + ".jpg", detection_type='None')
        camera.image_set.filter(add_time__lte=timezone.now() - datetime.timedelta(seconds=2), detection_type='None').delete()





