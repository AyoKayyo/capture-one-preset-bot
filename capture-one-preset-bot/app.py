from flask import Flask, request, jsonify, send_file
import rawpy
import numpy as np
import cv2
import os
import xml.etree.ElementTree as ET

app = Flask(__name__)

def build_costyle(settings, outname):
    tree = ET.parse('template.costyle')
    root = tree.getroot()
    def setE(key, val):
        for e in root.findall(f".//E[@K='{key}']"):
            e.set('V', str(val))
    # White Balance
    setE('WhiteBalanceTemperature', settings['white_balance']['kelvin'])
    setE('WhiteBalanceTint', settings['white_balance']['tint'])
    # Exposure
    setE('Exposure', settings['exposure']['exposure'])
    setE('Contrast', settings['exposure']['contrast'])
    setE('Brightness', settings['exposure']['brightness'])
    setE('Saturation', settings['exposure']['saturation'])
    tree.write(outname, encoding='utf-8', xml_declaration=True)
    return outname

@app.route('/.well-known/ai-plugin.json')
def plugin_manifest():
    return send_file(os.path.join(app.root_path, '.well-known', 'ai-plugin.json'))

@app.route('/openapi.json')
def openapi_spec():
    return send_file('openapi.json')

@app.route('/analyze', methods=['POST'])
def analyze():
    f = request.files['file']
    with rawpy.imread(f) as raw:
        rgb = raw.postprocess(output_bps=16)
    wb = {'kelvin': 3900, 'tint': 3}
    exp = {'exposure': 0.1, 'contrast': 6, 'brightness': 5, 'saturation': 2}
    return jsonify({'white_balance': wb, 'exposure': exp})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    settings = data['settings']
    album = data.get('album', 'AlbumPreset')
    fname = f"{album}.costyle"
    build_costyle(settings, fname)
    return send_file(fname, as_attachment=True, mimetype='application/octet-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=True)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3333))
    app.run(host="0.0.0.0", port=port, debug=True)
