# Generated manually to introduce Category model and migrate Product.category to a ForeignKey
import django.core.validators
from django.db import migrations, models
from django.utils.text import slugify


def forwards(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    Category = apps.get_model("products", "Category")

    for product in Product.objects.all():
        label = (getattr(product, "category_label", "") or "").strip()
        if not label:
            product.category_id = None
            product.save(update_fields=["category"])
            continue

        category, _ = Category.objects.get_or_create(
            name=label,
            defaults={"slug": slugify(label), "description": ""},
        )
        product.category = category
        product.save(update_fields=["category"])


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_product_category_product_content"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.RenameField(
            model_name="product",
            old_name="category",
            new_name="category_label",
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                blank=True,
                help_text="Archive category such as Lore, Rituals, or Chronicles",
                null=True,
                on_delete=models.SET_NULL,
                related_name="products",
                to="products.category",
            ),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="product",
            name="category_label",
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Price must be a positive value",
                max_digits=6,
                validators=[django.core.validators.MinValueValidator(0.01)],
            ),
        ),
    ]
