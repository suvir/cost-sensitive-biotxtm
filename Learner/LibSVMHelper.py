__author__ = 'suvir'
import numpy as np


class LibSVMHelper:
    def __init__(self, label_estimator_matrix):
        self.p = label_estimator_matrix

    def generate_weights_and_labels(self):
        p = self.p
        # Label vector
        y = np.zeros_like(p)
        # Cost vector
        c = np.zeros_like(p)
        for i in range(len(p)):
            y[i] = round(p[i])

        positive_ratio = sum(y) / len(y)

        for i in range(len(p)):
            if y[i] == 1.0:
                c[i] = p[i] / positive_ratio
            else:
                c[i] = p[i] / (1 - positive_ratio)
        return y, c

    def createWeightsFile(self, weights_filename):
        labels, costs = self.generate_weights_and_labels()
        f = open(weights_filename, "w")
        for i in costs:
            f.write(str(i) + '\n')
        f.close()

if __name__ == "__main__":
    p = np.loadtxt("../Label_Estimator_output.txt")
    helper = LibSVMHelper(p)
    helper.createWeightsFile("../deleteme_cost_output.txt")
