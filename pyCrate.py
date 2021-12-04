import time

from fourni import simulateur
from fourni import personnage as p
from fourni import caisse as c
from fourni import case_vide as cv
from fourni import mur as m
from outils import \
    creer_image, \
    creer_caisse, creer_case_vide, creer_cible, creer_mur, creer_personnage, \
    coordonnee_x, coordonnee_y, est_egal_a

# Constante à utiliser

VALEUR_COUP: int = 50


# Fonctions à développer

def jeu_en_cours(caisses: list, cibles: list) -> bool:
    """
    Fonction testant si le jeu est encore en cours et retournant un booléen comme réponse sur l'état de la partie.
    :param caisses: La liste des caisses du niveau en cours
    :param cibles: La liste des cibles du niveau en cours
    :return: True si la partie est finie, False sinon
    """
    total_cible_filled: int = 0

    for cible in cibles:
        for caisse in caisses:
            total_cible_filled += 1 if est_egal_a(cible, caisse) else 0

    if total_cible_filled == len(cibles):
        return True
    else:
        return False


def charger_niveau(joueur: list, caisses: list, cibles: list, murs: list, path: str):
    """
    Fonction permettant de charger depuis un fichier.txt et de remplir les différentes listes permettant le
    fonctionnement du jeu (joueur, caisses, murs, cibles)
    :param joueur: liste des personnages
    :param caisses: liste des caisses
    :param cibles: liste des cibles
    :param murs: liste des murs
    :param path: chemin du fichier.txt
    :return:
    """
    level = open(path, "r")
    for y, line in enumerate(level.readlines()):
        for x, item in enumerate(line):
            if item == '#':
                murs.append(creer_mur(x, y))
            elif item == '.':
                cibles.append(creer_cible(x, y))
            elif item == '$':
                caisses.append(creer_caisse(x, y))
            elif item == '@':
                joueur.append(creer_personnage(x, y))


def definir_mouvement(direction: str, can, joueur: list[p.Personnage], murs: list, caisses: list[c.Caisse], liste_image: list):
    """
    Fonction permettant de définir les cases de destinations (il y en a 2 si le joueur pousse une caisse) selon la
    direction choisie.
    :param direction: Direction dans laquelle le joueur se déplace (droite, gauche, haut, bas)
    :param can: Canvas (ignorez son fonctionnement), utile uniquement pour créer_image()
    :param joueur: liste des joueurs
    :param murs: liste des murs
    :param caisses: liste des caisses
    :param liste_image: liste des images (murs, caisses etc...) détaillée dans l'énoncé
    :return:
    """
    # Calculate the new coordinate of the player after the move
    new_player_position: cv.CaseVide = update_new_coordinate(joueur[0], direction)


    # Check if there is a crate on the next player position
    crate_index: int = -1
    new_crate_position: cv.CaseVide = cv.CaseVide(-1, -1)
    for i, caisse in enumerate(caisses):
        if caisse == new_player_position:
            new_crate_position: cv.CaseVide = update_new_coordinate(caisse, direction)
            crate_index = i
            break

    effectuer_mouvement(caisses, murs, joueur, can, new_player_position, liste_image, new_crate_position, crate_index)


def update_new_coordinate(_entity: object, _direction) -> cv.CaseVide:
    # Calculate the new coordinate of the player after the move
    x: int = _entity.get_x()
    y: int = _entity.get_y()

    if _direction == 'droite':
        x += 1

    elif _direction == 'gauche':
        x -= 1

    elif _direction == 'haut':
        y -= 1

    elif _direction == 'bas':
        y += 1

    return creer_case_vide(x, y)


def check_next_coordinate(_case_vide: cv.CaseVide, _murs: list[m.Mur], _caisses: list[c.Caisse]) -> bool:
    for mur in _murs:
        if _case_vide == mur:
            return False

    for caisse in _caisses:
        if _case_vide == caisse:
            return False

    return True


