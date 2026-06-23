#!/usr/bin/env python3
"""
Instalador automatico do SIGIC
Fase IV - Energia para Sobreviver | FIAP 2026
"""

import subprocess
import sys
import os
import platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, 'venv')


def print_header():
    print()
    print('=' * 55)
    print('  SIGIC - Instalador Automatico')
    print('  Fase IV - Energia para Sobreviver')
    print('=' * 55)
    print()


def criar_venv():
    print('[1/3] Criando ambiente virtual...')
    if os.path.exists(VENV_DIR):
        print('  Ambiente virtual ja existe, pulando.')
        return True
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', VENV_DIR])
        print('  Ambiente virtual criado com sucesso.')
        return True
    except subprocess.CalledProcessError:
        print('  ERRO: Nao foi possivel criar o ambiente virtual.')
        return False


def pip_do_venv():
    if platform.system() == 'Windows':
        return os.path.join(VENV_DIR, 'Scripts', 'pip')
    return os.path.join(VENV_DIR, 'bin', 'pip')


def python_do_venv():
    if platform.system() == 'Windows':
        return os.path.join(VENV_DIR, 'Scripts', 'python')
    return os.path.join(VENV_DIR, 'bin', 'python')


def instalar_dependencias():
    print('[2/3] Instalando dependencias (flask, fpdf2)...')
    pip = pip_do_venv()
    try:
        subprocess.check_call([pip, 'install', 'flask', 'fpdf2'],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.STDOUT)
        print('  Dependencias instaladas com sucesso.')
        return True
    except subprocess.CalledProcessError:
        print('  ERRO: Falha ao instalar dependencias.')
        return False


def executar():
    print('[3/3] Iniciando o SIGIC...')
    print()
    python = python_do_venv()
    codigo = os.path.join(BASE_DIR, 'codigo_fonte.py')
    try:
        subprocess.call([python, codigo])
    except KeyboardInterrupt:
        print('\n  SIGIC encerrado.')


def main():
    print_header()
    if not criar_venv():
        sys.exit(1)
    if not instalar_dependencias():
        sys.exit(1)
    executar()


if __name__ == '__main__':
    main()
