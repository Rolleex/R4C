import datetime
import io
from openpyxl import Workbook
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Robot
from orders.models import Order


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
                check_for_available(robot.serial)  # Вызываем функцию для проверки списка ожидания
                return JsonResponse({'message': 'Новый дрон создан'}, status=201)
            else:
                robot.save()
                return JsonResponse({'message': "Двести тысяч единиц уже готовы, еще миллион на подходе"}, status=201)

        else:
            return JsonResponse({'message': 'Неккортектные данные'})


def make_report():
    """
    Функция записи данных из бд в Ексель таблицу
    Созадем файл, собираем уникальные модели
    Задаем настройки для последующей фильтрации по времени
    перебираем каждую модель, создавая для неё отдбельный лист
    и получаем версию робота и количество в бд
    убираем лишний лист и передаем книгу дальше
    """
    wb = Workbook()
    queryset = Robot.objects.values('model').distinct()
    current_day = datetime.datetime.now()
    start_of_week = current_day - datetime.timedelta(weeks=1)

    for item in queryset:
        model = item['model']
        ws = wb.create_sheet(model)
        headers = ['Модель', 'Версия', 'Количество за неделю']
        ws.append(headers)
        version = Robot.objects.filter(model=model, created__range=[start_of_week, current_day]).values(
            'version').annotate(total_count=Count('version')).distinct()

        for ver in version:
            row = [model, ver['version'], ver['total_count']]
            ws.append(row)
    wb.remove(wb['Sheet'])
    return wb


def report_of_week(request):
    """ Вызываем функцию make_report
        создаем байтовый обьект
        Сохраняем книгу в этот обект
        помещаем его в начало
        передаем файл с заголовками
     """
    wb = make_report()
    report = io.BytesIO()
    wb.save(report)
    report.seek(0)
    response = HttpResponse(report, headers={
        'Content-Type': 'application/vnd.ms-exel',
        'Content-Disposition': 'attachment; filename="report.xlsx"'
    })

    return response


def check_for_available(serial):
    """
    Проверяем на наличие заказов для новых роботов
    Для каждого заказа отправляем уведомление
    """
    queryset = Order.objects.filter(robot_serial=serial)
    for i in queryset:
        model_and_version = Robot.objects.filter(serial=i.robot_serial).first()
        send_email_to_customer(i.customer.email, model_and_version.model, model_and_version.version)


def send_email_to_customer(email, model, version):
    """
    Принимаем данные заказа и отправляем письмо
    """
    subject = 'Робот доступепен к покупке'
    message = f'Добрый день!\nНедавно вы интересовались нашим роботом модели {model}, версии {version}.\nЭтот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами'
    send_mail(subject, message, 'example@gmail.com', [email])
