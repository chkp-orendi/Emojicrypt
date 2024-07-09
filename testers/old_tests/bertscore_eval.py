from transformers import BertTokenizer, BertModel
from bert_score import BERTScorer
import os

os.environ["REQUESTS_CA_BUNDLE"]= r'C:\Users\orendi\Documents\EmojiCrypt\ca-certificates.crt'

reference_1 = "a 👦🏻 went to school on sunday"
candidate_1 = "a boy went to school on sunday"
# # BERTScore calculation
scorer = BERTScorer(model_type='microsoft/deberta-xlarge-mnli')
P, R, F1 = scorer.score([candidate_1], [reference_1])
print(f"BERTScore Precision: {P.mean():.4f}, Recall: {R.mean():.4f}, F1: {F1.mean():.4f}")


reference_1 = "The bear in the zoo is very cute"
candidate_1 = "a boy went to school on sunday"
P, R, F1 = scorer.score([candidate_1], [reference_1])
print(f"BERTScore Precision: {P.mean():.4f}, Recall: {R.mean():.4f}, F1: {F1.mean():.4f}")