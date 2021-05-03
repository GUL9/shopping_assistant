import os
import keras
import numpy as np
from bert.tokenization.bert_tokenization import FullTokenizer
class IntentHandler(object):

    def __init__(self, path_to_bert_model, path_to_intent_model):
        vocab_file = os.path.join(path_to_bert_model, "vocab.txt")

        self.tokenizer = FullTokenizer(vocab_file)
        self.intent_model = keras.models.load_model(path_to_intent_model)

    def extract_intent(self, query):
        input = [query]
        #tokenize input
        tokens = map(self.tokenizer.tokenize, input)
        #add [CLS] and [SEP] Tokens
        tokens = map(lambda token: ["[CLS]"] + token + ["[SEP]"], tokens)
        #convert each tokens to ids
        token_ids = list(map(self.tokenizer.convert_tokens_to_ids, tokens))
        #add padding MAX LEN = 20
        token_ids = map(lambda tids: tids + [0] * (20-len(tids)), token_ids)
        token_ids = np.array(list(token_ids))
        #predict
        prediction = self.intent_model.predict(token_ids).argmax(axis = -1)
        return "objective" if prediction == 0 else "subjective"
