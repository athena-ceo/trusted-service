La Préfecture des Yvelines reçoit chaque jour plusieurs dizaines de messages de la part de demandeurs étrangers.

Chacune de ces demandes est en rapport avec le séjour ou l'asile et correspond à une intention parmi les intentions listées dans le fichier `intentions.csv` ci-joint.

Afin de m'aider à construire un modèle NLP de classification des messages en fonction de l'intention, merci de générer un fichier csv contenant, pour chacune de ces intentions, 5 exemples de messages pour l'entraînement et 5 exemples pour le test.

Recommendations:
- Ne pas faire apparaître de façon trop évidente le nom de l'intention dans les exemples de messages. Paraphraser plutôt l'intention dans le message. 
- Eviter autant que possible de répéter des phrases d'un message à l'autre
- Ne pas passer par la génération d'un programme Python qui génère les messages en assemblant de façon aléatoire des morceaux prédéfinis, car cela crée des messages semblables. Passer plutôt par la génération des exemples par complétion LLM. 
- Assurer une grande variabilité entre les 10 messages de chaque intention
=> o3

---

Merci de créer un programme Python qui entraîne et teste 5 modèles NLP de classification différents à partir des données contenues dans le fichier `intentions_examples.csv` ci-joint.

