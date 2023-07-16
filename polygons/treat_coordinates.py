from bs4 import BeautifulSoup
import pandas as pd

with open(r'apenas_jardins.kml') as file:
    soup = BeautifulSoup(file.read(), 'lxml')

latitudes = []
longitudes = []
cordenadas = soup.find('coordinates').text.strip().replace(',0', '').split(',')
print(cordenadas)
cordenadas = map(str, cordenadas)
for conjunto in cordenadas:
    splitado = conjunto.split(' ')
    if len(splitado) == 2:
        latitudes.append(splitado[0])
        longitudes.append(splitado[1])

df = pd.DataFrame(data={'Latitude':latitudes, 'Longitude':longitudes})
print(df)
# df.to_csv('apenas_jardins_coordenadas.csv', sep=',', index=False)
# print(len(latitudes), len(longitudes))
# print(latitudes)