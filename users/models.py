from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
from multiselectfield import MultiSelectField
from PIL import Image
from .choices import choices

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	image = models.ImageField(default = 'default.jpg', upload_to = 'profile_pics/')
	stocks = models.CharField(default='', max_length=500)

	def __str__(self):
		return f'{self.user.username} Profile'
	
	def save(self, *args, **kwargs):
			
		super(Profile, self).save(*args, **kwargs)
		img = Image.open(self.image.path)

		if img.height > 300 or img.width > 300:
			output_size = (300, 300)
			img.thumbnail(output_size)
			img.save(self.image.path)

	def get_stocks(self):
		return self.stocks
