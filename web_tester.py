import sys

def parse_uri(uri):
    # URI format: protocol://host[:port]/filepath
    # NOTE ADD HANDLING FOR URI'S WITH NO PORT

    uri_data = []

    uri = uri.split("://")
    uri_data.append(uri[0])
    print(uri[0])

    uri = uri[1].split("[:")
    uri_data.append(uri[0])
    print(uri[0])

    uri = uri[1].split("]/")
    uri_data.append(uri[0])
    print(uri[0])

    uri = uri[1].split("]/")
    uri_data.append(uri[0])
    print(uri[0])

    return uri_data

def open_connection(host, port, use_tls):
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