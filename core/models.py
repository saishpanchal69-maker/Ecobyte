from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('USER', 'User'),
        ('RECYCLER', 'Recycler'),
        ('AGENT', 'Delivery Agent'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    is_recycler = models.BooleanField(default=False) 
    is_agent = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Recycler(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    location = models.TextField()
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return self.name

class EwasteRequest(models.Model):

    ITEM_CHOICES = (
        ('mobile', 'Mobile'),
        ('battery', 'Battery'),
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('headphone', 'Headphone'),
        ('earphone', 'Earphone'),
        ('charger', 'Charger'),
        ('smartwatch', 'Smartwatch'),
        ('camera', 'Camera'),
        ('printer', 'Printer'),
        ('monitor', 'Monitor'),
        ('router', 'Router'),
    )

    CONDITION_CHOICES = (
        ('working', 'Working'),
        ('dead', 'Dead'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending Admin Review'),
        ('VERIFIED', 'Verified by Admin'),
        ('SCHEDULED', 'Pickup Scheduled'),
        ('PICKED', 'Picked Up'),
        ('PAID', 'Payment Completed'),
        ('REJECTED', 'Rejected'),
    )

    assigned_agent = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="assigned_jobs"
)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=20, choices=ITEM_CHOICES)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)

    device_details = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    estimated_amount = models.IntegerField(default=0)
    final_amount = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_price(self):
        PRICE_TABLE = {
            'mobile': {'working': 800, 'dead': 150},
            'battery': {'working': 500, 'dead': 70},
            'laptop': {'working': 3000, 'dead': 700},
            'desktop': {'working': 2000, 'dead': 300},
            'tablet': {'working': 1000, 'dead': 250},
            'keyboard': {'working': 200, 'dead': 50},
            'mouse': {'working': 150, 'dead': 30},
            'headphone': {'working': 300, 'dead': 70},
            'earphone': {'working': 250, 'dead': 60},
            'charger': {'working': 400, 'dead': 80},
            'smartwatch': {'working': 1200, 'dead': 300},
            'camera': {'working': 1600, 'dead': 500},
            'printer': {'working': 1800, 'dead': 400},
            'monitor': {'working': 2100, 'dead': 500},
            'router': {'working': 900, 'dead': 200},
        }

        unit_price = PRICE_TABLE.get(self.item_name, {}).get(self.condition, 0)
        return unit_price * self.quantity
    
    @staticmethod
    def get_price_table():
        return {
            'mobile': {'working': 800, 'dead': 150},
            'battery': {'working': 500, 'dead': 70},
            'laptop': {'working': 3000, 'dead': 700},
            'desktop': {'working': 2000, 'dead': 300},
            'tablet': {'working': 1000, 'dead': 250},
            'keyboard': {'working': 200, 'dead': 50},
            'mouse': {'working': 150, 'dead': 30},
            'headphone': {'working': 300, 'dead': 70},
            'earphone': {'working': 250, 'dead': 60},
            'charger': {'working': 400, 'dead': 80},
            'smartwatch': {'working': 1200, 'dead': 300},
            'camera': {'working': 1600, 'dead': 500},
            'printer': {'working': 1800, 'dead': 400},
            'monitor': {'working': 2100, 'dead': 500},
            'router': {'working': 900, 'dead': 200},
        }

    def save(self, *args, **kwargs):
        try:
             self.estimated_amount = self.calculate_price()
        except Exception:
           self.estimated_amount = 0
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Request #{self.id} | {self.item_name} | {self.user.username}"

class Payment(models.Model):
    request = models.ForeignKey(EwasteRequest, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, default="Completed")
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.amount)

class EwastePhoto(models.Model):
    request = models.ForeignKey(
        EwasteRequest,
        related_name='photos',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='ewaste_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)