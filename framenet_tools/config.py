import configparser
import logging
import os
import re

from typing import List

from framenet_tools.data_handler.frame_embedding_manager import FrameEmbeddingManager
from framenet_tools.data_handler.word_embedding_manager import WordEmbeddingManager

CONFIG_PATH = "config.file"


class ConfigManager(object):

    saved_model: str

    train_files: List[List[str]]
    eval_files: List[List[str]]
    semeval_files: List[str]
    all_files: List[List[str]]

    use_cuda: bool
    use_spacy: bool
    syntax_only_mode: bool

    hidden_sizes: List[int]
    activation_functions: List[str]
    batch_size: int
    num_epochs: int
    learning_rate: float
    embedding_size: int

    def __init__(self):

        self.train_files = []
        self.eval_files = []
        self.semeval_files = []

        # NOTE: model is actually saved in three individual files (.ph, .in_voc, .out_voc)
        model_name = "model"
        dir_models = "data/models/"
        self.saved_model = os.path.join(dir_models, model_name)

        self.use_cuda = True
        self.use_spacy = True
        self.syntax_only_mode = True

        self.all_files = self.train_files + self.eval_files

        self.hidden_sizes = [512, 256]
        self.activation_functions = ["ReLU", "ReLU"]
        self.batch_size = 10
        self.num_epochs = 5
        self.learning_rate = 0.001
        self.embedding_size = 300

        self.level = 3

        if not self.load_config():
            self.create_config()

        self.wEM = WordEmbeddingManager()
        self.fEM = FrameEmbeddingManager()

    def load_defaults(self):
        """
        Loads the builtin defaults

        :return:
        """

        # NOTE this path is also the default path for pyfn
        dir_data = "data/experiments/xp_001/data/"

        # The files generated by pyfn
        train_files = ["train.sentences", "train.frame.elements"]
        dev_files = ["dev.sentences", "dev.frames"]
        test_files = ["test.sentences", "test.frames"]

        self.train_files = [train_files]
        self.eval_files = [dev_files, test_files]

        self.semeval_files = [
            "data/experiments/xp_001/data/train.gold.xml",
            "data/experiments/xp_001/data/dev.gold.xml",
            "data/experiments/xp_001/data/test.gold.xml",
        ]

        for handle in self.train_files:
            handle[0] = os.path.join(dir_data, handle[0])
            handle[1] = os.path.join(dir_data, handle[1])

        for handle in self.eval_files:
            handle[0] = os.path.join(dir_data, handle[0])
            handle[1] = os.path.join(dir_data, handle[1])

    def load_config(self, path: str = CONFIG_PATH):
        """
        Loads the config file and saves all found variables

        NOTE: If no config file was found, the default configs will be loaded instead

        :type path: The path of the config file to load
        :return: A boolean - True if the config file was loaded, False if defaults were loaded
        """

        if not os.path.isfile(path):
            logging.info(f"Config not found, creating Config file!")
            self.load_defaults()
            return False

        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)

        for section in config.sections():

            if section == "TRAINPATHS":
                for key in config[section]:

                    path = config[section][key].rsplit("\t")
                    self.train_files.append(path)

            if section == "EVALPATHS":
                for key in config[section]:

                    path = config[section][key].rsplit("\t")
                    self.eval_files.append(path)

            if section == "SEMEVAL":
                for key in config[section]:
                    self.semeval_files.append(config[section][key])

            if section == "VARIABLES":
                for key in config[section]:
                    if key == "model_path":
                        self.saved_model = config[section][key]

                    if key == "use_cuda":
                        self.use_cuda = config[section][key] == "True"

                    if key == "use_spacy":
                        self.use_spacy = config[section][key] == "True"

                    if key == "syntax_only_mode":
                        self.syntax_only_mode = config[section][key] == "True"

                    if key == "level":
                        self.level = int(config[section][key])

            if section == "HYPERPARAMETER":
                for key in config[section]:
                    if key == "hidden_sizes":
                        # Find numbers and convert to int using regex
                        found_numbers = re.findall(r"[0-9.]+", config[section][key])
                        self.hidden_sizes = [float(t) for t in found_numbers]

                    if key == "activation_functions":
                        self.activation_functions = re.findall(
                            r"\w+", config[section][key]
                        )

                    if key == "batch_size":
                        self.batch_size = int(config[section][key])

                    if key == "num_epochs":
                        self.num_epochs = int(config[section][key])

                    if key == "learning_rate":
                        self.learning_rate = float(config[section][key])

                    if key == "embedding_size":
                        self.embedding_size = int(config[section][key])

        return True

    def paths_to_string(self, files: List[List[str]]):
        """
        Helper function for turning a list of file paths into a structured string

        :param files: A list of files
        :return: The string containing all files
        """

        string = ""

        for handle in files:
            string += (
                handle[0].rsplit(".")[0].rsplit("/")[-1]
                + ": "
                + handle[0]
                + "\t"
                + handle[1]
                + "\n"
            )

        string += "\n"

        return string

    def create_config(self, path: str = CONFIG_PATH):
        """
        Creates a config file and saves all necessary variables

        :type path: The path of the config file to save to
        :return:
        """

        config_string = "[TRAINPATHS]\n"
        config_string += self.paths_to_string(self.train_files)

        config_string += "[EVALPATHS]\n"
        config_string += self.paths_to_string(self.eval_files)

        config_string += "[SEMEVAL]\n"
        for file_path in self.semeval_files:
            config_string += file_path.rsplit("/")[-1].rsplit(".")[0] + ": " + file_path + "\n"

        config_string += "\n[VARIABLES]\n"
        config_string += "model_path: " + self.saved_model + "\n"
        config_string += "use_cuda: " + str(self.use_cuda) + "\n"
        config_string += "use_spacy: " + str(self.use_spacy) + "\n"
        config_string += "syntax_only_mode: " + str(self.syntax_only_mode) + "\n"
        config_string += "level: " + str(self.level) + "\n"

        config_string += "\n[HYPERPARAMETER]\n"
        config_string += "hidden_sizes: " + str(self.hidden_sizes) + "\n"
        config_string += (
            "activation_functions: " + str(self.activation_functions) + "\n"
        )
        config_string += "batch_size: " + str(self.batch_size) + "\n"
        config_string += "num_epochs: " + str(self.num_epochs) + "\n"
        config_string += "learning_rate: " + str(self.learning_rate) + "\n"
        config_string += "embedding_size: " + str(self.embedding_size) + "\n"

        with open(path, "w") as file:
            file.write(config_string)
