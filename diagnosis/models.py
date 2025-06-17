from django.db import models
from django.db import transaction
from django.contrib.auth.hashers import make_password



class Aturangejala(models.Model):
    id_aturangejala = models.BigIntegerField(db_column='id_aturanGejala', primary_key=True)  # Field name made lowercase.
    id_detailaturan = models.BigIntegerField(db_column='id_detailAturan', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'aturangejala'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Detailaturan(models.Model):
    id_detailaturan = models.BigIntegerField(db_column='id_detailAturan', primary_key=True)  # Field name made lowercase.
    id_gejala = models.ForeignKey('Gejala', models.DO_NOTHING, db_column='id_gejala', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detailaturan'


class Diagnosis(models.Model):
    id_diagnosis = models.BigIntegerField(primary_key=True)
    nama_diagnosis = models.CharField(max_length=255, blank=True, null=True)
    deskripsi_diagnosis = models.TextField(blank=True, null=True)
    gambar_diagnosis = models.TextField(blank=True, null=True)
    solusi_diagnosis = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'diagnosis'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

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
    id = models.BigAutoField(primary_key=True)
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


class Gejala(models.Model):
    id_gejala = models.BigIntegerField(primary_key=True)
    nama_gejala = models.CharField(max_length=255, blank=True, null=True)
    kode_gejala = models.CharField(max_length=100, blank=True, null=True)
    pertanyaan_gejala = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gejala'


class Laporandiagnosis(models.Model):
    id_laporandiagnosis = models.BigAutoField(db_column='id_laporanDiagnosis', primary_key=True)
    id_pengguna = models.ForeignKey('Pengguna', models.DO_NOTHING, db_column='id_pengguna', blank=True, null=True)
    id_diagnosis = models.ForeignKey(Diagnosis, models.DO_NOTHING, db_column='id_diagnosis', blank=True, null=True)
    tanggal_diagnosis = models.DateField(blank=True, null=True)
    probabilitas = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'laporandiagnosis'


class Laporangejala(models.Model):
    id_laporangejala = models.BigIntegerField(db_column='id_laporanGejala', primary_key=True)
    id_laporandiagnosis = models.ForeignKey(Laporandiagnosis, models.DO_NOTHING, db_column='id_laporanDiagnosis', blank=True, null=True)
    id_gejala = models.ForeignKey(Gejala, models.DO_NOTHING, db_column='id_gejala', blank=True, null=True)
    value = models.BooleanField(default=False)  # ← perubahan di sini

    class Meta:
        managed = False
        db_table = 'laporangejala'


class Pengguna(models.Model):
    id_pengguna = models.BigAutoField(primary_key=True)
    nama_pengguna = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=5, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'pengguna'

    def save(self, *args, **kwargs):
        if not self.id_pengguna:
            with transaction.atomic():
                last = Pengguna.objects.select_for_update().order_by('-id_pengguna').first()
                self.id_pengguna = (last.id_pengguna + 1) if last else 1

        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)