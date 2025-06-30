from uuid import uuid4 as UUID4
import os
from django.db import models
from django.utils.timezone import now as djnow
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.sessions.models import Session
import pytz
from django.conf import settings
from django.utils.translation import gettext_lazy as _

TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', 'English'),
    ('vi', 'Vietnam'),
)


class Account(AbstractUser):
    uuid = models.UUIDField(default=UUID4,
                            primary_key=True,
                            max_length=64,
                            unique=True,
                            # null=True,
                            editable=True)
    telephone = models.CharField(max_length=15,
                                 blank=True,
                                 null=True)
    manager = models.ForeignKey('self', on_delete=models.SET_DEFAULT,
                                default=None,
                                null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True)
    updated_at = models.DateTimeField(default=djnow, editable=False)
    created_at = models.DateTimeField(default=djnow, editable=False)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username +  '-' + str(self.uuid)

    def get_total(self):
        account = Account.objects.all().count()
        return account

class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    )
    uuid = models.UUIDField(
        default=UUID4,
        max_length=64,
        editable=True,
        unique=True,
        primary_key=True
    )
    name = models.CharField(max_length=200,
                            editable=True,
                            default="",
                            null=False)
    first_name = models.CharField(max_length=200,
                                  editable=True,
                                  default="",
                                  null=False)
    last_name = models.CharField(max_length=200,
                                 editable=True,
                                 default="",
                                 null=False)
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatar-upload/%Y/%m/%d/', blank=True, null=True, default='default/default-avatar.jpg')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birthday = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10,
                                null=False,
                                choices=LANGUAGES,
                                default=LANGUAGE_CODE)
    timezone = models.CharField(max_length=255,
                                null=False,
                                choices=TIMEZONES,
                                default=settings.TIME_ZONE)
    updated_at = models.DateTimeField(default=djnow)
    created_at = models.DateTimeField(default=djnow, editable=False)

    def __str__(self):
        return f"Hồ sơ của {self.account.username}"

    def get_full_name(self):
        fullname = f"{self.first_name} {self.last_name}"
        if fullname != "":
            return f"{self.first_name} {self.last_name}"
        return None