import logging

from framenet_tools.config import ConfigManager
from framenet_tools.data_handler.reader import DataReader
from framenet_tools.fee_identification.feeidentifier import FeeIdentifier
from framenet_tools.pipelinestage import PipelineStage


class FeeID(PipelineStage):
    """
    The Frame evoking element identification stage

    Only relies on static predictions
    """

    def __init__(self, cM: ConfigManager):
        super().__init__(cM)

    def train(self, m_reader: DataReader, m_reader_dev: DataReader):
        """
        No training needed

        :param m_reader: The DataReader object which contains the training data
        :param m_reader_dev: The DataReader object for evaluation and auto stopping
                            (NOTE: not necessarily given, as the focus might lie on maximizing the training data)
        :return:
        """

        # Nothing to train on this stage
        logging.debug(f"Training FeeID complete!")

        return

    def predict(self, m_reader: DataReader):
        """
        Predict the given data

        NOTE: Changes the object itself

        :param m_reader: The DataReader object
        :return:
        """

        fee_finder = FeeIdentifier(self.cM)

        fee_finder.predict_fees(m_reader)
