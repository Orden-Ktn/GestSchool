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
from django.db.models.functions import Rank, Coalesce
from django.db.models import Prefetch, Q, Sum, DecimalField
from decimal import Decimal
from .forms import *
from collections import defaultdict


#vue pour l'inscription
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Ne pas enregistrer immédiatement
            if user.username == 'Admin-GS':
                user.role = 'Superadmin'  # Définit le rôle sur Superadmin
            else:
                user.role = 'Personnel'  # Définit le rôle par défaut
            user.save()  # Enregistre l'utilisateur avec le rôle approprié
            messages.success(request, 'Inscription réussie ! Connectez-vous.')
            return redirect('login_view')
        else:
            messages.error(request, 'Erreur lors de l\'inscription. Veuillez vérifier les informations.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentification/register.html', {'form': form})


#vue pour la connexion
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Redirige vers le tableau de bord
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        form = LoginForm()
    return render(request, 'authentification/connexion.html', {'form': form})

def lock_screen(request):
    return render(request, 'authentification/lock_screen.html')    


@login_required
def profile(request):
    matieres = Matiere.objects.all()
    try:
        professeur = Professeur.objects.get(email=request.user.email)
    except Professeur.DoesNotExist:
        professeur = None
    return render(request, 'personne/profil.html', {'matieres': matieres, 'professeur': professeur})


@login_required
def editer_profile(request):
    try:
        professeur = Professeur.objects.get(user=request.user)
        # Le profil existe déjà, donc on refuse la modification
        messages.error(request, "Le profil a déjà été créé. Vous ne pouvez pas le modifier.")
        return redirect('index')
    except Professeur.DoesNotExist:
        if request.method == 'POST':
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            role = request.POST.get('role')
            contact = request.POST.get('contact')
            email = request.POST.get('email')
            matiere = request.POST.get('matiere_enseignee')
            annee_active = AnneeScolaire.objects.filter(active=True).first()

            try:
                Professeur.objects.create(
                    user=request.user,
                    nom=nom,
                    prenom=prenom,
                    role=role,
                    contact=contact,
                    email=email,
                    matiere=Matiere.objects.get(id=matiere),
                    annee_scolaire=annee_active,
                )
                messages.success(request, "Profil créé!")
                return redirect('index')
            except (ValueError, Matiere.DoesNotExist) as e:
                messages.error(request, f'Veuillez bien renseigner les informations. {e}')
                return redirect('index')
        else:
            return redirect(request.META.get('HTTP_REFERER', '/'))  

    return redirect('index')

