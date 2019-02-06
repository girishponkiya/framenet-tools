from framenet_tools.config import ConfigManager
from framenet_tools.frame_identification.frameidentifier import FrameIdentifier
from framenet_tools.frame_identification.reader import DataReader


def calc_f(tp: int, fp: int, fn: int):
    """
    Calculates the F1-Score

    NOTE: This follows standard evaluation metrics
    TAKEN FROM: Open-SESAME (https://github.com/swabhs/open-sesame)

    :param tp: True Postivies Count
    :param fp: False Postivies Count
    :param fn: False Negatives Count
    :return: A Triple of Precision, Recall and F1-Score
    """
    if tp == 0.0 and fp == 0.0:
        pr = 0.0
    else:
        pr = tp / (tp + fp)
    if tp == 0.0 and fn == 0.0:
        re = 0.0
    else:
        re = tp / (tp + fn)
    if pr == 0.0 and re == 0.0:
        f = 0.0
    else:
        f = 2.0 * pr * re / (pr + re)
    return pr, re, f


def evaluate_fee_identification(files: list):
    """
    Evaluates the F1-Score of the Frame Evoking Element Identification only

    :param files: The Files to evaluate on
    :return: A Triple of Precision, Recall and F1-Score
    """
    m_data_reader = DataReader()
    m_data_reader.read_data(files[0], files[1])

    gold_sentences = m_data_reader.annotations.copy()

    m_data_reader.predict_fees()

    tp = fp = fn = 0

    for gold_annotations, predictied_annotations in zip(
        gold_sentences, m_data_reader.annotations
    ):
        for gold_annotation in gold_annotations:
            if gold_annotation.fee_raw in [x.fee_raw for x in predictied_annotations]:
                tp += 1
            else:
                fn += 1

        for predicted_annotation in predictied_annotations:
            if predicted_annotation not in [x.fee_raw for x in gold_annotations]:
                fp += 1

    print(tp, fp, fn)

    return calc_f(tp, fp, fn)


def evaluate_frame_identification(cM: ConfigManager):
    """
    Evaluates the F1-Score for a model on a given file set

    :param cM: The ConfigManager containing the saved model and evaluation files
    :return:
    """

    f_i = FrameIdentifier(cM)
    f_i.load_model(cM.saved_model)

    for file in cM.eval_files:
        print("Evaluating " + file[0])
        tp, fp, fn = f_i.evaluate_file(file)
        pr, re, f1 = calc_f(tp, fp, fn)

        print(
            "Evaluation complete!\n True Positives: %d False Postives: %d False Negatives: %d \n Precision: %f Recall: %f F1-Score: %f"
            % (tp, fp, fn, pr, re, f1)
        )


"""
f1 = evaluate_fee_identification(DEV_FILES)
print(f1)

f1 = evaluate_frame_identification(SAVED_MODEL, DEV_FILES)
print(f1)

f_i = FrameIdentifier()
f_i.load_model(SAVED_MODEL)
f_i.write_predictions("../data/experiments/xp_001/data/WallStreetJournal20150915.txt", "here.txt")
"""