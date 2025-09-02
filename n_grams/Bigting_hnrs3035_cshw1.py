class N_grams:
    # n here for ngrams
    def __init__(self, n):
        self.n = n
        
    def train(self, text):
        # list all of the punctuations 
        # got from printing all unique characters in the file besides the numbers and letters
        punctuation = "!#$%&()*,-./:;?[]_£—‘’“”•™"
        for p in punctuation:
            text = text.replace(p, " " + p + " ")
        words = text.split()
        
        # here i will create 2 dictionary:
        # the first one is for counting pairs
        # the second one is for counting word occurance so i can divide
        tris = {}
        pairs = {}
        unique = {}
        # subtract some because of indexing issue
        for w in range(len(words)):
            word = words[w]
            unique[word] = unique.get(word, 0) + 1
            
        for w in range(len(words) - 1):
            pair = (words[w], words[w + 1])
            pairs[pair] = pairs.get(pair, 0) + 1
            
        for w in range(len(words) - 2):
            tri = (words[w], words[w + 1], words[w + 2])
            tris[tri] = tris.get(tri, 0) + 1
            
        # now we should have all pairs and all unique and counts
        # so the point of making unique is so we can divide, and with pairs
        for (k1, k2, k3), v in tris.items():
            if (k1, k2) in pairs:
                tris[(k1, k2, k3)] = v / pairs[(k1, k2)]
            else:
                raise ValueError("Word not found")
                
        for (k1, k2), v in pairs.items():
            if k1 in unique:
                pairs[(k1, k2)] = v / unique[k1]
            else:
                raise ValueError("Word not found")
                
        for k, v in unique.items():
            unique[k] = v / len(words)
            
        # now we should have all pairs and its probability
        # note that this is expandable for n grams > 3
        self.unique = unique
        self.pairs = pairs
        self.tris = tris
    
    def predict_next_word(self, user_input, deterministic = False):
        import random
        exist = False
        if self.n != 2 and self.n != 3:
            raise SystemExit("n value is not 2 or 3")
            
        # n_grams = 2
        if len(user_input) == 1:
            for k in self.unique:
                if user_input[0] == k:
                    for (k1, k2) in self.pairs:
                        if k1 == user_input[0]:
                            exist = True
                            break
                if exist == True:
                    break
            # check if exist first, if not throw an error
            if exist == False:
                raise SystemExit("Word not found, can't predict next word")
            else:
                # If deterministic True then pick the highest probability
                if deterministic == True:
                    best = 0
                    solution = ""
                    for (k1, k2), v in self.pairs.items():
                        if k1 == user_input[0]:
                            if best < v:
                                best = v
                                solution = k2
                # Else we need to put all probability into one bag then pool using random
                # Idea: since the prob adds up to 1, we can put it all into a dictionary
                # Then add 1 prob to all previous probs
                # This way random (0-1) will reach whatever threshold, that will be the word
                else:
                    sol_bag = {}
                    for (k1, k2), v in self.pairs.items():
                        if k1 == user_input[0]:
                            sol_bag[k2] = v   
                    r = random.random()
                    # How this work: we will subtract until r becomes negative
                    # Mathematically, this can simulate randomness
                    for k, v in sol_bag.items():
                        r = r - v
                        if r < 0:
                            solution = k
                            break    
                        
        # n_grams = 3
        # Repeat all steps for n_grams = 3 similarly to n_grams = 2
        elif len(user_input) == 2:
            for k in self.pairs:
                if user_input == k:
                    for (k1, k2, k3) in self.tris:
                        if (k1, k2) == user_input:
                            exist = True
                            break
                if exist == True:
                    break
            if exist == False:
                raise SystemExit("Word not found, can't predict next word")
            else:
                if deterministic == True:
                    best = 0
                    solution = ""
                    for (k1, k2, k3), v in self.tris.items():
                        if (k1, k2) == user_input:
                            if best < v:
                                best = v
                                solution = k3
                else:
                    sol_bag = {}
                    for (k1, k2, k3), v in self.tris.items():
                        if (k1, k2) == user_input:
                            sol_bag[k3] = v   
                    r = random.random()
                    for k, v in sol_bag.items():
                        r = r - v
                        if r < 0:
                            solution = k
                            break
        return solution
    
import argparse
# Start a parser
parser = argparse.ArgumentParser(description = 'N_grams models')
# Required, 2 options
parser.add_argument("activity", choices=["train_ngram", "predict_ngram"])
# Optional, path to the training data
parser.add_argument("--data", type=str)
# Optional, path to where the N_grams model will be saved
parser.add_argument("--save", type=str)
# Optional, path to where the N_grams model was saved
parser.add_argument("--load", type=str)
# Optional, specifies the words for predict_ngram activity
parser.add_argument("--word", type=str)
# Optional, specifies the numbers of words to predict
parser.add_argument("--nwords", type=int)
# Optional, specifies the order of the ngram
parser.add_argument("--n", type=int, choices=[1, 2, 3])
# Optional, specifies the deterministic flag
parser.add_argument("--d", action="store_true")

import pickle
args = parser.parse_args()

if args.activity == "train_ngram":
    if not args.data or not args.save or not args.n:
        raise SystemExit("must provide for train_ngram")
    file = open(args.data, "r", encoding="utf-8")
    data = file.read()
    file.close()
    model = N_grams(args.n)
    model.train(data)
    filep = open(args.save, "wb")
    pickle.dump(model, filep)
    filep.close()
        
if args.activity == "predict_ngram":
    if not args.load or not args.word or not args.nwords:
       raise SystemExit("must provide for predict_ngram")
    filep = open(args.load, "rb")
    model = pickle.load(filep)
    filep.close()
    final_ans = args.word
    user_input = tuple(args.word.split())
    for i in range(args.nwords):
        next_word = model.predict_next_word(user_input, deterministic=args.d)
        final_ans = final_ans + " " + next_word
        if model.n == 2:
            user_input = (next_word,)
        elif model.n == 3:
            user_input = (user_input[-1], next_word)
    print(final_ans)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        