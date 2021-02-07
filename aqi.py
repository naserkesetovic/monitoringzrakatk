import math

class aqi:
    ''' 
    Izračuvana AQI u odnosu na unešene podatke 
    Bazirano na osnovu: https://www3.epa.gov/airnow/aqicalctest/nowcast.htm

    @param: vrijednost - lista [] vrijednosti, od najnovije do najstarije
    '''

    def __init__(self, values = []):
        if len(values) > 1:
            self.koncentracija = self.__concentration(values)
            self.aqi = self.__aqi(self.koncentracija)
            self.jedinica = "µg/m³"
            self.opis = self.__description(self.aqi)

        else:
            raise Exception('Nisu unešene vrijednosti za računanje AQI (list[vrijednosti])')
            return

    def __str__(self):
        return "Izračunate vrijednosti: AQI: {0}, koncentracija: {1} {2}, opis: '{3}'.".format(
            self.aqi,
            self.koncentracija,
            self.jedinica,
            self.opis
        )

    @staticmethod
    def __description(value):
        if value < 50:
            return "dobro"
        elif value < 100:
            return "srednje zagađeno"
        elif value < 150:
            return "nezdravo za osjetljive"
        elif value < 200:
            return "nezdravo"
        elif value < 300:
            return "izrazito nezdravo"
        else:
            return "opasno"

    @staticmethod
    def __linear(AQIhigh, AQIlow, Conchigh, Conclow, Concentration):
        linear = 0
        Conc = float(Concentration)
        value = round((((Conc - Conclow) / (Conchigh - Conclow)) * (AQIhigh - AQIlow) + AQIlow), 0)
        return value

    def __aqi(self, conc):
        AQI = 0
        if (conc >= 0 and conc < 12.1):
            AQI = self.__linear(50, 0, 12, 0, conc)

        elif (conc >= 12.1 and conc < 35.5):
            AQI = self.__linear(100, 51, 35.4, 12.1, conc)

        elif (conc >= 35.5 and conc < 55.5):
            AQI = self.__linear(150, 101, 55.4, 35.5, conc)

        elif (conc >= 55.5 and conc < 150.5):
            AQI = self.__linear(200, 151, 150.4, 55.5, conc)

        elif (conc >= 150.5 and conc < 250.5):
            AQI = self.__linear(300, 201, 250.4, 150.5, conc)

        elif (conc >= 250.5 and conc < 350.5):
            AQI = self.__linear(400, 301, 350.4, 250.5, conc)

        elif (conc >= 350.5 and conc < 500.5):
            AQI = self.__linear(500, 401, 500.4, 350.5, conc)

        else:
            AQI = 0

        return AQI

    @staticmethod
    def __concentration(values):
        range = 0
        rate_of_change = 0
        weight_factor = 0
        sum_of_data_times_weight_factor = 0
        sum_of_weight_factor = 0
        hour = 0

        min_value = min(values)
        max_value = max(values)

        range = max_value - min_value
        if range > 0:
            rate_of_change = range / max_value
        else:
            return 0

        weight_factor = 1 - rate_of_change

        if weight_factor < 0.5:
            weight_factor = 0.5

        for value in values:
            sum_of_data_times_weight_factor += value*(pow(weight_factor, hour))
            sum_of_weight_factor +=pow(weight_factor, hour)
            hour += 1

        nowCast = sum_of_data_times_weight_factor / sum_of_weight_factor
        nowCast = math.floor(10*nowCast)/10

        Conc = math.floor(10 * float(nowCast)) / 10

        return Conc