# Set your server IP and port
SERVER_IP="127.0.0.1"
SERVER_PORT="8080"

# Variables for storing session cookies and response body
SESSION_COOKIE=""
RESPONSE_BODY=""

# Common curl options for HTTP/1.0 and connection close
CURL_OPTIONS="--http1.0 --connect-timeout 5 --max-time 10 --fail --silent"

# Test 1: No Username (POST at the root)
RESPONSE=$(curl -i -v -X POST -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/")
echo -e "\nTest 1: No Username Response:\n$RESPONSE"

# Test 2: No Password (POST at the root)
RESPONSE=$(curl -i -v -X POST -H "username: Richard" "http://${SERVER_IP}:${SERVER_PORT}/")
echo -e "\nTest 2: No Password Response:\n$RESPONSE"

# Test 3: Username incorrect (POST at the root)
RESPONSE=$(curl -i -v -X POST -H "username: IncorrectUser" -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/")
echo -e "\nTest 3: Username Incorrect Response:\n$RESPONSE"

# Test 4: Password incorrect (POST at the root)
RESPONSE=$(curl -i -v -X POST -H "username: Richard" -H "password: IncorrectPassword" "http://${SERVER_IP}:${SERVER_PORT}/")
echo -e "\nTest 4: Password Incorrect Response:\n$RESPONSE"

# Test 5: Username (1st username) correct/password correct (POST at the root)
RESPONSE=$(curl -i -v -X POST -H "username: Richard" -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/")
SESSION_COOKIE=$(echo "$RESPONSE" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)
echo -e "\nTest 5: Username/Password Correct Response:\n$RESPONSE"
echo -e "\nCookie (sessionID) for user: $SESSION_COOKIE"

# Test 6: Username (1st username) correct/password correct (POST at the root) -> Generate a new cookie
RESPONSE=$(curl -i -v -X POST -H "username: Richard" -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/")
NEW_SESSION_COOKIE=$(echo "$RESPONSE" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)
echo -e "\nTest 6: Generate New Cookie Response:\n$RESPONSE"
echo -e "\nNew Cookie (sessionID) for user: $NEW_SESSION_COOKIE"

# Test 7: Invalid cookie (GET)
RESPONSE=$(curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=InvalidCookie" "http://${SERVER_IP}:${SERVER_PORT}/file.txt")
echo -e "\nTest 7: Invalid Cookie Response:\n$RESPONSE" 

# Test 8: Username (1st username) (GET filename for user 1) correct
RESPONSE=$(curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt")
echo -e "\nTest 8: GET File for User 1 Response:\n$RESPONSE"

# Test 9: Username (2nd username) correct/password correct (POST)
RESPONSE=$(curl -i -v -X POST -H "username: Tammy" -H "password: PI97KS29IZ4IESA" "http://${SERVER_IP}:${SERVER_PORT}/")
ANOTHER_SESSION_COOKIE=$(echo "$RESPONSE" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)
echo -e "\nTest 9: Another User Login Response:\n$RESPONSE"
echo -e "\nNew Cookie (sessionID) for Another User: $ANOTHER_SESSION_COOKIE"

# Test 10: GET file successful (GET filename for user 2)
RESPONSE=$(curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$ANOTHER_SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt")
echo -e "\nTest 10: GET File for User 2 Response:\n$RESPONSE"

# Test 11: GET file not found (GET FAIL) Sleep for 6 seconds
RESPONSE=$(curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$ANOTHER_SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/nonexistent_file.txt")
echo -e "\nTest 11: GET Nonexistent File Response:\n$RESPONSE"
sleep 6

# Test 12: Expired cookie with username 2 (GET filename for user 2)
RESPONSE=$(curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$ANOTHER_SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt")
echo -e "\nTest 12: Expired Cookie Response:\n$RESPONSE"