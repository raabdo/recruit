from PIL import Image

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from .choices import (TIMEZONE_CHOICES, COUNTRY_CHOICES, GENDER_CHOICES,
	EDUCATION_CHOICES, EMPLOYER_TYPE_CHOICES, POSITION_TYPE_CHOICES, 
	DESIRED_MONTHLY_SALARY_CHOICES)

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	timezone = models.CharField(max_length=50, blank=True)
	citizenship = models.CharField(max_length=50, blank=True)
	user_type = models.CharField(
		choices = (('Candidate', 'Candidate'), ('Recruiter', 'Recruiter'), ('Employer', 'Employer'),),
		max_length = 50,
		default = False,
	)
	is_admin = models.BooleanField(default=False)
	last_modified = models.DateTimeField(auto_now_add=False, auto_now=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return self.user.email

class Candidate(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	birth_year = models.CharField(max_length=4, blank=False)
	date_of_birth = models.DateField(blank=True, null=True)
	gender = models.CharField(choices=(('male', 'Male'), ('female', 'Female'),), max_length = 10, blank=True, null=True)
	education = models.CharField(
			max_length=25,
			blank=True,
			choices=EDUCATION_CHOICES,
		)	
	education_major = models.CharField(max_length=250, blank=True)
	current_location = CountryField(blank=True)

	def __str__(self):
		return self.user.email

class CandidateRequirements(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	# location = models.ManyToManyField(Location, on_delete=models.CASCADE)  create m2m
	employer_type = models.CharField(
			max_length=25,
			blank=True,
			choices=EMPLOYER_TYPE_CHOICES,
		)


class Employer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)	
	phone_number = PhoneNumberField(blank=False)
	name_english = models.CharField(blank=False, max_length=200)
	name_local = models.CharField(blank=False, max_length=200)
	address_english = models.CharField(blank=False, max_length=200)
	address_local = models.CharField(blank=False, max_length=200)
	business_license = models.ImageField(upload_to='employer/%Y/%m/%d')
	business_license_thumb = models.ImageField(upload_to='employer/%Y/%m/%d', blank=True)

	def __str__(self):
		return self.name_english

	def save(self, *args, **kwargs):
		from .utils import generate_thumbnail
		thumb,filename=generate_thumbnail(self.business_license)
		# print(thumb.filename, thumb.size)
		# print(dir(thumb))
		# print(thumb)
		# print(dir(self.business_license_thumb))
		self.business_license_thumb=thumb

		

		super(Employer, self).save(*args, **kwargs)

class EmployerRequirements(models.Model):
	employer = models.OneToOneField(Employer, on_delete=models.CASCADE)
	education = models.CharField(
			max_length=25,
			blank=True,
			choices=EDUCATION_CHOICES,
		)
	education_major = models.CharField(max_length=50, blank=True)
	age_range_low = models.IntegerField(blank=True)
	age_range_high = models.IntegerField(blank=True)
	years_of_experience = models.IntegerField(blank=True)
	citizenship = CountryField(blank=True)

class Recruiter(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	phone_number = PhoneNumberField(blank=False)
	date_of_birth = models.DateField(blank=True, null=True)
	location = models.CharField(blank=True, max_length=100)
	id_card = models.ImageField(upload_to='recruiter/%Y/%m/%d')

	def __str__(self):
		return self.user.email

from django.db.models.signals import post_save
from django.dispatch import receiver

def thumbnail(file):
	print('file: ', file)
	size = 75, 75
	im = Image.open(file)
	# filename, ext = file.filename.split('.')
	# filename = filename + '-thumb.' + ext
	im.thumbnail(size)
	return im
	# memory_file = cStringIO.StringIO()
	# im.save(memory_file, ext)
	# return memory_file, filename

@receiver(post_save, sender=Employer)
def my_callback(sender, instance, **kwargs):
	print('sender: ', sender)
	# employer = Employer.objects.get(pk=instance.pk)
	# thumb = thumbnail(instance.business_license)
	# # print('request finished', thumb)
	# employer.business_license_thumb = thumb
	# employer.save()
	# return employer

post_save.connect(my_callback, sender=Employer)		
