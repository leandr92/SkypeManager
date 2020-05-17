from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Contact(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contactId = models.CharField(default="", max_length=300, verbose_name="Контакт")

    def __str__(self):
        return self.contactId

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("У пользователя должен быть email")
        if not username:
            raise ValueError("У пользователя должно быть имя")

        user = self.model(
                email=self.normalize_email(email),
                username=username,
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
                email=self.normalize_email(email),
                password=password,
                username=username,
            )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class Account(AbstractBaseUser):

    email           = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username        = models.CharField(max_length=30, unique=True)
    date_joined     = models.DateTimeField(verbose_name="дата добавления", auto_now_add=True)
    last_login      = models.DateTimeField(verbose_name="последний логин", auto_now=True)
    is_admin        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    is_superuser    = models.BooleanField(default=False)
    skype_login     = models.CharField(max_length=200, default="", verbose_name="Логин Skype")
    skype_password  = models.CharField(max_length=200, default="", verbose_name="Пароль Skype")

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ['username',]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_Label):
        return True
