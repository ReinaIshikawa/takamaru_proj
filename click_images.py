import os
import numpy as np
import argparse
import cv2
import glob
from scipy.spatial.transform import Rotation as R

from read_write_model import read_model,qvec2rotmat

def concat_rotation_and_translation(rotation_mat,translation_mat):
    con_mat = np.zeros((3,4))
    con_mat[:,:3] = rotation_mat
    con_mat[:,3] = translation_mat 
    return con_mat


def create_intrinsic_mat(f, cx, cy):
    """
    @ f : floal length. If it is single focal lenth, f is a single float otherwise, a float tuple. 
    @ cx, cy: a principal point at pixel location 
    """
    if isinstance(f, (float, tuple)):
        fx, fy = f
    else:
        fx, fy = f, f
    intrinsic_mat = np.eye(3)
    intrinsic_mat[0,0] = fx
    intrinsic_mat[1,1] = fy
    intrinsic_mat[0,2] = cx
    intrinsic_mat[1,2] = cy
    return intrinsic_mat

def create_perspective_projection_mat(intrinsic_mat, extrinsic_mat):
    return np.dot(intrinsic_mat, extrinsic_mat)

def image_to_world_coord(P1,P2,s1,s2):
    """
    @ P1:perspective matirix of camera 1
    @ P2:perspective matirix of camera 2
    @ s1:a pixel of camera 1
    @ s2:a pixel of camera 2
    """
    u1 = s1[0]
    v1 = s1[1]
    u2 = s2[0]
    v2 = s2[1]
    P1_11, P1_12, P1_13, P1_14 = P1[0,0], P1[0,1], P1[0,2], P1[0,3]
    P1_21, P1_22, P1_23, P1_24 = P1[1,0], P1[1,1], P1[1,2], P1[1,3]
    P1_31, P1_32, P1_33, P1_34 = P1[2,0], P1[2,1], P1[2,2], P1[2,3]
    P2_11, P2_12, P2_13, P2_14 = P2[0,0], P2[0,1], P2[0,2], P2[0,3]
    P2_21, P2_22, P2_23, P2_24 = P2[1,0], P2[1,1], P2[1,2], P2[1,3]
    P2_31, P2_32, P2_33, P2_34 = P2[2,0], P2[2,1], P2[2,2], P2[2,3]
    A = np.array([[P1_31*u1-P1_11, P1_32*u1-P1_12, P1_33*u1-P1_13],
                  [P1_31*v1-P1_21, P1_32*v1-P1_22, P1_33*v1-P1_23],
                  [P2_31*u2-P2_11, P2_32*u2-P2_12, P2_33*u2-P2_13],
                  [P2_31*v2-P2_21, P2_32*v2-P2_22, P2_33*v2-P2_23]])

    B = np.array([[P1_14-P1_34*u1], [P1_24-P1_34*v1], [P2_14-P2_34*u2], [P2_24-P2_34*v2]])

    pseudo_inv_A = np.linalg.pinv(A)
    return np.dot(pseudo_inv_A,B)

def world_to_image_coord(P, W):
    """
    @ P: perspective matrix (3*4)
    @ W: world coordinate (3*1)
    return x : camera coordinate(4,1)
    """
    H = np.ones((4,1))
    H[:3] = W
    x = np.dot(P,H)
    x = x/x[2,0]
    return np.array([x[0,0], x[1,0]])

def calc_reprojection_error(P_list, W, x_list):
    """
    @ P_list: list of perspective matrix (4*3 ndarray)
    @ W: a world coordinate (3*1 ndarray)
    @ x_list: list of image coordinate (2, ndarray or list)
    """
    error_sum = 0
    for P, x in zip(P_list, x_list):
        x = np.array(x)
        _x = world_to_image_coord(P,W)
        print("x,_x:\n", x, _x)
        error_sum += np.sqrt(np.sum((_x - x)**2 )) 
    return error_sum

