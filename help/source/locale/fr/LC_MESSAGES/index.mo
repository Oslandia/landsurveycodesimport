��    S      �  q   L        �     4   �  8   �  4     4   S  4   �  8   �  4   �     +	     -	     /	     <	     >	     K	     M	     Z	     g	     w	     �	  �   �	  
   ,
  N   7
     �
     �
  !   �
     �
     �
     �
  O        h  �   �     h     {    �     �  G   �  p   �     n     s  	   |     �     �     �     �     �     �     �     �     �  $   �  ;     9   R     �     �     �     �  �   �  H   i  B   �  �  �  �   �  6   �  I  �  P   $  O   u  �   �  �   y     �  4         5     7    ;  a  N    �  	   �     �     �     �     �                   %  �   ;  4     8   ;  4   t  4   �  4   �  8     4   L     �     �     �     �     �     �     �     �     �     �     �  �   �  	   �   [   �      �      !  (   !  $   H!     m!     z!  s   �!     "    +"     /#     F#  /  Y#     �$  Q   �$  �   �$     �%  	   �%  	   �%     �%     �%     �%     �%     �%     �%      &     	&     &  (   0&  E   Y&  ;   �&  	   �&     �&      �&     '  �   +'  W   �'  O   2(  '  �(  t  �*  :   ,  �  Z,  Z   �.  Y   9/  �   �/  �   W0     �0  :   �0     1     1  N  !1  q  p2  M  �3     05     75     L5     [5     a5     o5     |5     �5        9   *         @                     M   5   2             K   %      L           B   R      O       Q       C                   <   (       J   $   "      )   3   F         
            N      6      +      A   I   1      :      G   '       .   =      0   &       S          ?       E             P           #       >   D       ;   8   /         7   !   4           ,       	                  H       -               "Code" can be alphanumeric, no restriction is imposed, but it must be compatible with your device. It is preferable not to insert spaces or special characters '1', '1980242.941', '5190519.460', '1002.521', '200' '1', '1980242.941', '5190519.460', '1002.521', '200+300' '1', '1980242.941', '5190519.460', '1002.521', '300' '2', '1980244.900', '5190520.938', '1002.461', '200' '2', '1980244.900', '5190520.938', '1002.461', '300' '2', '1980244.900', '5190520.938', '1002.461', '300+200' '3', '1980249.438', '5190515.953', '1002.329', '101' 0 1 1,..., 100-1 2 2,..., 100-2 3 3,..., 100-2 4,..., 100-9 :ref:`genindex` :ref:`modindex` :ref:`search` At the end of the import, you have to refresh the canvas to see the drawing. The data is obviously displayed with the style determined in the project. Attributes By clicking on the icon |icon|, the codification configuration window appears. Circle by 2 points Circle by 3 points Circle by centre and diameter [1] Circle by centre and radius [1] Codification Creation of the codification Error points can be added in a particular layer as well as all points recorded. Explanation of the parameters For now, the tool only allows CSV files to be read, so the operator must export his data in CSV format in this order: Point identifier, x coordinate, y coordinate, z coordinate, code, attribute 1, attribute 2,..., attribute N General parameters General principle If the exported data from the logbook has additional attributes, it is possible to integrate them by specifying in the expression field'_attN' where N corresponds to the field number (starting with 1). There is no limitation on attributes as long as the CSV file is compliant. Indices and tables It is possible to add a comment on the code in the "Description" field. Items that do not conform to the coding rule, e.g. code with 3 points and only 2 points, etc., are called error. Line Line [2] Minimum 2 No Number of parameters Number of points Open / Save Point Points import Polygon Present Processing import Rectangle by 2 points and height [1] Rectangle by 3 points (3rd point = distance from 2nd point) Rectangle by 3 points (3rd point = orthogonal projection) Result Special points Square by 2 diagnoal points Square by 2 points The "Geometry" is to be chosen from the one indicated above. It is filtered on the geometry of the "Output Layer" from the "GeoPackage" selected below. The File menu allows opening, closing, saving, etc. of the codification. The codification is saved in a YAML format whose extension is.qlsc The codification preparation cannot be done without first having opened a qgis project containing the layers in which the data will be inserted. For the times the layers must be in geopackages. There is no limit to the number of these geopackages. A good practice is to group the layers in thematic geopackages: water, sanitation, roads, etc. If the data is in a postgresql database, it is possible to export them in geopackages via the "Package layers" tool. The general parameters define the separators used. A separator to indicate the different codes on the same point and a separator to indicate the parameters. These must be adapted according to the capacities of the field book. The import is done via a new module in the processing. The plugin works according to topography codification principles. The topographic department must first create a codification that will be used by operators in the field. On his field book, when he records a point, the operator will also enter a code. The operator has the possibility to survey several codes for the same point. This codified survey will allow the automatic generation of the drawing, with the possibility of pre-filling attributes that will be processed later. The GIS administrator will be able to link the import with other treatments thanks to the QGIS processing. The tool asks for the configuration file (.qlsc file) and the points file (.csv) The tool proposes to generate the following elements for each type of geometry: The tool will process the codes in queue, special attention is requested to the operator entering the codes because an input error will delay the coding and the resulting drawing. The tool will separate the codes that are on the same point, and then match them according to their code. For example a csv like: Type Welcome to Land survey codes import's documentation! X Yes You can automatically generate attributes in the layer columns using the same principles as the QGIS expression calculator. Attention, however, this one does not have vocation to accept complex requests, it is preferable to carry out this stage after the import of the data. [1] Means that the code must have a parameter and that it is of a numerical type. Example of the circle by a center and radius. You enter the center of the circle by a point whose code is 100 and you must enter the radius (in the projection unit) by adding the parameter character and the measurement, i.e. 100-1 for a circle with a radius of one meter. [2] a line is handled in a special way since it needs information indicating the opening and closing of the line, as well as changes of nature (arcs - not yet implemented). Taking as an example, a line with a code of 100, this line has 4 points must be filled in this way: and then: will be transformed into: |codification| |csv| |processing1| |processing| |result| |yaml| Project-Id-Version: Land survey codes import 0.0.1
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2019-07-17 11:30+0200
Last-Translator: 
Language-Team: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Language: fr
X-Generator: Poedit 1.8.4
 "Code" peut être alphanumérique, aucune restriction n'est imposée, mais il faut qu'il soit compatible avec votre appareil. Il est préférable de ne pas insérer d'espaces ou de caractères spéciaux '1', '1980242.941', '5190519.460', '1002.521', '200' '1', '1980242.941', '5190519.460', '1002.521', '200+300' '1', '1980242.941', '5190519.460', '1002.521', '300' '2', '1980244.900', '5190520.938', '1002.461', '200' '2', '1980244.900', '5190520.938', '1002.461', '300' '2', '1980244.900', '5190520.938', '1002.461', '300+200' '3', '1980249.438', '5190515.953', '1002.329', '101' 0 1 1,..., 100-1 2 2,..., 100-2 3 3,..., 100-2 4,..., 100-9 :ref:`genindex` :ref:`modindex` :ref:`search` À la fin de l'import, il faut rafraîchir le canevas pour voir apparaître le dessin. Les données s'affichent évidemment avec le style déterminé dans le projet. Attributs En cliquant sur l'icône |icon|, la fenêtre de configuration de la codification apparaît. Cercle par 2 points Cercle par 3 points Cercle par le centre et le diamètre [1] Cercle par le centre et le rayon [1] Codification Création de la codification Les points en erreur peuvent être ajouté dans une couche particulière tout comme l'ensemble des points relevés. Explication sur les paramètres À ce jour, l'outil ne permet la lecture que des fichiers CSV, l'opérateur doit donc exporter sa donnée au format CSV devant respecter cet ordre : Identifiant du point, Coordonnée x,Coordonnée y,Coordonnée z, Code, Attribut 1, Attribut 2, ..., Attribut N Paramètres généraux Principe général Si les données exportées du carnet possèdent des attributs supplémentaires, il est possible de les intégrer en spécifiant dans le champ expression '_attN' ou N correspond au numéro du champ (en commençant par 1). Il n'y a pas de limitation sur les attributs tant que le fichier CSV est conforme. Indexes et tables Il est possible d'ajouter un commentaire sur le code dans le champ "Description". On appelle erreur, les points qui ne sont pas conformes à la règle de codification, par exemple code devant avoir 3 points et n'ayant que 2 points, etc. Ligne Ligne [2] Minimum 2 Non Nombre de paramètres Nombre de points Ouverture / Enregistrement Point Import des points Polygone Présent Importation via le processing Rectangle par 2 points et la hauteur [1] Rectangle par 3 points (3ème point = distance depuis le 2ème point) Rectangle par 3 points (3ème point = projeté orthogonale) Résultat Points spéciaux Carré par 2 points en diagonale Carré par 2 points La "Géométrie" est à choisir parmi celle indiquée ci-avant. Elle est filtrée sur la géométrie de la "Couche de sortie" depuis le "GeoPackage" sélectionné en dessous. Le menu Fichier permet l'ouverture, fermeture, enregistrement, etc. de la codification. La codification est enregistrée dans un format YAML dont l'extension est .qlsc La préparation de la codification ne peut se faire sans avoir au préalable ouvert un projet qgis contenant les couches dans lesquelles les données seront insérées.
Pour les moments les couches doivent être dans des geopackages. Il n'y a pas de limitation quant aux nombres de ces geopackages. Une bonne pratique est de regrouper les couches dans des geopackages thématiques : eau, assainissement, voirie, etc. 
Si la donnée est dans une base postgresql, il est possible de les exporter dans des geopackages via l'outil "Empaquetage de couche". Les paramètres généraux définissent les séparateurs utilisés. Un séparateur pour indiquer les différents codes sur un même point et un séparateur pour indiquer les paramètres. Ceux-ci doivent être adaptés en fonction des capacités du carnet de terrain.

Le lien vers le geopackage permet de fournir l'interface pour la codification dans le groupe ci-dessous. L'import se fait via un nouveau module dans le processing. Le fonctionnement de ce plugin reprend les principes de codification en topographie. Le service topographique doit d'abord créer une codification qui servira aux opérateurs sur le terrain. Sur son carnet de terrain numérique, lorsqu'il relèvera un point, l'opérateur entrera également un code. L'opérateur à la possibilité de lever plusieurs codes pour le même point. Ce levé codifié, permettra la génération automatique du dessin, avec la possibilité de pré renseigner des attributs qui seront traités par la suite. L'administrateur SIG aura la possibilité d'enchaîner l'import avec le traitement grâce au traitement QGIS. L'outil demande le fichier de configuration (fichier .qlsc) et le fichier de points (.csv) L'outil propose(ra) de générer les éléments suivant pour chaque type de géométrie : L'outil traitera les codes à la file, une attention particulière est demandé à l'opérateur saisissant les codes car une erreur de saisie décalera la codification et le dessin en résultant. L'outil va séparer les codes qui sont sur un même point, pour ensuite les apparier suivant leur code.  Par exemple un csv comme : Type Bienvenue sur la documentation de Land survey codes import X Oui Vous avez la possibilité de générer automatiquement des attributs dans les colonnes de la couche en utilisant les mêmes principes que le calculateur d'expression de QGIS.
Attention, toutefois celui-ci n'a pas vocation à accepter des requêtes complexes, il est préférable de réaliser cette étape après l'import des données. Signifie que le code doit avoir un paramètre et que celui-ci est de type numérique. Exemple du cercle par un centre et le rayon. Vous renseignez le centre du cercle par un point dont le code est 100 et vous devez renseigner le rayon (dans l'unité de la projection) en accolant le caractère de paramètre et la mesure, soit 100-1 pour un cercle d'un mètre de rayon. [2] une ligne est traité de façon spéciale puisqu'elle a besoin d'une information indiquant l'ouverture et la fermeture de la ligne, ainsi que des changements de nature (arcs - non implémenté pour le moment). En prenant pour exemple, une ligne avec un code de 100, cette ligne a 4 points doit être renseignée de cette façon : puis : sera transformé en: |codification| |csv| |processing1| |processing| |result| |yaml| 