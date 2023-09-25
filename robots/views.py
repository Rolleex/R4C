import datetime
from django.http import JsonResponse
from django.shortcuts import render
import json
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from .models import Robot


@csrf_exempt
def add_robot(request):
    """ Создаем нового робота на основе json данных
    request : форма ввода данных {"model":"R2","version":"D2","created":"2022-12-31 23:59:59"}
    Получаем json данные
    Делаем валидацию с возможными ошибками
    в случае успеха проверяем на наличие данной модели
    если модель есть - создаем нового робота
    если модели нет, создаем нового робота но с другим ответом
    """
    if request.method == "POST":
        data = json.loads(request.body)
        model = data.get('model')
        version = data.get('version')
        created = data.get('created')

        if model and version and created:
            try:
                created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return JsonResponse({'message': 'Неверный формат даты'}, status=400)

            if not isinstance(model, str):
                return JsonResponse({'message': 'Модель должна быть строкой'})
            if len(model) > 2:
                return JsonResponse({'message': 'Длина модели не может превышать 2 симола'})
            elif ' ' in model:
                return JsonResponse({'message': 'Модель не должна соджержать пробелы'})

            if not isinstance(version, str):
                return JsonResponse({'message': 'Версия должна быть строкой'})
            if len(version) > 2:
                return JsonResponse({'message': 'Длина верисии не может превышать 2 символа'})
            elif ' ' in version:
                return JsonResponse({'message': 'Версия не должна содержать пробелов'})

            robot = Robot(model=model, version=version, created=created)
            robot.serial = f'{robot.model}-{robot.version}'
            if not Robot.objects.filter(model=robot.model, version=robot.version).exists():
                robot.save()
                return JsonResponse({'message': 'Новый дрон создан'}, status=201)
            else:
                robot.save()
                return JsonResponse({'message': "Двести тысяч единиц уже готовы, еще миллион на подходе"}, status=201)

        else:
            return JsonResponse({'message': 'Неккортектные данные'})