class ReadModel():
    def __init__(self, input_model):
        self.cameras, self.images, self.points3D = read_model(path=os.path.join(input_model,'dense','sparse'), ext=".bin")
        self.img_dir_pth = os.path.join(input_model, 'images')
        
    def get_id_list(self, clicked_images):
        """
        @ clicked_images: list of image names (length:2)
        """
        im_id_list = []
        for im_id in self.images.keys():
            if self.images[im_id].name in clicked_images:
                im_id_list.append(im_id)
        return im_id_list

    def get_rescaled_coord_from_img(self, im_id, im_x, im_y):
        cam_id = self.images[im_id].camera_id
        img_pth = self.images[im_id].camera_id
        img_pth = os.path.join(self.img_dir_pth, self.images[im_id].name)
        img = cv2.imread(img_pth)
        im_width, im_height = img.shape[1], img.shape[0]
        cam_width = self.cameras[cam_id].width
        cam_height = self.cameras[cam_id].height
        rescaled_x= im_x*cam_width/im_width
        rescaled_y= im_y*cam_height/im_height
        print("image name:{} im_x:{}, im_y:{} -> rescaled_x:{}, rescaled_y:{}".format(self.images[im_id].name, im_x, im_y, rescaled_x, rescaled_y))
        return rescaled_x, rescaled_y
        

    def calc_p_mat(self, im_id):
        im_data = self.images[im_id]
        rotmat = qvec2rotmat(im_data.qvec)
        transmat = im_data.tvec
        extrinsic_mat = concat_rotation_and_translation(rotation_mat=rotmat, translation_mat=transmat)
        camera_id = im_data.camera_id
        cam_data = self.cameras[camera_id]
        # print(cam_data.width, cam_data.height)
        if len(cam_data.params) == 4:
            fx, fy, cx, cy = cam_data.params
            intrinsic_mat = create_intrinsic_mat((fx,fy),cx,cy)
        else:
            f, cx, cy = cam_data.params
            intrinsic_mat = create_intrinsic_mat(f,cx,cy)
        P_mat = create_perspective_projection_mat(intrinsic_mat, extrinsic_mat)
        return P_mat


class ImageInterface():
    def __init__(self,img_dir_pth):  
        self.image_files = glob.glob(os.path.join(img_dir_pth,'*'))
        # print(image_files)
        self.image_list = []
        self.point_list = []
        self.idx = 0  
        self.img = None

    def onMouse(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.image_list) <2:
                self.image_list.append(self.image_files[self.idx].rsplit(os.sep, 1)[1])
                self.point_list.append([x,y])
                print(self.idx, x, y)


    def show_images(self):
        self.img = cv2.imread(self.image_files[self.idx])
        window_name = 'images'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.onMouse)
        while (True):
            if len(self.image_list)>=2:
                break
            cv2.imshow(window_name, self.img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            elif cv2.waitKey(1) & 0xFF == ord("e"):
                if self.idx < len(self.image_files)-1:
                    self.idx += 1
                    self.img = cv2.imread(self.image_files[self.idx])
                    print('changed to {}'.format(self.image_files[self.idx]))
            elif cv2.waitKey(1) & 0xFF == ord("w"):
                if self.idx > 0:
                    self.idx -= 1
                    self.img = cv2.imread(self.image_files[self.idx])
                    print('changed to {}'.format(self.image_files[self.idx]))
        cv2.destroyAllWindows()
        return self.image_list, self.point_list

def main():
    parser = argparse.ArgumentParser(description="Read and write COLMAP binary and text models")
    parser.add_argument("--input_model", help="path to input model folder")

    args = parser.parse_args()
    im_interface = ImageInterface(os.path.join(args.input_model, 'images'))
    clicked_images, clicked_points = im_interface.show_images()
    
    model = ReadModel(args.input_model)
    # clicked_images = ['IMG_2425.JPG','IMG_2426.JPG']
    # clicked_points = [[100,100],[200,200]]
    id_list = model.get_id_list(clicked_images)
    print("id_list:", id_list)
    p_mat_list = []
    for idx, (point, id) in enumerate(zip(clicked_points, id_list)):
        print(id)
        p_mat_list.append(model.calc_p_mat(id))
        x, y =  point
        x, y= model.get_rescaled_coord_from_img(id, x, y) 
        clicked_points[idx] = [x,y]
    world_coord = image_to_world_coord(p_mat_list[0], 
                                        p_mat_list[1], 
                                        clicked_points[0], 
                                        clicked_points[1])
    print("world_coord:\n", world_coord)
    reprojection_error = calc_reprojection_error(p_mat_list, world_coord, clicked_points)
    print("reprojection_error:", reprojection_error)
    



if __name__ == "__main__":
    main()