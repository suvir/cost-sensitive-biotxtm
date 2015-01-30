__author__ = 'suvir'
import numpy as np
from pprint import pprint


class LabelEstimator(object):
    def __init__(self, matrix_filename):
        self.mat = np.loadtxt(matrix_filename)

    def estimate(self):
        mat = self.mat
        rows = mat.shape[0]
        cols = mat.shape[1]
        P = np.zeros(shape=(rows, 1))
        E = np.zeros(shape=(1, cols))
        I, J = rows, cols

        # Laplace priors
        k1, K1 = 1, 1
        k2, K2 = 1, 1

        # More tunable constants
        t = 0
        eps = 1
        maxT = 1000
        threshold = 1e-10

        while t < maxT:
            if eps <= threshold:
                print "Converged. Delta below threshold."
                print eps
                break
            print t
            updates = np.zeros(shape=(1, cols))
            P_past = P

            print "Updating p(t)"
            for i in range(rows):
                errSum = 0.0
                for j in range(cols):
                    errSum += (1 - E[0, j]) * mat[i, j]
                P[i, 0] = (errSum + k1) / (J + K1)

            print "Updating e(t)"
            for j in range(cols):
                passageSum = 0.0
                for i in range(rows):
                    passageSum += P[i, 0] * mat[i, j]
                updates[0, j] = (passageSum + k2) / (I + K2)

            print "Calculating delta"
            eps = max(abs(updates - E).max(), abs(P_past - P).max())

            print "Updating error vector"
            E = updates
            t += 1
        return (P, E)


if __name__ == "__main__":
    est = LabelEstimator("../committee_matrix.txt")
    cost, errors = est.estimate()
    pprint(cost)
    pprint(errors)
    np.savetxt("../Label_Estimator_output.txt", cost)