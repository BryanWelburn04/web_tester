import sys
from socket import *
import ssl



def parse_uri(uri):
    # URI format: protocol://host[:port]/filepath
    # NOTE ADD HANDLING FOR URI'S WITH NO PORT

    uri_data = {}

    uri = uri.split("://", 1)
    uri_data["protocol"] = uri[0]
    # print(uri_data["protocol"])


    if ":" in uri[1]:
        uri = uri[1].split("[:", 1)
        uri_data["host"] = uri[0]
        # print(uri_data["host"])

        uri = uri[1].split("]/", 1)
        uri_data["port"] = uri[0]
        print(uri_data["port"])
    else:
        uri = uri[1].split("/", 1)
        uri_data["host"] = uri[0]
        # print(uri_data["host"])

        if uri_data["protocol"] == "https":
            uri_data["port"] = 443
        else:
            uri_data["port"] = 80

    uri = uri[1].split("]/", 1)
    uri_data["filepath"] = "/" + uri[0]
    # print(uri_data["filepath"])

    print(uri_data)

    return uri_data

def open_connection(host, port, use_tls):

    # create socket
    s = socket(AF_INET, SOCK_STREAM)

    # establish a connection
    s.connect((host, port))

    # if https use tls
    if use_tls:
        context = ssl.create_default_context()
        s = context.wrap_socket(s, server_hostname=host)

    return s

def make_request(host, filepath):
    request = (
        f"GET {filepath} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return request

def send_http_request(s, request):
    s.sendall(request.encode())
    print(request)

    return s

def receive_request(socket):

    response = b""

    # loop through the chunks of 4096 bytes until data is empty
    while 1:
        data = socket.recv(4096)
        # print(data.decode())
        print(data.decode("utf-8", errors="replace"), end="")
        if not data:
            break
        response += data

    socket.close()
    return response

def parse_response(response):

    response_data = {}

    # Separate headers from body
    data = response.split(b"\r\n\r\n", 1)
    header_data = data[0]
    response_data["body"] = data[1]

    # Decode only the HTTP headers
    header_lines = header_data.decode("iso-8859-1").split("\r\n")

    # Parse status line
    data = header_lines[0].split(" ", 2)
    response_data["version"] = data[0]
    response_data["status_code"] = data[1]
    response_data["reason"] = data[2]

    # Parse headers
    headers = {}

    for line in header_lines[1:]:
        if ":" in line:
            data = line.split(":", 1)
            key = data[0]
            value = data[1]
            headers[key.strip().lower()] = value.strip()

    response_data["headers"] = headers

    return response_data

def handle_redirects(response):
    # All codes related to redirects
    redirect_codes = {301, 302, 303, 307, 308}

    if response["status_code"] in redirect_codes:
        return response["headers"].get("location")

    return None

def check_http2_support(response):
    # check for ...
    alt_svc = response["headers"].get("alt-svc", "")
    http2_support = "h2=" in alt_svc
    return http2_support

def extract_cookies(headers):
    return

def check_password_protection(status_code):
    return

def main():
    print("======================\n")

    # require a valid input
    if len(sys.argv) < 2:
        print("Error: Too few arguements provided, please provide a URI")
        return
    if len(sys.argv) > 2:
        print("Error: Too many arguements provided, please provide only a URI")
        return

    # parse and store URI data
    unparsed_uri = sys.argv[1]
    main2(unparsed_uri, 0)

    return

def main2(unparsed_uri, redirect_count):
    
    parsed_uri = parse_uri(unparsed_uri)

    print("\n======================\n")

    # Send data from URI to socket function
    socket = open_connection(parsed_uri["host"], parsed_uri["port"], parsed_uri["protocol"] == "https")

    # make/send request
    request = make_request(parsed_uri["host"], parsed_uri["filepath"])
    send_http_request(socket, request)

    print("======================\n")

    response = receive_request(socket)

    print("\n======================\n")

    response_data = parse_response(response)
    print(response_data)

    print("\n======================\n")

    # check for redirects, if so start over with new URI
    redirect = handle_redirects(response_data)
    if redirect:
        print("Redirect: True")
        print("Total redirect count:", redirect_count)
        redirect_count += 1
        main2(redirect, redirect_count) # Restart with new URI but ignore comandline input (main())
    else:
        print("Redirect: False")
        print("Total redirect count:", redirect_count)

    print("\n======================\n")

    http2_support = check_http2_support(response_data)
    print("http2 support:", http2_support)

    print("\n======================\n")

    return

main()
