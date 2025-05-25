from rest_framework import serializers

from .models import Country, Name, NameCountryProbability


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'code',
            'name',
            'official_name',
            'region',
            'subregion',
            'independent',
            'google_maps',
            'open_street_maps',
            'capital_name',
            'capital_lat',
            'capital_lng',
            'flag_png',
            'flag_svg',
            'flag_alt',
            'coat_of_arms_png',
            'coat_of_arms_svg',
            'borders',
        ]


class NameCountryProbabilitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = NameCountryProbability
        fields = ['country', 'probability']


class NameSerializer(serializers.ModelSerializer):
    countries = NameCountryProbabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Name
        fields = ['id', 'name', 'count', 'last_accessed', 'countries']
