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


need_to_check_desire = False
for line in sys.stdin:
    if 'stop' == line.strip():
        break
    if line.strip():
        if need_to_check_desire:
            if 'no' in line.strip() or 'yes' in line.strip():
                response = ontology.get_compliment_response() if 'no' in line.strip() else ontology.get_critique_response()
                ontology.check_current_user_desire()
                need_to_check_desire = False
            else:
                intent = intent_handler.extract_intent(line)
                product_info = qna_handler.extract_product_info(line)
                query = ontology.generate_query(intent, product_info)
                response = ontology.get_control_response()
        else:
            intent = intent_handler.extract_intent(line)
            product_info = qna_handler.extract_product_info(line)
            print(f"intent: {intent}  Product info: {product_info}")

            query = ontology.generate_query(intent, product_info)
            desire = ontology.update_desire(intent, query)
            response = ontology.get_answer_to_query(query)
            need_to_check_desire = False if ontology.is_current_user_desire_checked() else True

        print(response)
        speak(response)

print("exiting")
