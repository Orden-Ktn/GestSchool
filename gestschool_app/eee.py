@login_required
def fiche_notes(request, classe_nom):
    trimestre = Trimestre.objects.filter(active=True).first()
    try:
        professeur = Professeur.objects.get(user=request.user)
        matiere = professeur.matiere
        classe = Classe_exist.objects.get(fusion=classe_nom)
        classe_attribuee = Professeur_Classe.objects.get(professeur=professeur, classe=classe)
        eleves = Eleve.objects.filter(classe=classe_nom)
        notes = Note.objects.filter(eleve__classe=classe_nom, matiere_id=matiere.id, trimestre=trimestre)

        # Préparation des notes par élève
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
            }

            # Calcul de la moyenne d'interrogation (avec les trois notes)
            interro_notes = [note.note for note in notes_par_eleve[eleve] if note.option in ['Interro 1', 'Interro 2', 'Interro 3']]
            if interro_notes:
                eleve_data['moyenne_interro'] = sum(interro_notes) / len(interro_notes)

            # Récupération des notes Devoir 1 et Devoir 2
            devoir_notes = {note.option: note.note for note in notes_par_eleve[eleve] if note.option in ['Devoir 1', 'Devoir 2']}
            devoir1 = devoir_notes.get('Devoir 1', 0)
            devoir2 = devoir_notes.get('Devoir 2', 0)

            # Calcul de la moyenne générale
            if eleve_data['moyenne_interro'] or devoir1 or devoir2:
                eleve_data['moyenne_generale'] = round((eleve_data['moyenne_interro'] + devoir1 + devoir2) / 3, 2)

            eleves_avec_moyennes.append(eleve_data)

        return render(request, 'fiche_notes.html', {
            'eleves_avec_moyennes': eleves_avec_moyennes,
            'matiere': matiere,
            'classe_nom': classe_nom,
            'eleves_par_classe': {classe_nom: eleves}
        })
    except Professeur.DoesNotExist:
        return render(request, 'fiche_notes.html', {'error': "Votre profil professeur n'existe pas.", 'eleves_par_classe': {}})
    except Classe_exist.DoesNotExist:
        return render(request, 'fiche_notes.html', {'error': "Classe non trouvée.", 'eleves_par_classe': {}})
    except Professeur_Classe.DoesNotExist:
        return render(request, 'fiche_notes.html', {'error': "Classe non attribuée à ce professeur.", 'eleves_par_classe': {}})
