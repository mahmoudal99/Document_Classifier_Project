from tkinter import filedialog
import os
from tkinter import *
import tkinter as tk
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
        self.learned_classes = {}
        self.__vocabulary = BagOfWords()
        self.window = Tk()

    def sum_words_in_class(self, dclass):
        """ The number of times all different words of a dclass appear in a class """
        sum = 0
        for word in self.__vocabulary.Words():
            WaF = self.learned_classes[dclass].WordsAndFreq()
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
        self.learned_classes[dclass_name] = document_class
        document_class.SetNumberOfDocs(len(class_files_list))
        print(document_class.WordsAndFreq())
        print('Number Of Documents:', str(document_class.NumberOfDocuments()))

    def Probability(self, test_doc, document_class=""):

        if document_class:

            sum_of_words_in_doc_class = self.sum_words_in_class(document_class)
            prob = 0

            test_document = Document(self.__vocabulary)
            test_document.read_document(test_doc)

            print("2nd For Loop")
            """ Loop through each learned class """
            for _class in self.learned_classes:

                print('\tClass: ', str(_class))

                sum_of_words_in_class = self.sum_words_in_class(_class)

                product = 1
                for word_in_doc in test_document.Words():

                    if word_in_doc not in removable_words_symbols:

                        freq_of_words_given_docClass = 1 + self.learned_classes[document_class].WordFreq(word_in_doc)
                        freq_of_words_in_class = 1 + self.learned_classes[_class].WordFreq(word_in_doc)

                        result = freq_of_words_in_class * sum_of_words_in_doc_class / (freq_of_words_given_docClass * sum_of_words_in_class)
                        product *= result

                prob += product * self.learned_classes[_class].NumberOfDocuments() / self.learned_classes[document_class].NumberOfDocuments()

            if prob != 0:
                return 1 / prob
            else:
                return -1
        else:
            prob_list = []

            """ Loop through each learned document class """
            for document_class in self.learned_classes:
                print("\n1st For Loop")
                print("Learned Class: ", str(document_class))
                prob = self.Probability(test_doc, document_class)
                prob_list.append([document_class, prob])

            prob_list.sort(key=lambda x: x[1], reverse=True)
            print('\n')
            print(prob_list)
            return prob_list

    def start_program(self):

        self.window.title("Document Classifier")
        self.window.geometry('800x400')

        btn = Button(self.window, text="Open File", bg="black", fg="white", command=classifier.choose_file)
        btn.grid(sticky=W, row=0, padx=5)

        btn = Button(self.window, text="Learn Files", bg="black", fg="white", command=classifier.start_learning)
        btn.grid(column=1, row=0, padx=5)

        btn = Button(self.window, text="Classify File", bg="black", fg="white", command=classifier.start_classifying)
        btn.grid(column=2, row=0, padx=5)

        self.window.mainloop()


    def choose_file(self):

        file1 = filedialog.askopenfile()
        data = file1.read()

        f = open("test/test.txt", "w+")
        for i in data:
            f.write(i)
        f.close()

        w = tk.Label(self.window, text="File Opened")
        w.grid(column=0, row=1)

    def start_learning(self):
        DClasses = ["heart", "volcanoes", "mongol"]

        type_of_docs = "learn/"

        w = tk.Label(self.window, text="Learning Data")
        w.grid(column=1, row=1)

        """ Learn each text file related to a particular class """
        for doc_class in DClasses:
            print('\nCurrent Class: ', doc_class)
            self.learn(type_of_docs + doc_class, doc_class)

    def start_classifying(self):
        w = tk.Label(self.window, text="Classifying Your Document")
        w.grid(column=2, row=1)
        type_of_docs = "test/"
        result = self.Probability(type_of_docs + "/" + "test.txt")

        T = Text(self.window, height=6, width=30)
        T.grid(column=0, row=2)

        for word in result:
            T.insert(END, word)
            T.insert(END, "\n")



classifier = Classifier()
classifier.start_program()