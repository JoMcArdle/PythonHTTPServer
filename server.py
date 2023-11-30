import sys
import socket
import json
import random
import datetime
import hashlib

session_data = {}

def file_exists(root_directory, username, target):

    try:
        with open(root_directory + username + target) as file:
            text = file.read()
        return text
    except IOError:
        return False
    


def startServer(IP, PORT, ACCOUNTS_FILE, SESSION_TIMEOUT, ROOT_DIRECTORY):

    accounts_file = ACCOUNTS_FILE

    TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (IP, int(PORT))
    TCP_socket.bind(server_address)

    TCP_socket.listen()

    while True:
        client_socket, client_address = TCP_socket.accept()
        request = client_socket.recv(1024).decode('utf-8')
        request = request.replace('\n', '\r\n')
        lines = request.split("\r\n")
        start_line = lines[0]
        method,target,version = start_line.split(" ")
        headers = {}
        for header in lines[1:]:
            if header == "": break #empty line, reached body
            #hkey, hval = header.split(": ", 1)
            key_val = header.split(": ", 1)
            if len(key_val) == 2:
                hkey, hval = key_val
                headers[hkey] = hval
            #print(method,target,version)
            #print(headers)
        
        #print(method,target,version)
        #print(headers)

        if (method == "POST") and (target == "/"):
            client_socket.sendall(POSTRequest(version, headers, accounts_file).encode('utf-8'))
        
        elif (method == "GET"):
            client_socket.sendall(GETRequest(version, headers, target, SESSION_TIMEOUT, ROOT_DIRECTORY).encode('utf-8'))

        else:
            client_socket.sendall((f'HTTP/1.0 501 Not Implemented\r\n').encode('utf-8'))
        
        client_socket.close()
        




def POSTRequest(version, headers, accounts_file):

    currentDateAndTime = datetime.datetime.now()

    formattedDateTime = currentDateAndTime.strftime("%Y-%m-%d-%H-%M-%S")

    #print(formattedDateTime)

    with open(accounts_file) as account:
        account_details = json.load(account)

    #print(account_details)

    if (headers.get('username') == None) or (headers.get('password') == None):
        print("SERVER LOG: " + formattedDateTime + " LOGIN FAILED")
        return f'HTTP/1.0 501 Not Implemented\r\n'
    else:
        username = headers["username"].replace("\r", "")
        password = headers["password"].replace("\r", "")
        #print("Username: " + username)
        #print("Password: " + password)
    
    if username in account_details:
        stored_password = account_details[username][0]
        #print("Stored password is: " + stored_password)
        salt = account_details[username][1]
        #print("Salt is: " + salt)
        password = password + salt
        #print("Password with salt appended to it: " + password)
        password = password.encode('utf-8')
        sha256_hash = hashlib.sha256()
        sha256_hash.update(password)
        hashed_password = sha256_hash.hexdigest()
        #print("Hashed password with salt is: " + hashed_password)
    
        if hashed_password == stored_password:
            #print("User exists!")

             sessionID = format(random.getrandbits(64), 'x')
             #random_hex = format(random_number, '016x')
             #sessionID = hex(random_number)
             #print(sessionID)

             #print("Random hex number is: " + session_id)

             timestamp = datetime.datetime.now()

             #print(timestamp)

             '''
             session_data = {
                 
                 sessionID : [username, timestamp]
                 
             }
             '''

             session_data.update({sessionID : [username, timestamp]})

             #print(session_data)

             print("SERVER LOG: " + formattedDateTime + " LOGIN SUCCESSFUL: " + username + " : " + (password.decode().replace(salt, "")))
             return f'HTTP/1.0 200 OK\r\nSet-Cookie: sessionID=0x{sessionID}\r\n\r\nLogged in!'

        else:
            print("SERVER LOG: " + formattedDateTime + " LOGIN FAILED: " + username + " : " + (password.decode().replace(salt, "")))
            return f'HTTP/1.0 200 OK\r\n\r\nLogin failed!'
    
    else:
        print("SERVER LOG: " + formattedDateTime + " LOGIN FAILED: " + username + " : " + password)
        return f'HTTP/1.0 200 OK\r\n\r\nLogin failed!'
    
    





