#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.api import app

if __name__ == '__main__':
    print("=" * 60)
    print("  SISTEMA DE CONTROLE DE CONDOMÍNIOS - VERSÃO WEB")
    print("=" * 60)
    print()
    print("🌐 Servidor iniciado!")
    print("📱 Acesse: http://localhost:5000")
    print()
    print("=" * 60)

    app.run(debug=False, host='0.0.0.0', port=10000)
