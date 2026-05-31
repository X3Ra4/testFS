from flask import jsonify


def error_response(error, details, status_code):
    return jsonify({"error": error, "details": details}), status_code


def success_response(data=None, message="Success", status_code=200):
    return jsonify({"data": data, "message": message}), status_code
