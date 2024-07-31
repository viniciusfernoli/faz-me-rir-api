from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS
from .fundamentuApi import get_data
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Inicializar lista e dia como None
lista = None
dia = None

def carregar_dados():
    """Carrega os dados e retorna a lista e o dia atual."""
    lista = dict(get_data())
    lista = {outer_k: {inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in lista.items()}
    dia = datetime.strftime(datetime.today(), '%d')
    return lista, dia

@app.route('/ativo', methods=['GET'])
def obter_informacoes_ativo():
    global lista, dia

    # Verifica se os dados precisam ser carregados
    if lista is None or dia != datetime.strftime(datetime.today(), '%d'):
        lista, dia = carregar_dados()

    # Converter os dados para um DataFrame
    df = pd.DataFrame.from_dict(lista, orient='index')        
    
    # Aplicação dos filtros
    pl = (df['P/L'] >= 3) & (df['P/L'] <= 10)
    pvp = (df['P/VP'] >= 0.5) & (df['P/VP'] <= 2)
    divYield = (df['DY'] * 100 >= 7) & (df['DY'] * 100 <= 15)
    roe = (df['ROE'] * 100 >= 15) & (df['ROE'] * 100 <= 30)
    liq2mounth = df['Liq.2meses'] >= 1000000
    cresc5years = (df['Cresc.5anos'] * 100) >= 10
    
    # Filtros combinados
    filters = (
        pl & pvp & divYield & roe & liq2mounth & cresc5years
    )

    # Renomear as colunas para manter a consistência com a API anterior
    df = df.rename(columns={
        'index':'papel',
        'Cotacao': 'cotacao',
        'P/L': 'pl',
        'P/VP': 'pvp',
        'PSR': 'psr',
        'DY': 'dy',
        'P/Ativo': 'pa',
        'P/Cap.Giro': 'pcg',
        'P/EBIT': 'pebit',
        'P/ACL': 'pacl',
        'EV/EBIT': 'evebit',
        'EV/EBITDA': 'evebitda',
        'Mrg.Ebit': 'mrgebit',
        'Mrg.Liq.': 'mrgliq',
        'Liq.Corr.': 'liqc',
        'ROIC': 'roic',
        'ROE': 'roe',
        'Liq.2meses': 'liq2m',
        'Pat.Liq': 'patrliq',
        'Div.Brut/Pat.': 'divbpatr',
        'Cresc.5anos': 'c5y'
    })

    # Aplicação dos filtros ao DataFrame
    df_filtered = df[filters]
    
    # Resetando o índice para incluir o ticker nos dados
    df_filtered = df_filtered.reset_index()
    result = df_filtered.to_dict(orient='records')

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)