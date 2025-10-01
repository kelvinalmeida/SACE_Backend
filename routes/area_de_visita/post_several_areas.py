from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from bluprint import area_para_visita

@area_para_visita.route('/areas_de_visita', methods=['POST'])
@token_required
def criar_varias_areas_de_visita(current_user):
    pass