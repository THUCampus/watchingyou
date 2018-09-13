import cv2
import os
import datetime
from django.utils import timezone

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WatchingYou.settings")
    import django  # 导入Django

    django.setup()  # 执行
    from cctv.models import Image
    source = "rtsp://admin:admin@59.66.68.38:554/cam/realmonitor?channel=1&subtype=0"
    camLocal = cv2.VideoCapture(source)
    while True:
        rtn, frame = camLocal.read()
        timeStamp = datetime.datetime.now().strftime('%M%S%f')
        cv2.imwrite("cctv/static/tmp/" + timeStamp + ".jpg",frame)
        newFrame = Image(img="tmp/" + timeStamp + ".jpg")
        newFrame.save()
        Image.objects.filter(add_time__lte=timezone.now() - datetime.timedelta(seconds=2)).delete()





