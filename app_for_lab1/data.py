IMGS_DIR = '/home/tim/Desktop/bmstu/5_sem/rip/internet_applications_development/static/images'
from django.templatetags.static import static


CARDS_DATA = [
    {
        'label': 'ResNet-50 and CIFAR-10',
        'benchmark_performance': 2850,
        'dataset_size': 60000,
        # 'img': 'images/ResNet-50_CIFAR-10.png'
        'img': 'http://172.18.0.5:9000/forlab1images/ResNet-50_CIFAR-10.png'
    },
    {
        'label': 'ResNet-50 and ImageNet-1k',
        'benchmark_performance': 1050,
        'dataset_size': 1281167,
        'img': 'http://172.18.0.5:9000/forlab1images/ResNet-50%20and%20ImageNet-1k.png'
    },
    {
        'label': 'YOLO-v5s and COCO',
        'benchmark_performance': 220,
        'dataset_size': 330000,
        'img': 'http://172.18.0.5:9000/forlab1images/YOLOv5m%20and%20COCO.png'
    },
    {
        'label': 'YOLO-v8m and COCO',
        'benchmark_performance': 125,
        'dataset_size': 330000,
        'img': 'http://172.18.0.5:9000/forlab1images/YOLOv5s%20and%20COCO.png'
    },
    {
        'label': 'ViT-Base/16 and CIFAR-10',
        'benchmark_performance': 1950,
        'dataset_size': 60000,
        'img': 'http://172.18.0.5:9000/forlab1images/ViT-Base_16%20and%20CIFAR-10.png'
    },
    {
        'label': 'ViT-Base/16 and ImageNet-1k',
        'benchmark_performance': 850,
        'dataset_size': 1281167,
        'img': 'http://172.18.0.5:9000/forlab1images/ViT-Base_16%20and%20ImageNet-1k.png'
    },
    {
        'label': 'ViT-Base/16 and ImageNet-1k - 2',
        'benchmark_performance': 850,
        'dataset_size': 1281167,
        'img': 'http://172.18.0.5:9000/forlab1images/ViT-Base_16%20and%20ImageNet-1k.png'
    },
]


USERS_DATA = [
    {
        'id': 0,
        'first_name': 'Гость',
        'last_name': '',
        'chosen_models': [0, 4, 5, 6],
    },
    {
        'id': 1,
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'chosen_models': [1, 3],
    },
    {
        'id': 2,
        'first_name': 'Виктор',
        'last_name': 'Викторов',
        'chosen_models': [0, 3, 5],
    },
    {
        'id': 3,
        'first_name': 'Виктор',
        'last_name': 'Викторов',
        'chosen_models': [1, 2, 3],
    },
    {
        'id': 4,
        'first_name': 'Виктор',
        'last_name': 'Викторов',
        'chosen_models': [1, 2, 3],
    },
]

