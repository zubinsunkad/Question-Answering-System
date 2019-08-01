# Word Sense Disambiguation with overlap words.

Word Sense Disambiguation is a NLP task where the correct meaning of a word in a context is found with the help of a given lexicon with word meanings. Here, the simplified lesk algorithm is implemented to disambiguate the word bank in the sentence. WordNet Library API is used to access the WordNet dictionary.

### Prerequisites and Installation

1. Python3

For windows:
* [Python Installation](https://www.python.org/downloads/)

For Mac:

Use the command:

```
brew install python3
```

2. Packages – nltk

For Windows:

* [Canopy Installation](https://store.enthought.com/downloads/)

For Mac/Unix: Canopy is not required, download packages using pip.

```
sudo pip install -U nltk
```

These commands assume you already have pip installed.

## Running the tests

Sample Commands: 

```
$$ python word_sense_disambiguation.py --word "bank" --sentence "I need to withdraw money from bank"
```

```
$$ python word_sense_disambiguation.py --word "bank" --sentence "The bank can guarantee deposits will eventually cover future tution adjustable-rate mortgage securities"
```

Following are the input functions:

--word : The word that needs to be disambiguated.

--sentence : Full sentence with word that will be disambiguated.

Extra tips : If you want the output of above program to be printed in file, add ‘>> output.txt’ at end of above code.

## Results
The output shows the word overlap for each sense of the word bank in WordNet and the final chosen sense.
Results are documented in the file output.txt.

## Authors

* **Zubin Sunkad**
