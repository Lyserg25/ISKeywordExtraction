import networkx
import treetaggerwrapper
import pprint
import itertools
import nltk
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


    def extract_keywords(self, text):
        """Extracts keywords from a text.
        
        :param text: text the keywords are extracted from
        :return: keywords of the text
        """
        tagged_text = self.tag_text(text)
        filtered_words = self.filter_words(tagged_text)
        graph = self.build_graph_keywords(filtered_words)
        pagerank = networkx.pagerank(graph, alpha=self.d, tol=self.threshold)
        #graph = self.build_graph_levenshtein_distance(filtered_words)
        #pagerank = networkx.pagerank(graph, alpha=self.d, tol=self.threshold, weight='weight')
        pagerank_sorted = sorted(pagerank, key=pagerank.get, reverse=True)
        keywords = self.reconstruct_keywords(tagged_text, pagerank_sorted)
        return ', '.join(keyword for keyword in keywords)


    def tag_text(self, text):
        """Uses TreeTagger to add pos tags to the words of a given text.
        
        :param text: text to be tagged
        :return: list of tagged words
        """
        treetagger = treetaggerwrapper.TreeTagger(TAGLANG='de')
        return [item.split('\t') for item in treetagger.tag_text(text)]


    def filter_words(self, tagged_text, tags=['NN', 'ADJA']):
        """Filters words with certain tags from a list of tagged words.
        
        :param tagged_text: list of tagged words
        :param tags: the tags of the words that should be filtered
        :return: list of filtered words
        """
        return [word[0] for word in tagged_text if word[1] in tags]


    def build_graph_keywords(self, nodes):
        """Builds an undirected unweighted graph where only the nodes that co-occur within a window of 2 are connected

        :param nodes: list of nodes that are added to the graph
        :return: the constructed graph
        """
        nodes_unique = list(set(nodes))
        graph = networkx.Graph()
        graph.add_nodes_from(nodes_unique)
        for i in range(0, len(nodes) - 2):
            graph.add_edge(nodes[i], nodes[i + 1])
        return graph


    def build_graph_sentences(self, nodes):
        """Builds an undirected weighted graph where all nodes are connected using a sentence similarity between two nodes as weight.

        :param nodes: list of nodes that are added to the graph
        :return: the constructed graph
        """
        graph = networkx.Graph()
        graph.add_nodes_from(nodes)
        node_pairs = list(itertools.combinations(nodes, 2))
        for nodePair in node_pairs:
            sentence_similarity = self.calc_sentence_similatity(nodePair[0], nodePair[1])
            graph.add_edge(nodePair[0], nodePair[1], weight=sentence_similarity)
        return graph


    def calc_sentence_similatity(self, sentence1, sentence2):
        """Calculates the similarity of two sentences (list of words). 
        The similarity is the amount of words that occur in both sentence divided by the length of each sentence.  
                
        :param sentence1: first sentence (list of words)
        :param sentence2: second sentence (list of words)
        :return: the calculated similarity
        """
        amount_same_words = len([word for word in sentence1 if word in sentence2])
        return amount_same_words / (log(len(sentence1)) * log(len(sentence2)))


    def build_graph_levenshtein_distance(self, nodes):
        """Builds an undirected weighted graph where all nodes are connected using levenshtein distance between two nodes as weight.
        
        :param nodes: list of nodes that are added to the graph
        :return: the constructed graph
        """
        nodes_unique = list(set(nodes))
        graph = networkx.Graph()
        graph.add_nodes_from(nodes_unique)
        node_pairs = list(itertools.combinations(nodes, 2))
        for nodePair in node_pairs:
            lev_distance = self.calc_levenshtein_distance(nodePair[0], nodePair[1])
            graph.add_edge(nodePair[0], nodePair[1], weight=lev_distance)
        return graph


    def calc_levenshtein_distance(self, str1, str2):
        """Levenshtein distance is calculated.
        Levenshtein distance between two strings is the minimum number of single-character edits (insertions, deletions or substitutions) required to change one string into the other.
        
        :param str1: first string
        :param str2: second string
        :return: calculated levenshtein distance
        """
        if len(str1) > len(str2):
            str1, str2 = str2, str1
        distances = range(len(str1) + 1)
        for index2, char2 in enumerate(str2):
            new_distances = [index2 + 1]
            for index1, char1 in enumerate(str1):
                if char1 == char2:
                    new_distances.append(distances[index1])
                else:
                    new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))
            distances = new_distances
        return distances[-1]


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


    def extract_sentences(self, text):
        """Extracts sentences from a text that can be used for a summary.
        
        :param text: text the sentences are extracted from
        :return: extracted sentences
        """
        tokenizer = nltk.data.load('tokenizers/punkt/german.pickle')
        sentences = tokenizer.tokenize(text)
        #tagged_sentences = [self.tag_text(sentence) for sentence in sentences]
        #sentences_filtered = [self.get_filtered_words(sentence, tags=['NN', 'ADJA', 'VVFIN', 'VVPP']) for sentence in tagged_sentences]
        graph = self.build_graph_sentences(sentences)
        #graph = self.build_graph_levenshtein_distance(sentences)
        pagerank = networkx.pagerank(graph, alpha=self.d, tol=self.threshold, weight='weight')
        pagerank_sorted = sorted(pagerank, key=pagerank.get, reverse=True)
        pagerank_sorted = pagerank_sorted[0:len(pagerank_sorted)//3]
        summary = ' '.join(sentence for sentence in sentences if sentence in pagerank_sorted)
        return summary


KeywordExtraction()