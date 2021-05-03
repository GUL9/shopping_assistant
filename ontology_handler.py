import owlready2
import random
from num2words import num2words
from word2number import w2n
class OntologyHandler:
    def __init__ (self, path_to_ontology, path_for_saving_ontology, path_to_shoppinglist, path_to_response_templates):
        self.path_for_saving_ontology = path_for_saving_ontology
        self.ontology = owlready2.get_ontology(path_to_ontology).load()
        # USER
        self.user = self.ontology.User
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

    def product_with_name_exists(self, name):
        products = self.ontology.Product.instances()
        for product in products:
            if product.p_name == name:
                return True
        return False

    def insert_query(self, intent_type, product_info):
        product_name = product_info['name']
        query = self.ontology.Query(query_p_name=product_name, query_intent_type=intent_type)

        if not self.product_with_name_exists(product_name):
            self.ontology.Product(name=product_name, p_name=product_name)

        self.run_reasoner()
        return query


    def is_affirmative_answer(self, query):
        known_products = self.ontology.KnownProduct.instances()
        query_product = query.is_about
        print(f"ABOUT: {query_product} KNOWN PRODS: {known_products}")
        if query_product in known_products:
            return True
        return False

    def get_answer(self, query):
        suggestions = query.can_be_answered_with

        if suggestions:
            if self.is_affirmative_answer(query):
                suggestions = list(filter(lambda suggestion: suggestion.response_type == 'affirmative', suggestions))
            else:
                suggestions = list(filter(lambda suggestion: suggestion.response_type == 'negative', suggestions))

            selected_index = random.randint(0, len(suggestions)-1)
            response = suggestions[selected_index]
            if response and query.is_about:
                return response.has_response_template.replace('??', num2words(query.is_about.quantity)).replace('?', query.is_about.p_name)
        return "I am sorry, I have no answer to you query :/"
