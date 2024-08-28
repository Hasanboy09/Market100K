from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db.models import CharField, ForeignKey, CASCADE, Model, DateTimeField, SlugField, ImageField, FloatField, \
    IntegerField, TextField, FileField, TextChoices
from django.utils.text import slugify
from django_resized import ResizedImageField


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        user = self.create_user(phone_number, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractUser):
    class Role(TextChoices):
        ADMIN = "admin", 'Admin'
        OPERATOR = "operator", 'Operator'
        MANAGER = "manager", 'Manager'
        DRIVER = "driver", 'Driver'
        USER = "user", 'User'

    username = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    role = CharField(max_length=50, choices=Role.choices, default=Role.USER)
    phone_number = CharField(max_length=12, unique=True)


class BaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModelSlug(Model):
    name = CharField(max_length=255)
    slug = SlugField(unique=True)

    class Meta:
        abstract = True  # o`zi table bo1lib yaratilmasligi kerak # noqa

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):  # noqa
        self.slug = slugify(self.name)
        while self.__class__.objects.filter(slug=self.slug).exists():
            self.slug += '-1'
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Category(BaseModel, BaseModelSlug):
    image = ImageField(upload_to='images/')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(BaseModel, BaseModelSlug):
    price = FloatField()
    category = ForeignKey('apps.Category', on_delete=CASCADE, to_field='slug', related_name='products')
    order_count = IntegerField(default=0)
    description = TextField()
    video = FileField(upload_to='videos', null=True,
                      validators=[
                          FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    store = ForeignKey('apps.Store', on_delete=CASCADE, related_name='products')
    payment = FloatField(default=25000)
    seller = CharField(max_length=40)
    count = IntegerField(default=0)

    def __str__(self):
        return self.name


class ProductImage(Model):
    image = ResizedImageField(size=[200, 200], quality=100, upload_to='products/')
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='images')


class Order(BaseModel):
    class StatusType(TextChoices):
        NEW = "new", 'New'
        READY = "ready", 'Ready'
        DELIVER = "deliver", 'Deliver'
        DELIVERED = "delivered", 'Delivered'
        CANT_PHONE = "cant_phone", 'Cant_phone'
        CANCELED = "canceled", 'Canceled'
        ARCHIVED = 'archived', 'Archived'

    class Region(TextChoices):
        ANDIJON = "andijon", "Andijon"
        BUXORO = "buxoro", "Buxoro"
        FARGONA = "fargona", "Farg'ona"
        JIZZAX = "jizzax", "Jizzax"
        XORAZM = "xorazm", "Xorazm"
        NAMANGAN = "namangan", "Namangan"
        NAVOIY = "navoiy", "Navoiy"
        QASHQADARYO = "qashqadaryo", "Qashqadaryo"
        QORAQALPOGISTON = "qoraqalpogiston", "Qoraqalpog'iston"
        SAMARQAND = "samarqand", "Samarqand"
        SIRDARYO = "sirdaryo", "Sirdaryo"
        SURXONDARYO = "surxondaryo", "Surxondaryo"
        TOSHKENTVILOYATI = "toshkentviloyati", "Toshkentviloyati"
        TOSHKENT = "toshkent", "Toshkent"

    user = ForeignKey('apps.User', CASCADE, related_name='orders')
    product = ForeignKey('apps.Product', CASCADE, related_name='orders')
    stream = ForeignKey('apps.Stream', CASCADE, related_name='orders', null=True)
    phone_number = CharField(max_length=25)
    full_name = CharField(max_length=255)
    region = CharField(max_length=30, choices=Region.choices)
    status = CharField(max_length=50, choices=StatusType.choices, default=StatusType.NEW)


class Store(BaseModel):
    owner = ForeignKey('apps.User', on_delete=CASCADE, related_name='stores')
    image = ImageField(upload_to='static/images/', null=True, blank=True)


class Comment(BaseModel):
    text = CharField(max_length=255, null=True, blank=True)
    user = ForeignKey('apps.User', on_delete=CASCADE)
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='comments')

    def __str__(self):
        return self.text


class Stream(BaseModel):
    name = CharField(max_length=255)
    discount = FloatField()
    count = IntegerField(default=0)
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='streams')
    owner = ForeignKey('apps.User', on_delete=CASCADE, related_name='streams')
