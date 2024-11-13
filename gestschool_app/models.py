from django.db import models
from django.db.models import F, Window
from django.db.models.functions import Rank


class AnneeScolaire(models.Model):
    annee = models.CharField(max_length=20)  
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.annee
    

class Matiere(models.Model):
    nom = models.CharField(max_length=80)
    sigle = models.CharField(max_length=50)

class Classe_exist(models.Model):
    fusion = models.CharField(max_length=80)


class Serie(models.Model):
    intitule = models.CharField(max_length=50)


class Classe(models.Model):
    nom = models.CharField(max_length=80)
    sigle = models.CharField(max_length=50) 

class Emploi(models.Model):
    cours1 = models.CharField(max_length=80)
    cours2 = models.CharField(max_length=80)
    cours3 = models.CharField(max_length=80)
    cours4 = models.CharField(max_length=80)
    cours5 = models.CharField(max_length=80)
    cours6 = models.CharField(max_length=80)
    cours7 = models.CharField(max_length=80)
    cours8 = models.CharField(max_length=80)
    cours9 = models.CharField(max_length=80)
    cours10 = models.CharField(max_length=80)
    cours11 = models.CharField(max_length=80)
    cours12 = models.CharField(max_length=80)
    cours13 = models.CharField(max_length=80)
    cours14 = models.CharField(max_length=80)
    cours15 = models.CharField(max_length=80)
    cours16 = models.CharField(max_length=80)
    cours17 = models.CharField(max_length=80)
    cours18 = models.CharField(max_length=80)
    cours19 = models.CharField(max_length=80)
    cours20 = models.CharField(max_length=80)
    classe = models.CharField(max_length=100)
    serie = models.CharField(max_length=100)


class Eleve(models.Model):
    id_eleve = models.AutoField(primary_key=True)  # Utilisation d'AutoField pour l'identifiant
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=100)
    date_naissance = models.DateField(max_length=100)
    contact = models.CharField(max_length=100)
    classe = models.CharField(max_length=100)
    serie = models.CharField(max_length=100)
    statut = models.CharField(max_length=100)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)


class Note(models.Model):
    eleve_id = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    matiere_id = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    interro1 = models.CharField(max_length=50)
    interro2 = models.CharField(max_length=50)
    interro3 = models.CharField(max_length=50)
    dev1 = models.CharField(max_length=50)
    dev2 = models.CharField(max_length=50)
    coef = models.CharField(max_length=50)
    tri = models.CharField(max_length=50)
    moy_interro = models.CharField(max_length=50)
    moy_coef = models.CharField(max_length=50)



class Bulletin(models.Model):
    id_eleve = models.CharField(max_length=80)
    classe = models.CharField(max_length=100)
    total = models.CharField(max_length=50)
    moyenne = models.CharField(max_length=50)
    tri = models.CharField(max_length=50)

    @classmethod
    def update_ranks(cls, classe, tri):
        return cls.objects.filter(classe=classe, tri=tri).annotate(
            rank=Window(expression=Rank(), order_by=F('moyenne').desc())
        )

