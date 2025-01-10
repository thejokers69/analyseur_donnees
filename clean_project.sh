#!/bin/bash

# Activer l'environnement virtuel
source env/bin/activate

# Nettoyer les fichiers inutiles avec pyclean
pyclean .

# Désactiver l'environnement virtuel
deactivate

# Confirmation du nettoyage
echo "Nettoyage terminé avec pyclean."