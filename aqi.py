import math
import enum

class ErrorAQIValues(Exception):
    def __init__(self):
        super().__init__("Nisu unešene vrijednosti za računanje AQI - potrebno inicijalizirati!")

class ErrorOutOfRange(Exception):
    def __init__(self):
        super().__init__("Izračunate vrijednosti su izvan opsega!")

class ErrorCalculation(Exception):
    def __init__(self):
        super().__init__("Nije moguće izračunati!")

class CalculationType(enum.Enum):
    PM25 = "pm2.5"
    PM10 = "pm10"
    CO = "CO"
    SO2_1hr = "SO2 (1h)"
    SO2_24hr = "SO2 (24h)"
    O3_1hr = "O3 (1h)"
    O3_8hr = "O3 (8h)"
    NO2 = "NO2"

class Description(enum.Enum):
    good = "Dobro"
    moderate = "Srednje zagađeno"
    unhealthy = "Nezdravo za osjetljive grupe"
    very_unhealthy = "Vrlo nezdravo"
    hazardous = "Opasno"
    beyond = "Van mjernog opsega"

class aqi:
    ''' 
    Izračuvana AQI u odnosu na unešene podatke 
    Bazirano na osnovu: https://www3.epa.gov/airnow/aqicalctest/nowcast.htm

    @param: values - lista [] vrijednosti, od najnovije do najstarije
    @param: calculation_type: enum.CalculationType - vrsta polutanta (pm2.5, pm10, co, so2, o3, no)
    '''

    def __init__(self, values = [], calculation_type : CalculationType = CalculationType.PM25):
        if len(values) > 1:
            self.koncentracija = self.__concentration(values)
            self.jedinica = "µg/m³"

            self.__calculation_type = calculation_type.value

            if calculation_type == CalculationType.PM25:
                self.aqi = self.__aqi_pm25(self.koncentracija)
            elif calculation_type == CalculationType.PM10:
                self.aqi = self.__aqi_pm10(self.koncentracija)
            elif calculation_type == CalculationType.CO:
                self.aqi = self.__aqi_co(self.koncentracija)
            elif calculation_type == CalculationType.SO2_1hr:
                self.aqi = self.__aqi_so2_1hr(self.koncentracija)
            elif calculation_type == CalculationType.SO2_24hr:
                self.aqi = self.__aqi_so2_24hr(self.koncentracija)
            elif calculation_type == CalculationType.O3_1hr:
                self.aqi = self.__aqi_o3_1hr(self.koncentracija)
            elif calculation_type == CalculationType.O3_8hr:
                self.aqi = self.__aqi_o3_8hr(self.koncentracija)
            elif calculation_type == CalculationType.NO2:
                self.aqi = self.__aqi_no2(self.koncentracija)

            self.opis = self.__description(self.aqi).value

        else:
            raise ErrorAQIValues
            return

    def __str__(self):
        return "Izračunate vrijednosti: AQI: {0} (za: {1}), koncentracija: {2} {3}, opis: '{4}'.".format(
            self.aqi,
            self.__calculation_type,
            self.koncentracija,
            self.jedinica,
            self.opis
        )

    def __description(self, value):
        if value < 50:
            return Description.good
        elif value < 100:
            return Description.moderate
        elif value < 150:
            return Description.unhealthy
        elif value < 200:
            return Description.very_unhealthy
        elif value < 300:
            return Description.hazardous
        else:
            return Description.hazardous

    @staticmethod
    def __linear(AQIhigh, AQIlow, Conchigh, Conclow, Concentration):
        linear = 0
        Conc = float(Concentration)
        value = round((((Conc - Conclow) / (Conchigh - Conclow)) * (AQIhigh - AQIlow) + AQIlow), 0)
        return value

    def __aqi_pm25(self, conc):
        AQI = 0
        if (0 <= conc < 12.1):
            AQI = self.__linear(50, 0, 12, 0, conc)
        elif (12.1 <= conc < 35.5):
            AQI = self.__linear(100, 51, 35.4, 12.1, conc)
        elif (35.5 <= conc < 55.5):
            AQI = self.__linear(150, 101, 55.4, 35.5, conc)
        elif (55.5 <= conc < 150.5):
            AQI = self.__linear(200, 151, 150.4, 55.5, conc)
        elif (150.5 <= conc < 250.5):
            AQI = self.__linear(300, 201, 250.4, 150.5, conc)
        elif (250.5 <= conc < 350.5):
            AQI = self.__linear(400, 301, 350.4, 250.5, conc)
        elif (350.5 <= conc < 500.5):
            AQI = self.__linear(500, 401, 500.4, 350.5, conc)
        else:
            raise ErrorOutOfRange

        return AQI

    def __aqi_pm10(self, conc):
        AQI = 0
        c = math.floor(conc)
        if (0 <= c < 55):
            AQI = self.__linear(50, 0, 54, 0, c)
        elif (55 <= c < 155):
            AQI = self.__linear(100, 51, 154, 55, c)
        elif (155 <= c < 255):
            AQI = self.__linear(150, 101, 254, 155, c)
        elif (255 <= c < 355):
            AQI = self.__linear(200, 151, 354, 255, c)
        elif (355 <= c < 425):
            AQI = self.__linear(300, 201, 424, 355, c)
        elif (425 <= c < 505):
            AQI = self.__linear(400, 301, 504, 425, c)
        elif (505 <= c < 605):
            AQI = self.__linear(500, 401, 604, 505, c)
        else:
            raise ErrorOutOfRange

        return AQI

    def __aqi_co(self, conc):
        AQI = 0
        c = (math.floor(10 * conc)) / 10

        if (0 <= c < 4.5):
            AQI = self.__linear(50, 0, 4.4, 0, c)
        elif(4.5 <= c < 9.5):
            AQI = self.__linear(100, 51, 9.4, 4.5, c)
        elif(9.5 <= c < 12.5):
            AQI = self.__linear(150, 101, 12.4, 9.5, c)
        elif(12.5 <= c < 15.5):
            AQI = self.__linear(200, 151, 15.4, 12.5, c)
        elif(15.5 <= c < 30.5):
            AQI = self.__linear(300, 201, 30.4, 15.5, c)
        elif(30.5 <= c < 40.5):
            AQI = self.__linear(400, 301, 40.4, 30.5, c)
        elif(40.5 <= c < 50.5):
            AQI = self.__linear(500, 401, 50.4, 40.5, c)
        else:
            raise ErrorOutOfRange

        return AQI

    def __aqi_so2_1hr(self, conc):
        AQI = 0
        c = math.floor(conc)

        if (0 <= c < 36):
            AQI = self.__linear(50, 0, 35, 0, c)
        elif(36 <= c < 76):
            AQI = self.__linear(100, 51, 75, 36, c)
        elif(76 <= c < 186):
            AQI = self.__linear(150, 101, 185, 76, c)
        elif(186 <= c < 304):
            AQI = self.__linear(200, 151, 304, 186, c)
        elif(304 <= c < 604):
            # AQI = "SO2message" ?
            raise ErrorCalculation
        else:
            raise ErrorOutOfRange

        return AQI

    def __aqi_so2_24hr(self, conc):
        AQI = 0
        c = math.floor(conc)

        if (0 <= c < 304):
            # AQI = "SO2message" ? 
            raise ErrorCalculation
        elif(304 <= c < 605):
            AQI = self.__linear(300, 201, 604, 305, c)
        elif(605 <= c < 805):
            AQI = self.__linear(400, 301, 804, 605, c)
        elif(805 <= c < 1004):
            AQI = self.__linear(500, 401, 1004, 805, c)
        else:
            raise ErrorOutOfRange

        return AQI 

    def __aqi_o3_8hr(self, conc):
        AQI = 0
        c = (math.floor(conc)) / 1000

        if (0 <= c < 0.060):
            AQI = self.__linear(50, 0, 0.059, 0, c)
        elif (0.060 <= c < 0.076):
            AQI = self.__linear(100, 51, 0.075, 0.060, c)
        elif (0.076 <= c < 0.096):
            AQI = self.__linear(150, 101, 0.095, 0.076, c)
        elif (0.096 <= c < 0.116):
            AQI = self.__linear(200, 151, 0.115, 0.096, c)
        elif (0.116 <= c < 0.375):
            AQI = self.__linear(300, 201, 0.374, 0.116, c)
        elif (0.375 <= c < 0.605):
            raise ErrorCalculation
        else:
            raise ErrorOutOfRange

        return AQI

    def __aqi_o3_1hr(self, conc):
        AQI = 0
        c = (math.floor(conc)) / 1000

        if (0.125 <= c < 0.165):
            AQI = self.__linear(150, 101, 0.164, 0.125, c)
        elif (0.165 <= c < 0.205):
            AQI = self.__linear(200, 151, 0.204, 0.165, c)
        elif (0.205 <= c < 0.405):
            AQI = self.__linear(300, 201, 0.404, 0.205, c)
        elif (0.405 <= c < 0.505):
            AQI = self.__linear(400, 301, 0.504, 0.405, c)
        elif (0.505 <= c < 0.605):
            AQI = self.__linear(500, 401, 0.604, 0.505, c)
        else:
            raise ErrorOutOfRange

        return AQI

    def __aqi_no2(self, conc):
        AQI = 0
        c = (math.floor(conc)) / 1000

        if (0 <= c < 0.054):
            AQI = self.__linear(50, 0, 0.053, 0, c)
        elif (0.054 <= c <= 0.101):
            AQI = self.__linear(100, 51, 0.100, 0.054, c)
        elif (0.101 <= c <= 0.361):
            AQI = self.__linear(150, 101, 0.360, 0.101, c)
        elif (0.361 <= c <= 0.650):
            AQI = self.__linear(200, 151, 0.649, 0.361, c)
        elif (0.650 <= c <= 1.250):
            AQI = self.__linear(300, 201, 1.249, 0.650, c)
        elif (1.250 <= c <= 1.650):
            AQI = self.__linear(400, 301, 1.649, 1.250, c)
        elif (1.650 <= c <= 2.049):
            AQI = self.__linear(500, 401, 2.049, 1.650, c)
        else:
            raise ErrorOutOfRange

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