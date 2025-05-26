from datetime import timedelta

import requests
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Country, Name, NameCountryProbability
from .serializers import CountrySerializer, NameSerializer


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Тільки для авторизованих"})


class NameCountryView(GenericAPIView):
    serializer_class = NameSerializer
    def get(self, request):
        name_param = request.query_params.get('name')
        if not name_param:
            return Response({"error": "Parameter 'name' is required."}, status=400)

        name_param = name_param.lower()
        thirty_minutes_ago = timezone.now() - timedelta(days=1)

        name_obj = Name.objects.filter(name=name_param).first()

        # Якщо є свіжа інформація — повертаємо з бази
        if name_obj and name_obj.last_accessed > thirty_minutes_ago:
            serializer = NameSerializer(name_obj)
            return Response(serializer.data)

        # Інакше — отримуємо нові дані з API
        response = requests.get(f'https://api.nationalize.io?name={name_param}')
        if response.status_code != 200:
            return Response({'error': 'Failed to fetch data from nationalize.io'}, status=500)

        data = response.json()

        # Створюємо або оновлюємо об'єкт Name
        if not name_obj:
            name_obj = Name.objects.create(name=name_param, count=data.get("count", 0))
        else:
            name_obj.count = data.get("count", 0)
            name_obj.last_accessed = timezone.now()
            name_obj.save()
            name_obj.countries.all().delete()  # Очищуємо попередні зв'язки

        for item in data.get('country', []):
            country_code = item.get('country_id')
            probability = item.get('probability')

            # Шукаємо або створюємо країну в БД
            country = Country.objects.filter(code=country_code).first()
            if not country:
                country_response = requests.get(f'https://restcountries.com/v3.1/alpha/{country_code}')
                if country_response.status_code == 200:
                    country_data = country_response.json()[0]
                    country = Country.objects.create(
                        code=country_code,
                        name=country_data.get('name', {}).get('common'),
                        official_name=country_data.get('name', {}).get('official'),
                        region=country_data.get('region'),
                        subregion=country_data.get('subregion'),
                        independent=country_data.get('independent'),
                        google_maps=country_data.get('maps', {}).get('googleMaps'),
                        open_street_maps=country_data.get('maps', {}).get('openStreetMaps'),
                        capital_name=country_data.get('capital', [None])[0],
                        capital_lat=country_data.get('capitalInfo', {}).get('latlng', [None, None])[0],
                        capital_lng=country_data.get('capitalInfo', {}).get('latlng', [None, None])[1],
                        flag_png=country_data.get('flags', {}).get('png'),
                        flag_svg=country_data.get('flags', {}).get('svg'),
                        flag_alt=country_data.get('flags', {}).get('alt'),
                        coat_of_arms_png=country_data.get('coatOfArms', {}).get('png'),
                        coat_of_arms_svg=country_data.get('coatOfArms', {}).get('svg'),
                        borders=country_data.get('borders')
                    )

            # Створюємо зв'язок ймовірності з країною
            if country:
                NameCountryProbability.objects.create(
                    name=name_obj,
                    country=country,
                    probability=probability
                )

        serializer = NameSerializer(name_obj)
        return Response(serializer.data)


class CountryDetailView(GenericAPIView):
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'Parameter "code" is required.'}, status=400)

        # Пробуємо знайти країну в БД
        country = Country.objects.filter(code__iexact=code).first()
        if country:
            serializer = CountrySerializer(country)
            return Response(serializer.data)

        # Якщо не знайдено — робимо запит до API
        response = requests.get(f'https://restcountries.com/v3.1/alpha/{code}')
        if response.status_code != 200:
            return Response({'error': 'Country not found via external API.'}, status=404)

        country_data = response.json()[0]

        # Створюємо країну
        country = Country.objects.create(
            code=code.upper(),
            name=country_data.get('name', {}).get('common'),
            official_name=country_data.get('name', {}).get('official'),
            region=country_data.get('region'),
            subregion=country_data.get('subregion'),
            independent=country_data.get('independent'),
            google_maps=country_data.get('maps', {}).get('googleMaps'),
            open_street_maps=country_data.get('maps', {}).get('openStreetMaps'),
            capital_name=country_data.get('capital', [None])[0],
            capital_lat=country_data.get('capitalInfo', {}).get('latlng', [None, None])[0],
            capital_lng=country_data.get('capitalInfo', {}).get('latlng', [None, None])[1],
            flag_png=country_data.get('flags', {}).get('png'),
            flag_svg=country_data.get('flags', {}).get('svg'),
            flag_alt=country_data.get('flags', {}).get('alt'),
            coat_of_arms_png=country_data.get('coatOfArms', {}).get('png'),
            coat_of_arms_svg=country_data.get('coatOfArms', {}).get('svg'),
            borders=country_data.get('borders')
        )

        serializer = CountrySerializer(country)
        return Response(serializer.data)
