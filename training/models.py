from django.db import models
from geographies.models import State
from videos.models import Language
from people.models import Animator

# Create your models here.
class Trainer(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)
	email = models.EmailField()
	language = models.ForeignKey(Language, null=True, blank=True)

class Assessment(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)

class Question(models.Model):
	id = models.AutoField(primary_key=True)
	assessment = models.ForeignKey(Assessment, null=True, blank=True)
	language = models.ForeignKey(Language, null=True, blank=True)
	section = models.IntegerField()
	serial = models.IntegerField()
	text = models.CharField(max_length = 100)

class Training(models.Model):
	id = models.AutoField(primary_key=True)
	date = models.DateField()
	place = models.CharField(max_length=200)
	state = models.ForeignKey(State, null=True, blank=True)
	trainer = models.ManyToManyField(Trainer, null=True, blank=True)
	language = models.ForeignKey(Language, null=True, blank=True)
	participants = models.ManyToManyField(Animator)

class Score(models.Model):
	id = models.AutoField(primary_key=True)
	training = models.ForeignKey(Training, null=True, blank=True)
	participant = models.ForeignKey(Animator, null=True, blank=True)
	question = models.ForeignKey(Question, null=True, blank=True)
	score = models.IntegerField()






