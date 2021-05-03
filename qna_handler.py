from transformers import pipeline
import inflect

class QnaHandler:
    qna = pipeline("question-answering")
    inflect_engine = inflect.engine()

    def extract_name(self, context):
        result = self.qna(question="what product?", context=context)
        return result.get('answer').lower()

    def extract_quantity(self, context):
        result = self.qna(question="what number?", context=context)
        return result.get('answer').lower()

    def extract_unit(self, context, name, quantity):
        result = self.qna(question="how much?", context=context)
        return result.get('answer').lower()

    def extract_product_info(self, context):
        product_name = self.extract_name(context)
        name_as_singular = self.inflect_engine.singular_noun(product_name)
        name = product_name if not name_as_singular else name_as_singular

        quantity = self.extract_quantity(context)
        unit = self.extract_unit(context, name, quantity)
        return {'name': name, 'quantity': quantity, 'unit': unit}