def GETRequest(version, headers, target, session_timeout, root_directory):

    #Obtain cookies from HTTP request header
    cookie = headers["Cookie"].replace("sessionID=0x", "")
    cookie = cookie.replace("\r", "")
    #print(cookie)

    if cookie == "":
        return f'HTTP/1.0 401 Unauthorized\r\n'
    
    if cookie in session_data:
        username = session_data[cookie][0]
        #print(username)
        timestamp = session_data[cookie][1]
        #print(timestamp)
        #timestamp_seconds = timestamp.total_seconds()
        current_time = datetime.datetime.now()
        #current_time_seconds = current_time.total_seconds()
        
        if (current_time - timestamp).total_seconds() < int(session_timeout):
            session_data.update({cookie : [username, current_time]})

            if file_exists(root_directory, username, target) != False:
                file = file_exists(root_directory, username, target)
                log_timestamp = datetime.datetime.now()
                formattedDateTime = log_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
                print("SERVER LOG: " + formattedDateTime + " GET SUCCEEDED: " + username + " : " + target)
                return f'HTTP/1.0 200 OK\r\n\r\n{file}'
            else:
                log_timestamp = datetime.datetime.now()
                formattedDateTime = log_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
                print("SERVER LOG: " + formattedDateTime + " GET FAILED: " + username + " : " + target)
                return f'HTTP/1.0 404 NOT FOUND\r\n'
        else:
            log_timestamp = datetime.datetime.now()
            formattedDateTime = log_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
            print("SERVER LOG: " + formattedDateTime + " SESSION EXPIRED: " + username + " : " + target)
            return f'HTTP/1.0 401 Unauthorized\r\n'
    else:
        log_timestamp = datetime.datetime.now()
        formattedDateTime = log_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
        print("SERVER LOG: " + formattedDateTime + " COOKIE INVALID: " + target)
        return f'HTTP/1.0 401 Unauthorized\r\n'





def main():
 
    '''
    #From the command line, argv[0] = server.py
    input0 = sys.argv[0]
    print(input0)

    #From the command line, argv[1] = 127.0.0.1 [IP] - The IP address on which the server will bind to.
    input1 = sys.argv[1]
    print(input1)

    #From the command line, argv[2] = 8080 [PORT] - The port on which the server will listen for incoming connections.
    input2 = sys.argv[2]
    print(input2)

    #From the command line, argv[3] = accounts.json [ACCOUNTS_FILE] - A JSON file containing user accounts and their hashed passwords along with the corresponding salt.
    input3 = sys.argv[3]
    print(input3)

    #From the command line, argv[4] = 5 [SESSION_TIMEOUT] - The session timeout duration (in seconds).
    input4 = sys.argv[4]
    print(input4)
    
     #From the command line, argv[5] = accounts/ [ROOT_DIRECTORY] - The root directory containing user directories.
    input4 = sys.argv[5]
    print(input5)

    '''

    ip_address = sys.argv[1]
    port = sys.argv[2]
    accounts_file = sys.argv[3]
    session_timeout = sys.argv[4]
    root_directory = sys.argv[5]

    
    startServer(ip_address, port, accounts_file, session_timeout, root_directory)
    
    '''
    headers = {

        "username" : "Jerry",
        "password" : "4W61E0D8P37GLLX"

    }

    headers2 = {

        "Cookie" : "sessionID=0x68938897ef8fdfc8"
    }
    '''

    #POSTRequest("HTTP/1.0", headers, accounts_file)
    #GETRequest("HTTP/1.0", headers2, "/file.txt", session_timeout, root_directory)
    


if __name__ == "__main__":
    main()