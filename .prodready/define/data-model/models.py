"""
persocart data model (Django ORM + django-mptt).

Schema definition for the Define phase. Mirrors entities.md. Field details
(validators, admin wiring) are finalized in the Design/Implement phases.
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# --- Authentication -------------------------------------------------------

class OperatorManager(BaseUserManager):
    """Manager for the email-based custom user model."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Operators must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Argon2 via settings.PASSWORD_HASHERS
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Operator(AbstractBaseUser, PermissionsMixin):
    """Custom user keyed on email instead of username."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = OperatorManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# --- Catalog --------------------------------------------------------------

class Category(MPTTModel):
    """Arbitrary-depth category tree (Modified Preorder Tree Traversal)."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE,
        null=True, blank=True, related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


# --- Per-category custom filtering (core value) ---------------------------

class CategoryFilter(models.Model):
    """A filter definition attached to a category, e.g. 'Heat level'."""

    class FilterType(models.TextChoices):
        CHOICE = "choice", "Single choice"
        MULTICHOICE = "multichoice", "Multiple choice"
        NUMBER = "number", "Number"
        BOOLEAN = "boolean", "Boolean"

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="filters",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    type = models.CharField(max_length=12, choices=FilterType.choices)
    unit = models.CharField(max_length=20, blank=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"], name="uniq_filter_slug_per_category",
            ),
        ]

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class CategoryFilterOption(models.Model):
    """Allowed value for a choice / multichoice filter, e.g. 'Hot'."""

    filter = models.ForeignKey(
        CategoryFilter, on_delete=models.CASCADE, related_name="options",
    )
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.label


class ProductFilterValue(models.Model):
    """A product's value for one of its category's filters.

    Exactly one typed column is populated based on the filter's type.
    Multichoice values are stored as multiple rows (one option each).
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="filter_values",
    )
    filter = models.ForeignKey(
        CategoryFilter, on_delete=models.CASCADE, related_name="product_values",
    )
    option = models.ForeignKey(
        CategoryFilterOption, on_delete=models.CASCADE,
        null=True, blank=True, related_name="product_values",
    )
    value_number = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True,
    )
    value_boolean = models.BooleanField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["product", "filter"]),
            models.Index(fields=["filter", "option"]),
            models.Index(fields=["filter", "value_number"]),
        ]

    def __str__(self):
        return f"{self.product.name} :: {self.filter.name}"
