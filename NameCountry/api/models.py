from django.db import models


class Country(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)
    official_name = models.TextField()
    region = models.CharField(max_length=100)
    subregion = models.CharField(max_length=100, blank=True, null=True)
    independent = models.BooleanField(default=False)
    google_maps = models.URLField(blank=True, null=True)
    open_street_maps = models.URLField(blank=True, null=True)
    capital_name = models.CharField(max_length=100, blank=True, null=True)
    capital_lat = models.FloatField(blank=True, null=True)
    capital_lng = models.FloatField(blank=True, null=True)
    flag_png = models.URLField(blank=True, null=True)
    flag_svg = models.URLField(blank=True, null=True)
    flag_alt = models.TextField(blank=True, null=True)
    coat_of_arms_png = models.URLField(blank=True, null=True)
    coat_of_arms_svg = models.URLField(blank=True, null=True)
    borders = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Name(models.Model):
    name = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class NameCountryProbability(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE, related_name='countries')
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    probability = models.FloatField()

    class Meta:
        unique_together = ('name', 'country')

    def __str__(self):
        return f"{self.name.name} - {self.country.code} ({self.probability})"



