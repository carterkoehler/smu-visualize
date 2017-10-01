import cv2
import numpy as np
import os,glob


class Cam:
    def __init__(self,device,resolution):
        #Initialize camera <device> at <resolution>
        self.device = device
        self.w = resolution[0]
        self.h = resolution[1]
        self.camera = cv2.VideoCapture(device)
        self.camera.set(3,self.w)
        self.camera.set(4,self.h)

        self.canvas = np.zeros((self.h,int(self.h*(16.0/9.0)),3), np.uint8)

        self.t = 0

    def getFrame(self):
        return self.camera.read()[1]

    def calibImage(self):
        theFrame = self.camera.read()[1]
        cv2.imshow('Captured frame',theFrame)
        cv2.waitKey(0)
        cv2.imwrite('calibration%d.png'%self.device,theFrame)

        self.calibrate(1)

    def calibrate(self,show=False):
        if show:
            path = './calibration%d.png'%self.device
        else:
            path = './src/calibration%d.png'%self.device

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        w = 7
        h = 7
        board = np.zeros((w*h,3), np.float32)
        board[:,:2] = np.mgrid[0:h,0:w].T.reshape(-1,2)
        board = board.reshape(-1,1,3)

        if len(glob.glob(path)) == 0:
            print("calibration file %d does not exist!!!"%self.device)
            raise ValueError
        img = cv2.imread(path)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (h,w),None)

        if ret == True:
            objpoints = [board]

            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints = [corners2]

            # Draw and display the corners
            cv2.drawChessboardCorners(img, (h,w), corners2,ret)
            if show:
                cv2.imshow('img',img)
                cv2.waitKey(0)

            ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
        else:
            print('No chess board found')
            return -1
        return img

    def project(self,points):
        inp = np.array(points,dtype=np.float32)
        projected,_ = cv2.projectPoints(inp, self.rvecs[0], self.tvecs[0], self.mtx, self.dist)
        return [(i[0][0],i[0][1]) for i in projected]

    def rotateX(self,points,theta):
        rotation = np.matrix([[1,0,0],[0,np.cos(theta),np.sin(theta)],[0,-np.sin(theta),np.cos(theta)]])
        ret = []
        for p in points:
            ret.append(rotation*p.reshape([3,1]))
        return ret

    def rotateY(self,points,theta):
        rotation = np.matrix([[np.cos(theta),0,-np.sin(theta)],[0,1,0],[np.sin(theta),0,np.cos(theta)]])
        ret = []
        for p in points:
            ret.append(rotation*p.reshape([3,1]))
        return ret

    def rotateZ(self,points,theta):
        rotation = np.matrix([[np.cos(theta),np.sin(theta),0],[-np.sin(theta),np.cos(theta),0],[0,0,1]])
        ret = []
        for p in points:
            ret.append(rotation*p.reshape([3,1]))
        return ret


def main(cams):
    img = [0,0]
    img[0] = cams[0].getFrame()
    #img[1] = cams[1].getFrame()

    #Draw a cube
    x = 0
    y = 0
    z = 0
    for ii in range(1):
        vertices = [np.array([i,j,k]) for i in [x-1,x+1] for j in [y-1,y+1] for k in [z-1,z+1]]
        #vertices = cams[ii].rotateX(vertices,cams[ii].t)
        #vertices = cams[ii].rotateY(vertices,cams[ii].t)
        #vertices = cams[ii].rotateZ(vertices,cams[ii].t)
        for i in vertices:
            for j in vertices:
                aLine = cams[ii].project([i,j])
                cv2.line(img[ii],aLine[0],aLine[1],(255,0,0),1)
        #cams[ii].t += 0.1

    s = int(cams[0].h*(8.0/9.0))
    cams[0].canvas[:,:s] = img[0][:,:s]
    cams[0].canvas[:,s:] = img[0][:,:s]
    return cams[0].canvas

if __name__ == '__main__':
    #main()
    theCamera = Cam(2,(320,240))
    cameraTwo = Cam(0,(320,240))
    theCamera.calibImage()
    cameraTwo.calibImage()