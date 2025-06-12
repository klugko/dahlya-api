import os
import json
from openai import OpenAI
from app.core.config import settings
from typing import Dict, List, Optional

class RecommendationEngineService:
    """
    Service pour générer des recommandations professionnelles en utilisant l'API OpenAI GPT-4o.
    """
    def __init__(self):
        # Initialise le client OpenAI avec la clé API des paramètres.
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if not settings.OPENAI_API_KEY:
            print("AVERTISSEMENT: La clé API OpenAI n'est pas configurée dans .env")
            print("Veuillez définir OPENAI_API_KEY dans votre fichier .env pour utiliser ce service.")

    def generate_recommendations(self, cv_raw_text: str) -> Optional[Dict]:
        """
        Génère des recommandations professionnelles basées sur le texte brut d'un CV
        en utilisant GPT-4o.
        """
        if not self.client.api_key:
            print("Erreur: Clé API OpenAI manquante. Impossible de générer les recommandations.")
            return None

        # Définit les prompts système et utilisateur.
        # Le prompt système instruit GPT-4o sur son rôle et le format de sortie attendu (JSON).
        system_prompt = """
        Vous êtes un conseiller en carrière expert. Votre tâche est d'analyser le texte d'un CV et de fournir des recommandations d'orientation professionnelle.
        La sortie doit être un objet JSON avec les clés suivantes :
        - "job_type": Une chaîne suggérant un type de poste ou un rôle approprié.
        - "environment": Une chaîne décrivant l'environnement de travail idéal (ex: "startup", "grande entreprise", "freelance", "association").
        - "suggested_trainings": Une liste de chaînes recommandant des formations complémentaires ou certifications pertinentes.
        - "skills_to_develop": Une liste de chaînes identifiant les compétences clés que le candidat devrait renforcer ou acquérir.
        Assurez-vous que la réponse est toujours un objet JSON valide.
        """

        # Le prompt utilisateur contient le texte réel du CV à analyser.
        user_prompt = f"Analysez le texte de CV suivant et fournissez des recommandations au format JSON spécifié :\n\n{cv_raw_text}"

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model="gpt-4o",
                response_format={"type": "json_object"}, # Assure une sortie JSON
                temperature=0.7 # Ajuste la créativité vs la cohérence
            )

            # Extrait la chaîne JSON de la réponse
            response_content = chat_completion.choices[0].message.content
            # Parse la chaîne JSON en dictionnaire Python
            recommendations_data = json.loads(response_content)
            return recommendations_data

        except Exception as e:
            print(f"Erreur lors de l'appel à l'API OpenAI: {e}")
            return None

# Instancie le service pour une utilisation dans les endpoints
recommendation_engine_service = RecommendationEngineService()