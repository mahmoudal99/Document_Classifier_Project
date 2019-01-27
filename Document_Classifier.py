import re, os
from nltk.corpus import stopwords

removable_words_symbols = {'test', 'hi'}
stop_words = stopwords.words("english")
removable_words_symbols.update(stop_words)
symbols = ["!", "@", "#", "$", "%", "^", "&", "*", "()", "_", "+", "<>", "?", ".", "/", ",", " "]
removable_words_symbols.update(symbols)


class BagOfWords(object):
    """ Bag Of Words Class """

    def __init__(self):
        self.__number_of_words = 0
        self.__bag_of_words = {}

    def __add__(self, other):

        """ Joining two BagOfWords """
        bag = BagOfWords()
        bag_of_words = bag.__bag_of_words

        for word in self.__bag_of_words:

            if word not in removable_words_symbols:

                bag_of_words[word] = self.__bag_of_words[word]
                if word in other.__bag_of_words:
                    bag_of_words[word] += other.__bag_of_words[word]

        for word in other.__bag_of_words:
            if word not in removable_words_symbols:

                if word not in bag_of_words:
                    bag_of_words[word] = other.__bag_of_words[word]

        return bag

    def add_word(self, word):

        """ A word is added to the Bag Of Words"""
        self.__number_of_words += 1
        if word in self.__bag_of_words:
            self.__bag_of_words[word] += 1
        else:
            self.__bag_of_words[word] = 1

    def len(self):
        """ Returning the number of different words of an object """
        return len(self.__bag_of_words)

    def Words(self):
        """ Returning a list of the words contained in the object """
        return self.__bag_of_words.keys()

    def BagOfWords(self):
        """ Returning the dictionary, containing the words (keys) with their
            frequency (values)"""
        return self.__bag_of_words

    def WordFreq(self, word):
        """ Returning the frequency of a word """
        if word in self.__bag_of_words:
            return self.__bag_of_words[word]
        else:
            return 0


class Document(object):

    def __init__(self, vocabulary):
        self.__name = ""
        self.__document_class = None
        self._words_and_freq = BagOfWords()
        Document._vocabulary = vocabulary

    def read_document(self, filename, learn=False):
        """ A document is read. It is assumed, that the document is either
            encoded in utf-8 or in iso-8859... (latin-1).
            The words of the document are stored in a Bag of Words, i.e.
            self._words_and_freq = BagOfWords() """
        try:
            text = open(filename, "r", encoding='utf-8').read()
        except UnicodeDecodeError:
            text = open(filename, "r", encoding='latin-1').read()

        text = text.lower()
        words = re.split(r"\W", text)

        self._number_of_words = 0

        """ Adds each word in the document into the Bag Of Words """
        for word in words:
            self._words_and_freq.add_word(word)
            if learn:
                Document._vocabulary.add_word(word)

    def __add__(self, other):
        """ Adding two documents consists in adding the BagOfWords of the Documents """

        res = Document(Document._vocabulary)

        res._words_and_freq = self._words_and_freq + other._words_and_freq
        return res

    def vocabulary_length(self):
        """ Returning the length of the vocabulary """
        return len(Document._vocabulary)

    def WordsAndFreq(self):
        """ Returning the dictionary, containing the words (keys) with
        their frequency (values) as contained in the BagOfWords attribute
        of the document"""
        return self._words_and_freq.BagOfWords()

    def Words(self):
        """ Returning the words of the Document object """
        d = self._words_and_freq.BagOfWords()
        return d.keys()

    def WordFreq(self, word):
        """ Returning the number of times the word "word" appeared in the
        document """
        bow = self._words_and_freq.BagOfWords()
        if word in bow:
            return bow[word]
        else:
            return 0

    def __and__(self, other):
        """ Intersection of two documents. A list of words occuring in
        both documents is returned """
        intersection = []
        words1 = self.Words()
        for word in other.Words():
            if word in words1:
                intersection += [word]
        return intersection


