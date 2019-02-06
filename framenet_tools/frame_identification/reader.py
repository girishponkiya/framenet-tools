import nltk

from framenet_tools.frame_identification.feeidentifier import FeeIdentifier


class Annotation(object):
    def __init__(
        self,
        frame: str = "Default",
        fee: str = None,
        position: int = None,
        fee_raw: str = None,
        sentence: list = None,
    ):
        self.frame = frame
        self.fee = fee
        self.position = position
        self.fee_raw = fee_raw
        self.sentence = sentence


class DataReader(object):
    def __init__(
        self, path_sent: str = None, path_elements: str = None, raw_path: str = None
    ):

        # Provides the ability to set the path at object creation (can also be done on load)
        self.path_sent = path_sent
        self.path_elements = path_elements
        self.raw_path = raw_path

        self.sentences = []
        self.annotations = []

        # Flags
        self.is_annotated = None
        self.is_loaded = False

        self.dataset = []

    def digest_raw_data(self, elements: list, sentences: list):
        """
        Converts the raw elements and sentences into a nicely structured dataset

        NOTE: This representation is meant to match the one in the "frames-files"

        :param elements: the annotation data of the given sentences
        :param sentences: the sentences to digest
        :return:
        """

        # Append sentences
        for sentence in sentences:
            words = sentence.split(" ")
            if "" in words:
                words.remove("")
            self.sentences.append(words)

        for element in elements:
            # Element data
            element_data = element.split("\t")

            frame = element_data[3]  # Frame
            fee = element_data[4]  # Frame evoking element
            position = element_data[5]  # Position of word in sentence
            fee_raw = element_data[6]  # Frame evoking element as it appeared

            sent_num = int(element_data[7])  # Sentence number

            if sent_num <= len(self.annotations):
                self.annotations.append([])

            self.annotations[sent_num].append(
                Annotation(frame, fee, position, fee_raw, self.sentences[sent_num])
            )

    def loaded(self, is_annotated: bool):
        """
        Helper for setting flags

        :param is_annotated: flag if loaded data was annotated
        :return:
        """

        self.is_loaded = True
        self.is_annotated = is_annotated

    def read_raw_text(self, raw_path: str = None):
        """
        Reads a raw text file and saves the content as a dataset

        NOTE: Applying this function removes the previous dataset content

        :param raw_path: The path of the file to read
        :return:
        """

        if raw_path is not None:
            self.raw_path = raw_path

        if self.raw_path is None:
            raise Exception("Found no file to read")

        file = open(raw_path, "r")
        raw = file.read()
        file.close()

        sents = nltk.sent_tokenize(raw)

        for sent in sents:
            words = nltk.word_tokenize(sent)
            self.sentences.append(words)

        self.loaded(False)

    def read_data(self, path_sent: str = None, path_elements: str = None):
        """
        Reads a the sentence and elements file and saves the content as a dataset

        NOTE: Applying this function removes the previous dataset content

        :param path_sent: The path to the sentence file
        :param path_elements: The path to the elements
        :return:
        """

        if path_sent is not None:
            self.path_sent = path_sent

        if path_elements is not None:
            self.path_elements = path_elements

        if self.path_sent is None:
            raise Exception("Found no sentences-file to read")

        if self.path_elements is None:
            raise Exception("Found no elements-file to read")

        file = open(self.path_sent, "r")
        sentences = file.read()
        file.close()

        file = open(self.path_elements, "r")
        elements = file.read()
        file.close()

        sentences = sentences.split("\n")
        elements = elements.split("\n")

        # Remove empty line at the end
        if elements[len(elements) - 1] == "":
            # print("Removed empty line at eof")
            elements = elements[: len(elements) - 1]

        if sentences[len(sentences) - 1] == "":
            # print("Removed empty line at eof")
            sentences = sentences[: len(sentences) - 1]

        # print(sentences)

        self.digest_raw_data(elements, sentences)

        self.loaded(True)

    def predict_fees(self):
        """
        Predicts the Frame Evoking Elements
        NOTE: This drops current annotation data

        :return:
        """

        self.annotations = []
        fee_finder = FeeIdentifier()

        for sentence in self.sentences:
            possible_fees = fee_finder.query([sentence])
            predicted_annotations = []

            # Create new Annotation for each possible frame evoking element
            for possible_fee in possible_fees:
                predicted_annotations.append(
                    Annotation(fee_raw=possible_fee, sentence=sentence)
                )

            self.annotations.append(predicted_annotations)

    # print(possible_fees)

    def get_annotations(self, sentence=None):
        # TODO
        return None