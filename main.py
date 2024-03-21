
import os
import streamlit as st
import shutil
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# on souhaite ici accéder à Azure, afin de pouvoir modifier en live la base de données
account_url = "https://visionannotation.blob.core.windows.net"
account_key = "ChrAuRqiX7eMyPTPZzPvAp8RI0J5Cw/2FG0DR8tReMshhdqTmfAwXe5AVduy33dV9D5JmCjw2S7X+AStx9/WWg=="
container_name_initial = "annotation"
container_name_clean = "annotationclean"

# on teste 2-3 choses avec Azure
blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)

# Récupérez le conteneur spécifié
container_client_initial = blob_service_client.get_container_client(container_name_initial)
container_client_clean = blob_service_client.get_container_client(container_name_clean)


# Titre de la page
st.title("Application d'annotation d'images pour créer un dataset propre")

# Sélection de l'onglet dans la barre latérale
onglet_selectionne = st.sidebar.radio("Navigation", ["Colère", "Dégoût", "Joie", "Angoisse", "Tristesse", "Neutre", "Surprise"])

# Affichage du contenu de la sous-page en fonction de l'onglet 


def set_custom_variable(custom_variable_name, new_value):
    st.session_state[custom_variable_name] = new_value

# fonction importante
def page(chemin_fichier,chemin_valide, chemin_invalide,emotion):
    # partie image
    path = chemin_fichier
    path_valide = chemin_valide
    path_invalide = chemin_invalide
    
    # Chemin local de votre image
    
    
    liste_fichier = os.listdir(path)
    liste_chemin = [path + fichier for fichier in liste_fichier]
    liste_chemin_valide = [path_valide + fichier for fichier in liste_fichier]
    liste_chemin_invalide = [path_invalide + fichier for fichier in liste_fichier]
    
    var_index = 'current_index_'+emotion
    var_restant = 'nombre_restant_'+emotion
    current_f = 'nom_fichier_' + emotion
    
    current_index = st.session_state.get(var_index, 0)
    current_fichier = st.session_state.get(current_f, liste_fichier[0])
    nombre_restant = st.session_state.get(var_restant, len(liste_fichier))
    
    
    st.write("Encore "+ str(nombre_restant) + " images à traiter dans cette catégorie")
    st.write("Nom de l'image: "+ str(current_fichier))
    
    col1, col2 = st.columns(2)
    
    st.image(liste_chemin[current_index], caption='Image actuelle', use_column_width=True)
    
    # definition des colonnes
    
    with col1:
        if st.button('Valide'):
            shutil.move(liste_chemin[current_index], liste_chemin_valide[current_index])
            del liste_chemin[current_index]
            del liste_fichier[0]
            
            # remplacement du fichier dans la base clean, puis on supprime de la base initiale
            fichier_azure_initial =  container_client_initial.get_blob_client(current_fichier)
            # recuperation contenu
            content_fichier_azure_initial = fichier_azure_initial.download_blob().readall()
            # ecriture base
            fichier_azure_ecriture = container_client_clean.get_blob_client(current_fichier)
            fichier_azure_ecriture.upload_blob(content_fichier_azure_initial)
            # suppression dans la base initiale
            fichier_azure_initial.delete_blob()
            
            # Vérifier l'état de l'image actuelle et mettre à jour en conséquence
            #current_index = (current_index + 1) % len(liste_chemin)
            nombre_restant = len(liste_chemin)
            current_fichier = liste_fichier[0]
            #set_custom_variable(var_index, current_index)
            set_custom_variable(var_restant, nombre_restant)
            set_custom_variable(current_f, current_fichier)
            st.experimental_rerun()
    
    
    with col2:
        if st.button('Invalide'):
            shutil.move(liste_chemin[current_index], liste_chemin_invalide[current_index])
            del liste_chemin[current_index]
            del liste_fichier[0]
            
            # suppression du fichier via Azure, dans la base initiale
            blob_client = container_client_initial.get_blob_client(current_fichier)
            # suppression
            blob_client.delete_blob()
            
            # Vérifier l'état de l'image actuelle et mettre à jour en conséquence
            #current_index = (current_index + 1) % len(liste_chemin)
            nombre_restant = len(liste_chemin)
            current_fichier = liste_fichier[0]
            #set_custom_variable(var_index, current_index)
            set_custom_variable(var_restant, nombre_restant)
            set_custom_variable(current_f, current_fichier)
            st.experimental_rerun()


def create_path(chaine):
    c1 = "data/train/" + chaine + "/"
    c2 = "data/triage/" + chaine + "/valid/"
    c3 = "data/triage/" + chaine + "/invalid/"
    return c1,c2,c3


if onglet_selectionne == "Colère":
    st.header("La colère")
    a,b,c = create_path("angry")
    page(a,b,c,'angry')
    
elif onglet_selectionne == "Dégoût":
    st.header("Le dégoût")
    a,b,c = create_path("disgust")
    page(a,b,c,'disgust')
    
elif onglet_selectionne == "Joie":
    st.header("La joie")
    a,b,c = create_path("happy")
    page(a,b,c,'happy')
    
elif onglet_selectionne == "Angoisse":
    st.header("L'angoisse")
    a,b,c = create_path("fear")
    page(a,b,c,'fear')

elif onglet_selectionne == "Tristesse":
    st.header("La tristesse")
    a,b,c = create_path("sad")
    page(a,b,c,'sad')
    
elif onglet_selectionne == "Neutre":
    st.header("Visage neutre")
    a,b,c = create_path("neutral")
    page(a,b,c,'neutral')

elif onglet_selectionne == "Surprise":
    st.header("La surprise")
    a,b,c = create_path("surprise")
    page(a,b,c,'surprise')