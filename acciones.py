import os
import yfinance as yf
from datetime import datetime, timedelta
from tabulate import tabulate
import matplotlib.pyplot as plt

#Obtiene la ruta absoluta del archivo de estilo
style_path = os.path.abspath('./estilos/mi_estilo.mplstyle')
plt.style.use(style_path)

#Se define la clase que representa una acción específica
class Accion():           
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = None
        self.precio_promedio_semana = None
        self.precio_actual = None
        self.porcentaje_diferencia = None

    #Obtiene los datos durante el plazo que se estipule
    def obtener_datos_diarios(self, start_date, end_date):
        try:
            self.data = yf.download(self.symbol, start=start_date, end=end_date)
        except Exception as e:
            print(f"Error al obtener datos para {self.symbol}: {e}")

    #Calcula el promedio semanal del precio de la acción
    def calcular_precio_promedio(self):
        if self.data is not None and not self.data.empty:
            self.precio_promedio_semana = self.data['Close'].mean()
        else:
            self.precio_promedio_semana = None
    
    #Obtiene el precio actual contra el cual se va a comparar el promedio
    def obtener_precio_actual(self):
        try:
            ticker = yf.Ticker(self.symbol)
            self.precio_actual = ticker.history(period='1d')['Close'].iloc[-1]
        except Exception as e:
            print(f"Error al obtener el precio actual para {self.symbol}: {e}")
            self.precio_actual = None

     #Si el precio actual es menor que el semanal, calcula el porcentaje de diferencia entre el precio actual y el promedio semanal
    def comparar_precios(self):
        if self.precio_promedio_semana is not None and self.precio_actual is not None:
            if self.precio_actual < self.precio_promedio_semana:
                self.porcentaje_diferencia = ((self.precio_promedio_semana - self.precio_actual) / self.precio_promedio_semana) * 100
                return [self.symbol, self.precio_actual, self.precio_promedio_semana, self.porcentaje_diferencia]
        return None

#Se define la clase que gestiona y analiza el conjunto de acciones
class GestorAcciones():
    def __init__(self, symbols):
        self.acciones = [Accion(symbol) for symbol in symbols]

    def procesar_acciones(self):
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        resultados = []

        for accion in self.acciones:
            accion.obtener_datos_diarios(start_date, end_date)
            accion.calcular_precio_promedio()
            accion.obtener_precio_actual()
            resultado = accion.comparar_precios()
            if resultado:
                resultados.append(resultado)

        return resultados

def main():
    #Se definen las acciones a analizar
    symbols = ['AGRO.BA', 'ALUA.BA', 'AUSO.BA', 'BBAR.BA', 'BHIP.BA', 'BMA.BA', 'BOLT.BA', 'BPAT.BA', 'BYMA.BA', 'CADO.BA',
                'CAPX.BA', 'CARC.BA', 'CECO2.BA', 'CELU.BA', 'CEPU.BA', 'CGPA2.BA', 'COME.BA', 'CRES.BA', 'CVH.BA', 'CTIO.BA',
                'DGCU2.BA', 'DOME.BA', 'DYCA.BA', 'EDN.BA', 'FERR.BA', 'FIPL.BA', 'GAMI.BA', 'GARO.BA', 'GBAN.BA', 'GCDI.BA',
                'GCLA.BA', 'GGAL.BA', 'GRIM.BA', 'HARG.BA', 'HAVA.BA', 'INTR.BA', 'INVJ.BA', 'IRSA.BA', 'LEDE.BA', 'LONG.BA',
                'LOMA.BA', 'METR.BA', 'MIRG.BA', 'MOLA.BA', 'MOLI.BA', 'MORI.BA', 'OEST.BA', 'PAMP.BA', 'PATA.BA', 'POLL.BA',
                'RIGO.BA', 'ROSE.BA', 'SAMI.BA', 'SEMI.BA', 'SUPV.BA', 'Teco2.BA', 'TGNO4.BA', 'TGSU2.BA', 'TRAN.BA',
                'TXAR.BA', 'VALO.BA', 'YPFD.BA']

    gestor_acciones = GestorAcciones(symbols)
    resultados = gestor_acciones.procesar_acciones()

    if resultados: 
        #Se genera una tabla que muestra las acciones por debajo del promedio
        headers = ["Símbolo", "Precio Actual", "Precio Promedio Semanal", "Porcentaje de Diferencia"]
        print("\nAcciones por debajo del promedio:")
        resultados = sorted(resultados, key=lambda x: x[3], reverse=True)
        print(tabulate(resultados, headers=headers, tablefmt="grid"))
        table_html = tabulate(resultados, headers=headers, tablefmt="html")
        
        #Se inserta la tabla en el archivo informe.html
        start_marker = '<!-- Inicio Tabla de Resultados -->'
        end_marker = '<!-- Fin Tabla de Resultados -->'
        
        with open('informe.html', 'r') as file:
            informe_content = file.read()

        new_content = f'{start_marker}\n{table_html}\n{end_marker}'
        updated_content = informe_content.split(start_marker)[0] + new_content + informe_content.split(end_marker)[1]

        #Guarda la tabla actualizada en informe.html
        with open('informe.html', 'w') as file:
            file.write(updated_content)
        
        #Se seleccionan y se grafican las cinco acciones con mayor baja
        top_5_bajas = resultados[:5]
        
        plt.figure(figsize=(14, 7))
        
        for accion in top_5_bajas:
            symbol = accion[0]
            plt.bar(symbol, accion[3])
        
        plt.xlabel('Símbolo de la Acción')
        plt.ylabel('Porcentaje de Diferencia')
        plt.title('Acciones con Mayor Baja en la Última Semana')
        
        #Se guarda el gráfico como imagen 
        plt.savefig("img/grafico_acciones.png")
        
    else:
        print("\nNo hay acciones por debajo del promedio esta semana.")

if __name__ == "__main__":
    main()