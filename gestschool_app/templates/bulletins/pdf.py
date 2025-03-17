import pdfkit

# Configuration de wkhtmltopdf (Indiquer le chemin de l'exécutable si nécessaire)
config = pdfkit.configuration(wkhtmltopdf='C:\FICHIERS D\'INSTALLATION\wkhtmltopdf')

# HTML à convertir
html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <title>Bulletin de Notes</title>
</head>
<body>
<div class="row o-hidden border-0 shadow-lg my-5 table-responsive">
    <div class="p-5">
        <img class="img-profile rounded-circle" style="border-radius:50%; height: auto; width: 80px;" src="/static/image/img1.png">
        <div style="text-align: center; margin-top:-7.5%;">
            <p style="font-size: medium; font-weight:bolder; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                REPUBLIQUE DU BENIN <br> MINISTERE DES ENSEIGNEMENTS SECONDAIRE, TECHNIQUE <br> ET DE LA
                FORMATION PROFESSIONNELLE <br> <br> COMPLEXE SCOLAIRE GESTSCHOOL
            </p>
        </div>
        <img class="img-profile rounded-circle" style="border-radius:50%; height: auto; width: 80px; margin-left:90%;" src="/static/image/logo_gestschool.png">
        <h1 style="text-align: center; font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;">
            BULLETIN DE NOTES
        </h1>
        <table class="table table-bordered" style="color: black;">
            <thead>
                <tr>
                    <th style="text-align: center;">IDENTIFIANT</th>
                    <th style="text-align: center;">NOM</th>
                    <th style="text-align: center;">PRENOMS</th>
                    <th style="text-align: center;">SEXE</th>
                    <th style="text-align: center;">CLASSE</th>
                    <th style="text-align: center;">STATUT</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="text-align: center;">{{ eleve.id_eleve }}</td>
                    <td style="text-align: center;">{{ eleve.nom }}</td>
                    <td style="text-align: center;">{{ eleve.prenom }}</td>
                    <td style="text-align: center;">{{ eleve.sexe }}</td>
                    <td style="text-align: center;">{{ eleve.classe }} {{ eleve.serie }}</td>
                    <td style="text-align: center;">{{ eleve.statut }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
"""

# Options de configuration pour le PDF
options = {
    'page-size': 'A4',
    'encoding': 'UTF-8',
    'no-outline': None,
}

# Chemin du fichier de sortie
output_file = 'bulletin_notes.pdf'

# Génération du PDF
pdfkit.from_string(html_content, output_file, configuration=config, options=options)

print(f"Le PDF a été généré et enregistré sous le nom : {output_file}")
