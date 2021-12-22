import time

from fourni import actor as a
from fourni import simulateur
from fourni import personnage as p
from fourni import caisse as c
from fourni import case_vide as cv
from fourni import mur as m
from outils import \
    creer_image, creer_caisse, \
    creer_case_vide, creer_cible, \
    creer_mur, creer_personnage, \
    est_egal_a

# Constante à utiliser
VALEUR_COUP: int = 50


###############################################################################################################
#       GAMES MANAGEMENT
###############################################################################################################
def jeu_en_cours(caisses: list, cibles: list) -> bool:
    """
    Fonction testant si le jeu est encore en cours et retournant un booléen comme réponse sur l'état de la partie.
    :param caisses: La liste des caisses du niveau en cours
    :param cibles: La liste des cibles du niveau en cours
    :return: True si la partie est finie, False sinon
    """
    total_cible_filled: int = 0

    # Check if all crate have the same coordinate as target
    for cible in cibles:
        for caisse in caisses:
            total_cible_filled += 1 if est_egal_a(cible, caisse) else 0

    # All crate on target ?
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
    # Read level file
    level = open(path, "r")

    # For each line in the files
    for y, line in enumerate(level.readlines()):

        # Add element to the correct list according to the symbol
        for x, item in enumerate(line):
            if item == '#':
                murs.append(creer_mur(x, y))
            elif item == '.':
                cibles.append(creer_cible(x, y))
            elif item == '$':
                caisses.append(creer_caisse(x, y))
            elif item == '@':
                joueur.append(creer_personnage(x, y))


###############################################################################################################
#       MOVES MANAGEMENT
###############################################################################################################
def definir_mouvement(_direction: str,
                      _can,
                      _joueurs: list[p.Personnage],
                      _murs: list,
                      _caisses: list[c.Caisse],
                      _liste_image: list):
    """
    Cette fonction permet de savoir si le mouvement souhaité est possible (pas d'élément bloquant (deuxième caisse
    ou mur sur la prochaine posision
    Elle permet de définir quelles entités doivent êtres bouger en fonction du mouvement. Il peux y avoir deux entités
    (le joueur + une caisse)
    :param _direction: Direction dans laquelle le joueur se déplace (droite, gauche, haut, bas)
    :param _can: Canvas (ignorez son fonctionnement), utile uniquement pour créer_image()
    :param _joueurs: liste des joueurs
    :param _murs: liste des murs
    :param _caisses: liste des caisses
    :param _liste_image: liste des images (murs, caisses etc...) détaillée dans l'énoncé
    :return: none
    """
    # Calculate the new coordinate of the player after the move
    new_player_position: cv.CaseVide = generate_new_coordinates(_joueurs[0], _direction)

    # is there a wall on this next position
    if not wall_on_next_coordinate(new_player_position, _murs):

        # is there no crate to push  on this next position
        idx_pushed: int = crate_on_next_coordinate(new_player_position, _caisses)
        if not idx_pushed > -1:

            # -----------------------------------------
            #   MOVE PLAYER ONLY
            # -----------------------------------------

            # with no crate no wall on the next position, my player can be moved
            # update_player_coordinate
            effectuer_mouvement(new_player_position, _joueurs, 0, _liste_image[4], _liste_image[6], _can)

        else:

            # Being here mean that there is a crate to push
            # Calculate the new coordinate of the crate that will be pushed by the player after the move
            # This is the new player position updated from 1 step towards the move direction
            # Two position away from the current player position
            new_crate_position: cv.CaseVide = generate_new_coordinates(new_player_position, _direction)

            # is there a wall right behind the crate to push
            if not wall_on_next_coordinate(new_crate_position, _murs):

                # is there a second crate right behind the first one to push
                idx_blocker: int = crate_on_next_coordinate(new_crate_position, _caisses)
                if not idx_blocker > -1:

                    # -----------------------------------------
                    #   MOVE PLAYER AND PUSH A CRATE
                    # -----------------------------------------

                    # if there is no crate, my player can push the crate on her next position
                    # both can move without problem
                    # update_crate_coordinate
                    effectuer_mouvement(new_crate_position, _caisses, idx_pushed, _liste_image[2], _liste_image[6],
                                        _can)
                    # update_player_coordinate
                    effectuer_mouvement(new_player_position, _joueurs, 0, _liste_image[4], _liste_image[6],
                                        _can)


