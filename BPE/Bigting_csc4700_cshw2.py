class BPE:
    # vocab is the class attribute
    vocabulary = {}
    
    # this function is to print the vocabulary
    def show(self):
        print(self.vocabulary)
        
    # the train function with 2 arguments
    def train(self, text, k = 500):
        # This is our starting string 
        chars = list(text)
        # This is just our enumeration
        num = 0
        # This is just a simple for loop to put things in the vocabulary
        # The set to keep track of seen characters
        s = set()
        for i in chars:
            if i not in s:
                s.add(i)
                self.vocabulary[i] = num
                num = num + 1
        # I would like to save this number now to make the tokenize process easier
        self.n = num 
        # So step 1 is complete
        # put all of step 2 in a for loop
        for loop in range(k):
            # Step 2a: Count the number of occurrence for each unique consecutive pair of tokens
            # This can be done by using another dictionary
            count = {}
            # We want to index it now
            for i in range(len(chars) - 1):
                string = chars[i] + chars[i + 1]
                count[string] = count.get(string, 0) + 1
            # We should have all the counts now
            # Step 2b
            # Now we can easily select the one with the highest count with a simple for loop
            max_count = 0
            save = ""
            for k, v in count.items():
                if v > max_count:
                    max_count = v
                    save = k
            # Now save is basically pmax and by checking v must be >, we assure that we pick the first one for tie breaker
            # Step 2c: adding save to the vocab
            self.vocabulary[save] = num
            num = num + 1
            # Now the vocab is expanded by 1
            # Step 2d: Now we change all instance of the unmerged from chars to merged
            # again we are going to index it
            # I will initialized a constant to be 0 to handle list shifting whenever something is deleted
            shift = 0
            for i in range(len(chars) - 1):
                string = chars[i - shift] + chars[i - shift + 1]
                if string == save:
                    chars[i - shift] = string
                    del chars[i - shift + 1]
                    shift = shift + 1
    
    def tokenize(self, text):
        chars = list(text)
        # This loops from the first instance of a merge to the end of the vocabulary
        for i in range(self.n, len(self.vocabulary)):
            # We will shrink this chars just like we did in train
            shift = 0
            for j in range(len(chars) - 1):
                string = chars[j - shift] + chars[j - shift + 1]
                # This whole sequence is to get the key of such i index
                if string == list(self.vocabulary.keys())[i]:
                    chars[j - shift] = string
                    del chars[j - shift + 1]
                    shift = shift + 1
        # After this step we should get all the merges
        # chars should be our first item
        # This loop will determine the numerical values of the updates chars
        num = chars.copy()
        for i in range(len(num)):
            num[i] = self.vocabulary[num[i]]
        # After this step we should get the numerical representation
        return (chars, num)            
        

import argparse
# Start a parser
parser = argparse.ArgumentParser(description = 'BPE models')
# Required, 2 options
parser.add_argument("activity", choices=["train_bpe", "tokenize"])
# Optional, path to the training data
parser.add_argument("--data", type=str)
# Optional, path to where the BPE model will be saved
parser.add_argument("--save", type=str)
# Optional, path to where the BPE model was saved
parser.add_argument("--load", type=str)
# Optional, specifies the text for tokenize
parser.add_argument("--text", type=str)
# Optional, specifies the k value, default to 500 
parser.add_argument("--k", type=int, default=500)

import pickle
args = parser.parse_args()

if args.activity == "train_bpe":
    if not args.data or not args.save:
        raise SystemExit("must provide for train_bpe")
    file = open(args.data, "r", encoding="utf-8")
    data = file.read()
    file.close()
    model = BPE()
    model.train(data)
    filep = open(args.save, "wb")
    pickle.dump(model, filep)
    filep.close()
        
if args.activity == "tokenize":
    if not args.load or not args.text:
       raise SystemExit("must provide for predict_ngram")
    filep = open(args.load, "rb")
    model = pickle.load(filep)
    filep.close()
    print(model.tokenize(args.text))
    model.show()
        
        
        
        
        