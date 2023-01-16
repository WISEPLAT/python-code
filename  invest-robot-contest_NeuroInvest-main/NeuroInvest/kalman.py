from pykalman import KalmanFilter
from numpy import array

class Kalman:
    __smoothData = {}

    def __init__(self, priceData):

        measurements = array(list(priceData.values()), dtype = float)

        if len(measurements) > 1:
            initial_state_mean = [measurements[0], 0,
                                  measurements[1], 0]

            kalmanFilter = KalmanFilter(initial_state_mean = initial_state_mean)

            kalmanFilter = kalmanFilter.em(measurements, n_iter = 5)
            (smoothed_state_means, smoothed_state_covariances) = kalmanFilter.smooth(measurements)

            self.__smoothData = smoothed_state_means[:, 0]

    def getSmoothData(self):
        return self.__smoothData