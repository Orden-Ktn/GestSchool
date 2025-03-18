from django.db import models
from django.db.models import F, Window
from django.db.models.functions import Rank
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Choississez un rôle', 'Choississez un rôle'),
        ('Censeur', 'Censeur'),
        ('Surveillant', 'Surveillant'),
        ('Secrétaire', 'Secrétaire'),
        ('Professeur', 'Professeur'),
        ('Comptable', 'Comptable'),
        ('superadmin', 'superadmin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Personnel')

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",  # Ajout de related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions_set", # Ajout de related_name
        related_query_name="user",
    )

    def __str__(self):
        return self.username


class AnneeScolaire(models.Model):
    annee = models.CharField(max_length=20)  
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.annee

class Trimestre(models.Model):
    trimestre = models.CharField(max_length=20)  
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.trimestre    


class Matiere(models.Model):
    nom = models.CharField(max_length=80)
    sigle = models.CharField(max_length=50)


class Classe_exist(models.Model):
    fusion = models.CharField(max_length=80)


class Tarif(models.Model):
    montant = models.CharField(max_length=20)  
    classe_id = models.ForeignKey(Classe_exist, on_delete=models.CASCADE)

    def __str__(self):
        return self.montant    


class Solde_Scolarite(models.Model):
    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2)
    date_modification = models.DateTimeField(auto_now=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Solde de {self.eleve.nom} {self.eleve.prenom}"


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
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)


class Eleve(models.Model):
    id_eleve = models.AutoField(primary_key=True)  
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=100)
    date_naissance = models.DateField(max_length=100)
    contact = models.CharField(max_length=100)
    classe = models.CharField(max_length=100)
    statut = models.CharField(max_length=100)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)

class Personnel(models.Model):
    id_personnel = models.AutoField(primary_key=True)  
    username = models.CharField(max_length=80)
    contact = models.CharField(max_length=100)
    role = models.CharField(max_length=100, default='Personnel')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)
    password = models.CharField(max_length=255) 
 
    def save(self, *args, **kwargs):
        # Hacher le mot de passe uniquement si le mot de passe est en texte brut
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        # Vérifie si le mot de passe brut correspond au mot de passe haché
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

class Professeur(models.Model):  
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)


class Professeur_Classe(models.Model): 
    classe = models.ForeignKey(Classe_exist, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)


class Note(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    option = models.CharField(max_length=100)
    note = models.DecimalField(max_digits=5, decimal_places=2)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)
    trimestre = models.ForeignKey(Trimestre, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Note de {self.eleve.nom} en {self.matiere.sigle} ({self.option})"



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

