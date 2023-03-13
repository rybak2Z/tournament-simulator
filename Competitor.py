import cv2
import numpy as np
import os


class Competitor:
    """
    
    """
    
    __files_to_delete = []    # If new files are made due to conversion from .jpg to .png
    
    def __init__(self, path: str, img_resolution: tuple[int, int]):
        """
        
        :param path:
        """
        
        # Set title
        image_file_name = path.split('/')[-1]
        self.title = image_file_name[:-4]
        
        self.path = path
        self.file_extension = image_file_name[-4:]
        self.img_resolution = img_resolution
        
        # If .jpg -> add filename to files to delete (it will later be converted to a .png by creating a new image)
        if image_file_name.endswith(('.jpg', '.jpeg')):
            self.__files_to_delete.append(self.title + '.png')  # .png because this .jpg gets converted to .png
    
    
    def get_img_data(self, resolution: tuple[int, int] = None):
        """
        
        :param img_resolution:
        :param path:
        :return:
        """
        
        # Get image
        img = cv2.imread(self.path)
        if self.path.endswith('.jpg'):    # If .jpg -> convert to .png (because PySimpleGUI-Images don't support .jpg)
            filename = self.title + '.png'
            cv2.imwrite(filename, img)
            img = cv2.imread(filename)
        
        # Resize & reshape to 1:1
        img = cv2.resize(img, self.img_resolution if resolution is None else resolution)
        img = self.__get_1to1_img(img)
        
        # Encode image
        img_bytes = cv2.imencode('.png', img)[1].tobytes()  # I do not know how this works
        
        return img_bytes
    
    
    @staticmethod
    def __get_1to1_img(image):
        """

        :param image:
        :return:
        """
        
        shape_tuple = image.shape
        height, width = shape_tuple[:2]
        if width == height:
            return image
        else:
            longer_edge = int(max(width, height))
            half_diff = int(0.5 * (longer_edge - min(width, height)))
            if half_diff == 0:
                half_diff = 1
        
            if longer_edge == width:
                filling = np.zeros((half_diff, width), np.uint8)
                filling = cv2.cvtColor(filling, cv2.COLOR_GRAY2BGR)
                image = np.concatenate((filling, image, filling))
            else:
                row_filling = np.zeros(half_diff, np.uint8)
                row_filling = cv2.cvtColor(row_filling, cv2.COLOR_GRAY2BGR)
                row_filling = np.array([bgr_double_list[0] for bgr_double_list in
                                        row_filling])  # Because row_filling is made out of a list of double lists
            
                new_image = []
                for row in image:
                    new_row = np.concatenate((row_filling, row, row_filling))
                    new_image.append(new_row)
            
                image = np.array(new_image)
        
            return image
    
    
    @classmethod
    def delete_files(cls):
        current_path = os.path.abspath(os.getcwd())
        for filename in cls.__files_to_delete:
            os.remove(os.path.join(current_path, filename))
            pass
