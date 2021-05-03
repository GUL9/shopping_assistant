from qna_handler import QnaHandler
from intent_handler import IntentHandler
from ontology_handler import OntologyHandler
from text_to_speech import speak
import sys

PATH_TO_BERT_MODEL = 'C:/Coding/projects/shopping_assistant/uncased_L-12_H-768_A-12'
PATH_TO_INTENT_MODEL = 'C:/Coding/projects/shopping_assistant/bert_intent2.0'

PATH_TO_ONTOLOGY = "C:/Coding/projects/shopping_assistant/ontology/knowledgebase.owl"
PATH_FOR_SAVING_ONTOLOGY = "C:/Coding/projects/shopping_assistant/ontology/knowledgebase.owl"
PATH_TO_SHOPPINGLIST = "C:/Coding/projects/shopping_assistant/shoppinglist.txt"

PATH_TO_RESPONSE_TEMPLATES = "C:/Coding/projects/shopping_assistant/response_templates.txt"

ontology = OntologyHandler(PATH_TO_ONTOLOGY, PATH_FOR_SAVING_ONTOLOGY, PATH_TO_SHOPPINGLIST, PATH_TO_RESPONSE_TEMPLATES)
print("Ontology LOADED")

qna_handler = QnaHandler()
print("QnA LOADED")

intent_handler = IntentHandler(PATH_TO_BERT_MODEL, PATH_TO_INTENT_MODEL)
print("Intent LOADED")


print("Please query me :)")
for line in sys.stdin:
    if 'stop' == line.strip():
        break

    if line.strip():
        intent = intent_handler.extract_intent(line)
        product_info = qna_handler.extract_product_info(line)
        print(f"intent: {intent}  Product info: {product_info}")

        query = ontology.insert_query(intent, product_info)
        response = ontology.get_answer(query)

        print(response)
        speak(response)

print("exiting")
