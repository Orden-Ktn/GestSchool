from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .models import *
import time
from plyer import notification
from django.db.models import Count, F, Value, Window
from django.db.models.functions import Rank
from django.db.models import Prefetch, Q
from decimal import Decimal



#vue pour l'inscription
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form = CustomUserCreationForm()
    return render(request, 'compte/register.html', {'form': form})

def validation_inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inscription réussie. Veuillez vous connecter.')
            return redirect('login')  # Redirige vers la page de connexion
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'inscription.html', {'form': form})

def inscription(request):
    return render(request, 'compte/register.html')

def login(request):
    return render(request, 'compte/connexion.html')

#vue pour la connexion
def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request)
            
            return redirect('index')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'compte/connexion.html')

def lock_screen(request):
    return render(request, 'compte/lock_screen.html')    


def profile(request):
    matieres = Matiere.objects.all()
    return render(request, 'profile.html', {'matieres':matieres})   

def editer_profile(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        role = request.POST.get('role')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        matiere = request.POST.get('matiere_enseignee')
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        
        
        existing_matiere = Professeur.objects.filter(email=email).exists()

        if existing_matiere:
            messages.error(request, "Les informations existent déjà pour votre profile.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
            if nom and prenom and role and contact and email and matiere:
               Professeur.objects.create(nom=nom, prenom=prenom, role=role, contact=contact, email=email, matiere_id=matiere, annee_scolaire=annee_active) 
               messages.success(request, "Profile mise à jour!")
               return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
               # Gérer les erreurs si les données sont invalides
               return render(request, 'profile.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('profile')

def professeur(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    classes = Classe_exist.objects.all()
    professeurs = Professeur.objects.filter(annee_scolaire_id=annee_active)

    for professeur in professeurs:
        # Récupérer les classes attribuées à ce professeur
        classes_attribuees = Professeur_Classe.objects.filter(professeur=professeur)
        professeur.classes_attribuees = [pc.classe.fusion for pc in classes_attribuees]

    return render(request, 'professeur.html', {'professeurs': professeurs, 'classes': classes})

def attribuer_classe_professeur(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        id_professeur = request.POST.get('id_professeur')
        id_matiere = request.POST.get('matiere_enseignee')
        id_classe = request.POST.get('id_classe')
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        
        
        existing_matiere = Professeur_Classe.objects.filter(Q(professeur_id=id_professeur) & Q(classe_id=id_classe)).exists()

        if existing_matiere:
            messages.error(request, "La classe est déjà attribuée.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
            if id_classe and id_professeur and id_matiere:
               Professeur_Classe.objects.create(classe_id=id_classe, professeur_id=id_professeur, matiere_id=id_matiere, annee_scolaire=annee_active) 
               messages.success(request, "Attribution de classe réussie!")
               return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
               # Gérer les erreurs si les données sont invalides
               return render(request, 'professeur.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('professeur')

def delete_professeur(request, id):
    objet = Professeur.objects.get(pk=id)
    objet.delete()      
    return redirect(request.META.get('HTTP_REFERER', '/'))


def index(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    if annee_active:
        total_classes = Classe_exist.objects.count()
        total_students = Eleve.objects.filter(annee_scolaire=annee_active).count()
        total_personnels = Personnel.objects.exclude(role="Superadmin").exclude(role="Aucun").filter(annee_scolaire=annee_active).count()
        total_students_boys = Eleve.objects.filter(annee_scolaire=annee_active, sexe='M').count()
        total_students_girls = Eleve.objects.filter(annee_scolaire=annee_active, sexe='F').count()
        
        pourcentage_boys = (total_students_boys * 100) / total_students if total_students > 0 else 0
        pourcentage_girls = (total_students_girls * 100) / total_students if total_students > 0 else 0
        percent_girls = round(float(pourcentage_girls), 2)
        percent_boys = round(float(pourcentage_boys), 2)
        
    else:
        total_classes = 0
        total_students = 0
        total_personnels = 0
        total_students_boys = 0
        total_students_girls = 0
        percent_boys = 0
        percent_girls = 0

    context = {
        'total_classes': total_classes,
        'total_students': total_students,
        'total_personnels': total_personnels,
        'total_students_boys': total_students_boys,
        'total_students_girls': total_students_girls,
        'percent_boys': percent_boys,
        'percent_girls': percent_girls,
        'annee_active': annee_active
    }
    
    return render(request, 'interfaces/index.html', context)




#vue pour la déconnexion
def deconnexion(request):
    logout(request)
    return redirect('connexion')

def changer_user(request):
    return render(request, 'compte/change_user.html')

#vue pour le changement de nom et mot de passe
def change_user(request):
    if request.method == 'POST':
        form = ChangeUserForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['new_username']
            new_password = form.cleaned_data['new_password']

            # Update user information
            user = request.user
            user.username = new_username
            user.set_password(new_password)
            user.save()

            # Important: update session to keep user logged in with new credentials
            update_session_auth_hash(request, user)

            return redirect('connexion')  # Redirect to profile page or any other page
    else:
        form = ChangeUserForm()

    return render(request, 'compte/change_user.html', {'form': form})





#vues pour les matières
def ajouter_matiere(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        sigle = request.POST.get('sigle')

        existing_matiere = Matiere.objects.filter(sigle=sigle).exists()

        if existing_matiere:
            messages.error(request, "Cette matière a déjà été enregistrée.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
           
           # Validation simple
           if nom and sigle:
               # Création de l'objet Classe et sauvegarde dans la base de données
               Matiere.objects.create(nom=nom, sigle=sigle) 
               messages.success(request, "Matière enregistrée!")
               return redirect(request.META.get('HTTP_REFERER', '/'))
           else:
               # Gérer les erreurs si les données sont invalides
               return render(request, 'matiere.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('matiere')   

def matiere(request):
       # Récupération de toutes les matieres
       matieres = Matiere.objects.all()
       return render(request, 'matiere.html', {'matieres': matieres})





#vues pour les tarifs
def ajouter_tarif(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        montant = request.POST.get('montant')
        classe_id = request.POST.get('classe_id')

        existing_tarif = Tarif.objects.filter(classe_id_id=classe_id).exists()

        if existing_tarif:
            messages.error(request, "Cette classe a déjà un tarif enregistré.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
           
           if montant and classe_id:
               Tarif.objects.create(montant=montant, classe_id_id=classe_id) 
               messages.success(request, "Tarif enregistré!")
               return redirect(request.META.get('HTTP_REFERER', '/'))
           else:
               return render(request, 'fiance/grille_tarif.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('tarif')   

def modify_tarif(request, id):
    tarif = Tarif.objects.get(id=id)
    classes = Classe_exist.objects.all()
    if request.method == 'POST':
        tarif.montant = request.POST['montant']
        tarif.classe_id_id = request.POST['classe_id']
        
        tarif.save()
        return redirect('tarif')
    return redirect(request.META.get('HTTP_REFERER', '/'))

def fiche_paiement(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    eleves = Eleve.objects.filter(annee_scolaire_id=annee_active)

    for eleve in eleves:
        try:
            # Récupérer la classe de l'élève
            classe_eleve = eleve.classe

            # Récupérer le tarif correspondant à la classe
            classe_exist = Classe_exist.objects.get(fusion=classe_eleve)
            tarif = Tarif.objects.get(classe_id_id=classe_exist.id)

            # Assigner le montant du tarif à l'élève
            eleve.tarif_montant = tarif.montant

            # Calculer la somme des montants payés pour cet élève
            cotisations = Solde_Scolarite.objects.filter(eleve=eleve)
            total_cotisations = sum(int(cotisation.montant_paye) for cotisation in cotisations if cotisation.montant_paye)
            eleve.total_cotisations = total_cotisations

            # Comparer le montant total payé au tarif
            if total_cotisations == int(eleve.tarif_montant):
                eleve.statut_paiement = "Soldé"
            elif total_cotisations > int(eleve.tarif_montant):
                eleve.statut_paiement = "Marge dépassée mais soldé"
            else:
                eleve.statut_paiement = "En dette"

        except (Classe_exist.DoesNotExist, Tarif.DoesNotExist):
            # Si le tarif n'est pas trouvé, définir une valeur par défaut
            eleve.tarif_montant = 0
            eleve.total_cotisations = 0
            eleve.statut_paiement = "N/A"  # Statut par défaut si le tarif n'est pas trouvé

    return render(request, 'finance/fiche_paiement.html', {'eleves': eleves})


def modifier_solde(request, eleve_id):
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    if request.method == 'POST':
        try:
            nouveau_montant = request.POST['nouveau_montant']

            Solde_Scolarite.objects.create(
                eleve=eleve,
                montant_paye=nouveau_montant,   # Utiliser directement le nouveau montant
            )

            messages.success(request, 'Le nouveau montant a été enregistré avec succès.')
            return redirect('fiche_paiement')
        except ValueError:
            messages.error(request, 'Le nouveau montant doit être un nombre valide.')
            return redirect('fiche_paiement')
    return redirect('fiche_paiement')

def tarif(request):
    tarifs = Tarif.objects.all()
    classes = Classe_exist.objects.all()
    return render(request, 'finance/grille_tarif.html', {'tarifs': tarifs, 'classes': classes})


#vues pour le personnel
def personnel(request):
       personnels = Personnel.objects.exclude(role="Superadmin")
       return render(request, 'personnel.html', {'personnels': personnels})

def modifier_role(request, personnel_id):
    if request.method == "POST":
        personnel = get_object_or_404(Personnel, id_personnel=personnel_id)
        nouveau_role = request.POST.get("role")

        ROLES_VALIDES = ["Censeur", "Professeur", "Secrétaire", "Surveillant", "Aucun"]
        
        if nouveau_role in ROLES_VALIDES and personnel.role=="Personnel" or personnel.role=="Aucun":
            personnel.role = nouveau_role
            personnel.save()
            messages.success(request, f"Le rôle de {personnel.username} a été mis à jour en {nouveau_role}.")
        else:
            messages.error(request, f"Attribution de rôle non réussie. {personnel.username} a déjà un rôle.")

    return redirect("personnel")  

#vues pour les classes
def ajouter_classe(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        sigle = request.POST.get('sigle')

        existing_classe = Classe.objects.filter(sigle=sigle).exists()

        if existing_classe:
            messages.error(request, "La classe a été enregistrée.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
           
           # Validation simple
           if nom and sigle:
               # Création de l'objet Classe et sauvegarde dans la base de données
               Classe.objects.create(nom=nom, sigle=sigle) 
               messages.success(request, "Classe enregistrée!")
               return redirect(request.META.get('HTTP_REFERER', '/'))
           else:
               # Gérer les erreurs si les données sont invalides
               return render(request, 'classe.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('classe')
 
def classe(request):
    classes = Classe_exist.objects.all()
    classes_professeurs = []

    for classe in classes:
        professeurs = Professeur_Classe.objects.filter(classe=classe)
        classes_professeurs.append({
            'classe': classe,
            'professeurs': [{'professeur': professeur.professeur, 'matiere': professeur.matiere} for professeur in professeurs]
        })

    return render(request, 'classe.html', {'classes_professeurs': classes_professeurs})




#vues pour les annees
def ajouter_annee(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        annee = request.POST.get('annee')

        existing_annee = AnneeScolaire.objects.filter(annee=annee).exists()

        if existing_annee:
            messages.error(request, "Cette année a déjà été enregistrée.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
        
           # Validation simple
           if annee:
               # Création de l'objet annee et sauvegarde dans la base de données
               AnneeScolaire.objects.create(annee=annee) 
               messages.success(request, "Année Scolaire enregistrée!")
               return redirect(request.META.get('HTTP_REFERER', '/'))
           else:
               # Gérer les erreurs si les données sont invalides
               return render(request, 'annee_scolaire.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('annee_scolaire')    

def activer_annee(request, annee_id):
    # Désactiver toutes les années scolaires
    AnneeScolaire.objects.update(active=False)
   
    # Activer l'année scolaire sélectionnée
    annee = AnneeScolaire.objects.get(id=annee_id)
    annee.active = True
    annee.save()

    return redirect('annee_scolaire') 

def annee_scolaire(request):
       # Récupération de toutes les annees
       annees = AnneeScolaire.objects.all()
       return render(request, 'annee_scolaire.html', {'annees': annees})



#vues pour les annees
def ajouter_trimestre(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        trimestre = request.POST.get('trimestre')

        existing_trimestre = Trimestre.objects.filter(trimestre=trimestre).exists()

        if existing_trimestre:
            messages.error(request, "Cet trimestre a déjà été enregistré.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
        
           # Validation simple
           if trimestre:
               # Création de l'objet trimestre et sauvegarde dans la base de données
               Trimestre.objects.create(trimestre=trimestre) 
               messages.success(request, "Trimestre enregistré!")
               return redirect(request.META.get('HTTP_REFERER', '/'))
           else:
               # Gérer les erreurs si les données sont invalides
               return render(request, 'trimestre.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('trimestre')    

def activer_trimestre(request, trimestre_id):
    Trimestre.objects.update(active=False)
 
    trimestre = Trimestre.objects.get(id=trimestre_id)
    trimestre.active = True
    trimestre.save()

    return redirect('trimestre') 

def trimestre(request):
       trimestres = Trimestre.objects.all()
       return render(request, 'trimestre.html', {'trimestres': trimestres})



#vues pour les emplois
def ajout_emploi(request):
       # Récupération de toutes les matieres2
       matieres = Matiere.objects.all()
       classes = Classe.objects.all()
       series = Serie.objects.all()
       return render(request, 'emploi/ajout_emploi.html', {'matieres': matieres, 'classes': classes, 'series': series})

def ajouter_emploi(request):
    if request.method == 'POST':
        cours1 = request.POST.get('cours1')
        cours2 = request.POST.get('cours2')
        cours3 = request.POST.get('cours3')
        cours4 = request.POST.get('cours4')
        cours5 = request.POST.get('cours5')
        cours6 = request.POST.get('cours6')
        cours7 = request.POST.get('cours7')
        cours8 = request.POST.get('cours8')
        cours9 = request.POST.get('cours9')
        cours10 = request.POST.get('cours10')
        cours11 = request.POST.get('cours11')
        cours12 = request.POST.get('cours12')
        cours13 = request.POST.get('cours13')
        cours14 = request.POST.get('cours14')
        cours15 = request.POST.get('cours15')
        cours16 = request.POST.get('cours16')
        cours17 = request.POST.get('cours17')
        cours18 = request.POST.get('cours18')
        cours19 = request.POST.get('cours19')
        cours20 = request.POST.get('cours20')
        classe = request.POST.get('classe')
        annee_active = AnneeScolaire.objects.filter(active=True).first()

        fusion = f"{classe}"

        existing_emploi = Emploi.objects.filter(classe=classe).exists()

        if existing_emploi:
            error_message = messages.error(request, "L'emploi du temps a été enregistré pour cette classe.")
            return redirect(request.META.get('HTTP_REFERER', '/'),{'error_message': error_message} )
        
        try:
            if cours1 and cours2 and cours3 and cours4 and cours5 and cours6 and cours7 and cours8 and cours9 and cours10 and cours11 and cours12 and cours13 and cours14 and cours15 and cours16 and cours17 and cours18 and cours19 and cours20 and classe:
                # Création de l'objet Classe et sauvegarde dans la base de données
                Emploi.objects.create(cours1=cours1, cours2=cours2, cours3=cours3, cours4=cours4, cours5=cours5, cours6=cours6, cours7=cours7, cours8=cours8, cours9=cours9, cours10=cours10, cours11=cours11, cours12=cours12, cours13=cours13, cours14=cours14, cours15=cours15, cours16=cours16, cours17=cours17, cours18=cours18, cours19=cours19, cours20=cours20, classe=classe, annee_scolaire=annee_active)
                Classe_exist.objects.create(fusion=fusion)
                messages.success(request, "Emploi enregistré!")
                return redirect(request.META.get('HTTP_REFERER', '/'))
                
            else:
                # Gérer les erreurs si les données sont invalides
                return render(request, 'ajout_emploi.html', {'error': 'Tous les champs sont requis.'})
            
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')
     
    return render(request, 'ajout_emploi.html')

def emploi(request):
    emploi1 = Emploi.objects.filter()
    matieres = Matiere.objects.all()
    classes = Classe.objects.all()
    return render(request, 'emploi.html', {'emploi1': emploi1, 'matieres': matieres, 'classes': classes,})





#vues pour les eleves
def ajouter_eleve(request):
    if request.method == 'POST':
           nom = request.POST.get('nom')
           prenom = request.POST.get('prenom')
           sexe = request.POST.get('sexe')
           date_naissance = request.POST.get('date')
           contact = request.POST.get('contact')
           classe = request.POST.get('classe')
           statut = request.POST.get('statut')
           annee_active = AnneeScolaire.objects.filter(active=True).first()
           
           # Validation simple
           if nom and prenom and sexe and statut and date_naissance and contact and classe and statut:
                Eleve.objects.create(
                    nom=nom, 
                    prenom=prenom, 
                    sexe=sexe, 
                    date_naissance=date_naissance, 
                    contact=contact, 
                    classe=classe, 
                    statut=statut, 
                    annee_scolaire=annee_active) 
                messages.success(request, "Enregistrement réussie pour l'élève!")
                return redirect(request.META.get('HTTP_REFERER', '/'))
           else:
               return render(request, 'eleve.html', {'error': 'Tous les champs sont requis.'})

    return redirect('eleve')  

def eleve(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    classes = Classe.objects.all()
    eleves = Eleve.objects.filter(annee_scolaire_id=annee_active)
    return render(request, 'eleve.html', {'eleves': eleves, 'classes': classes})


def modify_information(request, id_eleve):
    eleve = Eleve.objects.get(id_eleve=id_eleve)
    classes = Classe.objects.all()
    if request.method == 'POST':
        eleve.nom = request.POST['nom']
        eleve.prenom = request.POST['prenom']
        eleve.sexe = request.POST['sexe']
        eleve.date_naissance = request.POST['date']
        eleve.contact = request.POST['contact']
        eleve.classe = request.POST['classe']
        eleve.statut = request.POST['statut']
        
        eleve.save()
        return redirect('eleve')
    return redirect(request.META.get('HTTP_REFERER', '/'))

def delete_student(request, id_eleve):
    objet = Eleve.objects.get(pk=id_eleve)
    objet.delete()      
    return redirect(request.META.get('HTTP_REFERER', '/'))



def update(request):
    if request.method == 'POST':
           # Récupération des données du formulaire
           eleve = request.POST.get('id')
           nom = request.POST.get('nom')
           prenom = request.POST.get('prenom')
           sexe = request.POST.get('sexe')
           contact = request.POST.get('contact')
           date_naissance = request.POST.get('date')
           classe = request.POST.get('classe')
           serie = request.POST.get('serie')
           statut = request.POST.get('statut')

           # Vérification si la matière existe déjà pour cet élève
           existing_eleve = Eleve.objects.filter(id_eleve=eleve).first()

           if existing_eleve:

                # Validation simple
                if nom and prenom and sexe and contact and date_naissance and classe and serie and statut:
                    # Création de l'objet Classe et sauvegarde dans la base de données
                    Eleve.objects.filter(id_eleve=eleve).update(nom=nom, prenom=prenom, sexe=sexe, contact=contact, date_naissance=date_naissance, classe=classe, serie=serie, statut=statut)
                    return redirect('all_eleve')  # Remplacez par l'URL de redirection après l'enregistrement
                else:
                    # Gérer les erreurs si les données sont invalides
                    return render(request, 'ajout_eleve.html', {'error': 'Tous les champs sont requis.'})

    return render(request, 'ajout_eleve.html')



#vues pour les notes
def all_eleve(request):
    eleve6 = Eleve.objects.filter(classe="6ème")
    eleve5 = Eleve.objects.filter(classe="5ème")
    eleve4 = Eleve.objects.filter(classe="4ème")
    eleve3 = Eleve.objects.filter(classe="3ème")
    eleve0 = Eleve.objects.filter(classe="2nde D")
    eleve1 = Eleve.objects.filter(classe="1ère")
    eleve2 = Eleve.objects.filter(classe="Tle")
    return render(request, 'notes/all_eleve.html', {'eleve6': eleve6, 'eleve5': eleve5, 'eleve4': eleve4, 'eleve3': eleve3, 'eleve0': eleve0, 'eleve1': eleve1, 'eleve2': eleve2})


def ajout_note(request, id_eleve):
    eleves = Eleve.objects.filter(id_eleve=id_eleve)
    matieres = Matiere.objects.all()
    return render(request, 'notes/ajout_note.html', {'eleves': eleves, 'matieres': matieres})

def ajouter_note(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        eleve_id = request.POST.get('eleve_id')
        matiere_id = request.POST.get('matiere_id')
        n1 = request.POST.get('n1')
        n2 = request.POST.get('n2')
        n3 = request.POST.get('n3')
        n4 = request.POST.get('n4')
        n5 = request.POST.get('n5')
        coef = request.POST.get('coef')
        tri = request.POST.get('tri')

        # Vérification si la matière existe déjà pour cet élève
        existing_note = Note.objects.filter(eleve_id=eleve_id, matiere_id=matiere_id, tri=tri).first()

        if existing_note:
            # Si l'enregistrement existe déjà, afficher un message d'erreur
            messages.error(request, "Les notes ont déjà été enregistrées pour cette matière.")
            return redirect(request.META.get('HTTP_REFERER', '/'))


        try:
            # Convertir les notes en float, en gérant les valeurs vides ou non valides
            interro1 = float(n1) if n1.strip() else 0.0
            interro2 = float(n2) if n2.strip() else 0.0
            interro3 = float(n3) if n3.strip() else 0.0
            dev1 = float(n4) if n4.strip() else 0.0
            dev2 = float(n5) if n5.strip() else 0.0
            coef = float(coef) if coef.strip() else 1.0  # Valeur par défaut pour le coefficient

            # Calcul des moyennes
            moy_int = (interro1 + interro2 + interro3) / 3 if (interro1 + interro2 + interro3) > 0 else 0.0
            moy_interro = round(moy_int, 2)
            moy = (moy_interro + dev1 + dev2) / 3 if (moy_interro + dev1 + dev2) > 0 else 0.0
            moy_coe = moy * coef
            moy_coef = round(moy_coe, 2)

            # Validation simple
            if all([eleve_id, matiere_id, n1, n2, n3, n4, n5, coef, tri]):
                # Création de l'objet NoteCycle2 et sauvegarde dans la base de données
                Note.objects.create(
                    eleve_id_id=eleve_id,
                    matiere_id_id=matiere_id,
                    interro1=interro1,
                    interro2=interro2,
                    interro3=interro3,
                    dev1=dev1,
                    dev2=dev2,
                    coef=coef,
                    tri=tri,
                    moy_interro=moy_interro,
                    moy_coef=moy_coef
                )

                messages.success(request, "Les notes ont été enregistrées pour cette matière.")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                # Gérer les erreurs si les données sont invalides
                messages.error(request, 'Tous les champs sont requis.')

        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez entrer des valeurs numériques valides pour les notes.')

    return render(request, 'interfaces/index.html')




#vues pour les bulletins
def eleve1(request):
       eleve6 = Eleve.objects.filter(classe="6ème")
       eleve5 = Eleve.objects.filter(classe="5ème")
       eleve4 = Eleve.objects.filter(classe="4ème")
       eleve3 = Eleve.objects.filter(classe="3ème")
       return render(request, 'bulletins/eleve_cycle1.html', {'eleve6': eleve6, 'eleve5': eleve5, 'eleve4': eleve4, 'eleve3': eleve3})

def eleve2(request):
       eleve0 = Eleve.objects.filter(classe="2nde")
       eleve1 = Eleve.objects.filter(classe="1ère")
       eleve2 = Eleve.objects.filter(classe="Tle")
       return render(request, 'bulletins/eleve_cycle2.html', {'eleve0': eleve0, 'eleve1': eleve1, 'eleve2': eleve2})

def bulletin_trim1(request, id_eleve):
    eleve = get_object_or_404(Eleve, id_eleve=id_eleve)
    classes = Classe.objects.all()
    series = Serie.objects.all()
    matieres = Matiere.objects.all()
    trim = 1

    bul = Note.objects.filter(eleve_id=id_eleve, tri=trim)

    existing_note = Note.objects.filter(eleve_id=id_eleve, tri=trim)
    if not bul:
        messages.error(request, "Aucune note n'a déjà été enregistrée pour cet/cette élève dans le compte du Trimestre 1.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if existing_note:
        total1 = 0
        total2 = 0
        moy1 = 0

        for buls in bul:

            total1 += float(buls.moy_coef)
            total1 = round(total1,2)
            total2 += float(buls.coef)

            moy1 = total1/total2
            moy1 = float(moy1)
            moy_gen1 = round(moy1,2)

        return render(request, 'bulletins/bulletin1.html', {'bul': bul, 'matieres': matieres, 'eleve': eleve, 'total1': total1 , 'moy_gen1': moy_gen1, 'trim': trim})


    return redirect(request.META.get('HTTP_REFERER', '/'))

def bulletin_trim2(request, id_eleve):
    eleve = get_object_or_404(Eleve, id_eleve=id_eleve)
    classes = Classe.objects.all()
    series = Serie.objects.all()
    matieres = Matiere.objects.all()
    trim = 2

    bul = Note.objects.filter(eleve_id=id_eleve, tri=trim)

    existing_note = Note.objects.filter(eleve_id=id_eleve, tri=trim)
    if not bul:
        messages.error(request, "Aucune note n'a déjà été enregistrée pour cet/cette élève dans le compte du Trimestre 2.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if existing_note:
        total3 = 0
        total4 = 0
        moy2 = 0

        for buls in bul:

            total3 += float(buls.moy_coef)
            total3 = round(total3,2)
            total4 += float(buls.coef)

            moy2 = total3/total4
            moy2 = float(moy2)
            moy_gen2 = round(moy2,2)

        return render(request, 'bulletins/bulletin2.html', {'bul': bul, 'matieres': matieres, 'eleve': eleve, 'total3': total3 , 'moy_gen2': moy_gen2, 'trim': trim})
    return redirect(request.META.get('HTTP_REFERER', '/'))

def bulletin_trim3(request, id_eleve):
    eleve = get_object_or_404(Eleve, id_eleve=id_eleve)
    classes = Classe.objects.all()
    series = Serie.objects.all()
    matieres = Matiere.objects.all()
    trim = 3

    bul = Note.objects.filter(eleve_id=id_eleve, tri=trim)

    existing_note = Note.objects.filter(eleve_id=id_eleve, tri=trim)
    if not bul:
        messages.error(request, "Aucune note n'a déjà été enregistrée pour cet/cette élève dans le compte du Trimestre 3.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if existing_note:
        total5 = 0
        total6 = 0
        moy3 = 0

        for buls in bul:

            total5 += float(buls.moy_coef)
            total5 = round(total5,2)
            total6 += float(buls.coef)

            moy3 = total5/total6
            moy3 = float(moy3)
            moy_gen3 = round(moy3,2)

        return render(request, 'bulletins/bulletin3.html', {'bul': bul, 'matieres': matieres, 'eleve': eleve, 'total5': total5 , 'moy_gen3': moy_gen3, 'trim': trim})

    return redirect(request.META.get('HTTP_REFERER', '/'))


def save_bulletin(request):
    if request.method == 'POST':
        total = request.POST.get('total')
        moyenne = request.POST.get('moyenne')
        tri = request.POST.get('tri')
        classe = request.POST.get('classe')
        eleve_id = request.POST.get('eleve_id')

        eleve = Eleve.objects.filter(id_eleve=eleve_id).first()
        bul = Note.objects.filter(eleve_id_id=eleve_id, tri=tri)
        bul1 = Bulletin.objects.filter(id_eleve=eleve_id, tri=tri).first()

        existing_info = Bulletin.objects.filter(id_eleve=eleve_id, tri=tri, total=total).first()

        if existing_info:
            messages.error(request, "L'enregistrement a déjà été éffectuée pour cet/cette élève.")
            return redirect(request.META.get('HTTP_REFERER', '/'))


        if not existing_info:
            if total and moyenne and tri and eleve_id and classe:
                Bulletin.objects.create(total=total, moyenne=moyenne, tri=tri, id_eleve=eleve_id, classe=classe)
                messages.error(request, "Bulletin enregistré pour cet/cette élève.")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect(request.META.get('HTTP_REFERER', '/'))


def verification(request):
    eleves = Eleve.objects.all()
    return render(request, 'bulletins/check.html', {'eleves': eleves})

# Fonction utilitaire pour convertir une chaîne en float
def convert_to_float(value):
    try:
        return float(value.replace(',', '.'))
    except (ValueError, AttributeError):
        return 0.0

def download(request):
    if request.method == 'POST':
        tri = int(request.POST.get('tri', 0))
        eleve_id = request.POST.get('id_eleve')

        eleve = Eleve.objects.filter(id_eleve=eleve_id).first()
        bul = Note.objects.filter(eleve_id_id=eleve_id, tri=tri)
        bul1 = Bulletin.objects.filter(id_eleve=eleve_id, tri=tri)



        if bul and bul1:
            b1 = Bulletin.objects.filter(id_eleve=eleve_id, tri=1).first()
            b2 = Bulletin.objects.filter(id_eleve=eleve_id, tri=2).first()
            b3 = Bulletin.objects.filter(id_eleve=eleve_id, tri=3).first()
            bulletin = Bulletin.objects.filter(id_eleve=eleve_id, tri=3).first()

            classe = bulletin.classe

            moyenne1 = convert_to_float(b1.moyenne) if b1 else 0
            moyenne2 = convert_to_float(b2.moyenne) if b2 else 0
            moyenne3 = convert_to_float(b3.moyenne) if b3 else 0
            total = b3.total
            moyenne_generale = (moyenne1 + moyenne2 + moyenne3) /3

            classe_ranks = Bulletin.update_ranks(classe, tri)
            rang = classe_ranks.filter(id_eleve=eleve_id).values_list('rank', flat=True).first()

            statut = 'Admis' if moyenne_generale >= 10 else 'Echoué'

            if tri in [1, 2] and (bul.exists() and bul1.exists()):

                return render(request, 'bulletins/download_bulletin.html', {
                    'bul': bul,
                    'bul1': bul1,
                    'eleve': eleve,
                    'tri': tri,
                    'total': total,
                    'rang':rang,
                    'classe': classe,
                    'moyenne1': moyenne1,
                    'moyenne2': moyenne2,
                    'moyenne3': moyenne3,
                    'moyenne_generale': moyenne_generale,  # Ajout de la moyenne générale
                })

            # Condition pour le trimestre 3
            elif tri == 3 and (bul.exists() or bul1.exists() or b1 or b2):

                return render(request, 'bulletins/download_last_bulletin.html', {
                    'bul': bul,
                    'bul1': bul1,
                    'moyenne1': moyenne1,
                    'moyenne2': moyenne2,
                    'moyenne3': moyenne3,
                    'moyenne_generale': moyenne_generale,
                    'b2': b2,
                    'classe': classe,
                    'total': total,
                    'eleve': eleve,
                    'tri': tri,
                    'statut': statut,
                    'rang':rang,
                })

            else:
                messages.error(request, "Aucune note n'a été enregistrée pour cet élève.")
                return redirect(request.META.get('HTTP_REFERER', '/'))


    messages.error(request, "Aucune note n'a été enregistrée pour cet élève.")
    return redirect('verification')

