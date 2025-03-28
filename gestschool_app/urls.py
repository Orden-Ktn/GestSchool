from django.urls import path
from django.contrib import admin
# from .views import register, user_login, user_logout
from . import views

urlpatterns = [

    path('', views.login_view, name='login_view'),
    path('connexion/', views.login_view, name='login_view'),
    path('inscription/', views.register, name='register'),
    path('déconnexion/', views.deconnexion, name='deconnexion'),
    path('index/', views.index, name='index'),

#urls pour professeur
    path('profile/', views.profile, name='profile'),
    path('professeur/', views.professeur, name='professeur'),
    path('editer profile/', views.editer_profile, name='editer_profile'),
    path('attribuer classe professeur/', views.attribuer_classe_professeur, name='attribuer_classe_professeur'),
    path('supprimer professeur/<int:id>/', views.delete_professeur, name='delete_professeur'),

#urls des matières 
    path('matière/', views.matiere, name='matiere'),
    path('ajouter matière/', views.ajouter_matiere, name='ajouter_matiere'),


#urls des finances 
    path('tarif/', views.tarif, name='tarif'),
    path('fiche de paiement/', views.fiche_paiement, name='fiche_paiement'),
    path('modifier_solde/<int:eleve_id>/', views.modifier_solde, name='modifier_solde'),
    path('ajouter tarif/', views.ajouter_tarif, name='ajouter_tarif'),
    path('modifier tarif/<int:id>/', views.modify_tarif, name='modify_tarif'),


#urls des annees
    path('ajouter année scolaire/', views.ajouter_annee, name='ajouter_annee'),
    path('année scolaire/', views.annee_scolaire, name='annee_scolaire'),
    path('annees/activer/<int:annee_id>/', views.activer_annee, name='activer_annee'),
    

#urls des trimestre
    path('ajouter trimestre/', views.ajouter_trimestre, name='ajouter_trimestre'),
    path('timestre/', views.trimestre, name='trimestre'),
    path('trimestres/activer/<int:trimestre_id>/', views.activer_trimestre, name='activer_trimestre'),



#urls des classes
    path('ajouter classe/', views.ajouter_classe, name='ajouter_classe'),
    path('classe/', views.classe, name='classe'),


#urls des emplois
    path('ajouter emploi/', views.ajouter_emploi, name='ajouter_emploi'),
    path('emploi/', views.emploi, name='emploi'),
    path('supprimer emploi/<int:id>/', views.delete_emploi, name='delete_emploi'),



#urls des eleves
    path('ajouter élève/', views.ajouter_eleve, name='ajouter_eleve'),
    path('élève/', views.eleve, name='eleve'),
    path('modifier elève/<int:id_eleve>/', views.modify_information, name='modify_information'),
    path('supprimer élève/<int:id_eleve>/', views.delete_student, name='delete_student'),


#urls pour les notes
    path('mes classes/', views.mes_classes, name='mes_classes'),
    path('élève/', views.eleve, name='eleve'),
    path('fiche de notes classe/<str:classe_nom>/', views.fiche_notes, name='fiche_notes'),
    path('ajout de notes classe/<str:classe_nom>/', views.ajout_notes, name='ajout_notes'),
    path('enregistrer_note/', views.enregistrer_note, name='enregistrer_note'),
    path('ajouter_coefficient/', views.ajouter_coefficient, name='ajouter_coefficient'),
    path('enregistrer_resultats/', views.enregistrer_resultats, name='enregistrer_resultats'),
    path('fiches de notes/', views.all_fiche_notes, name='all_fiche_notes'),
    

#urls pour cahier de texte
    path('cahier de texte/<str:classe_nom>/', views.cahier_texte, name='cahier_texte'),
    path('ajouter_contenu_cahier_texte/', views.ajouter_contenu_cahier_texte, name='ajouter_contenu_cahier_texte'),
    path('cahier_texte/', views.visualisation_cahier_texte, name='visualisation_cahier_texte'),


#urls pour les bulletins
    path('élève cycle1/', views.eleve1, name='eleve1'),
    path('élève cycle2/', views.eleve2, name='eleve2'),
    path('bulletin trimestre 1/<int:id_eleve>/', views.bulletin_trim1, name='bulletin_trim1'),
    path('bulletin trimestre 2/<int:id_eleve>/', views.bulletin_trim2, name='bulletin_trim2'),
    path('bulletin trimestre 3/<int:id_eleve>/', views.bulletin_trim3, name='bulletin_trim3'),
    path('save bulletin/', views.save_bulletin, name='save_bulletin'),
    path('vérification/', views.verification, name='verification'),
    path('download/', views.download, name='download'),

#urls pour les utilisateurs
    path('personnel/', views.personnel, name='personnel'),
    path("modifier_role/", views.modifier_role, name="modifier_role"),
    path('supprimer_utilisateur/<int:personnel_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),

]
