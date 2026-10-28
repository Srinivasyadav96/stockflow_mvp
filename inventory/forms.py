
from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Organization, OrganizationSettings, Product

User = get_user_model()


class RegisterForm(forms.Form):
    email = forms.EmailField()
    organization_name = forms.CharField(max_length=150)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")

        if password1:
            from django.contrib.auth.password_validation import (
                validate_password,
            )

            try:
                validate_password(password1)
            except forms.ValidationError as error:
                self.add_error("password1", error)

        return cleaned_data

    @transaction.atomic
    def save(self):
        email = self.cleaned_data["email"]

        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password1"],
        )

        organization = Organization.objects.create(
            user=user,
            name=self.cleaned_data["organization_name"].strip(),
        )

        OrganizationSettings.objects.create(
            organization=organization,
            default_low_stock_threshold=5,
        )

        return user




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "description",
            "quantity",
            "cost_price",
            "selling_price",
            "low_stock_threshold",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter product name",
            }),
            "sku": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter unique SKU",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "cost_price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "low_stock_threshold": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "placeholder": "Uses organization default if empty",
            }),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization

    def clean_sku(self):
        sku = self.cleaned_data["sku"].strip()

        if self.organization is None:
            raise forms.ValidationError("Organization is required.")

        duplicate = Product.objects.filter(
            organization=self.organization,
            sku__iexact=sku,
        )

        if self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)

        if duplicate.exists():
            raise forms.ValidationError(
                "This SKU already exists in your organization."
            )

        return sku

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity < 0:
            raise forms.ValidationError(
                "Quantity cannot be negative."
            )

        return quantity

    def clean_cost_price(self):
        price = self.cleaned_data.get("cost_price")

        if price is not None and price < 0:
            raise forms.ValidationError(
                "Cost price cannot be negative."
            )

        return price

    def clean_selling_price(self):
        price = self.cleaned_data.get("selling_price")

        if price is not None and price < 0:
            raise forms.ValidationError(
                "Selling price cannot be negative."
            )

        return price

    def clean_low_stock_threshold(self):
        threshold = self.cleaned_data.get("low_stock_threshold")

        if threshold is not None and threshold < 0:
            raise forms.ValidationError(
                "Low-stock threshold cannot be negative."
            )

        return threshold
