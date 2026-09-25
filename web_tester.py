import sys
from socket import *
import ssl


def parse_uri(uri):
    # URI format: protocol://host[:port]/filepath
    # NOTE ADD HANDLING FOR URI'S WITH NO PORT

    uri_data = {}

    if not uri.endswith("/"):
        uri += "/"

    uri = uri.split("://", 1)
    uri_data["protocol"] = uri[0]

    if ":" in uri[1]:
        uri = uri[1].split("[:", 1)
        uri_data["host"] = uri[0]

        uri = uri[1].split("]/", 1)
        uri_data["port"] = uri[0]
        print(uri_data["port"])
    else:
        uri = uri[1].split("/", 1)
        uri_data["host"] = uri[0]

        if uri_data["protocol"] == "https":
            uri_data["port"] = 443
        else:
            uri_data["port"] = 80

    uri = uri[1].split("]/", 1)
    uri_data["filepath"] = "/" + uri[0]

    return uri_data

def open_connection(host, port, use_tls):

    # create socket
    s = socket(AF_INET, SOCK_STREAM)

    # establish a connection
    s.connect((host, port))

    # if https use tls
    if use_tls:
        context = ssl.create_default_context()
        # Perform TLS handshake
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
    return s, request

def receive_request(s):

    response = b""

    # loop through the chunks of 4096 bytes until data is empty
    while 1:
        data = s.recv(4096)
        if not data:
            break
        response += data

    s.close()
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
            key = data[0].strip().lower()
            value = data[1].strip()

            if key not in headers:
                headers[key] = []

            headers[key].append(value)

    response_data["headers"] = headers

    return response_data

def handle_redirects(response):
    redirect_codes = {"301", "302", "303", "307", "308"}

    if response["status_code"] in redirect_codes:
        locations = response["headers"].get("location", [])

        if locations:
            return locations[0]

    return None

def check_http2_support(host, port, use_tls): # check for http2 support (h2)

    # create socket
    s = socket(AF_INET, SOCK_STREAM)

    # establish a connection
    s.connect((host, port))

    # if https use tls
    if use_tls:
        context = ssl.create_default_context()

        # Configure ALPN BEFORE the TLS handshake
        context.set_alpn_protocols(["h2", "http/1.1"])

        # Perform TLS handshake
        s = context.wrap_socket(s, server_hostname=host)
    
        return True

    s.close()

    return False

def extract_cookies(headers):
    cookies = []

    for cookie in headers.get("set-cookie", []):
        cookies.append("Set-Cookie: " + cookie)

    return cookies

def check_password_protection(status_code):
    return status_code == "401"

def main():

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

    # Send data from URI to socket function
    socket = open_connection(parsed_uri["host"], parsed_uri["port"], parsed_uri["protocol"] == "https")

    # make/send request
    request = make_request(parsed_uri["host"], parsed_uri["filepath"])
    s, send_request = send_http_request(socket, request)

    response = receive_request(socket)

    response_data = parse_response(response)

    # check for redirects, if so start over with new URI
    redirect = handle_redirects(response_data)
    if redirect:
        redirect_count += 1
        main2(redirect, redirect_count) # Restart with new URI but ignore comandline input (main())
        return

    http2_support = check_http2_support(parsed_uri["host"], parsed_uri["port"], parsed_uri["protocol"] == "https")

    cookies = extract_cookies(response_data["headers"])

    check_password = check_password_protection(response_data["status_code"])

    print("=== Request begin ===\n")
    print(send_request)

    print("=== Request end ===\n")
    print("RECEIVING RESPONSE...")

    print("\n\n=== Response header ===\n")
    for header, values in response_data["headers"].items():
        if header == "set-cookie":
            continue

        print(header + ": " + values[0])

    print("\n\n=== Cookies ===\n")
    for cookie in cookies:
        print(cookie)
        print()

    print("\n=== HTTP2 support ===\n")
    print("http2 support:", http2_support)

    print("\n\n=== Check password ===\n")
    print("Password protected:", check_password)

    print("\n\n=== Redirects ===\n")
    if redirect:
        print("Total redirect count:", redirect_count)
    else:
        print("Total redirect count:", redirect_count)

    print("\n")

    return

main()
