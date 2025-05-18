import json

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        fixture_path = f'{settings.FIXTURE_PATH}/ingredients.json'

        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                ingredients = json.load(f)

                Ingredient.objects.bulk_create(
                    [
                        Ingredient(
                            name=ingredient['name'],
                            measurement_unit=ingredient['measurement_unit']
                        ) for ingredient in ingredients
                    ], ignore_conflicts=True
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно загружено. \n'
                        f'Записей в файле: {len(ingredients)}'
                    )
                )
                self.stdout.write(self.style.SUCCESS('Команда завершена'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл не найден: {fixture_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Ошибка формата JSON'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
