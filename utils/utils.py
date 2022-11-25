######################################
# utils.py                           #
# part of VolumeTracker project      #
# Classes used to annotate images.   #
######################################

import numpy as np
import cv2, time, math, argparse


class coords:

     def __init__(self,imsrc,volumes,od,id):
         '''
         Class attributes.
         '''

         self.im = imsrc        # Image.
         self.volumes = volumes # Volumes to track.
         self.od = od           # Capillary OD in mm.
         self.id = id           # Capillary ID in mm.
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
         self.fontscale = 0.7


     def callback_fun(self, event, x, y, flags, params):
         '''
         Callback method responding to mouse events.
         '''

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


     def draw_pts(self):
         '''
         Method used to draw points and lines on image.
         '''

         if(len(self.pts)>0 and len(self.pts)<3):
             for i in range(len(self.pts)):
                 cv2.circle(self.im, tuple(self.pts[i]), 5, (0, 255, 0), -1)
             if self.closest is not None:
                 cv2.circle(self.im, tuple(self.closest), 20, (255, 255, 0), 1)
             if(len(self.pts) <= 2):
                 cv2.line(self.im, tuple(self.pts[-1]), tuple(self.current), (0, 255, 0), 1)

         if len(self.pts) == 2:
             for i in range(len(self.pts) - 1):
                 cv2.line(self.im, tuple(self.pts[i]), tuple(self.pts[i + 1]), (0, 255, 0), 1)

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
                 vpts = np.round([[-self.vitc1/self.vslp,0] , [(self.im.shape[0]-self.vitc1)/self.vslp,self.im.shape[0]]]).astype(int)
             else:  # If line linking pair of most vertical points perfectly vertical.
                 self.vslp = math.inf
                 vpts = [[arr[idx,0],0],[arr[idx,0],self.im.shape[0]]]
             cv2.line(self.im, tuple(vpts[0]), tuple(vpts[1]), (0, 0, 255), 1)  # Draw most vertical line.

             # Draw parallel (also vertical) line going through third point:
             l = [0,1,2,0]
             gi = list(set(l) - set(l[idx:(idx+2)]))[0]  # Find remaining point.
             if(v[0]!=0):  # If line not perfectly vertical.
                 self.vitc2 = arr[gi,1] - self.vslp*arr[gi,0]  # Intercept
                 vpts = np.round([[-self.vitc2/self.vslp,0] , [(self.im.shape[0]-self.vitc2)/self.vslp,self.im.shape[0]]]).astype(int)
             else:  # If line perfectly vertical.
                 vpts = [[arr[gi,0],0],[arr[gi,0],self.im.shape[0]]]
             cv2.line(self.im, tuple(vpts[0]), tuple(vpts[1]), (0, 0, 255), 1)  # Draw parallel vertical line.

         if len(self.pts) == 4:

             # Draw horizontal lines:
             # - horizontal line where user clicked to indicate position of meniscus.
             # - horizontal lines below to indicate volumes.

             if(self.vslp == math.inf):
                 self.hslp = 0
                 vpts = np.array([[0,self.pts[3][1]] , [self.im.shape[1],self.pts[3][1]]])
             else:
                 # x = -self.vslp * y + b for line perpendicular to vertical lines.
                 self.hslp = -self.vslp
                 self.hitc = self.pts[3][0] - self.hslp*self.pts[3][1]
                 vpts = np.round([[0,-self.hitc/self.hslp] , [self.im.shape[1],(self.im.shape[1]-self.hitc)/self.hslp]]).astype(int)
             cv2.line(self.im, tuple(vpts[0]), tuple(vpts[1]), (0, 0, 255), 1)

             # Intersection of horizontal and vertical lines (left = (x1,y1), right = (x2,y2)).
             if(self.vslp!=math.inf):
                 x1 = (self.vitc1 * self.hslp + self.hitc) / (1 - self.vslp*self.hslp)
                 y1 = self.vslp * x1 + self.vitc1
             else:
                 x1 = np.min(np.unique(np.array(self.pts)[:,0])).astype(int)
                 y1 = self.pts[3][1]
             self.pt_left = list(np.round([x1,y1]).astype(int))
             # cv2.circle(self.im, tuple(self.pt_left), 5, (0, 0, 255), -1)
             if(self.vslp!=math.inf):
                 x2 = (self.vitc2 * self.hslp + self.hitc) / (1 - self.vslp*self.hslp)
                 y2 = self.vslp * x2 + self.vitc2
             else:
                 x2 = np.max(np.unique(np.array(self.pts)[:,0])).astype(int)
                 y2 = self.pts[3][1]
             self.pt_right = list(np.round([x2,y2]).astype(int))
             # cv2.circle(self.im, tuple(self.pt_right), 5, (0, 0, 255), -1)
             cv2.putText(self.im, 'Start', tuple(list(np.round([x2+10,y2-10]).astype(int))),cv2.FONT_HERSHEY_SIMPLEX, self.fontscale, (0, 0, 255), lineType=cv2.LINE_AA)
             cv2.putText(self.im, 'OD = ' + str(self.od) + ' mm', tuple([10,22]),cv2.FONT_HERSHEY_SIMPLEX, self.fontscale, (0, 0, 0), lineType=cv2.LINE_AA)
             cv2.putText(self.im, 'ID = ' + str(self.id) + ' mm', tuple([10,42]),cv2.FONT_HERSHEY_SIMPLEX, self.fontscale, (0, 0, 0), lineType=cv2.LINE_AA)


             # Vertical lines showing inner diameter.
             # Compute width of capillary on image.
             wdth = math.sqrt((self.pt_right[0]-self.pt_left[0])**2 + (self.pt_right[1]-self.pt_left[1])**2)
             if(self.vslp == math.inf):
                 dx = 0.5*(self.od-self.id) * wdth / self.od
                 vpts1 = np.round(np.array([[self.pt_left[0] + dx,0] , [self.pt_left[0] + dx,self.im.shape[1]]])).astype(int)
                 dx = (0.5*(self.od-self.id)+self.id) * wdth / self.od
                 vpts2 = np.round(np.array([[self.pt_left[0] + dx,0] , [self.pt_left[0] + dx,self.im.shape[1]]])).astype(int)
             else:
                 dy = math.sqrt((0.5*(self.od-self.id) * wdth / self.od)**2 / (1 + self.hslp**2))
                 dx = self.hslp * dy
                 if(self.vslp>0):
                     x = self.pt_left[0] - dx
                     y = self.pt_left[1] - dy
                 if(self.vslp<0):
                     x = self.pt_left[0] + dx
                     y = self.pt_left[1] - dy
                 itc = y - self.vslp * x
                 vpts1 = np.round(np.array([[-itc/self.vslp,0] , [(self.im.shape[1]-itc)/self.vslp,self.im.shape[1]]])).astype(int)
                 dy = math.sqrt(((0.5*(self.od-self.id)+self.id) * wdth / self.od)**2 / (1 + self.hslp**2))
                 dx = self.hslp * dy
                 if(self.vslp>0):
                     x = self.pt_left[0] - dx
                     y = self.pt_left[1] - dy
                 if(self.vslp<0):
                     x = self.pt_left[0] + dx
                     y = self.pt_left[1] - dy
                 itc = y - self.vslp * x
                 vpts2 = np.round(np.array([[-itc/self.vslp,0] , [(self.im.shape[1]-itc)/self.vslp,self.im.shape[1]]])).astype(int)
             cv2.line(self.im, tuple(vpts1[0]), tuple(vpts1[1]), (0, 0, 255), 1)
             cv2.line(self.im, tuple(vpts2[0]), tuple(vpts2[1]), (0, 0, 255), 1)

             for i in self.volumes:
                 self.draw_vol_line(i,(255, 255, 0))


     def draw_vol_line(self,vol,col):
         '''
         Method used to draw volume lines.
         (vol in microL)
         '''

         # Compute width of capillary (= 1 mm in real life) on image.
         wdth = math.sqrt((self.pt_right[0]-self.pt_left[0])**2 + (self.pt_right[1]-self.pt_left[1])**2)
         # Height in mm for a volume of 100 microL in a cylinder of radius self.id (capillary ID):
         h = (vol/1000) / (math.pi * (self.id/2)**2)  # h in mm
         # Compute delta x and delta y
         if(self.vslp!=math.inf):
             dy = abs(self.vslp*math.sqrt((h*wdth / self.od)**2 / (1 + self.vslp**2)))
             dx = dy/self.vslp
         else:
             dy = h*wdth / self.od
             dx = 0
         # (x3,y3) is lower left point showing V = vol
         x3 = self.pt_left[0] + dx
         y3 = self.pt_left[1] + dy
         # cv2.circle(self.im, tuple(list(np.round([x3,y3]).astype(int))), 5, col, -1)
         # (x4,y4) is lower right point showing V = 100 microL
         x4 = self.pt_right[0] + dx
         y4 = self.pt_right[1] + dy
         # cv2.circle(self.im, tuple(list(np.round([x4,y4]).astype(int))), 5, col, -1)
         # Draw line
         cv2.line(self.im, tuple(list(np.round([x3,y3]).astype(int))), tuple(list(np.round([x4,y4]).astype(int))), col, 1)
         cv2.putText(self.im, str(vol) + ' uL', tuple(list(np.round([x4+10,y4]).astype(int))),cv2.FONT_HERSHEY_SIMPLEX, self.fontscale, col, lineType=cv2.LINE_AA)

