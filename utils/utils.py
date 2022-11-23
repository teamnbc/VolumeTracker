######################################
# utils.py                           #
# part of Teslong project            #
# Classes used to annotate images.   #
######################################

import numpy as np
import cv2, time, math


class coords:

     def __init__(self):
         self.pts = []          # Where clicked positions will be stored.
         self.current = None    # Where current position (not yet clicked) is stored.
         self.vslp = None       # Vertical slope.
         self.vitc1 = None      # Vertical intercept 1 (left).
         self.vitc2 = None      # Vertical intercept 2 (right).
         self.hslp = None       # Horizontal slope.
         self.hitc = None       # Vertical intercept.
         self.pt_left = None    # Left point of upper limit.
         self.pt_right = None   # Right point of upper limit.
         self.closest = None
         self.closest_last = None

     def callback_fun(self, event, x, y, flags, params):
         # self.pts has a maximum of 4 points.
         if event == cv2.EVENT_LBUTTONDOWN and (len(self.pts) <= 4):  # Left button click.
             if(len(self.pts)==4):
                 del self.pts[-1]
             self.closest = [x, y]
             self.current = [x, y]
             self.pts.append([x, y])  # Append clicked position.
         if event == cv2.EVENT_MBUTTONDOWN and (len(self.pts) > 0):  # Middle (wheel) button click.
             if(len(self.pts)>1):
                 diff = np.sum(np.power(np.tile([x, y], [len(self.pts), 1]) - np.array(self.pts),2),1)
                 del self.pts[diff.argmin()]
                 diff = np.sum(np.power(np.tile([x, y], [len(self.pts), 1]) - np.array(self.pts), 2), 1)
                 self.closest = self.pts[diff.argmin()]
                 self.closest_last = self.closest
             elif(len(self.pts)==1):
                 self.pts = []
                 self.closest = None
                 self.closest_last = None
         if event == cv2.EVENT_MOUSEMOVE and (len(self.pts) > 0):
             self.current = [x, y]
             # Find reference point closest to latest mouse position
             diff = np.sum(np.power(np.tile([x, y], [len(self.pts), 1]) - np.array(self.pts), 2), 1)
             self.closest = self.pts[diff.argmin()]
             # Update coordinates of closest reference point
             if self.closest_last != self.closest:
                 self.closest_last = self.closest


     def draw_pts(self,im):
         '''
         Draw points and lines on image
         '''

         if(len(self.pts)>0 and len(self.pts)<3):
             for i in range(len(self.pts)):
                 cv2.circle(im, tuple(self.pts[i]), 5, (0, 255, 0), -1)
             if self.closest is not None:
                 cv2.circle(im, tuple(self.closest), 20, (255, 255, 0), 1)
             if(len(self.pts) <= 2):
                 cv2.line(im, tuple(self.pts[-1]), tuple(self.current), (0, 255, 0), 1)

         if len(self.pts) == 2:
             for i in range(len(self.pts) - 1):
                 cv2.line(im, tuple(self.pts[i]), tuple(self.pts[i + 1]), (0, 255, 0), 1)

         if len(self.pts) >= 3:

             # Draw most vertical line:
             tmp = self.pts.copy()  # Copy list of points.
             tmp.append(tmp[0])  # Add first point at end of list (to compute all possible diff).
             arr = np.array(tmp)  # Convert to np.
             idx = np.argmin(np.abs(np.diff(arr[:,0])))  # Index of most vertical pair of points (can take values 0,1,2)
             v = np.diff(np.transpose(arr[idx:(idx+2),:]))[:,0]  # Diff along x and y.
             if(v[0]!=0):  # If line linking pair of most vertical points not perfectly vertical.
                 # y = ax + b.
                 self.vslp = v[1]/v[0]  # Slope of vertical line.
                 self.vitc1 = arr[idx,1] - self.vslp*arr[idx,0]  # Intercept.
                 vpts = np.round([[-self.vitc1/self.vslp,0] , [(im.shape[0]-self.vitc1)/self.vslp,im.shape[0]]]).astype(int)
             else:  # If line linking pair of most vertical points perfectly vertical.
                 self.vslp = math.inf
                 vpts = [[arr[idx,0],0],[arr[idx,0],im.shape[0]]]
             cv2.line(im, tuple(vpts[0]), tuple(vpts[1]), (0, 0, 255), 1)  # Draw most vertical line.

             # Draw parallel line going through third point:
             l = [0,1,2,0]
             gi = list(set(l) - set(l[idx:(idx+2)]))[0]  # Find remaining point.
             if(v[0]!=0):  # If line not perfectly vertical.
                 self.vitc2 = arr[gi,1] - self.vslp*arr[gi,0]  # Intercept
                 vpts = np.round([[-self.vitc2/self.vslp,0] , [(im.shape[0]-self.vitc2)/self.vslp,im.shape[0]]]).astype(int)
             else:  # If line perfectly vertical.
                 vpts = [[arr[gi,0],0],[arr[gi,0],im.shape[0]]]
             cv2.line(im, tuple(vpts[0]), tuple(vpts[1]), (0, 0, 255), 1)  # Draw parallel vertical line.

         if len(self.pts) == 4:
             # Draw horizontal lines.
             if(self.vslp == math.inf):
                 self.hslp = 0
                 vpts = [[0,-self.pts[3][1]] , [im.shape[1],-self.pts[3][1]]]
             else:
                 # x = ay + b.
                 self.hslp = -self.vslp
                 self.hitc = self.pts[3][0] - self.hslp*self.pts[3][1]
                 vpts = np.round([[0,-self.hitc/self.hslp] , [im.shape[1],(im.shape[1]-self.hitc)/self.hslp]]).astype(int)
             cv2.line(im, tuple(vpts[0]), tuple(vpts[1]), (255, 0, 255), 1)

             # Intersection points (left = (x1,y1), right = (x2,y2)).
             if(self.vslp!=math.inf):
                 x1 = (self.vitc1 * self.hslp + self.hitc) / (1 - self.vslp*self.hslp)
                 y1 = self.vslp * x1 + self.vitc1
             else:
                 x1 = np.min(np.unique(np.array(self.pts)[:,0])).astype(int)
                 y1 = self.pts[3][1]
             self.pt_left = np.round([x1,y1]).astype(int)
             cv2.circle(im, tuple(self.pt_left), 5, (255, 0, 255), -1)
             if(self.vslp!=math.inf):
                 x2 = (self.vitc2 * self.hslp + self.hitc) / (1 - self.vslp*self.hslp)
                 y2 = self.vslp * x2 + self.vitc2
             else:
                 x2 = np.max(np.unique(np.array(self.pts)[:,0])).astype(int)
                 y2 = self.pts[3][1]
             self.pt_right = np.round([x2,y2]).astype(int)
             cv2.circle(im, tuple(self.pt_right), 5, (255, 0, 255), -1)

             im = self.draw_vol_line(im,100,(255, 0, 255))
             im = self.draw_vol_line(im,25,(127, 127, 255))
             im = self.draw_vol_line(im,50,(127, 127, 255))
             im = self.draw_vol_line(im,75,(127, 127, 255))
             im = self.draw_vol_line(im,125,(127, 127, 255))
             im = self.draw_vol_line(im,150,(127, 127, 255))

         return(im)


     def draw_vol_line(self,im,vol,col):
         '''
         Draw volume lines
         vol in microL
         '''

         id = 0.5  # in mm
         od = 1  # in mm
         # Compute width of capillary (= 1 mm in real life) on image.
         wdth = math.sqrt((self.pt_right[0]-self.pt_left[0])**2 + (self.pt_right[1]-self.pt_left[1])**2)
         # Height in mm for a volume of 100 microL in a cylinder of radius 0.5 mm (capillary ID):
         h = (vol/1000) / (math.pi * (id/2)**2)  # h in mm
         # Compute delta x and delta y
         dy = abs(self.vslp*math.sqrt((h*wdth)**2 / (1 + self.vslp**2)))
         dx = dy/self.vslp
         # (x3,y3) is lower left point showing V = vol
         x3 = self.pt_left[0] + dx
         y3 = self.pt_left[1] + dy
         cv2.circle(im, tuple(np.round([x3,y3]).astype(int)), 5, (255, 0, 255), -1)
         # (x4,y4) is lower right point showing V = 100 microL
         x4 = self.pt_right[0] + dx
         y4 = self.pt_right[1] + dy
         cv2.circle(im, tuple(np.round([x4,y4]).astype(int)), 5, (255, 0, 255), -1)
         # Draw line
         cv2.line(im, tuple(np.round([x3,y3]).astype(int)), tuple(np.round([x4,y4]).astype(int)), col, 1)
         cv2.putText(im, str(vol) + ' uL', tuple(np.round([x4,y4]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX, 1.0, col, lineType=cv2.LINE_AA)

         return(im)
