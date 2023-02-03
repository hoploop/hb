import logging
import datetime
import numpy as np

import os.path
from typing import List

import cv2

from hb.models.record import Event, Frame, Scenario

log = logging.getLogger(__name__)


class Video:

    def __init__(self, folder: str, scenario: Scenario):
        self.scenario: Scenario = scenario
        fpath = os.path.join(os.path.join(folder, scenario.name))
        filename = os.path.join(fpath, 'video.avi')
        vidcap = cv2.VideoCapture(filename)
        success, image = vidcap.read()
        success = True
        tot = 0
        previous = None
        while success:
            frame = scenario.frames[tot]
            # vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))  # added this line
            success, image = vidcap.read()
            print('Read a new frame [{0}]: {1}'.format(frame.number, frame.timestamp))
            for evt in self.events(tot):
                print("\t{0} {1}".format(evt.ts,evt.cls))
            # cv2.imwrite(pathOut + "\\frame%d.jpg" % count, image)  # save frame as JPEG file
            if previous is not None and image is not None:
                cmp_mse, cmp_ssim = self.compare(previous,image)
                print('Similarity with previous frame - MSE: {0} - SSIM: {1}'.format(cmp_mse,cmp_ssim))
            tot += 1
            previous = image
        print('Total frames: {0}'.format(tot))


    def mse(self,imageA, imageB):

        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageB.shape[1])

        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err

    def get_image_difference(self,image_1, image_2):
        first_image_hist = cv2.calcHist([image_1], [0], None, [256], [0, 256])
        second_image_hist = cv2.calcHist([image_2], [0], None, [256], [0, 256])

        img_hist_diff = cv2.compareHist(first_image_hist, second_image_hist, cv2.HISTCMP_BHATTACHARYYA)
        img_template_probability_match = \
        cv2.matchTemplate(first_image_hist, second_image_hist, cv2.TM_CCOEFF_NORMED)[0][0]
        img_template_diff = 1 - img_template_probability_match

        # taking only 10% of histogram diff, since it's less accurate than template method
        commutative_image_diff = (img_hist_diff / 10) + img_template_diff
        return commutative_image_diff

    def compare(self,imageA, imageB):
        imA = np.squeeze(imageA)
        imB = np.squeeze(imageB)
        # compute the mean squared error and structural similarity
        # index for the images
        m = self.mse(imageA, imageB)
        s = self.get_image_difference(imageA,imageB)

        return m, s
        # setup the figure
        #fig = plt.figure(title)
        #plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
        # show first image
        #ax = fig.add_subplot(1, 2, 1)
        #plt.imshow(imageA, cmap=plt.cm.gray)
        #plt.axis("off")
        # show the second image
        #ax = fig.add_subplot(1, 2, 2)
        #plt.imshow(imageB, cmap=plt.cm.gray)
        #plt.axis("off")
        # show the images
        #plt.show()

    def events(self, frame_number: int) -> List[Event]:
        ret = []
        previous_frame = None
        next_frame = None
        current_frame: Frame = self.scenario.frames[frame_number]
        if frame_number > 0:
            previous_frame = self.scenario.frames[frame_number - 1]
        if frame_number < len(self.scenario.frames) - 1:
            next_frame = self.scenario.frames[frame_number + 1]

        min_ts = current_frame.timestamp# - datetime.timedelta(milliseconds=1 / self.scenario.fps)
        max_ts = current_frame.timestamp + datetime.timedelta(milliseconds=1 / self.scenario.fps)
        if next_frame is not None:
            max_ts = next_frame.timestamp
        for evt in self.scenario.events:
            if min_ts <= evt.ts < max_ts:
                ret.append(evt)
        return ret
