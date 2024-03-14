from io import BytesIO
from typing import Callable, Collection

from PIL import Image

from loader import thread_pool, proccess_pool, loop


def generate_image(function: Callable, args: Collection) -> Image:
    image = function(*args).convert(mode='RGB')
    return image


async def get_image(function: Callable, *args, proc_pool: bool = True, save_to: str | None = None) -> BytesIO:
    pool = proccess_pool if proc_pool else thread_pool
    image = await loop.run_in_executor(pool, generate_image, function, args)
    image = image.convert(mode='RGB')
    if save_to:
        image.save(save_to)
    else:
        bio = BytesIO()
        bio.name = 'image.jpeg'
        image.save(bio, 'JPEG')
        bio.seek(0)
        return bio


def copy_image(image):
    image_copy = Image.open(image)
    return image_copy
