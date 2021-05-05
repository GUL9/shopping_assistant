import owlready2
import random
from num2words import num2words
from word2number import w2n
class OntologyHandler:
    def __init__ (self, path_to_ontology, path_for_saving_ontology, path_to_shoppinglist, path_to_response_templates):
        self.path_for_saving_ontology = path_for_saving_ontology
        self.ontology = owlready2.get_ontology(path_to_ontology).load()
        # USER
        self.user = self.ontology.User()
        # SHOPPINGLIST
        self.shoppinglist = self.ontology.Shoppinglist()
        lines = open(path_to_shoppinglist, 'r').readlines()
        for line in lines:
            tokens = line.strip().split(',')
            productname = tokens[0]
            quantity = float(tokens[1])
            unit = [2]
            self.ontology.Product(name=productname.replace(' ', ''), p_name=productname, quantity=quantity)

        self.shoppinglist.contains_products = self.ontology.Product.instances()
        # RESPONSES
        templates = open(path_to_response_templates, 'r').readlines()
        for template in templates:
            tokens = template.strip().split(',')
            intent = tokens[0]
            type = tokens[1]
            temp = tokens[2]

            response = self.ontology.Response()
            response.response_intent_type = intent
            response.response_type = type
            response.has_response_template = temp

        self.run_reasoner()

    def run_reasoner(self):
        try:
            owlready2.sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        except:
            print(f"INCONSISTENCIES")

        self.ontology.save(file = self.path_for_saving_ontology, format="rdfxml")

    def is_current_user_desire_checked(self):
        if self.user.has_current_desire:
            return self.user.has_current_desire.is_checked

    def check_current_user_desire(self):
        if self.user.has_current_desire:
            self.user.has_current_desire.is_checked = True
            self.run_reasoner()

    def product_with_name_exists(self, name):
        products = self.ontology.Product.instances()
        for product in products:
            if product.p_name == name:
                return True
        return False

    def generate_query(self, intent_type, product_info):
        product_name = product_info['name']
        query = self.ontology.Query(query_p_name=product_name, query_intent_type=intent_type, is_answered=False)

        # Check if qeried product exist
        if not self.product_with_name_exists(product_name):
            product = self.ontology.Product(name=product_name, p_name=product_name)
        else:
            product = next(prod for prod in self.ontology.Product.instances() if prod.p_name == product_name)

        self.run_reasoner()
        return query

    def update_desire(self, query):
        if query.query_intent_type == "subjective" and not self.is_affirmative_answer(query):
            self.user.has_current_desire = self.ontology.Desire(is_desire_about=query.is_about, is_checked=False)
            self.run_reasoner()
            return self.user.has_current_desire

        return None

    def is_affirmative_answer(self, query):
        known_products = self.ontology.KnownProduct.instances()
        query_product = query.is_about
        print(f"ABOUT: {query_product}  KNOWN: {known_products}")
        if query_product in known_products:
            return True
        return False

    def get_control_response(self):
        suggestions = self.ontology.ControlResponse.instances()
        selected_index = random.randint(0, len(suggestions)-1)
        response = suggestions[selected_index]

        return response.has_response_template.replace('?', self.user.has_current_desire.is_desire_about.p_name)

    def get_critique_response(self):
        suggestions = self.ontology.CritiqueResponse.instances()
        selected_index = random.randint(0, len(suggestions)-1)
        response = suggestions[selected_index]

        return response.has_response_template.replace('?', self.user.has_current_desire.is_desire_about.p_name)

    def get_compliment_response(self):
        suggestions = self.ontology.ComplimentResponse.instances()
        selected_index = random.randint(0, len(suggestions)-1)
        response = suggestions[selected_index]

        return response.has_response_template.replace('?', self.user.has_current_desire.is_desire_about.p_name)

    def get_oldest_unanswered_query(self):
        if self.user.has_unanswered_queries:
            return self.user.has_unanswered_queries[-1]

    def answer_query(self, query):
        suggestions = query.can_be_answered_with

        if suggestions:
            if self.is_affirmative_answer(query):
                suggestions = list(filter(lambda suggestion: suggestion.response_type == 'affirmative', suggestions))
            else:
                suggestions = list(filter(lambda suggestion: suggestion.response_type == 'negative', suggestions))

            selected_index = random.randint(0, len(suggestions)-1)
            response = suggestions[selected_index]

            if response and query.is_about:
                quantity_word = num2words(query.is_about.quantity) if query.is_about.quantity else 'it'
                answer = response.has_response_template.replace('??', quantity_word).replace('?', query.is_about.p_name)

        query.is_answered = True
        self.run_reasoner()
        return answer
