from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin

from app.repository.admin_repository import AdminRepository
from app.repository.commuter_repository import CommuterRepository
from app.service.commuter_service import CommuterService
from app.service.dtos.admin_dtos import User, Token, AdminFullInfo
from app.service.dtos.commuter_dtos import CommuterFullInfo, Commuter, CreditCard, Transaction, SearchAccessQuery
from app.service.dtos.admin_dtos import Admin, Access
from app.service.exceptions import RequestError, ErrorResponseStatus

from app.service.admin_service import AdminService
from app.repository.database import Database

database = Database()
app = Flask(__name__)

admin_repository = AdminRepository(database=database)
admin_service = AdminService(admin_repository)

commuter_repository = CommuterRepository(database=database)
commuter_service = CommuterService(commuter_repository, admin_repository)

CREATED = 201


@app.route("/user/signup", methods=["POST"])
@cross_origin()
def signup():
    """
    Endpoint for user signup. It can register both commuters and admins.
    """
    try:
        data = request.get_json()
        if "adminCode" in data:
            admin = AdminFullInfo(**data)
            message = admin_service.signup_admin(admin)
        else:
            commuter = CommuterFullInfo(**data)
            message = commuter_service.signup_commuter(commuter)
        response = jsonify(message)
        response.status_code = CREATED
        return response

    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/user/login", methods=["POST"])
@cross_origin()
def login():
    """
    Endpoint for user login. It authenticates both commuters and admins.
    """
    try:
        data = request.get_json()
        if "adminCode" in data:
            admin = Admin(**data)
            response = admin_service.login_admin(admin)
        else:
            commuter = Commuter(**data)
            response = commuter_service.login(commuter)
        return jsonify(response.to_json())

    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/admin/access", methods=["POST"])
@cross_origin()
def create_access():
    """
    Endpoint for creating a new access by an admin.
    """
    try:
        token = request.headers.get("Authorization")
        data = request.get_json()
        access = Access(**data)
        response = admin_service.create_access(access, Token(token))
        return jsonify(response.to_json()), 201
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/admin/access/<accessId>", methods=["DELETE"])
@cross_origin()
def suspend_access(accessId):
    """
    Endpoint for suspending an access by an admin.
    """
    try:
        token = request.headers.get("Authorization")
        response = admin_service.suspend_access(accessId, Token(token))
        return jsonify(response), 204
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/user/payment", methods=["POST"])
@cross_origin()
def add_payment_method():
    """
    Endpoint for adding a payment method for a commuter.
    """
    try:
        token = request.headers.get("Authorization")
        data = request.get_json()
        credit_card = CreditCard(**data)
        response = commuter_service.add_payment_method(credit_card, Token(token))
        return jsonify({"message": response}), 201
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/user/access/checkout", methods=["POST"])
@cross_origin()
def buy_access():
    """
    Endpoint for a commuter to buy access.
    """
    try:
        token = request.headers.get("Authorization")
        cvc = request.headers.get("cvc")
        data = request.get_json()
        transaction = Transaction(**data)

        response = commuter_service.buy_access(Token(token), int(cvc), transaction)
        bought_access_json = [bought_access.to_json() for bought_access in response]

        return jsonify(bought_access_json), 200
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/user/access", methods=["GET"])
@cross_origin()
def get_wallet():
    """
    Endpoint for retrieving the wallet of a commuter.
    """
    try:
        token = request.headers.get("Authorization")
        response = commuter_service.get_wallet(Token(token))
        bought_access_json = [bought_access.to_json() for bought_access in response]
        return jsonify(bought_access_json), 200
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/user/payment", methods=["DELETE"])
@cross_origin()
def delete_payment_method():
    """
    Endpoint for deleting a payment method for a commuter.
    """
    try:
        token = request.headers.get("Authorization")
        commuter_service.delete_payment_method(Token(token))
        return make_response("", 204)
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/user/access/search", methods=["POST"])
@cross_origin()
def commuter_access_search():
    """
    Endpoint for a commuter to search for access options.
    """
    try:
        token = request.headers.get("Authorization")
        data = request.get_json()
        search_query = SearchAccessQuery(**data)
        found_access = commuter_service.search_access(search_query, Token(token))

        response = [access.to_json() for access in found_access]

        return jsonify(response), 200
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/admin/access/search", methods=["GET"])
@cross_origin()
def admin_access_search():
    """
    Endpoint for an admin to search for a created access from his company.
    """
    try:
        token = request.headers.get("Authorization")
        found_access = admin_service.search_created_access(Token(token))

        response = [access.to_json() for access in found_access]

        return jsonify(response), 200
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/user/payment", methods=["GET"])
@cross_origin()
def get_card_info():
    """
    Endpoint for retrieving payment card information for a commuter.
    """
    try:
        token = request.headers.get("Authorization")
        response = commuter_service.get_card_info(Token(token))
        return jsonify(response.to_json()), 200
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/user", methods=["GET"])
@cross_origin()
def get_commuter():
    """
    Endpoint for retrieving full information about a commuter.
    """
    try:
        token = request.headers.get("Authorization")
        response = commuter_service.get_commuter_full_info(Token(token))
        return jsonify(response.to_json()), 200
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/admin", methods=["GET"])
@cross_origin()
def get_admin():
    """
    Endpoint for retrieving full information about an admin.
    """
    try:
        token = request.headers.get("Authorization")
        response = admin_service.get_admin_full_info(Token(token))
        return jsonify(response.to_json()), 200
    except RequestError as error:
        response = jsonify(error.to_json())
        response.status_code = error.error_response_status
        return response
    except TypeError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response
    except ValueError as error:
        response = jsonify({"error": str(error)})
        response.status_code = ErrorResponseStatus.BAD_REQUEST.value
        return response


@app.route("/admin/online", methods=["GET"])
@cross_origin()
def is_admin_online():
    """
    Endpoint to check if an admin is currently logged in.
    """
    token = request.headers.get("Authorization")
    is_online = admin_service.is_admin_logged_in(Token(token))
    if is_online:
        return make_response("", 200)
    else:
        return make_response("", 401)


@app.route("/user/online", methods=["GET"])
@cross_origin()
def is_commuter_online():
    """
    Endpoint to check if a commuter is currently logged in.
    """
    token = request.headers.get("Authorization")
    is_online = commuter_service.is_commuter_logged_in(Token(token))
    if is_online:
        return make_response("", 200)
    else:
        return make_response("", 401)


@app.route("/admin/company", methods=["GET"])
@cross_origin()
def get_company():
    """
    Endpoint for retrieving all the companies.
    """
    company = admin_service.get_companies_names()
    return jsonify(company), 200


@app.route("/admin/logout", methods=["POST"])
@cross_origin()
def logout_admin():
    """
    Endpoint for logging out an admin.
    """
    token = request.headers.get("Authorization")
    admin_service.logout_admin(Token(token))
    return make_response("", 204)


# api call to logout commuter
@app.route("/user/logout", methods=["POST"])
@cross_origin()
def logout_commuter():
    """
    Endpoint for logging out a commuter.
    """
    token = request.headers.get("Authorization")
    commuter_service.logout_commuter(Token(token))
    return make_response("", 204)


