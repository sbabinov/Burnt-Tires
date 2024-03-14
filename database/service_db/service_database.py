from __future__ import annotations

import os
import copy
import json
from typing import Any, Callable, Dict, List

from PIL import Image


class Field:
    def __init__(self, value: Any) -> None:
        self.value = value


class ServiceDataBase:
    __database_path = './'
    __is_created = False
    __all_views = None
    __image_code = '#@^_^@#|'
    instance = None

    # fields
    message_id = Field(None)
    menu_views = Field([])
    collection_index = Field(0)
    brands = Field(None)
    selected_brand = Field(None)
    brand_collection_page_index = Field(0)
    brand_collection_brand_index = Field(0)
    selected_car = Field(None)
    car_collection_page_index = Field(0)
    car_collection_car_index = Field(0)
    car_collection_page = Field(None)

    def __new__(cls, path: str = None):
        if not cls.__is_created:
            cls.__is_created = True
            cls.instance = super(ServiceDataBase, cls).__new__(cls)
            if path is not None:
                cls.instance.__database_path = path
        return cls.instance

    def __get_user_path(self, user_id: int) -> str:
        return os.path.join(self.__database_path, str(user_id))

    def __get_last_image_id(self, user_id) -> int:
        path = os.path.join(self.__get_user_path(user_id), 'images')
        return max([0] + [int(f.split('.')[0]) for f in os.listdir(path)])

    def __commit(self, user_id: int, data: Dict) -> None:
        path = self.__get_user_path(user_id)
        if not os.path.exists(path):
            os.mkdir(path)
            os.mkdir(os.path.join(path, 'images'))
        path = os.path.join(self.__get_user_path(user_id), 'data.json')
        with open(path, 'w') as sdb:
            json.dump(data, sdb)

    def __save_image(self, user_id: int, image: Image.Image) -> int:
        name = image.__getattribute__('name')
        path = os.path.join(self.__get_user_path(user_id),
                            'images', f'{name}.jpg')
        image.convert(mode='RGB').save(path)
        return name

    def __get_image(self, user_id: int, image_name: str) -> Image.Image:
        path = os.path.join(self.__get_user_path(user_id), 'images', f'{image_name}.jpg')
        return Image.open(path)

    def update_views(self, views: Dict) -> None:
        self.__all_views = copy.deepcopy(views)

    @staticmethod
    def get_default_fields() -> Dict:
        fields = dict()
        for attr in ServiceDataBase.__dict__:
            if isinstance(ServiceDataBase.__dict__[attr], Field):
                fields[attr] = ServiceDataBase.__dict__[attr].value
        return fields

    def load_data(self, user_id: int) -> Dict:
        path = os.path.join(self.__get_user_path(user_id), 'data.json')
        try:
            with open(path, 'r') as sdb:
                data = json.load(sdb)
        except FileNotFoundError:
            data = ServiceDataBase.get_default_fields()
            self.__commit(user_id, data)
        return data

    def get(self, user_id: int, *attributes) -> Any | List[Any]:
        values = []
        data = self.load_data(user_id)
        for attr in data:
            if attr in attributes:
                if isinstance(data[attr], str) and \
                        data[attr].startswith(self.__image_code):
                    im_name = data[attr].split('|')[1]
                    image = self.__get_image(user_id, im_name)
                    data[attr] = image
                if isinstance(data[attr], (list, tuple)):
                    for i in range(len(data[attr])):
                        el = data[attr][i]
                        if isinstance(el, str) and el.startswith(self.__image_code):
                            im_name = el.split('|')[1]
                            image = self.__get_image(user_id, im_name)
                            data[attr][i] = image
                values.append(data[attr])
        if len(values) == 1:
            values = values[0]
        return values

    def set(self, user_id: int, new_data: dict) -> None:
        data = self.load_data(user_id)
        for attribute in new_data:
            if isinstance(new_data[attribute], Image.Image):
                im_name = self.__save_image(user_id, new_data[attribute])
                new_data[attribute] = self.__image_code + str(im_name)
            if isinstance(new_data[attribute], (list, tuple)):
                row = new_data[attribute]
                for i in range(len(row)):
                    if isinstance(row[i], Image.Image):
                        im_name = self.__save_image(user_id, row[i])
                        new_data[attribute][i] = self.__image_code + str(im_name)
            data[attribute] = new_data[attribute]
        self.__commit(user_id, data)

    def add_menu_view(self, user_id: int, view: Callable, clear: bool = False) -> None:
        data = self.load_data(user_id)
        if clear:
            data['menu_views'] = []
        data['menu_views'].append(view.__name__)
        self.__commit(user_id, data)

    def remove_menu_view(self, user_id: int) -> Callable | None:
        data = self.load_data(user_id)
        data['menu_views'].pop(-1)
        self.__commit(user_id, data)
        if data['menu_views']:
            view_name = data['menu_views'][-1]
            return self.__all_views[view_name]
        return None
