# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CasesPerCountry(models.Model):
    country_code = models.ForeignKey('Countries', models.DO_NOTHING, db_column='country_code', blank=True, null=True)
    date_collected = models.TextField()  # This field type is a guess.
    source = models.ForeignKey('Sources', models.DO_NOTHING)
    death_numbers = models.IntegerField(blank=True, null=True)
    case_numbers = models.IntegerField(blank=True, null=True)
    recovery_numbers = models.IntegerField(blank=True, null=True)
    hospitalization_numbers = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Cases_Per_Country'


class CasesPerDistrict(models.Model):
    district_code = models.ForeignKey('Districts', models.DO_NOTHING, db_column='district_code', blank=True, null=True)
    date_collected = models.TextField()  # This field type is a guess.
    source = models.ForeignKey('Sources', models.DO_NOTHING)
    death_numbers = models.IntegerField(blank=True, null=True)
    case_numbers = models.IntegerField(blank=True, null=True)
    recovery_numbers = models.IntegerField(blank=True, null=True)
    hospitalization_numbers = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Cases_Per_District'


class CasesPerRegion(models.Model):
    region_code = models.ForeignKey('Regions', models.DO_NOTHING, db_column='region_code', blank=True, null=True)
    date_collected = models.TextField()  # This field type is a guess.
    source = models.ForeignKey('Sources', models.DO_NOTHING)
    death_numbers = models.IntegerField(blank=True, null=True)
    case_numbers = models.IntegerField(blank=True, null=True)
    recovery_numbers = models.IntegerField(blank=True, null=True)
    hospitalization_numbers = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Cases_Per_Region'


class Countries(models.Model):
    country_code = models.CharField(primary_key=True, blank=False, null=False, max_length=2)
    country_name = models.CharField(unique=True, max_length=128, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'Countries'


class Districts(models.Model):
    district_code = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=128)
    region_code = models.ForeignKey('Regions', models.DO_NOTHING, db_column='region_code')
    longitude = models.TextField(blank=True, null=True)  # This field type is a guess.
    latitude = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Districts'


class PopulationPerCountry(models.Model):
    country_code = models.OneToOneField(Countries, models.DO_NOTHING, db_column='country_code', primary_key=True, blank=False, null=False)
    population_amount = models.BigIntegerField()
    date_collected = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Population_Per_Country'


class PopulationPerDistrict(models.Model):
    district_code = models.OneToOneField(Districts, models.DO_NOTHING, db_column='district_code', primary_key=True, blank=False, null=False)
    population_amount = models.BigIntegerField()
    date_collected = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Population_Per_District'


class PopulationPerRegion(models.Model):
    region_code = models.OneToOneField('Regions', models.DO_NOTHING, db_column='region_code', primary_key=True, blank=False, null=False)
    population_amount = models.BigIntegerField()
    date_collected = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Population_Per_Region'


class Regions(models.Model):
    region_code = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=128)
    country_code = models.ForeignKey(Countries, models.DO_NOTHING, db_column='country_code')
    longitude = models.FloatField(blank=True, null=True)  # This field type is a guess.
    latitude = models.FloatField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Regions'


class Sources(models.Model):
    source_id = models.AutoField(primary_key=True, null=False, blank=False)
    source_information = models.CharField(unique=True, max_length=256)

    class Meta:
        managed = False
        db_table = 'Sources'


class VaccinationsPerCountry(models.Model):
    first_vaccination_rate = models.TextField()  # This field type is a guess.
    second_vaccination_rate = models.TextField()  # This field type is a guess.
    third_vaccination_rate = models.TextField()  # This field type is a guess.
    country_code = models.OneToOneField(Countries, models.DO_NOTHING, db_column='country_code', primary_key=True, blank=False, null=False)
    source = models.ForeignKey(Sources, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Vaccinations_Per_Country'


class VaccinationsPerDistrict(models.Model):
    first_vaccination_rate = models.TextField()  # This field type is a guess.
    second_vaccination_rate = models.TextField()  # This field type is a guess.
    third_vaccination_rate = models.TextField()  # This field type is a guess.
    district_code = models.OneToOneField(Districts, models.DO_NOTHING, db_column='district_code', primary_key=True, blank=False, null=False)
    source = models.ForeignKey(Sources, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Vaccinations_Per_District'


class VaccinationsPerRegion(models.Model):
    first_vaccination_rate = models.TextField()  # This field type is a guess.
    second_vaccination_rate = models.TextField()  # This field type is a guess.
    third_vaccination_rate = models.TextField()  # This field type is a guess.
    region_code = models.OneToOneField(Regions, models.DO_NOTHING, db_column='region_code', primary_key=True, blank=False, null=False)
    source = models.ForeignKey(Sources, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Vaccinations_Per_Region'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_flag = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
