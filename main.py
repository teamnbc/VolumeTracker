######################################
# main.py                            #
# Main code of VolumeTracker project #
######################################

import cv2, os, time
import utils

scale_percent, volumes, od, id = utils.getargs()    # Get arguments.
vid = cv2.VideoCapture(0)                   # define a video capture object (find number matching desired cam).
wname = 'Cam'                               # Window name.
global _init                                # To deal with first call of while loop.
_init = True                                # First iteration?
_savepic = False                            # To be able to save both raw and annotated image.
picdir = os.path.join(os.getcwd(), 'pics')  # Where images will be saved.
if(not os.path.exists(picdir)):
    os.mkdir(picdir)

while(True):

    ret, frame = vid.read()         # Capture frame from cam.
    if(scale_percent != 100):
        frame = utils.resize_im(frame, scale_percent)

    key = cv2.waitKey(1) & 0xFF     # Monitor key strokes.
    if((key == ord('b')) or (key == ord('e')) or (key == ord('s'))):
        sfx = '_' + time.strftime("%Y%m%d-%H%M%S")  # Keep track of date and time.
        if key == ord('b'):                         # Press 'b' for saving image with suffix 'beginning'.
            sfx = '_beginning' + sfx
        elif key == ord('e'):                       # Press 'e' for saving image with suffix 'end'.
            sfx = '_end' + sfx
        cv2.imwrite(picdir + '/im_raw' + sfx + '.png',frame)
        _savepic = True                             # To remember saving annotated image.

    if(_init==True):                              # First iteration.
        pos = utils.coords(frame,volumes,od,id)   # Class which will contain position of clicked points and useful callbacks/methods.
        cv2.namedWindow(wname)                    # Create window.
        cv2.setMouseCallback(wname, pos.callback_fun)  # Bind to appropriate callback.
        cv2.imshow(wname, pos.im)                 # Display first frame.
        _init = False
    else:                                         # Second and following iterations.
        pos.im = frame
        pos.draw_pts()                            # Add annotations to image.
        cv2.imshow(wname, pos.im)                 # Display annotated image.
        if(_savepic==True):
            cv2.imwrite(picdir + '/im_annotated' + sfx + '.png',pos.im)
            _savepic = False

    if key == ord('q'):                           # 'q' button set as the quitting key.
        cv2.destroyWindow(wname)
        break

    time.sleep(0.01)                              # Slow down loop to save CPU.

vid.release()  # Release cap object
cv2.destroyAllWindows()  # Destroy all the windows
