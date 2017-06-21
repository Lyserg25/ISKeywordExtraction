import networkx
import treetaggerwrapper
import pprint
import itertools
import nltk
import re
from math import log


class KeywordExtraction:

    def __init__(self):
        #self.text = 'Beim Eintreffen der Feuerwehr befand sich eine Wohnung in der vierten Etage eines fünfgeschossigen Wohnhauses im Vollbrand. Vom Balkon der Brandwohnung wurde ein Mensch über eine Drehleiter in Sicherheit gebracht, rettungsdienstlich versorgt und in ein Krankenhaus transportiert. Die Brandbekämpfung erfolgte in vier Einsatzabschnitten mit zwei C-Rohren unter Einsatz von 24 Pressluftatmern. Ein Wasserschaden im dritten Obergeschoss konnte durch den Einsatz einer Wasserwehr teilweise eingedämmt werden. Die Einsatzstelle war um 23.33 Uhr übersichtlich und um 00.43 Uhr unter Kontrolle. Zur Sicherstellung des Brandschutzes wurden zwei Freiwillige Feuerwehren in Dienst gerufen, eine weitere Freiwillige Feuerwehr verlängerte ihren Einsatzdienst.'
        #self.text = 'Um 21:23 Uhr wurde die Berliner Feuerwehr zu einem Verkehrsunfall in Altglienicke alarmiert. Ein Pkw fuhr gegen eine Straßenlaterne und prallte gegen einen massiven Gartenzaun. Eine Personen wurde dabei im Pkw eingeschlossen. Nach notärztlicher Versorgung und zur besonders schonenden Rettung wurde eine Seitenöffnung geschaffen und das Dach abgenommen. Zum Einsatz kamen hydraulische Rettungsgeräte vom LHF und dem Rüstwagen vom Technischen Dienst. Die verletzte Person wurde dann unter Notarztbegleitung in ein Krankenhaus gebracht. Mit Trennarbeiten unterstützte die Feuerwehr den Energieversorger beim Freischalten und Beseitigen der umgestürzten Straßenlaterne.'
        self.d = 0.85 #damping factor
        self.threshold = 0.0001
        #keywords = self.extract_keywords(self.text)
        #print('Keywords: ')
        #print('\n'.join(keyword for keyword in keywords))
        #summary = self.extract_sentences(self.text)
        #print('\nSummary: \n' + summary)


    def extract_keywords(self, text, terms = {}):
        """Extracts keywords from a text.

        :param text: text the keywords are extracted from
        :param terms: dictionary with relevant words of the text and their probability to be a technical term
        :return: keywords of the text
        """
        text = re.sub('[‚‘„“"» «›‹]', '', text)
        tagged_text = self.tag_text(text)
        filtered_words = self.filter_words(tagged_text)
        weighted_words = self.get_weighted_words(filtered_words, terms)
        graph = self.build_graph_keywords(weighted_words)
        pagerank = networkx.pagerank(graph, alpha=self.d, tol=self.threshold, weight='weight')
        pagerank_sorted = sorted(pagerank, key=pagerank.get, reverse=True)
        keywords = self.reconstruct_keywords(tagged_text, pagerank_sorted)
        return ', '.join(keyword for keyword in keywords)

    def get_weighted_words(self, words, terms):
        weighted_words = {}
        for word in words:
            if word in terms.keys():
                weighted_words[word] = terms[word]['wahrscheinlichkeit']
            else:
                weighted_words[word] = 0.0001
        return weighted_words

    def tag_text(self, text):
        """Uses TreeTagger to add pos tags to the words of a given text.
        
        :param text: text to be tagged
        :return: list of tagged words
        """
        treetagger = treetaggerwrapper.TreeTagger(TAGLANG='de')
        return [item.split('\t') for item in treetagger.tag_text(text)]


    def filter_words(self, tagged_text, tags=['NN', 'NE', 'ADJA',]):
        """Filters words with certain tags from a list of tagged words.
        
        :param tagged_text: list of tagged words
        :param tags: the tags of the words that should be filtered
        :return: list of filtered words
        """
        unwanted = list('–-')
        return [word[2] for word in tagged_text if (len(word) > 1 and word[1] in tags and word[2] not in unwanted)]


    def build_graph_keywords(self, nodes):
        """Builds an undirected unweighted graph where only the nodes that co-occur within a window of 2 are connected

        :param nodes: list of nodes that are added to the graph
        :return: the constructed graph
        """
        nodes_unique = list(set(nodes))
        graph = networkx.Graph()
        graph.add_nodes_from(nodes_unique)
        keys = list(nodes.keys())
        values = list(nodes.values())
        for i in range(0, len(nodes) - 2):
            graph.add_edge(keys[i], keys[i + 1], weight=(values[i] * values[i + 1]))
        return graph


    def build_graph_sentences(self, nodes, terms):
        """Builds an undirected weighted graph where all nodes are connected using a sentence similarity between two nodes as weight.

        :param nodes: list of nodes that are added to the graph
        :return: the constructed graph
        """
        graph = networkx.Graph()
        graph.add_nodes_from(nodes)
        node_pairs = list(itertools.combinations(nodes, 2))
        for nodePair in node_pairs:
            sentence_similarity = self.calc_sentence_similatity(nodePair[0], nodePair[1], terms)
            graph.add_edge(nodePair[0], nodePair[1], weight=sentence_similarity)
        return graph


    def calc_sentence_similatity(self, sentence1, sentence2, terms):
        """Calculates the similarity of two sentences (list of words). 
        The similarity is the amount of words that occur in both sentence divided by the length of each sentence.  
                
        :param sentence1: first sentence (list of words)
        :param sentence2: second sentence (list of words)
        :return: the calculated similarity
        """
        sentence1_words = self.get_words_of_sentence(sentence1)
        sentence2_words = self.get_words_of_sentence(sentence2)
        same_words = [word for word in sentence1_words if word in sentence2_words]
        weighted_same_words = self.get_weighted_words(same_words, terms)
        if (len(sentence1) <= 1) or len(sentence2) <= 1:
            return 0.0
        return sum(weighted_same_words.values()) / (log(len(sentence1)) * log(len(sentence2)))


    def get_words_of_sentence(self, sentence):
        words = re.sub('[^A-Za-zÄäÖöÜüß ]+', '', sentence).split(' ')
        return [word for word in words if word != '']


    def reconstruct_keywords(self, text, candidates):
        """Keywords that consist of multiple words are constructed by joining candidate keywords that are occur one after another.
        
        :param text: text
        :param candidates: candidate keywords
        :return: list of keywords
        """
        amount_keywords = len(candidates) // 3
        candidates = candidates[0:amount_keywords]
        keywords = set([])
        added_words = set([])
        for i in range(0, len(text) - 1):
            word1 = text[i]
            word2 = text[i + 1]
            if word1[0] in candidates:
                if word2[0] in candidates:
                    keywords.add(word1[0] + ' ' + word2[0])
                    added_words.add(word1[0])
                    added_words.add(word2[0])
                elif word1[0] not in added_words:
                    keywords.add(word1[2])
                    added_words.add(word1[2])
            elif i == len(text) - 2 and word2[0] in candidates and word2[0] not in added_words:
                keywords.add(word2[0])
        return keywords


    def extract_sentences(self, text, terms={}):
        """Extracts sentences from a text that can be used for a summary.
        
        :param text: text the sentences are extracted from
        :return: extracted sentences
        """
        tokenizer = nltk.data.load('tokenizers/punkt/german.pickle')
        sentences = tokenizer.tokenize(text)
        graph = self.build_graph_sentences(sentences, terms)
        pagerank = networkx.pagerank(graph, alpha=self.d, tol=self.threshold, weight='weight')
        pagerank_sorted = sorted(pagerank, key=pagerank.get, reverse=True)
        summary = ''
        if len(pagerank_sorted) >= 3:
            pagerank_sorted = pagerank_sorted[0:len(pagerank_sorted)//3]
            for sentence in sentences:
                if sentence in pagerank_sorted and len(summary.split(' ')) < 100:
                    summary = summary + sentence + ' '
            #summary = ' '.join(sentence for sentence in sentences if sentence in pagerank_sorted)
        elif len(pagerank_sorted) > 0:
            summary = pagerank_sorted[0]
        return summary


KeywordExtraction()