def effectuer_mouvement(caisses: list, murs: list, joueur: list[p.Personnage], can, _new_player_position: cv.CaseVide,
                        liste_image: list, _new_crate_position: cv.CaseVide = cv.CaseVide(-1, -1), _crate_index: int = -1):
    """
    Fonction permettant d'effectuer le déplacement ou de ne pas l'effectuer si celui-ci n'est pas possible.
    Voir énoncé "Quelques règles".
    Cette methode est appelée par mouvement.
    :param caisses: liste des caisses
    :param murs: liste des murs
    :param joueur: liste des joueurs
    :param can: Canvas (ignorez son fonctionnement), utile uniquement pour créer_image()
    :param _new_crate_position: coordonnée à laquelle la caisse va être déplacée (si le joueur pousse une caisse)
    :param _new_player_position: coordonnée à laquelle le joueur va être déplacée
    :param _crate_index : index of the crate to push in the crate list
    :param liste_image: liste des images (murs, caisses etc...) détaillée dans l'énoncé
    :return:
    """
    able_to_move: bool = True
    crate_to_push: bool = _new_crate_position.get_x() != -1

    if crate_to_push:
        able_to_move = check_next_coordinate(_new_crate_position, murs, caisses)
    else:
        able_to_move = check_next_coordinate(_new_player_position, murs, caisses)

    if able_to_move:
        creer_image(can, joueur[0].get_x(), joueur[0].get_y(), liste_image[6])
        joueur[0].set_x(_new_player_position.get_x())
        joueur[0].set_y(_new_player_position.get_y())
        creer_image(can, joueur[0].get_x(), joueur[0].get_y(), liste_image[4])
        if crate_to_push:
            creer_image(can, caisses[_crate_index].get_x(), caisses[_crate_index].get_y(), liste_image[6])
            caisses[_crate_index].set_x(_new_crate_position.get_x())
            caisses[_crate_index].set_y(_new_crate_position.get_y())
            creer_image(can, caisses[_crate_index].get_x(), caisses[_crate_index].get_y(), liste_image[2])



def chargement_score(scores_file_path: str, dict_scores: dict):
    """
    Fonction chargeant les scores depuis un fichier.txt et les stockent dans un dictionnaire
    :param scores_file_path: le chemin d'accès du fichier
    :param dict_scores:  le dictionnaire pour le stockage
    :return:
    """
    scores = open(scores_file_path, "r")
    for x, line in enumerate(scores.readlines()):
        dict_scores[x+1] = line[2:]


def maj_score(niveau_en_cours: int, dict_scores: dict[int, str]) -> str:
    """
    Fonction mettant à jour l'affichage des scores en stockant dans un str l'affichage visible
    sur la droite du jeu.
    ("Niveau x
      1) 7699
      2) ... ").
    :param niveau_en_cours: le numéro du niveau en cours
    :param dict_scores: le dictionnaire pour stockant les scores
    :return str: Le str contenant l'affichage pour les scores ("\n" pour passer à la ligne)
    """
    scores_str: str = ""
    scores_list: list[str] = dict_scores[niveau_en_cours].split(';')
    scores_str = '\n'.join([f'{i}) {score}' for i, score in enumerate(scores_list)])
    return scores_str


def calcule_score(temps_initial: float, nb_coups: int, score_base: int) -> int:
    """
    calcule le score du jouer
    :param temps_initial: debut du jeu
    :param nb_coups: nombre des mouvements
    :param score_base: score de base
    :return: le score du jouer
    """
    pass


def enregistre_score(temps_initial: float, nb_coups: int, score_base: int, dict_scores: dict,
                     niveau_en_cours: int):
    """
    Fonction enregistrant un nouveau score réalisé par le joueur. Le calcul de score est le suivant :
    score_base - (temps actuel - temps initial) - (nombre de coups * valeur d'un coup)
    Ce score est arrondi sans virgule et stocké en tant que int. Le score est mis à jour dans le
    dictionnaire.
    :param temps_initial: le temps initial
    :param nb_coups: le nombre de coups que l'utilisateurs à fait (les mouvements)
    :param score_base: Le score de base identique pour chaque partie
    :param dict_scores: Le dictionnaire stockant les scores
    :param niveau_en_cours: Le numéro du niveau en cours
    """
    pass


def update_score_file(scores_file_path: str, dict_scores: dict):
    """
    Fonction sauvegardant tous les scores dans le fichier.txt.
    :param scores_file_path: le chemin d'accès du fichier de stockage des scores
    :param dict_scores: Le dictionnaire stockant les scores
    :return:
    """
    pass


if __name__ == '__main__':
    simulateur.simulate()
