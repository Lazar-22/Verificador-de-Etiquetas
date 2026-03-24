from flask import Flask, render_template, request, jsonify
import xmlrpc.client

app = Flask(__name__)

# Configuración Odoo
URL = 'https://ventasatc.opendrive.cl'
DB = 'PRODUCCION'
USER = 'admin'
PASS = 'atcdrive2018'

def format_order_name(name):
    """Normaliza el nombre de la orden a SOXXXXXXX"""
    clean_name = name.strip().upper()
    if not clean_name.startswith('SO') and clean_name:
        clean_name = f"SO{clean_name}"
    return clean_name

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def home():
    """Página principal con selección de Marketplace"""
    return render_template('home.html')

@app.route('/falabella')
def falabella():
    """Verificador estilo Falabella"""
    return render_template('falabella.html')

@app.route('/ripley')
def ripley():
    """Verificador estilo Ripley"""
    return render_template('ripley.html')

# --- LÓGICA DE NEGOCIO (API) ---

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    order_name = format_order_name(data.get('name', ''))
    client_ref = data.get('client_ref', '').strip()
    
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USER, PASS, {})
        
        if not uid:
            return {"status": "error", "message": "Fallo de autenticación en Odoo."}

        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

        # Buscamos la coincidencia exacta de Nombre y Referencia
        domain = [['name', '=', order_name], ['client_order_ref', '=', client_ref]]
        orders = models.execute_kw(DB, uid, PASS, 'sale.order', 'search_read', [domain], {'fields': ['partner_id']})

        if orders:
            # orders[0]['partner_id'][1] contiene el nombre del cliente (ej: "Falabella Retail")
            return {"status": "success", "message": f"¡Coincidencia! Cliente: {orders[0]['partner_id'][1]}"}
        else:
            return {"status": "error", "message": f"No se encontró la orden {order_name} con esa referencia."}
            
    except Exception as e:
        return {"status": "error", "message": f"Error de conexión: {str(e)}"}

# --- EJECUCIÓN DEL SERVIDOR ---

if __name__ == '__main__':
    # host='0.0.0.0' permite conexiones externas (Celulares, Tablets, otras PCs)
    # port=5000 es el puerto por defecto de Flask
    app.run(host='0.0.0.0', port=5000, debug=True)