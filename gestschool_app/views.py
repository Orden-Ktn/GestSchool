from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, ChangeUserForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .models import *
import time
from plyer import notification
from django.db.models import Count, F, Value, Window
from django.db.models.functions import Rank



#vue pour l'inscription
def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form = CustomUserCreationForm()
    return render(request, 'compte/inscription.html', {'form': form})


#vue pour la connexion
def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            return render(request, 'compte/connexion.html')
        
    return render(request, 'compte/connexion.html')

def lock_screen(request):
    return render(request, 'compte/lock_screen.html')


def deverouillage(request):
    if request.method == 'POST':
        password = request.POST['password']
        username = request.POST['username']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Nom d\'utilisateur ou Mot de passe incorrect.')

    return render(request, 'compte/lock_screen.html')
    
      
@login_required
def index(request):
    total_classes = Classe_exist.objects.count()
    total_students = Eleve.objects.count()
    total_students_boys = Eleve.objects.filter(sexe='M').count()
    total_students_girls = Eleve.objects.filter(sexe='F').count()
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    pourcentage_boys = (total_students_boys  * 100 )/total_students
    pourcentage_girls = (total_students_girls  * 100 )/total_students
    p_g = float(pourcentage_girls)
    percent_girls =round(p_g,2)
    percent_boys =round(pourcentage_boys,2)

    context = {
        'total_classes': total_classes,
        'total_students': total_students,
        'total_students_boys': total_students_boys,
        'total_students_girls':total_students_girls,
        'percent_boys':percent_boys,
        'percent_girls':percent_girls,
        'annee_active': annee_active}
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
def ajout_matiere(request):
    return render(request, 'matieres/ajout_matiere.html')

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
               return render(request, 'ajout_matiere.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return render(request, 'ajout_matiere.html')   

def liste_matieres(request):
       # Récupération de toutes les matieres
       matieres = Matiere.objects.all()
       return render(request, 'matieres/liste_matieres.html', {'matieres': matieres})





#vues pour les classes
def ajout_classe(request):
    return render(request, 'classes/ajout_classe.html')

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
               return render(request, 'ajout_classe.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return render(request, 'ajout_classe.html')    
 
def liste_classes(request):
       # Récupération de toutes les classes
       classes = Classe.objects.all()
       emplois = Emploi.objects.filter()
       return render(request, 'classes/liste_classes.html', {'classes': classes, 'emplois': emplois})




#vues pour les classes
def ajout_annee(request):
    return render(request, 'annee/ajout_annee.html')

def ajouter_annee(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        annee = request.POST.get('annee')

        existing_annee = AnneeScolaire.objects.filter(annee=annee).exists()

        if existing_annee:
            messages.error(request, "Cette anneée a déjà été enregistrée.")
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
               return render(request, 'annee/ajout_annee.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return render(request, 'annee/ajout_annee.html')    

def activer_annee(request, annee_id):
    # Désactiver toutes les années scolaires
    AnneeScolaire.objects.update(active=False)
   
    # Activer l'année scolaire sélectionnée
    annee = AnneeScolaire.objects.get(id=annee_id)
    annee.active = True
    annee.save()

    return redirect('liste_annees')  # Rediriger vers la vue de liste des années scolaires

def liste_annees(request):
       # Récupération de toutes les annees
       annees = AnneeScolaire.objects.all()
       return render(request, 'annee/liste_annee.html', {'annees': annees})






#vues pour les séries
def ajout_serie(request):
    return render(request, 'series/ajout_serie.html')

def ajouter_serie(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        serie = request.POST.get('serie')
        
        existing_serie = Serie.objects.filter(intitule=serie).exists()

        if existing_serie:
            messages.error(request, "Cette série a déjà été enregistrée.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
           # Validation simple
           if serie:
               # Création de l'objet serie et sauvegarde dans la base de données
               Serie.objects.create(intitule=serie)
               messages.success(request, "Série enregistrée.")
               return redirect(request.META.get('HTTP_REFERER', '/'))
           else:
               # Gérer les erreurs si les données sont invalides
               return render(request, 'ajout_serie.html', {'error': 'Tous les champs sont requis.'})
           
        except ValueError as e:
            # Gérer les erreurs de conversion
            messages.error(request, 'Veuillez bien renseigner les informations.')

    return render(request, 'ajout_serie.html')

def liste_series(request):
       # Récupération de toutes les series
       series = Serie.objects.all()
       return render(request, 'series/liste_series.html', {'series': series})




#vues pour les emplois
def ajout_emploi(request):
    return render(request, 'emploi/ajout_emploi.html')

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
        serie = request.POST.get('serie')

        fusion = f"{classe}/{serie}"

        existing_emploi = Emploi.objects.filter(classe=classe, serie=serie).exists()

        if existing_emploi:
            error_message = messages.error(request, "L'emploi du temps a été enregistré pour cette classe.")
            return redirect(request.META.get('HTTP_REFERER', '/'),{'error_message': error_message} )
        
        try:
            if cours1 and cours2 and cours3 and cours4 and cours5 and cours6 and cours7 and cours8 and cours9 and cours10 and cours11 and cours12 and cours13 and cours14 and cours15 and cours16 and cours17 and cours18 and cours19 and cours20 and classe and serie:
                # Création de l'objet Classe et sauvegarde dans la base de données
                Emploi.objects.create(cours1=cours1, cours2=cours2, cours3=cours3, cours4=cours4, cours5=cours5, cours6=cours6, cours7=cours7, cours8=cours8, cours9=cours9, cours10=cours10, cours11=cours11, cours12=cours12, cours13=cours13, cours14=cours14, cours15=cours15, cours16=cours16, cours17=cours17, cours18=cours18, cours19=cours19, cours20=cours20, classe=classe, serie=serie)
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

def liste_emploi(request):
    emploi1 = Emploi.objects.filter()
    return render(request, 'emploi/liste_emplois.html', {'emploi1': emploi1})





#vues pour les eleves
def ajout_eleve(request):
    return render(request, 'eleves/ajout_eleve.html')

def ajout_eleve(request):
    classes = Classe.objects.all()
    series = Serie.objects.all()
    return render(request, 'eleves/ajout_eleve.html', {'classes': classes, 'series': series})

def ajouter_eleve(request):
    if request.method == 'POST':
           # Récupération des données du formulaire
           nom = request.POST.get('nom')
           prenom = request.POST.get('prenom')
           sexe = request.POST.get('sexe')
           date_naissance = request.POST.get('date')
           contact = request.POST.get('contact')
           classe = request.POST.get('classe')
           serie = request.POST.get('serie')
           statut = request.POST.get('statut')

           annee_active = AnneeScolaire.objects.filter(active=True).first()
           
           # Validation simple
           if nom and prenom and sexe and statut and date_naissance and contact and classe and serie and statut:
               # Création de l'objet Classe et sauvegarde dans la base de données
               Eleve.objects.create(
                    nom=nom, 
                    prenom=prenom, 
                    sexe=sexe, 
                    date_naissance=date_naissance, 
                    contact=contact, 
                    classe=classe, 
                    serie=serie, 
                    statut=statut, 
                    annee_scolaire=annee_active) 
               messages.success(request, "Enregistrement réussie!")
               return redirect(request.META.get('HTTP_REFERER', '/'))
           else:
               # Gérer les erreurs si les données sont invalides
               return render(request, 'ajout_eleve.html', {'error': 'Tous les champs sont requis.'})

    return render(request, 'ajout_eleve.html')  

def liste_eleve_cycle1(request):
       annee_active = AnneeScolaire.objects.filter(active=True).first()
       eleve6 = Eleve.objects.filter(classe="6ème", annee_scolaire_id=annee_active)
       eleve5 = Eleve.objects.filter(classe="5ème", annee_scolaire_id=annee_active)
       eleve4 = Eleve.objects.filter(classe="4ème", annee_scolaire_id=annee_active)
       eleve3 = Eleve.objects.filter(classe="3ème", annee_scolaire_id=annee_active)
       return render(request, 'eleves/liste_eleve_cycle1.html', {'eleve6': eleve6, 'eleve5': eleve5, 'eleve4': eleve4, 'eleve3': eleve3})

def liste_eleve_cycle2(request):

       annee_active = AnneeScolaire.objects.filter(active=True).first()
       eleve0 = Eleve.objects.filter(classe="2nde", annee_scolaire_id=annee_active)
       eleve1 = Eleve.objects.filter(classe="1ère", annee_scolaire_id=annee_active)
       eleve2 = Eleve.objects.filter(classe="Tle", annee_scolaire_id=annee_active)
       return render(request, 'eleves/liste_eleve_cycle2.html', {'eleve0': eleve0, 'eleve1': eleve1, 'eleve2': eleve2})

def all_eleve(request):
       # Récupération de toutes les eleves1
       annee_active = AnneeScolaire.objects.filter(active=True).first()
       eleves = Eleve.objects.filter(annee_scolaire_id=annee_active).order_by('nom')

       return render(request, 'eleves/all_eleve.html', {'eleves': eleves})

def modify_information(request, id_eleve):
    eleve = Eleve.objects.get(id_eleve=id_eleve)
    classes = Classe.objects.all()
    series = Serie.objects.all()
    if request.method == 'POST':
        eleve.nom = request.POST['nom']
        eleve.prenom = request.POST['prenom']
        eleve.sexe = request.POST['sexe']
        eleve.date_naissance = request.POST['date']
        eleve.contact = request.POST['contact']
        eleve.classe = request.POST['classe']
        eleve.statut = request.POST['statut']
        
        eleve.save()
        return redirect('all_eleve')
    return render(request, 'eleves/modify_information.html', {'classes': classes, 'eleve': eleve, 'series': series})

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
def eleve_cycle1(request):
       eleve6 = Eleve.objects.filter(classe="6ème")
       eleve5 = Eleve.objects.filter(classe="5ème")
       eleve4 = Eleve.objects.filter(classe="4ème")
       eleve3 = Eleve.objects.filter(classe="3ème")
       return render(request, 'notes/eleve_cycle1.html', {'eleve6': eleve6, 'eleve5': eleve5, 'eleve4': eleve4, 'eleve3': eleve3})

def eleve_cycle2(request):
       eleve0 = Eleve.objects.filter(classe="2nde")
       eleve1 = Eleve.objects.filter(classe="1ère")
       eleve2 = Eleve.objects.filter(classe="Tle")
       return render(request, 'notes/eleve_cycle2.html', {'eleve0': eleve0, 'eleve1': eleve1, 'eleve2': eleve2})

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








