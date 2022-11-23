import cv2, os, time
import utils

vid = cv2.VideoCapture(0)   # define a video capture object.
wname = 'Teslong cam'       # Window name.
pos = utils.coords()        # Class which will contain position of clicked points and useful callbacks/methods.
global _init                # To deal with first call of while loop.
_init = True
_savepic = False            # To be able to save both raw and annotated image.

while(True):

    key = cv2.waitKey(1) & 0xFF     # Monitor key strokes.
    if(_init==True):
        key_copy = key              # To detect key strokes.

    ret, frame = vid.read()         # Capture frame from cam.

    if(key != key_copy):
        timestr = '_' + time.strftime("%Y%m%d-%H%M%S")  # Keep track of date and time.
        if key == ord('b'):                       # Press 'b' for saving image at beginning of injection.
            sff = '_beginning' + timestr
        elif key == ord('e'):                     # Press 'e' for saving image at end of injection.
            sff = '_end' + timestr
        else:                                     # All other keys will save image without suffix.
            sff = timestr
        cv2.imwrite(os.getcwd() + '/im_raw' + sff + '.png',frame)
        _savepic = True                           # To remember saving annotated image.

    if(_init==True):                              # First iteration.
        cv2.namedWindow(wname)                    # Create window.
        cv2.setMouseCallback(wname, pos.callback_fun)  # Bind to appropriate callback.
        cv2.imshow(wname, frame)                  # Display first frame.
        _init = False
    else:                                         # Second and following iterations.
        im = pos.draw_pts(frame)                  # Add annotations to image.
        cv2.imshow(wname, im)                     # Display annotated image.
        if(_savepic==True):
            cv2.imwrite(os.getcwd() + '/im_annotated' + sff + '.png',frame)
            _savepic = False

    # the 'q' button is set as the quitting button.
    if key == ord('q'):
        cv2.destroyWindow(wname)
        break

vid.release()  # Release cap object
cv2.destroyAllWindows()  # Destroy all the windows

# import numpy as np
# pts = [[151, 64], [151, 379], [523, 370]]
# np.min(np.unique(np.array(pts)[:,0]))
# x1 = np.min(np.unique(np.array(pts)[:,0])).astype(int)
# y1 = pts[2][1]
# np.round([x1,y1]).astype(int)
# np.min(np.unique(np.array(pts)[:,0])).astype(int)

# im = cv2.imread('/users/nbc/gdugue/Nextcloud_IBENS/PROJECTS/git/Teslong/pic.jpg')
#
# pts.append(pts[0])
# arr = np.array(pts)
# idx = np.argmin(np.abs(np.diff(arr[:,0])))  # Index of most vertical pair of points (can take values 0,1,2)
# v = np.diff(np.transpose(arr[idx:(idx+2),:]))[:,0]  # Diff along x and y.
# if(v[0]!=0):
#
# slp = v[1]/v[0]  # Slope
# itc = arr[1,1] - slp*arr[1,0]  # Intercept
# vpts = np.round([[-itc/slp,0] , [(im.shape[0]-itc)/slp,im.shape[0]]]).astype(int)
# cv2.line(im, tuple(vpts[0]), tuple(vpts[1]), (0, 0, 255), 1)
# while 1:
#     cv2.imshow('bla',im)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         cv2.destroyWindow(wname)
#         break
#
# l=[0,1,2,0]
# list(set(l) - set(l[idx:(idx+2)]))[0]
