import logging
from logging.handlers import RotatingFileHandler
##

def get_logger(name):
 # création de l'objet logger qui va nous servir à écrire dans les logs
 logger = logging.getLogger(name)
 # on met le niveau du logger à DEBUG, comme ça il écrit tout
 logger.setLevel(logging.DEBUG)

 # création d'un formateur qui va ajouter le temps, le niveau
 # de chaque message quand on écrira un message dans le log
 formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s')
 # création d'un handler qui va rediriger une écriture du log vers
 # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
 file_handler = RotatingFileHandler('logs.log', 'a', 1000000, 1)
 # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
 # créé précédemment et on ajoute ce handler au logger
 file_handler.setLevel(logging.DEBUG)
 file_handler.setFormatter(formatter)
 logger.addHandler(file_handler)

 # création d'un second handler qui va rediriger chaque écriture de log
 # sur la console (avec un autre formatage)
 stream_handler = logging.StreamHandler()
 formatter2 = logging.Formatter('[%(levelname)s] in %(name)s : %(message)s')
 stream_handler.setFormatter(formatter2)
 stream_handler.setLevel(logging.WARNING)
 logger.addHandler(stream_handler)

 return logger
