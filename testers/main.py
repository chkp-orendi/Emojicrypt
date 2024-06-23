import drop_eval
import embedding_eval
import hellaswag_eval
import winogrande_eval

models = ["llama3:8b", "phi3:mini"]

if __name__ == '__main__':
    drop_eval.main(1, models)
    hellaswag_eval.main(1, models)
    winogrande_eval.main(1, models)
    embedding_eval.main()