class DocumentClass(Document):
    def __init__(self, vocabulary):
        Document.__init__(self, vocabulary)
        self._number_of_docs = 0

    def Probability(self, word):
        """ returns the probabilty of the word "word" given the class "self" """
        doc_vocab_len = Document._vocabulary.len()
        SumN = 0
        for i in range(doc_vocab_len):
            SumN = DocumentClass._vocabulary.WordFreq(word)
        N = self._words_and_freq.WordFreq(word)
        erg = 1 + N
        erg /= doc_vocab_len + SumN
        return erg

    def __add__(self, other):
        """ Overloading the "+" operator. Adding two DocumentClass objects
        consists in adding the BagOfWords of the DocumentClass objectss """
        res = DocumentClass(self._vocabulary)
        res._words_and_freq = self._words_and_freq + other._words_and_freq

        return res

    def SetNumberOfDocs(self, number):
        self._number_of_docs = number

    def NumberOfDocuments(self):
        return self._number_of_docs


class Classifier(object):
    def __init__(self):
        self.__document_classes = {}
        self.__vocabulary = BagOfWords()

    def sum_words_in_class(self, dclass):
        """ The number of times all different words of a dclass appear in a class """
        sum = 0
        for word in self.__vocabulary.Words():
            WaF = self.__document_classes[dclass].WordsAndFreq()
            if word in WaF:
                sum += WaF[word]
        return sum

    def learn(self, directory, dclass_name):
        """ directory is a path, where the files of the class with the name
            dclass_name can be found """

        print('\tLearning Class: ', dclass_name)
        document_class = DocumentClass(self.__vocabulary)

        class_files_list = os.listdir(directory)
        print('dir', class_files_list, '\n')

        for file in class_files_list:
            doc = Document(self.__vocabulary)

            doc.read_document(directory + "/" + file, learn=True)
            document_class = document_class + doc



        """__document_classes stores the locations of each document class"""
        self.__document_classes[dclass_name] = document_class
        document_class.SetNumberOfDocs(len(class_files_list))
        print('Number Of Documents:', str(document_class.NumberOfDocuments()))

    def Probability(self, doc, document_class=""):
        """Calculates the probability for a class dclass given a document doc"""

        if document_class:

            """Variable to store the sum of words in a class """
            sum_word_in_class = self.sum_words_in_class(document_class)

            prob = 0

            d = Document(self.__vocabulary)
            d.read_document(doc)

            print('\n')
            for category in self.__document_classes:

                sum_word_in_category = self.sum_words_in_class(category)
                print('Class ->', category , 'Number Of Words:', sum_word_in_category)

                product = 1
                for word_in_doc in d.Words():

                    if word_in_doc not in removable_words_symbols:

                        word_freq_in_class = 1 + self.__document_classes[document_class].WordFreq(word_in_doc)
                        word_freq_in_category = 1 + self.__document_classes[category].WordFreq(word_in_doc)

                        result = word_freq_in_category * sum_word_in_class / (
                                word_freq_in_class * sum_word_in_category)

                        product *= result

                prob += product * self.__document_classes[category].NumberOfDocuments() / self.__document_classes[
                    document_class].NumberOfDocuments()

            if prob != 0:
                return 1 / prob
            else:
                return -1
        else:

            prob_list = []
            for document_class in self.__document_classes:

                print('\nCalculating Probability -> Document Class:', document_class)
                prob = self.Probability(doc, document_class)
                print('\t Probability:', str(prob))
                prob_list.append([document_class, prob])

            prob_list.sort(key=lambda x: x[1], reverse=True)
            print('List Of Probabilities:', prob_list)

            return prob_list


classifier = Classifier()

DClasses = ["clinton", "lawyer", "math", "medical", "music", "sex"]

type_of_docs = "learn/"

print('Learning\n')
for doc_class in DClasses:
    print('\nCurrent Class: ', doc_class)
    classifier.learn(type_of_docs + doc_class, doc_class)

type_of_docs = "test/"

print('Testing\n')
for doc_class in DClasses:
    print('\t\t\t\t\nNew Class\n')
    print('\t\nCurrent Class: ', doc_class)
    files_in_class_list = os.listdir(type_of_docs + doc_class)

    for file in files_in_class_list:
        print('\n\n----------> New File <-----------')
        print('\t\nCurrent File in Class: ', file)
        res = classifier.Probability(type_of_docs + doc_class + "/" + file)
