from django.db import models

class ContactGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Contact(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    contact_picture = models.ImageField(upload_to='contacts/')
    contact_group = models.ForeignKey(
                        ContactGroup, 
                        max_length=50,
                        related_name='contacts',
                        on_delete=models.CASCADE,
                    )
    
    def save(self, *args, **kwargs):
        if self.pk:
            old = Contact.objects.get(pk=self.pk)
            if old.contact_picture and old.contact_picture != self.contact_picture:
                old.contact_picture.delete(save=False)

        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.contact_picture:
            self.contact_picture.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']