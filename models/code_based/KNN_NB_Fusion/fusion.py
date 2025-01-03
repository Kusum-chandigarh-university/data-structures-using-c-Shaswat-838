from math import exp, pi, sqrt

# A small constant added to variance to prevent division by zero
DATA_NOISE = 10 ** (-5)


class KNNBayesClassifier:
    def __init__(self, space):
        """
        Initializes KNNBayesClassifier with the space to classify
        """
        self.total = None
        self.prior = None
        self.variance = None
        self.mean = None
        self.space = space

    def sort_by_distance(self, point):
        """
        Sorts the points in the space by distance to the given point
        """
        self.space.points.sort(key=lambda x: KNNBayesClassifier.calc_distance(x, point))

    @staticmethod
    def calc_distance(p1, p2):
        """
        Calculates Euclidean distance between two points
        """
        calc = lambda x1, x2: pow(x1 - x2, 2)
        return sqrt(sum(map(calc, p1.dimensions, p2.dimensions)))

    def add_mean_var(self, k):
        """
        Calculates mean, variance, and prior probabilities for each classification in the space
        based on the k-nearest points
        """
        global point
        self.mean = {}
        self.variance = {}
        self.prior = {}
        self.total = 0

        # initialize dictionaries for each classification
        for classification in self.space.classifications:
            self.mean[classification] = [[] for _ in self.space.points[0].dimensions]
            self.variance[classification] = self.mean.get(classification).copy()
            self.prior[classification] = 0

        # calculate mean, variance, and prior for each classification
        for point in self.space.points[:k]:
            for dimension in range(len(point.dimensions)):
                self.mean[point.classifier][dimension].append(point.dimensions[dimension])
            self.prior[point.classifier] += 1
            self.total += 1

        for classification in self.space.classifications:
            for dimension in range(len(self.mean.get(point.classifier))):
                self.mean[classification][dimension], self.variance[classification][
                    dimension] = KNNBayesClassifier.calc_mean_var(self.mean[classification][dimension])

    def classify(self, point, k=100):
        """
        Classifies a given point based on k-nearest points and Bayesian probabilities
        """
        self.sort_by_distance(point)
        data = point.dimensions
        self.add_mean_var(k)

        best_classification = None
        best_p = 0

        # calculate Bayesian probabilities for each classification and choose best one
        for classification in self.space.classifications:
            cumulative_p = self.prior[classification] / self.total

            for dimension in range(len(data)):
                variance = self.variance[classification][dimension] + DATA_NOISE
                mean = self.mean[classification][dimension]

                p = 1 / (sqrt(2 * pi * variance)) * exp(-((data[dimension] - mean) ** 2) / (2 * variance))
                cumulative_p *= p

            if cumulative_p > best_p:
                best_p = cumulative_p
                best_classification = classification

        return best_classification

    @staticmethod
    def calc_mean_var(data):
        """
        Calculates the mean and variance of a list of data points
        """
        if (len(data)) == 0:
            return 0, 0
        mean = sum(data) / len(data)
        if len(data) == 1:
            variance = 0
        else:
            variance = sum(map(lambda x: pow(x - mean, 2), data)) / (len(data) - 1)
        return mean, variance