@login_required
def professeur(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    classes = Classe_exist.objects.all()
    professeurs = Professeur.objects.filter(Q(role='Professeur') & Q(annee_scolaire_id=annee_active))

    for professeur in professeurs:
        # Récupérer les classes attribuées à ce professeur
        classes_attribuees = Professeur_Classe.objects.filter(professeur=professeur)
        professeur.classes_attribuees = [pc.classe.fusion for pc in classes_attribuees]

    return render(request, 'personne/professeur.html', {'professeurs': professeurs, 'classes': classes})

@login_required
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
               return render(request, 'personne/professeur.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('professeur')

@login_required
def delete_professeur(request, id):
    professeur = get_object_or_404(Professeur, pk=id)
    user = professeur.user 

    professeur.delete()

    if user:
        user.role = 'Personnel'
        user.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def index(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    trimestre_active = Trimestre.objects.filter(active=True).first()
    matieres = Matiere.objects.all()

    eleves_par_classe = {}  
    profil_manquant = False

    if annee_active:
        total_classes = Classe_exist.objects.count()
        total_students = Eleve.objects.filter(annee_scolaire=annee_active).count()
        total_professeurs = Professeur.objects.filter(Q(role='Professeur') & Q(annee_scolaire=annee_active)).count()
        total_personnels = CustomUser.objects.exclude(role="Superadmin").exclude(role="Aucun").exclude(role="Professeur").exclude(role="Personnel").filter(is_active="1").count()
        total_students_boys = Eleve.objects.filter(annee_scolaire=annee_active, sexe='M').count()
        total_students_girls = Eleve.objects.filter(annee_scolaire=annee_active, sexe='F').count()
        solde_paye = Solde_Scolarite.objects.aggregate(total_montant=Sum(Coalesce('montant_paye', 0), output_field=DecimalField()))['total_montant']
        if solde_paye is None:
            solde_paye = 0
        elif solde_paye == 0:
            solde_paye = 0

        pourcentage_boys = (total_students_boys * 100) / total_students if total_students > 0 else 0
        pourcentage_girls = (total_students_girls * 100) / total_students if total_students > 0 else 0
        percent_girls = round(float(pourcentage_girls), 2)
        percent_boys = round(float(pourcentage_boys), 2)

        # Récupérer le professeur connecté et compter ses classes
        try:
            professeur = Professeur.objects.get(user=request.user)
            nombre_classes_professeur = Professeur_Classe.objects.filter(Q (annee_scolaire=annee_active) & Q(professeur=professeur)).count()
            classes_attribuees = Professeur_Classe.objects.filter(Q(annee_scolaire=annee_active) & Q(professeur=professeur))

            eleves_par_classe = {}
            matiere_professeur = professeur.matiere_id
            matiere_prof = Matiere.objects.get(id=matiere_professeur)
            
            for classe_attribuee in classes_attribuees:
                eleves_par_classe[classe_attribuee.classe.fusion] = Eleve.objects.filter(classe=classe_attribuee.classe.fusion)

        except Professeur.DoesNotExist:
            nombre_classes_professeur = 0  # Si le professeur n'existe pas, le nombre est 0
            matiere_professeur = None
            matiere_prof = None
            profil_manquant = True,

    else:
        total_classes = 0
        total_students = 0
        total_professeurs = 0
        total_personnels = 0
        total_students_boys = 0
        total_students_girls = 0
        percent_boys = 0
        percent_girls = 0
        solde_paye = 0
        nombre_classes_professeur = 0  # si l'année scolaire n'est pas active, le nombre est 0
        matiere_professeur = None  
        matiere_prof= None
        profil_manquant = True

    context = {
        'total_classes': total_classes,
        'total_students': total_students,
        'total_professeurs': total_professeurs,
        'total_personnels': total_personnels,
        'total_students_boys': total_students_boys,
        'total_students_girls': total_students_girls,
        'percent_boys': percent_boys,
        'percent_girls': percent_girls,
        'annee_active': annee_active,
        'trimestre_active': trimestre_active,
        'matieres': matieres,
        'nombre_classes_professeur': nombre_classes_professeur,
        'eleves_par_classe': eleves_par_classe,
        'matiere_professeur': matiere_professeur,  # Ajouter la matière du professeur au contexte
        'solde_paye': solde_paye,
        'matiere_prof': matiere_prof,
        'profil_manquant': profil_manquant
    }

    return render(request, 'index.html', context)

#vue pour la déconnexion
def deconnexion(request):
    logout(request)
    return redirect('login_view')



#vues pour les matières
@login_required
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
               return render(request, 'autre/matiere.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('matiere')   

@login_required
def matiere(request):
       # Récupération de toutes les matieres
       matieres = Matiere.objects.all()
       return render(request, 'autre/matiere.html', {'matieres': matieres})



#vues pour les tarifs
@login_required
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

@login_required
def modify_tarif(request, id):
    tarif = Tarif.objects.get(id=id)
    classes = Classe_exist.objects.all()
    if request.method == 'POST':
        tarif.montant = request.POST['montant']
        tarif.classe_id_id = request.POST['classe_id']
        
        tarif.save()
        return redirect('tarif')
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
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
                reste = 0
            elif total_cotisations > int(eleve.tarif_montant):
                eleve.statut_paiement = "Marge dépassée mais soldé"
            else:
                eleve.statut_paiement = "En dette"
                reste_a_payer = int(eleve.tarif_montant) - int(eleve.total_cotisations)
                eleve.reste_a_payer = reste_a_payer
     

        except (Classe_exist.DoesNotExist, Tarif.DoesNotExist):
            # Si le tarif n'est pas trouvé, définir une valeur par défaut
            eleve.tarif_montant = 0
            eleve.total_cotisations = 0
            eleve.reste_a_payer = 0
            eleve.statut_paiement = "N/A"  # Statut par défaut si le tarif n'est pas trouvé

    return render(request, 'finance/fiche_paiement.html', {'eleves': eleves, 'reste_a_payer': reste_a_payer, 'reste': reste,})

@login_required
def modifier_solde(request, eleve_id):
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    if request.method == 'POST':
        try:
            nouveau_montant = request.POST['nouveau_montant']

            Solde_Scolarite.objects.create(
                eleve=eleve,
                montant_paye=nouveau_montant, 
                annee_scolaire=annee_active, 
            )

            messages.success(request, 'Le nouveau montant a été enregistré avec succès.')
            return redirect('fiche_paiement')
        except ValueError:
            messages.error(request, 'Le nouveau montant doit être un nombre valide.')
            return redirect('fiche_paiement')
    return redirect('fiche_paiement')

@login_required
def tarif(request):
    tarifs = Tarif.objects.all()
    classes = Classe_exist.objects.all()
    return render(request, 'finance/grille_tarif.html', {'tarifs': tarifs, 'classes': classes})


#vues pour le personnel
@login_required
def personnel(request):
    personnels = CustomUser.objects.exclude(role="Superadmin")
    return render(request, 'personne/personnel.html', {'personnels': personnels})

@login_required
def modifier_role(request):
    if request.method == "POST":
        personnel_id = request.POST.get("id_personnel")
        personnel = get_object_or_404(CustomUser, id=personnel_id)
        nouveau_role = request.POST.get("role")
        ROLES_VALIDES = ["Censeur", "Professeur", "Secrétaire", "Surveillant", "Comptable", "Aucun"]

        if nouveau_role in ROLES_VALIDES and (personnel.role == "Personnel" or personnel.role == "Aucun"):
            # Vérifier si le rôle est déjà attribué à un autre utilisateur
            if nouveau_role in ["Censeur", "Secrétaire", "Comptable"]:
                autre_utilisateur = CustomUser.objects.filter(role=nouveau_role).exclude(id=personnel_id).first()
                if autre_utilisateur:
                    messages.error(request, f"Le rôle '{nouveau_role}' est déjà attribué à {autre_utilisateur.username}.")
                    return redirect("personnel")  # Rediriger sans modifier le rôle

            personnel.role = nouveau_role
            personnel.save()
            messages.success(request, f"Le rôle de {personnel.username} a été mis à jour en {nouveau_role}.")
        else:
            messages.error(request, f"Attribution de rôle non réussie. {personnel.username} a déjà un rôle.")

    return redirect("personnel")


@login_required
def supprimer_utilisateur(request, personnel_id):
    personnel = get_object_or_404(CustomUser, id=personnel_id)
    personnel.delete()

    messages.success(request, "L'utilisateur a été supprimé avec succès.")
    return redirect(request.META.get('HTTP_REFERER', '/'))



#vues pour les classes
@login_required
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
               return render(request, 'autre/classe.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('classe')
 
@login_required
def classe(request):
    classes = Classe_exist.objects.all()
    classes_professeurs = []

    for classe in classes:
        professeurs = Professeur_Classe.objects.filter(classe=classe)
        classes_professeurs.append({
            'classe': classe,
            'professeurs': [{'professeur': professeur.professeur, 'matiere': professeur.matiere} for professeur in professeurs]
        })

    return render(request, 'autre/classe.html', {'classes_professeurs': classes_professeurs})




#vues pour les annees
@login_required
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
               return render(request, 'autre/annee_scolaire.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('annee_scolaire')    

@login_required
def activer_annee(request, annee_id):
    # Désactiver toutes les années scolaires
    AnneeScolaire.objects.update(active=False)
   
    # Activer l'année scolaire sélectionnée
    annee = AnneeScolaire.objects.get(id=annee_id)
    annee.active = True
    annee.save()
    messages.success(request, "Année Scolaire activée!")

    return redirect('annee_scolaire') 

@login_required
def annee_scolaire(request):
       # Récupération de toutes les annees
       annees = AnneeScolaire.objects.all()
       return render(request, 'autre/annee_scolaire.html', {'annees': annees})



#vues pour les annees
@login_required
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
               return render(request, 'autre/trimestre.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return redirect('trimestre')    

@login_required
def activer_trimestre(request, trimestre_id):
    Trimestre.objects.update(active=False)
 
    trimestre = Trimestre.objects.get(id=trimestre_id)
    trimestre.active = True
    trimestre.save()
    messages.success(request, "Trimestre activé!")

    return redirect('trimestre') 

@login_required
def trimestre(request):
       trimestres = Trimestre.objects.all()
       return render(request, 'autre/trimestre.html', {'trimestres': trimestres})



#vues pour les emplois
@login_required
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
                return render(request, 'autre/emploi.html', {'error': 'Tous les champs sont requis.'})
            
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')
     
    return render(request, 'autre/emploi.html')

@login_required
def emploi(request):
    emploi = Emploi.objects.filter()
    matieres = Matiere.objects.all()
    classes = Classe.objects.all()
    return render(request, 'autre/emploi.html', {'emploi': emploi, 'matieres': matieres, 'classes': classes,})

@login_required
def delete_emploi(request, id):
    emploi = get_object_or_404(Emploi, pk=id)
    classe_nom = emploi.classe 

    emploi.delete()

    try:
        classe_exist = Classe_exist.objects.get(fusion=classe_nom)
        classe_exist.delete()
    except Classe_exist.DoesNotExist:
        pass

    messages.error(request, "Suppression réussie pour cet emploi de temps et les classes associées.")
    return redirect(request.META.get('HTTP_REFERER', '/'))




#vues pour les eleves
@login_required
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
               return render(request, 'personne/eleve.html', {'error': 'Tous les champs sont requis.'})

    return redirect('eleve')  

@login_required
def eleve(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    classes = Classe.objects.all()
    eleves = Eleve.objects.filter(annee_scolaire_id=annee_active)
    return render(request, 'personne/eleve.html', {'eleves': eleves, 'classes': classes})

@login_required
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

@login_required
def delete_student(request, id_eleve):
    objet = Eleve.objects.get(pk=id_eleve)
    objet.delete()      
    return redirect(request.META.get('HTTP_REFERER', '/'))


#vues pour le cahier de texte 
@login_required
def cahier_texte(request, classe_nom):
    try:
        trimestre_active = Trimestre.objects.filter(active=True).first()
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        professeur = Professeur.objects.get(user=request.user)
        matiere = professeur.matiere
        classe = Classe_exist.objects.get(fusion=classe_nom)
        classe_attribuee = Professeur_Classe.objects.get(Q(annee_scolaire=annee_active) & Q(professeur=professeur) & Q(classe=classe))
        eleves = Eleve.objects.filter(classe=classe_nom)

        cahier_textes = Cahier_texte.objects.filter(Q(annee_scolaire=annee_active) & Q(id_prof=professeur) & Q(classe=classe_nom) & Q(trimestre_id=trimestre_active))

        return render(request, 'cahier de texte/cahier_texte.html', {
            'eleves': eleves,
            'matiere': matiere,
            'classe_nom': classe_nom,
            'eleves_par_classe': {classe_nom: eleves},
            'cahier_textes': cahier_textes,  # Ajout des données du cahier de texte
        })
    except Professeur.DoesNotExist:
        return render(request, 'cahier de texte/cahier_texte.html', {
            'error': "Votre profil professeur n'existe pas.",
            'eleves_par_classe': {},
            'cahier_textes': [],  # Ajout de liste vide pour éviter les erreurs
        })
    except Classe_exist.DoesNotExist:
        return render(request, 'cahier de texte/cahier_texte.html', {
            'error': "Classe non trouvée.",
            'eleves_par_classe': {},
            'cahier_textes': [],
        })
    except Professeur_Classe.DoesNotExist:
        return render(request, 'cahier de texte/cahier_texte.html', {
            'error': "Classe non attribuée à ce professeur.",
            'eleves_par_classe': {},
            'cahier_textes': [],
        })

@login_required
def ajouter_contenu_cahier_texte(request):
    if request.method == 'POST':
        classe = request.POST.get('classe')
        matiere = request.POST.get('matiere')
        date = request.POST.get('date')
        contenu = request.POST.get('contenu')
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        trimestre_active = Trimestre.objects.filter(active=True).first()

        existing_classe = Cahier_texte.objects.filter(Q(classe=classe) & Q(matiere=matiere) & Q(date=date)).exists()

        if existing_classe:
            messages.error(request, "Le contenu de ce cours est déjà ajouté pour cette date.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            if classe and matiere and date and contenu:
                customer_user = CustomUser.objects.get(id=request.user.id)
                professeur = customer_user.professeur

                if annee_active and trimestre_active is None:
                    messages.error(request, "Aucune année scolaire active n'est définie.")
                    return redirect(request.META.get('HTTP_REFERER', '/'))

                Cahier_texte.objects.create(id_prof=professeur, classe=classe, matiere=matiere, date=date, contenu=contenu, annee_scolaire=annee_active, trimestre=trimestre_active)
                messages.success(request, "Contenu ajouté dans le cahier de texte!")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                return render(request, 'cahier de texte/cahier_texte.html', {'error': 'Tous les champs sont requis.'})

        except ValueError as e:
            print(f"ValueError: {e}")
            messages.error(request, 'Veuillez bien renseigner les informations.')
        except CustomerUser.DoesNotExist:
            messages.error(request, "L'utilisateur connecté n'existe pas.")
        except Professeur.DoesNotExist:
            messages.error(request, "L'utilisateur connecté n'est pas un professeur valide.")

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def visualisation_cahier_texte(request):
    trimestre_active = Trimestre.objects.filter(active=True).first()
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    cahier_textes = Cahier_texte.objects.filter(Q(annee_scolaire=annee_active) & Q(trimestre=trimestre_active))
    return render(request, 'cahier de texte/visualisation_cahier_texte.html', {'cahier_textes': cahier_textes})


#vues pour les notes
@login_required
def mes_classes(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    try:
        professeur = Professeur.objects.get(user=request.user)  # Access Professeur through the 'user' field
        classes_attribuees = Professeur_Classe.objects.filter(Q(annee_scolaire=annee_active) & Q(professeur=professeur))

        eleves_par_classe = {}
        for classe_attribuee in classes_attribuees:
            eleves_par_classe[classe_attribuee.classe.fusion] = Eleve.objects.filter(classe=classe_attribuee.classe.fusion)

        return render(request, 'personne/all_eleve.html', {'eleves_par_classe': eleves_par_classe})
    except Professeur.DoesNotExist:
        #Handle the case where a professor profile does not exist for the user.
        return render(request, 'personne/all_eleve.html', {'error':"Votre profil professeur n'existe pas"})


@login_required
def fiche_notes(request, classe_nom):
    trimestre = Trimestre.objects.filter(active=True).first()
    try:
        professeur = Professeur.objects.get(user=request.user)
        matiere = professeur.matiere
        matiere_actuelle = matiere.sigle
        classe = Classe_exist.objects.get(fusion=classe_nom)
        classe_existe = classe.fusion
        classe_attribuee = Professeur_Classe.objects.get(professeur=professeur, classe=classe)
        eleves = Eleve.objects.filter(classe=classe_nom)
        notes = Note.objects.filter(eleve__classe=classe_nom, matiere_id=matiere.id, trimestre=trimestre)
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        coefficient_classe = Coefficient.objects.get(classe=classe_existe, annee_scolaire=annee_active, matiere=matiere_actuelle)
        coefficient_val = float(coefficient_classe.coefficient)

        notes_par_eleve = defaultdict(list)
        for note in notes:
            notes_par_eleve[note.eleve].append(note)

        # Calcul des moyennes
        eleves_avec_moyennes = []
        for eleve in eleves:
            eleve_data = {
                'eleve': eleve,
                'notes': notes_par_eleve[eleve],
                'moyenne_interro': 0,
                'moyenne_generale': 0,
                'moyenne_coefficientee': 0,
                'coefficient': coefficient_classe,
            }

            # Calcul de la moyenne d'interrogation (avec prise en compte des cas où interro 3 n'est pas rempli)
            interro_notes = [note.note for note in notes_par_eleve[eleve] if note.option in ['Interro 1', 'Interro 2', 'Interro 3']]
            if interro_notes:
                if len(interro_notes) >= 2:
                    eleve_data['moyenne_interro'] = round(sum(interro_notes[:2]) / min(len(interro_notes), 2), 2)
                elif len(interro_notes) == 1:
                    eleve_data['moyenne_interro'] = interro_notes[0] #Si une seule note d'interro.
                else:
                    eleve_data['moyenne_interro'] = 0 # Si aucune note d'interro.

            # Récupération des notes Devoir 1 et Devoir 2
            devoir_notes = {note.option: note.note for note in notes_par_eleve[eleve] if note.option in ['Devoir 1', 'Devoir 2']}
            devoir1 = devoir_notes.get('Devoir 1', 0)
            devoir2 = devoir_notes.get('Devoir 2', 0)

            # Calcul de la moyenne générale
            if eleve_data['moyenne_interro'] or devoir1 or devoir2:
                eleve_data['moyenne_generale'] = round((eleve_data['moyenne_interro'] + devoir1 + devoir2) / 3, 2)

            # Calcul de la moyenne coefficientée
            eleve_data['moyenne_coefficientee'] = round(float(eleve_data['moyenne_generale']) * coefficient_val, 2)

            if eleve_data['moyenne_coefficientee'] >= (coefficient_val * 10):
                eleve_data['message'] = "Coefficienté"
            else:
                eleve_data['message'] = "Non Coefficienté"

            eleves_avec_moyennes.append(eleve_data)

        return render(request, 'notes/fiche_notes.html', {
            'eleves_avec_moyennes': eleves_avec_moyennes,
            'matiere': matiere,
            'classe_nom': classe_nom,
            'eleves_par_classe': {classe_nom: eleves}
        })
    except Professeur.DoesNotExist:
        return render(request, 'notes/fiche_notes.html', {'error': "Votre profil professeur n'existe pas.", 'eleves_par_classe': {}})
    except Classe_exist.DoesNotExist:
        return render(request, 'notes/fiche_notes.html', {'error': "Classe non trouvée.", 'eleves_par_classe': {}})
    except Professeur_Classe.DoesNotExist:
        return render(request, 'notes/fiche_notes.html', {'error': "Classe non attribuée à ce professeur.", 'eleves_par_classe': {}})
    except Coefficient.DoesNotExist:
        return render(request, 'notes/fiche_notes.html', {'error': "Coefficient non trouvé pour cette classe.", 'eleves_par_classe': {}})

@login_required
def ajouter_coefficient(request):
    if request.method == 'POST':
        classe = request.POST.get('classe')
        matiere = request.POST.get('matiere')
        coefficient = request.POST.get('coefficient')
        annee_active = AnneeScolaire.objects.filter(active=True).first()

        existing_coefficient = Coefficient.objects.filter(Q(coefficient=coefficient) & Q(classe=classe) & Q(matiere=matiere)).exists()

        if existing_coefficient:
            messages.error(request, "Ce coefficient a déjà été enregistré pour cette matière.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            # Validation simple
            if coefficient and classe and matiere:
                Coefficient.objects.create(classe=classe, matiere=matiere, coefficient=coefficient, annee_scolaire=annee_active)
                messages.success(request, "Coefficient enregistré!")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                messages.error(request, "Tous les champs sont requis.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def ajout_notes(request, classe_nom):
    trimestre = Trimestre.objects.filter(active=True).first()
    try:
        professeur = Professeur.objects.get(user=request.user)
        matiere = professeur.matiere
        classe = Classe_exist.objects.get(fusion=classe_nom)
        classe_attribuee = Professeur_Classe.objects.get(professeur=professeur, classe=classe)
        eleves = Eleve.objects.filter(classe=classe_nom)
        notes = Note.objects.filter(eleve__classe=classe_nom, matiere_id=matiere.id,trimestre=trimestre) 

        notes_par_eleve = defaultdict(list)
        for note in notes:
            notes_par_eleve[note.eleve].append(note)

        return render(request, 'notes/gestion_notes.html', {'eleves': eleves, 'notes_par_eleve': notes_par_eleve, 'matiere': matiere, 'classe_nom': classe_nom, 'eleves_par_classe': {classe_nom:eleves} })
    except Professeur.DoesNotExist:
        return render(request, 'notes/gestion_notes.html', {'error': "Votre profil professeur n'existe pas.", 'eleves_par_classe': {}})
    except Classe_exist.DoesNotExist:
        return render(request, 'notes/gestion_notes.html', {'error': "Classe non trouvée.", 'eleves_par_classe': {}})
    except Professeur_Classe.DoesNotExist:
        return render(request, 'notes/gestion_notes.html', {'error': "Classe non attribuée à ce professeur.", 'eleves_par_classe': {}})


@login_required
def enregistrer_note(request):
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve_id')
        matiere_id = request.POST.get('matiere_id')
        option = request.POST.get('option')
        note_value = request.POST.get('note')
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        trimestre_active = Trimestre.objects.filter(active=True).first()

        try:
            eleve = Eleve.objects.get(id_eleve=eleve_id)
            matiere = Matiere.objects.get(id=matiere_id)

            # Vérifier si une note existe déjà
            existing_note = Note.objects.filter(
                eleve=eleve,
                matiere=matiere,
                option=option,
                trimestre=trimestre_active,
                annee_scolaire=annee_active
            ).first()

            if existing_note:
                messages.error(request, f"Une note pour {option} existe déjà pour cet élève et cette matière.")
            else:
                # Créer et enregistrer la nouvelle note
                note = Note(
                    eleve=eleve,
                    matiere=matiere,
                    option=option,
                    note=note_value,
                    trimestre=trimestre_active,
                    annee_scolaire=annee_active
                )
                note.save()
                messages.success(request, "Note enregistrée avec succès.")

        except (Eleve.DoesNotExist, Matiere.DoesNotExist):
            messages.error(request, "Élève ou matière introuvable.")
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {e}")

        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def enregistrer_resultats(request):
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve_id')
        matiere_id = request.POST.get('matiere_id')
        moyenne_interro = request.POST.get('moyenne_interro')
        moyenne_generale = request.POST.get('moyenne_generale')
        moyenne_coefficientee = request.POST.get('moyenne_coefficientee')
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        trimestre_active = Trimestre.objects.filter(active=True).first()

        # Vérifier si un enregistrement existe déjà
        if ResultatEleve.objects.filter(
            eleve_id=eleve_id,
            matiere_id=matiere_id,
            annee_scolaire=annee_active,
            trimestre=trimestre_active
        ).exists():
            messages.error(request, "Un enregistrement existe déjà pour cet élève et cette matière.")
        else:
            # Enregistrer les données dans votre modèle
            resultat = ResultatEleve(
                eleve_id=eleve_id,
                matiere_id=matiere_id,
                moyenne_interro=moyenne_interro,
                moyenne_generale=moyenne_generale,
                moyenne_coefficientee=moyenne_coefficientee,
                trimestre=trimestre_active,
                annee_scolaire=annee_active
            )
            resultat.save()
            messages.success(request, "Enregistrement réussi.")

        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def all_fiche_notes(request):
    # Récupérer tous les résultats
    resultats = ResultatEleve.objects.all()

    context = {
        'resultats': resultats,
    }

    return render(request, 'notes/all_fiche_notes.html', context)



#vues pour les bulletins
@login_required
def eleve1(request):
    eleve6 = Eleve.objects.filter(classe="6ème")
    eleve5 = Eleve.objects.filter(classe="5ème")
    eleve4 = Eleve.objects.filter(classe="4ème")
    eleve3 = Eleve.objects.filter(classe="3ème")
    return render(request, 'bulletins/eleve_cycle1.html', {'eleve6': eleve6, 'eleve5': eleve5, 'eleve4': eleve4, 'eleve3': eleve3})
@login_required
def eleve2(request):
    eleve0 = Eleve.objects.filter(classe="2nde")
    eleve1 = Eleve.objects.filter(classe="1ère")
    eleve2 = Eleve.objects.filter(classe="Tle")
    return render(request, 'bulletins/eleve_cycle2.html', {'eleve0': eleve0, 'eleve1': eleve1, 'eleve2': eleve2})
@login_required
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

@login_required
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

@login_required
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

@login_required
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

@login_required
def verification(request):
    eleves = Eleve.objects.all()
    return render(request, 'bulletins/check.html', {'eleves': eleves})

# Fonction utilitaire pour convertir une chaîne en float
@login_required
def convert_to_float(value):
    try:
        return float(value.replace(',', '.'))
    except (ValueError, AttributeError):
        return 0.0

@login_required
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

