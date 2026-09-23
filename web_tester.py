import sys
from socket import *


def parse_uri(uri):
    # URI format: protocol://host[:port]/filepath
    # NOTE ADD HANDLING FOR URI'S WITH NO PORT

    uri_data = {}

    uri = uri.split("://", 1)
    uri_data["protocol"] = uri[0]
    print(uri_data["protocol"])


    if ":" in uri[1]:
        uri = uri[1].split("[:", 1)
        uri_data["host"] = uri[0]
        print(uri_data["host"])

        uri = uri[1].split("]/", 1)
        uri_data["port"] = uri[0]
        print(uri_data["port"])
    else:
        uri = uri[1].split("/", 1)
        uri_data["host"] = uri[0]
        print(uri_data["host"])

        if uri_data["protocol"] == "https":
            uri_data["port"] = 443
        else:
            uri_data["port"] = 80

    uri = uri[1].split("]/", 1)
    uri_data["filepath"] = uri[0]
    print(uri_data["filepath"])

    return uri_data

def open_connection(host, port, use_tls):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((host, port))
    
    return

def send_http_request(socket, request):
    return

def receive_request(socket):
    return

def parse_response(response):
    return

def handle_redirects():
    return

def check_http2_support():
    return

def extract_cookies(headers):
    return

def check_password_protection(status_code):
    return

def main():
    print("======================")
    if len(sys.argv) < 2:
        print("Error: Too few arguements provided, please provide a URI")
        return
    if len(sys.argv) > 2:
        print("Error: Too many arguements provided, please provide only a URI")
        return
    unparsed_uri = sys.argv[1]
    parsed_uri = parse_uri(unparsed_uri)
    print(parsed_uri)
    return

main()