def effectuer_mouvement(_next_position: cv.CaseVide,
                        _entities: list[a.Actor],
                        _entity_idx: int,
                        _entity_image,
                        _floor_image,
                        _can):
    """"
    Cette fonction remplace l'image aux anciennes coordonnées de l'entité en mouvement par une image de sol vide
    Elle met également à jour les coordonnées de l'entité avec sa nouvelle position dans la liste correspondantes
    Enfin elle remplace l'image aux nouvelle coordonnées par l'image de l'entité
    :param _next_position: Case vide avec les nouvelles coordonnées de l'entité
    :param _entities: List contenant l'entité à bouger
    :param _entity_idx: Index de l'entité à bouger dans la liste
    :param _entity_image: Image de l'entité
    :param _floor_image: Image de sol vide
    :return: none
    """

    # Update old position with floor images
    creer_image(_can, _entities[_entity_idx].get_x(), _entities[_entity_idx].get_y(), _floor_image)

    # Update coordinates
    _entities[_entity_idx].set_x(_next_position.get_x())
    _entities[_entity_idx].set_y(_next_position.get_y())

    # Update new position with entity image
    creer_image(_can, _entities[_entity_idx].get_x(), _entities[_entity_idx].get_y(), _entity_image)


def generate_new_coordinates(_entity: a.Actor, _direction) -> cv.CaseVide:
    """
    Calculate the new coordinate of the entity (crate / player) after the move
    :param _entity: Entity to update
    :param _direction: Up, Down, Left, Right
    :return: CaseVide - Used to check if this position is free
    """
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


def wall_on_next_coordinate(_case_vide: cv.CaseVide, _murs: list[m.Mur]) -> bool:
    """
    Check if the next move will be on a wall
    :param: _case_vide: Entity with the new coordinates
    :param: _murs: Wall List
    :return: True -> There is a wall on the next coordinates // False There isn't any wall on the next position
    """
    for mur in _murs:
        if _case_vide == mur:
            return True

    return False


def crate_on_next_coordinate(_case_vide: cv.CaseVide, _caisses: list[c.Caisse]) -> int:
    """
    Check if the next move will be on a crate
    :param: _case_vide: Entity with the new coordinates
    :param: _caisses - Crates List
    :return: -1 -> There is no crate on the next coordinates // >-1 There is a crate on the next position
                                                                    Index from the list returned
    """
    for i, caisse in enumerate(_caisses):
        if _case_vide == caisse:
            return i

    return -1


###############################################################################################################
#       SCORES MANAGEMENT
################################################################################################################
def chargement_score(scores_file_path: str, dict_scores: dict[int, list[int]]):
    """
    Fonction chargeant les scores depuis un fichier.txt et les stockent dans un dictionnaire
    :param scores_file_path: le chemin d'accès du fichier
    :param dict_scores:  le dictionnaire pour le stockage
    :return:
    """
    scores = open(scores_file_path, "r")
    for line in scores.readlines():
        dict_scores[int(line.split(";")[0])] = [int(x) for x in line[2:].split(';')]


def maj_score(niveau_en_cours: int, dict_scores: dict[int, list[int]]) -> str:
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
    if niveau_en_cours in dict_scores:
        scores_list: list[int] = dict_scores[niveau_en_cours]
        scores_str: str = f'Niveau {niveau_en_cours}\n' + '\n'.join(
            [f'{i + 1}) {score}' for i, score in enumerate(scores_list)])
    else:
        scores_str: str = "Personne n'a encore joué à ce niveau !"

    return scores_str


def calcule_score(temps_initial: float, nb_coups: int, score_base: int) -> int:
    """
    calcule le score du jouer
    :param temps_initial: debut du jeu
    :param nb_coups: nombre des mouvements
    :param score_base: score de base
    :return: le score du jouer
    """
    return int(score_base - (time.time() - temps_initial) - (nb_coups * VALEUR_COUP))


def enregistre_score(temps_initial: float, nb_coups: int, score_base: int, dict_scores: dict[int, list[int]],
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
    current_score: int = calcule_score(temps_initial, nb_coups, score_base)
    if niveau_en_cours in dict_scores:
        dict_scores[niveau_en_cours].append(current_score)
    else:
        dict_scores[niveau_en_cours] = [current_score]
    scores_size: int = len(dict_scores[niveau_en_cours])
    if scores_size > 1:
        dict_scores[niveau_en_cours].sort(reverse=True)
        if scores_size > 10:
            dict_scores[niveau_en_cours].pop()


def update_score_file(scores_file_path: str, dict_scores: dict[int, list[int]]):
    """
    Fonction sauvegardant tous les scores dans le fichier.txt.
    :param scores_file_path: le chemin d'accès du fichier de stockage des scores
    :param dict_scores: Le dictionnaire stockant les scores
    :return:
    """
    score_file = open(scores_file_path, "w")
    score_file.truncate()
    score_string: list = []

    for key in dict_scores:
        dict_scores[key].insert(0, key)
        score_string.append(";".join([str(x) for x in dict_scores[key]]))

    score_file.writelines('\n'.join(score_string) + "\n")


if __name__ == '__main__':
    simulateur.simulate()