def getargs():
    '''
    Deal with arguments.
    '''

    parser = argparse.ArgumentParser()

    #-s SCALE -v VOLUME
    parser.add_argument("-s", "--scale", help="Scale (% of original)", type=int)
    parser.add_argument("-v", "--volume", help="Volume(s) in microL", type=list_str)
    parser.add_argument("-od", "--outer_diameter", help="Outer diameter in mm", type=float)
    parser.add_argument("-id", "--inner_diameter", help="Inner diameter in mm", type=float)

    args = parser.parse_args()

    if args.scale == None:
        scale_percent = 200         # Default value for scale (in percent).
    else:
        scale_percent = args.scale
    if args.volume == None:
        volume = [20,40,60,80,100]  # Default values for volumes.
    else:
        volume = args.volume
    if args.outer_diameter == None:
        od = 1
    else:
        od = args.outer_diameter
    if args.inner_diameter == None:
        id = 0.5
    else:
        id = args.inner_diameter

    print('Using the following values:\nScale: {}%\nVolume(s): {} microL\nOD: {} mm\nID: {} mm'.format(scale_percent,volume,od,id))

    return scale_percent, volume, od, id


def list_str(values):
    '''
    Convert list of strings into list of integers.
    '''
    return [int(x) for x in (values.split(','))]

def resize_im(im, scale):
    '''
    Image resizing.
    Scale: scaling factor in percent of original.
    '''

    width = int(im.shape[1] * scale / 100)
    height = int(im.shape[0] * scale / 100)
    resized = cv2.resize(im, (width, height), interpolation = cv2.INTER_AREA)
    return resized
