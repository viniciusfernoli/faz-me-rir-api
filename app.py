from flask import Flask, jsonify
import fundamentus
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*"]}})

@app.route('/ativo', methods=['GET'])
def obter_informacoes_ativo():
    try:
        df = fundamentus.get_resultado()
        
        # Aplicação dos filtros
        pl = (df['pl'] >= 3) & (df['pl'] <= 10)
        pvp = (df['pvp'] >= 0.5) & (df['pvp'] <= 2)
        divYield = (df['dy'] * 100 >= 7) & (df['dy'] * 100 <= 15)
        roe = (df['roe'] * 100 >= 15) & (df['roe'] * 100 <= 30)
        liq2mounth = df['liq2m'] >= 1000000
        cresc5years = (df['c5y'] * 100) >= 10

        # Filtros combinados
        filters = (
            pl & pvp & divYield & roe & liq2mounth & cresc5years
        )
        
        # Aplicação dos filtros ao DataFrame
        df_filtered = df[filters]
        
        # Resetando o índice para incluir o ticker nos dados
        df_filtered = df_filtered.reset_index()
        
        # Serialização dos dados para JSON
        result = df_filtered.to_dict(orient='records')
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)