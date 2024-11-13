from django.urls import path
from django.contrib import admin
# from .views import register, user_login, user_logout
from . import views

urlpatterns = [
  
    path('inscription/', views.inscription, name='inscription'),
    path('', views.connexion, name='connexion'),
    path('déconnexion/', views.deconnexion, name='deconnexion'),
    path('modification des identifiants/', views.change_user, name='change_user'),
    path('ecran de verouillage/', views.lock_screen, name='lock_screen'),
    path('dévérouillage/', views.deverouillage, name='deverouillage'),
    path('index/', views.index, name='index'),



#urls des matières 
    path('ajout matière/', views.ajout_matiere, name='ajout_matiere'),
    path('liste matières/', views.liste_matieres, name='liste_matieres'),
    path('ajouter matière/', views.ajouter_matiere, name='ajouter_matiere'),



#urls des annees
    path('ajout année scolaire/', views.ajout_annee, name='ajout_annee'),
    path('ajouter année scolaire/', views.ajouter_annee, name='ajouter_annee'),
    path('liste années scolaires/', views.liste_annees, name='liste_annees'),
    path('annees/activer/<int:annee_id>/', views.activer_annee, name='activer_annee'),



#urls des classes
    path('ajout classe/', views.ajout_classe, name='ajout_classe'),
    path('ajouter classe/', views.ajouter_classe, name='ajouter_classe'),
    path('liste classes/', views.liste_classes, name='liste_classes'),
 


#urls des séries
    path('ajout série/', views.ajout_serie, name='ajout_serie'),
    path('liste séries/', views.liste_series, name='liste_series'),
    path('ajouter série/', views.ajouter_serie, name='ajouter_serie'),



#urls des emplois
    path('ajout emploi/', views.ajout_emploi, name='ajout_emploi'),
    path('ajouter emploi/', views.ajouter_emploi, name='ajouter_emploi'),
    path('liste emploi/', views.liste_emploi, name='liste_emploi'),



#urls des eleves
    path('ajout élève/', views.ajout_eleve, name='ajout_eleve'),
    path('ajouter élève/', views.ajouter_eleve, name='ajouter_eleve'),
    path('liste élèves premier cycle/', views.liste_eleve_cycle1, name='liste_eleve_cycle1'),
    path('liste élèves second cycle/', views.liste_eleve_cycle2, name='liste_eleve_cycle2'),
    path('modifier elève/<int:id_eleve>/', views.modify_information, name='modify_information'),
    path('supprimer élève/<int:id_eleve>/', views.delete_student, name='delete_student'),
    path('update/', views.update, name='update'),



#urls pour les notes
      path('élève premier cycle/', views.eleve_cycle1, name='eleve_cycle1'),
      path('élève second cycle/', views.eleve_cycle2, name='eleve_cycle2'),
      path('liste générale des élèves/', views.all_eleve, name='all_eleve'),
      path('ajout note/<int:id_eleve>/', views.ajout_note, name='ajout_note'),
      path('ajouter note/', views.ajouter_note, name='ajouter_note'),



#urls pour les bulletins
      path('élève cycle1/', views.eleve1, name='eleve1'),
      path('élève cycle2/', views.eleve2, name='eleve2'),
      path('bulletin trimestre 1/<int:id_eleve>/', views.bulletin_trim1, name='bulletin_trim1'),
      path('bulletin trimestre 2/<int:id_eleve>/', views.bulletin_trim2, name='bulletin_trim2'),
      path('bulletin trimestre 3/<int:id_eleve>/', views.bulletin_trim3, name='bulletin_trim3'),
      path('save bulletin/', views.save_bulletin, name='save_bulletin'),
      path('vérification/', views.verification, name='verification'),
      path('download/', views.download, name='download'),



      ]
